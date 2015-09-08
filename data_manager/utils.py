from django.contrib import admin

from . import configuration as conf
from . import enumerations as enum
from .models import *

from django import forms

#Todel ?
from django.forms.models import inlineformset_factory, BaseInlineFormSet
import wdb

#class DebugBaseInlineFormSet(BaseInlineFormSet):
#    @property
#    def validate_max(self):
#        wdb.set_trace()
#        return True
#
#    @property
#    def validate_max(self, value):
#        self.validate_max = value
#
#    def full_clean(self):
#        wdb.set_trace()
#        super(DebugBaseInlineFormSet, self).full_clean()


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

def get_concept_inlines(concept_id, specifics_retriever):
    # todo: make it span all natures
    nature_set = Concept.objects.get(pk=concept_id).all_nature_tuple

    AdminInlines = []
    for ReleaseSpecific in specifics_retriever(nature_set):
        AdminInlines.append(admininline_factory(ReleaseSpecific, admin.StackedInline))

    return AdminInlines


def release_specific_inlines(request, obj):
    concept_id = 0
    if obj is not None:
        concept_id = obj.concept.pk
    elif hasattr(request, "collecster_payload") and "concept_id" in request.collecster_payload:
        concept_id = request.collecster_payload["concept_id"]

    return get_concept_inlines(concept_id, conf.ConceptNature.get_release_specifics) if concept_id != 0 else []

def occurrence_specific_inlines(request, obj):
    concept_id = 0
    if obj is not None:
        concept_id = obj.release.concept.pk
    elif hasattr(request, "collecster_payload") and "concept_id" in request.collecster_payload:
        concept_id = request.collecster_payload["concept_id"]

    return get_concept_inlines(concept_id, conf.ConceptNature.get_occurrence_specifics) if concept_id != 0 else []


    
def populate_occurrence_attributes(formset, request, obj, retrieve_function):
    if obj and hasattr(obj, "release"):
        release_id = obj.release.pk
    else:
        release_id = get_request_payload(request, "release_id", 0)
    
    attributes = retrieve_function(release_id)
    force_formset_size(formset, len(attributes))
    formset.initial = [{"release_corresponding_entry": attrib} for attrib in attributes]
    for form, rel_attrib in zip(formset, attributes):
        # This is very important: by default, forms in formsets have empty_permitted set to True
        # Then, a form with no other value than the initial(s) would skip fields validation, not populating cleaned_data     
        # see: https://github.com/django/django/blob/1.8.3/django/forms/forms.py#L389
        form.empty_permitted=False 
        form.fields['value'] = enum.Attribute.Type.to_form_field[rel_attrib.attribute.value_type]


##
## Request helpers
##
def get_request_payload(request, key, default=None):
    if hasattr(request, "collecster_payload") and key in request.collecster_payload:
        return request.collecster_payload[key] 
    return default 


  ## Dangerous, if var is immutable
#def get_request_payload_to_var(request, key, var):
#    if hasattr(request, "collecster_payload") and key in request.collecster_payload:
#        var = request.collecster_payload[key] 
#        print("Vr {}:".format(var))
#        return True
#    else:
#        return False

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
    return ReleaseComposition.objects.filter(container_release=release_id)

