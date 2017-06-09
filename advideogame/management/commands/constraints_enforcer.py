#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Must be first
#import os, django
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Collecster.settings")
#django.setup()

from advideogame.models import *
from advideogame.configuration import *
from advideogame import utils
from supervisor.models import *

import itertools


def cls_name(cls):
    return cls.__name__

def all_subclasses(cls):
    #return set(cls.__subclasses__() + [all_subclasses(subclass) for subclass in cls.__subclasses__()])
    return cls.__subclasses__() + [subsub for subclass in cls.__subclasses__() for subsub in all_subclasses(subclass)]

all_specifics = {
    Release:    [SpecificModel for SpecificModel in all_subclasses(ReleaseSpecific.AbstractBase) if not SpecificModel._meta.abstract],
    Occurrence: [SpecificModel for SpecificModel in all_subclasses(OccurrenceSpecific.AbstractBase) if not SpecificModel._meta.abstract],
}

def specific_Q(instance):
    return {
        Release: Q(release=instance),
        Occurrence: Q(occurrence=instance),
    }[instance.__class__]

def assigned_specifics(instance):
    cls = instance.__class__
    return [SpecificModel for SpecificModel in all_specifics[cls] if SpecificModel.objects.filter(specific_Q(instance)).exists()]

def get_field_data(instance, field_name):
    data = getattr(instance, field_name)
    #if isinstance(data, ManyRelatedManager): # Cannot find a way to import ManyRelatedManager, which is defined inside a function
    if hasattr(data, "all"): # Our way to check if data is a ManyRelatedManager
        data = [val for val in data.all()]
    return data


def enforce_specific(instance):
    natures = instance.concept.all_nature_tuple
    if isinstance(instance, Release):
        expected_specific_classes = set(ConfigNature.get_release_specifics(natures))
    elif isinstance(instance, Occurrence):
        expected_specific_classes = set(ConfigNature.get_occurrence_specifics(natures))
    assigned_specific_classes = set(assigned_specifics(instance))

    if expected_specific_classes != assigned_specific_classes:
        print("'{}', with natures {}, would expect the following specific classes {}, but instead was assigned {}"
                .format( instance, natures,
                         list(map(cls_name, expected_specific_classes)),
                         list(map(cls_name, assigned_specific_classes)) ))

    return assigned_specific_classes


def enforce_collecster_properties(instance, assigned_specific_classes):
    errors = CollecsterPropertiesHelper.validate(instance, instance, get_field_data)
    if errors:
        print ("'{}' has errors on 'collecster_properties': {}".format(instance, errors))
    for specific in [SpecificModel.objects.get(specific_Q(instance)) for SpecificModel in assigned_specific_classes]:
        errors = CollecsterPropertiesHelper.validate(specific, instance, get_field_data)
        if errors:
            print ("Specific '{}' associated to '{}' has errors on 'collectser_properties': {}".format(specific, instance, errors))


def instance_cleaner(instance):
    try:
        instance.full_clean()
    except ValidationError as e:
        print ("{classname} '{instance}' has validation errors: {errors}"
                    .format(classname=instance.__class__.__name__, instance=instance, errors=e))

def model_cleaner(model_class):
    for instance in model_class.objects.all():
        instance_cleaner(instance)


#####
# Main entry point
#####
def enforce_main(command):

    ##
    ## Concepts
    ##
    for concept in Concept.objects.all():
        # Enforces CONCEPT::1.b)
        if concept.primary_nature in concept.additional_nature_set.values_list("nature", flat=True):
            print("Concept '{con}' has it primary nature '{nat}' repeated in its additional natures."
                    .format(con=concept, nat=concept.primary_nature))

        if concept.distinctive_name.startswith('_'):
            # Enforces SPECIAL_CONCEPT::2.a)
            if concept.primary_nature != concept.distinctive_name:
                print("Special concept '{con}' has primary nature '{nat}', when it has to be '{exp}'."
                        .format(con=concept, nat=concept.primary_nature, exp=concept.distinctive_name))
            # Enforces SPECIAL_CONCEPT::2.b)
            if concept.additional_nature_set.exists():
                print("Special concept '{con}' is not allowed to have additional natures"
                        .format(con=concept))
        else:
            # Enforces SPECIAL_CONCEPT::2.c)
            special_natures = list(filter(lambda x: x.startswith('_'), concept.all_nature_tuple))
            if special_natures: # in case there are nature(s) starting with '_'
                print("Concept '{con}' is not special, thus it cannot have natures '{nats}'"
                        .format(con=concept, nats=", ".join(special_natures)))


    ##
    ## Releases
    ##
    for release in Release.objects.all():
        # clean (partial dates)
        instance_cleaner(release)

        # specific composition
        assigned_specific_classes = enforce_specific(release)

        # collecster_properties
        enforce_collecster_properties(release, assigned_specific_classes)

        ## immaterial special rules
        immaterial_errors = []
        if not release.is_material():
            # Enforces IMMATERIAL.1)
            if release.nested_releases.count():
                immaterial_errors.append("Nested releases are not allowed")
            # Enforces IMMATERIAL.3)
            if release.attributes.filter(attribute__name="self", attribute__category__name="content").count():
                immaterial_errors.append("[content] self is not allowed")
        for err in immaterial_errors:
            print("{} on imaterial Release '{}'.".format(err, release))

        ## Special case rules
        if release.special_case_release:
            # Enforces SpecialCase_Release::1)
            if release.nested_releases.count():
                command.warn("Release(s) were nested under the special case release '{}'".format(release))

            if release.special_case_release == "L" : # loose
                # Enforces SpecialCase_Release::2)
                if release.releasecomposition_set.exists():
                    command.warn("Release '{}' is *loose*, yet it is nested under other release(s): {}"
                                    #.format(release, release.releasecomposition_set.all()))
                                    .format(release, Release.objects.filter(nested_releases=release)))
                
        #
        # Regions
        #
        for parent_release in [release_compo.from_release for release_compo in release.releasecomposition_set.all()]:
            # Enforces RELEASE_REGIONS::2) 
            if ( release.release_regions.exists() 
                 and not utils.is_region_superset(release.release_regions.all(), parent_release.release_regions.all()) ):
                command.error("Release '{}' release-regions are {}. Yet it is nested under '{}' whose release-regions "
                              "{} are not strictly included"
                                .format(release, release.release_regions.all(),
                                        parent_release, parent_release.release_regions.all()))
        

    ##
    ## Occurrences
    ##
    for occurrence in Occurrence.objects.all():
        instance_cleaner(occurrence)

        #
        # SPECIFIC & COLLECSTER_PROPERTIES
        #
        assigned_specific_classes = enforce_specific(occurrence)
        enforce_collecster_properties(occurrence, assigned_specific_classes)

        #
        # ATTRIBUTES
        #
        generic_release_attributes = utils.retrieve_noncustom_custom_release_attributes(occurrence.release.pk)
        generic_occurrence_attributes = OccurrenceAnyAttribute.objects.filter(occurrence=occurrence).order_by("pk")
        for index, (release_att, occurrence_att) \
        in enumerate(itertools.zip_longest(generic_release_attributes, generic_occurrence_attributes)):
            corresponding_att = occurrence_att.release_corresponding_entry if occurrence_att else None

            # Enforces ATTRIBUTES::2.c)
            if corresponding_att and corresponding_att.release != occurrence.release:
                print("Occurrence '{occ}' has attribute '{occ_att}' in position {index} (zero indexed), which release {att_rel} does not match."
                            .format(att_rel=corresponding_att.release, index=index, occ=occurrence, occ_att=corresponding_att))
                continue
                
            # Enforces ATTRIBUTES::2.a) and ATTRIBUTES::2.d)
            if corresponding_att != release_att:
                    print("Release '{rel}' has attribute '{rel_att}' in position {index} (zero indexed), but occurrence '{occ}' has '{occ_att}'"
                            .format(rel=occurrence.release, rel_att=release_att, index=index, occ=occurrence, occ_att=corresponding_att))

            # Enforces ATTRIBUTES::3)
            if occurrence_att:
                # has to handle empty value as a special case: it is a choice on rating, but is not allowed by the form.
                if occurrence_att.value == "" or not OccurrenceAnyAttributeBase.is_clean_value(occurrence_att.value, corresponding_att):
                    print("Occurrence '{occ}' has attribute '{occ_att}' in position {index} (zero indexed), whose value {value} is not allowed."
                            .format(index=index, occ=occurrence, occ_att=corresponding_att, value=occurrence_att.value))

        #
        # COMPOSITION
        #
        release_composition = ReleaseComposition.objects.filter(from_release=occurrence.release)
        occurrence_composition = OccurrenceComposition.objects.filter(from_occurrence=occurrence)
        for index, (release_compo, occurrence_compo) \
        in enumerate(itertools.zip_longest(release_composition, occurrence_composition)):
            corresponding_compo = occurrence_compo.release_composition if occurrence_compo else None

            # Enforces COMPOSITION::2.c)
            if corresponding_compo:
                if corresponding_compo.from_release != occurrence.release:
                    print("Occurrence '{occ}' has composition '{occ_compo}' in position {index} (zero indexed), whose source release {compo_rel} does not match this occurrence release."
                                .format(compo_rel=corresponding_compo.from_release, index=index, occ=occurrence, occ_compo=corresponding_compo))
                    continue

            # Enforces COMPOSITION::2.a) and COMPOSITION::2.1)
            if corresponding_compo != release_compo:
                    print("Release '{rel}' has composition '{rel_compo}' in position {index} (zero indexed), but occurrence '{occ}' has '{occ_compo}'"
                            .format(rel=occurrence.release, rel_compo=release_compo, index=index, occ=occurrence, occ_compo=corresponding_compo))
        
        # Enforces COMPOSITION::3.a)
        for occurrence_compo_target in OccurrenceComposition.objects.filter(to_occurrence=occurrence):
            expected_target_release = occurrence_compo_target.release_composition.to_release
            if  expected_target_release != occurrence.release:
                    print("Occurrence '{occ}' is the target of '{occ_compo}', which expects an occurrence instantiating release '{rel}'"
                                .format(occ=occurrence, occ_compo=occurrence_compo_target.release_composition,
                                        rel=expected_target_release))
        #
        # PICTURES
        #
        for picture in occurrence.pictures.all():
            if picture.detail == PictureDetail.GROUP:
                # Enforces ADVIDEOGAME::1.b)
                try:
                    picture.release_corresponding_entry
                    print("Occurrence '{occ}' has picture '{pic}' detailing GROUP, which is not allowed to be assigned a release attribute."
                            .format(occ=occurrence, pic=picture))
                except AttributeError:
                    pass
            else:
                try:
                    # Enforces ADVIDEOGAME::1.a)
                    if picture.release_corresponding_entry.release != occurrence.release:
                        print("Occurrence '{occ}' has picture '{pic}', attached to an attribute of a different release '{rel}'"
                                .format(occ=occurrence, pic=picture, rel=picture.release_corresponding_entry.release))
                except AttributeError:
                    # Enforces ADVIDEOGAME::1.c)
                    print("Occurrence '{occ}' has picture '{pic}' of detail '{det}', but it is not associated to an attribute release."
                            .format(occ=occurrence, pic=picture, det=picture.detail))

        #
        # TAG TO OCCURRENCE
        #
        # Enforces TAGTOOCCURRENCE::1.a)
        if not TagToOccurrence.objects.filter(occurrence=occurrence).exists():
            command.error("Occurrence '{occ}' does not have a TagToOccurrence instance associated to it.".format(occ=occurrence))

        #
        # IMMATERIAL special rules
        #
        # Enforces IMMATERIAL.2)
        if not occurrence.release.is_material():
            if not OccurrenceComposition.objects.filter(to_occurrence=occurrence).exists():
                command.warn("Occurrence '{occ}' is immaterial, but is not nested under another occurrence.".format(occ=occurrence))

    #
    # PLATFORM
    #

    # Enforces PLATFORM::1)
    for required_interface in RequiredInterface.objects.filter(reused_interface__isnull=False):
        command.error("The required interface index #{}, found in '{}', is not allowed to reuse another interface."
                        .format(required_interface.pk, utils.find_interface_detail(required_interface)))
    
    ReuseTuple = collections.namedtuple("ReuseTuple", ("reusing_specinterface", "reused_mediapair"))
    specs_with_reuse = {}
    # First, generate a lookup table 'specs_with_reuse', associating each InterfaceSpecification to both
    # a list of its reusing interface and a list of its reused interfaces
    for provided_interface in ProvidedInterface.objects.filter(reused_interface__isnull=False):
        # { InterfaceSpecification: ([ReusingBaseSpecificationInterface], [ReusedSystemMediaPair])  }
        data = specs_with_reuse.setdefault(utils.find_interface_detail(provided_interface).interfaces_specification,
                                           ReuseTuple([], []))
        data.reusing_specinterface.append(provided_interface)
        data.reused_mediapair.append(provided_interface.reused_interface)

    # Use the lookup table to find any reused interface that would itself reuse an interface
    for interface_spec, reuse_tuple in specs_with_reuse.items():
        # Enforces PLATFORM::2)
        for provided_interface in [provided_interface for provided_interface in reuse_tuple.reusing_specinterface
                                                      if provided_interface.interface in reuse_tuple.reused_mediapair
                                                      if provided_interface.interface != provided_interface.reused_interface]:
            command.error("The interface index #{pk}, provided by '{spec}' is reused in this same specification, " \
                          "so it is not allowed to itself reuse {mp} ."
                            .format(pk=provided_interface.pk, spec=interface_spec, mp=provided_interface.reused_interface))


    ## More composition
    # Enforces COMPOSITION::1)
    model_cleaner(ReleaseComposition)

    ## Bundles
    model_cleaner(PurchaseContext)
    model_cleaner(Purchase)
