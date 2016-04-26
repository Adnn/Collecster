#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Collecster.settings")
django.setup()

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


for release in Release.objects.all():
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
        print("{} on imaterial Release '{}'.".format(err, release))


for occurrence in Occurrence.objects.all():
    #
    # SPECIFIC & COLLECSTER_PROPERTIES
    #
    assigned_specific_classes = enforce_specific(occurrence)
    enforce_collecster_properties(occurrence, assigned_specific_classes)

    #
    # ATTRIBUTES
    #
    generic_release_attributes = utils.all_release_attributes(occurrence.release.pk)
    generic_occurrence_attributes = OccurrenceAttribute.objects.filter(occurrence=occurrence)
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

        # Enforces COMPOSITION::2.a)
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
    # IMMATERIAL special rules
    #
    # Enforces IMMATERIAL.2)
    if not occurrence.release.is_material():
        if not OccurrenceComposition.objects.filter(to_occurrence=occurrence).exists():
            print("Occurrence '{occ}' is immaterial, but is not nested under another occurrence.".format(occ=occurrence))

