# TODO sort out enumeration
from data_manager import enumerations as enum
from data_manager import utils_payload

from .models import *
from .configuration import ConfigNature
from .forms_admins import PropertyAwareSaveInitialDataModelForm

from django import forms
from django.contrib import admin
from django.db.models import Q
from django.forms.models import BaseInlineFormSet, modelformset_factory

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


## Note: inherits from SaveInitialDataModelForm: in a situation where the model for a specific has defaults
## for each required field, we want it to be saved to DB even if the user leaves all fields to default.
## Also inherits from PropertyAware, so "collecster_properties" rule are available on specifics.
class SpecificForm(PropertyAwareSaveInitialDataModelForm):
    def get_base_instance(self):
        """ Needs to forward the base instance as the instance to which the specific as a relation. """
        return self.instance.get_parent_instance()

class SpecificStackedInline(admin.StackedInline):
    """ This derived inline allows to render the inline using admin_edit_inline_wrapper template. """
    """ This template simply render the original template, but wrapped in an additional custom <div>. """
    """ Those custom divs can then be identified by a JS script and be re-rooted under  """
    """ the #collecster_specifics <div>, supposed to contain all specifics. """
    """ """
    """ It also allows to specify a custom form, to handle collecster properties """
    collecster_wrapped_template = admin.StackedInline.template
    template = "collecster/admin_edit_inline_wrapper.html"
    form = SpecificForm

def admininline_factory(Model, Inline):
    classname = "{}{}".format(Model.__name__, "AdminInline")
    return type(classname, (Inline,), {"model": Model, "formset": OneFormFormSet,
                                       "min_num": 1, "max_num": 1, "can_delete": False})
    #tp = type(classname, (Inline,), {"model": Model, "extra": 2, "max_num": 1, "formset": inlineformset_factory(Release, Model, formset=DebugBaseInlineFormSet, fields="__all__", max_num=1, validate_max=True)})


def get_concept_id(request, release=None, occurrence=None):
    # Even if the forwarded object is not None, it could not have its related field not populated:
    # Eg. On creation of the empty form for a Release, a default constructed Release instance is forwarded to formsets
    # see: https://github.com/django/django/blob/1.8.3/django/contrib/admin/options.py#L1480

    # See forms_admins.py _collecster_fixup_request()
    release = release if release else utils_payload.get_request_payload(request, "release")
    occurrence = occurrence if occurrence else utils_payload.get_request_payload(request, "occurrence")

    if release and hasattr(release, "concept"):
        return release.concept.pk
    elif occurrence and hasattr(occurrence, "release"):
        return occurrence.release.concept.pk
    else:
        concept_id = utils_payload.get_request_payload(request, "concept_id", 0)
        if not concept_id:
            release_id = utils_payload.get_request_payload(request, "release_id", 0)
            if release_id:
                concept_id = Release.objects.get(pk=release_id).concept.pk
        return concept_id


def get_release_id(request, occurrence=None):
    # Even if the forwarded object is not None, it could not have its related field not populated
    if occurrence is not None and hasattr(occurrence, "release"):
        return occurrence.release.pk
    else:
        return utils_payload.get_request_payload(request, "release_id", 0)


def get_natures_specific_inlines(nature_set, specifics_retriever):
    AdminInlines = []
    for SpecificModel in specifics_retriever(nature_set):
        AdminInlines.append(admininline_factory(SpecificModel, SpecificStackedInline))

    return AdminInlines

def get_concept_specific_inlines(concept_id, specifics_retriever):
    nature_set = Concept.objects.get(pk=concept_id).all_nature_tuple
    return get_natures_specific_inlines(nature_set, specifics_retriever)

def get_concept_nature_set(request, obj):
    """ Retrieves the list of natures for a concept. """
    """ It is intended for the Concept form, and uniformizes the different sources for this list of natures """
    """ 1. Tries to retrieve it from the collecster payload in the request (populated by the ajax view, for live changes to the nature values) """
    """ 2. Tries to retrieve it from the POST data (usefull when there are errors in the Concept form, and it is re-presented to the user) """
    """ 3. Tries to retrieve it from the concept object (usefull when the form is used to change an existing Concept) """
    ConceptNatureFormSet = modelformset_factory(ConceptNature, fields="__all__")
    concept = obj if obj else utils_payload.get_request_payload(request, "concept")

    nature_set = utils_payload.get_request_payload(request, "nature_set", [])

    if not nature_set and request.method == "POST":
        formset = ConceptNatureFormSet(request.POST, prefix="additional_nature_set")
        formset.is_valid() # populate the cleaned_data member of each form
        for form in formset:
            if form.cleaned_data.get("nature"):
                nature_set.append(form.cleaned_data.get("nature"))
        if nature_set and concept and concept.primary_nature:
            nature_set.insert(0, concept.primary_nature)

    if not nature_set and concept:
        nature_set = list(concept.all_nature_tuple)

    return nature_set


def concept_specific_inlines(request, obj):
    nature_set = get_concept_nature_set(request, obj)
    return get_natures_specific_inlines(nature_set, ConfigNature.get_concept_specifics) if nature_set else []

def release_specific_inlines(request, obj):
    concept_id = get_concept_id(request, release=obj)
    return get_concept_specific_inlines(concept_id, ConfigNature.get_release_specifics) if concept_id != 0 else []

def occurrence_specific_inlines(request, obj):
    concept_id = get_concept_id(request, release=obj)
    return get_concept_specific_inlines(concept_id, ConfigNature.get_occurrence_specifics) if concept_id != 0 else []


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
    return ConfigNature.get_concept_automatic_attributes(Concept.objects.get(pk=concept_id)) if concept_id else []

def all_release_attributes(release_id):
    """ Returns non-custom attributes for a Release """
    """ Is a layer of abstraction in case we later introduce implicit attributes (not stored in the DB for each release, but logically present) """
    if not release_id:
        return []

    if isinstance(release_id, Release):
        release = release_id
    else:
        release = Release.objects.get(pk=release_id)

    attributes = []
    # get the implicit attributes first, disabled
    #attributes = ConfigNature.get_release_implicit_attributes(release)

    # then the explicit (non-custom) attributes
    attributes.extend(retrieve_any_attributes(ReleaseAttribute, release))
    return attributes
