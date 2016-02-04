
#from . import configuration as conf
#from shared import ConfNature as ConceptNature

# TODO
from data_manager import enumerations as enum

from .models import *
from .configuration import ConceptNature

from django import forms
from django.contrib import admin
from django.db.models import Q
from django.forms.models import BaseInlineFormSet

## TODEL
#import wdb


class OneFormFormSet(BaseInlineFormSet):
    """ We just need to have validate_min and _max set to True on the FormSet class used by the Admin """
    """ It seems impossible to forward them: https://groups.google.com/d/msg/django-users/xu2Ef7y4DPQ/u3z30vl_BwAJ """
    """ So hardcode the two attributes in the constructor """
    def __init__(self, data=None, files=None, instance=None,
                 save_as_new=False, prefix=None, queryset=None, **kwargs):
        super(OneFormFormSet,self).__init__(data, files, instance, save_as_new, prefix, queryset, **kwargs)
        self.validate_min = True
        self.validate_max = True


def admininline_factory(Model, Inline):
    classname = "{}{}".format(Model.__name__, "AdminInline")
    return type(classname, (Inline,), {"model": Model, "formset": OneFormFormSet,
                                       "min_num": 1, "max_num": 1, "can_delete": False})
    #tp = type(classname, (Inline,), {"model": Model, "extra": 2, "max_num": 1, "formset": inlineformset_factory(Release, Model, formset=DebugBaseInlineFormSet, fields="__all__", max_num=1, validate_max=True)})
    #wdb.set_trace() 
    #return tp


def get_concept_id(request, release=None, occurrence=None):
    # Even if the forwarded object is not None, it could not have its related field not populated:
    # Eg. On creation of the empty form for a Release, a default constructed Release instance is forwarded to formsets
    # see: https://github.com/django/django/blob/1.8.3/django/contrib/admin/options.py#L1480
    if release is not None and hasattr(release, "concept"):
        return release.concept.pk
    elif occurrence is not None and hasattr(occurrence, "release"):
        return occurrence.release.concept.pk
    else:
        concept_id = get_request_payload(request, "concept_id", 0)
        if not concept_id:
            release_id = get_request_payload(request, "release_id", 0)
            if release_id:
                concept_id = Release.objects.get(pk=release_id).concept.pk
        return concept_id


def get_release_id(request, occurrence=None):
    # Even if the forwarded object is not None, it could not have its related field not populated
    if occurrence is not None and hasattr(occurrence, "release"):
        return occurrence.release.pk
    else:
        return get_request_payload(request, "release_id", 0)


def get_concept_inlines(concept_id, specifics_retriever):
    nature_set = Concept.objects.get(pk=concept_id).all_nature_tuple

    AdminInlines = []
    for ReleaseSpecific in specifics_retriever(nature_set):
        AdminInlines.append(admininline_factory(ReleaseSpecific, admin.StackedInline))

    return AdminInlines


def release_specific_inlines(request, obj):
    concept_id = get_concept_id(request, release=obj)
    return get_concept_inlines(concept_id, ConceptNature.get_release_specifics) if concept_id != 0 else []

def occurrence_specific_inlines(request, obj):
    concept_id = get_concept_id(request, release=obj)
    return get_concept_inlines(concept_id, ConceptNature.get_occurrence_specifics) if concept_id != 0 else []


def release_automatic_attributes(formset, request, obj):
    concept_id = get_concept_id(request, release=obj)

    if not obj.pk: # test if the object is already in the DB, in which case the automatic attributes are not added
        formset.initial = [{"attribute": attribute} for attribute in retrieve_automatic_attributes(concept_id)]
    else:
        formset.extra = 1

    
def populate_occurrence_attributes(formset, request, obj, retrieve_function):
    release_id = get_release_id(request, obj)
    
    attributes = retrieve_function(release_id)
    force_formset_size(formset, len(attributes))
    formset.initial = [{"release_corresponding_entry": attrib} for attrib in attributes]
    for form, rel_attrib in zip(formset, attributes):
        # This is very important: by default, forms in formsets have empty_permitted set to True
        # Then, a form with no other value than the initial(s) would skip fields validation, not populating cleaned_data     
        # see: https://github.com/django/django/blob/1.8.3/django/forms/forms.py#L389
        form.empty_permitted=False 
        form.fields['value'] = enum.Attribute.Type.to_form_field[rel_attrib.attribute.value_type]


def occurrence_composition_queryset(formset, request, obj):
    release_id = get_release_id(request, obj)

    if release_id == 0:
        force_formset_size(formset, 0)
    else:
        release_compositions = retrieve_release_composition(release_id)
        force_formset_size(formset, len(release_compositions))
            ## Does not help with saving the emtpy forms (only with their initial values)...
        #formset.validate_min = True
        #formset.validate_max = True
        formset.initial = [{"release_composition": compo} for compo in release_compositions]

        for compo, form in zip(release_compositions, formset):
            release = compo.to_release
            #form.empty_permitted=False ## Does not help with empty forms either
            form.fields["to_occurrence"].queryset = (
                Occurrence.objects.filter(release=release)  # only propose occurrences of the right release
                                  .filter(Q(occurrence_composition__isnull=True) # not already nested in another occurrence
                                          | Q(occurrence_composition__from_occurrence=formset.instance)) # except if nested in this occurrence (for edit)
            )
            print(form.fields["to_occurrence"].queryset)
            form.fields["to_occurrence"].label     = "Nested {} occurrence".format(release.name)


##
## Request helpers
##
def set_request_payload(request, key, value):
    if not hasattr(request, "collecster_payload"):
        request.collecster_payload = {}
    request.collecster_payload[key] = value; 

def get_request_payload(request, key, default=None):
    if hasattr(request, "collecster_payload") and key in request.collecster_payload:
        return request.collecster_payload[key] 
    return default 


##
## Formset helpers
##
def force_formset_size(formset, size):
    formset.extra   = size
    formset.max_num = size


##
def retrieve_any_attributes(AttributeModel, release_id):
    return (AttributeModel.objects.filter(release=release_id)) if release_id else []

def retrieve_release_composition(release_id):
    return ReleaseComposition.objects.filter(from_release=release_id) ## on the "through" table
     ## Would return Release instances, NOT ReleaseComposition objects
    #return Release.objects.get(pk=release_id).nested_releases.all()

def retrieve_automatic_attributes(concept_id):
    return ConceptNature.get_concept_automatic_attributes(Concept.objects.get(pk=concept_id)) if concept_id else []

def all_release_attributes(release_id):
    if not release_id:
        return []

    if isinstance(release_id, Release):
        release = release_id
    else:
        release = Release.objects.get(pk=release_id)

    attributes = []
    # get the implicit attributes first, disabled
    #attributes = ConceptNature.get_release_implicit_attributes(release)

    # then the explicit (non-custom) attributes
    attributes.extend(retrieve_any_attributes(ReleaseAttribute, release))
    return attributes
