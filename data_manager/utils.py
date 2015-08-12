from django.contrib import admin

from . import configuration as conf
from .models import *

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


def dynamic_release_inlines(request, obj):
    concept_id = 0
    if obj is not None:
        concept_id = obj.concept.pk
    elif hasattr(request, "collecster_payload") and "concept" in request.collecster_payload:
        concept_id = request.collecster_payload["concept"]

    return get_concept_inlines(concept_id, conf.ConceptNature.get_release_specifics) if concept_id != 0 else []

def dynamic_occurrence_inlines(request, obj):
    concept_id = 0
    if obj is not None:
        concept_id = obj.release.concept.pk
    elif hasattr(request, "collecster_payload") and "concept" in request.collecster_payload:
        concept_id = request.collecster_payload["concept"]

    return get_concept_inlines(concept_id, conf.ConceptNature.get_occurrence_specifics) if concept_id != 0 else []
