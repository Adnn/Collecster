# TODO sort out enumeration
from data_manager import enumerations as enum
from data_manager import utils_payload
from data_manager import utils_id

from .models import *
from .configuration import ConfigNature
from .forms_admins import PropertyAwareSaveInitialDataModelForm

from django import forms
from django.contrib import admin
from django.db.models import Q
from django.forms.models import BaseInlineFormSet, modelformset_factory

import functools, collections

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

def specific_instance_callback(formset, request, obj, Model):
    Model.form_callback(formset[0], request, obj)

def admininline_factory(Model, Inline):
    classname = "{}{}".format(Model.__name__, "AdminInline")
    class_attributes = {"model": Model, "formset": OneFormFormSet, "min_num": 1, "max_num": 1, "can_delete": False}
    #{"model": Model, "extra": 2, "max_num": 1, "formset": inlineformset_factory(Release, Model,
    #  formset=DebugBaseInlineFormSet, fields="__all__", max_num=1, validate_max=True)}

    if hasattr(Model, "form_callback"):
        SpecificFormSet = type("{}SpecificFormSet".format(Model.__name__), (OneFormFormSet,),
                               {"collecster_instance_callback": functools.partialmethod(specific_instance_callback, Model=Model)})
        class_attributes["formset"] = SpecificFormSet

    return type(classname, (Inline,), class_attributes)

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
    concept_id = utils_id.get_concept_id(request, release=obj)
    return get_concept_specific_inlines(concept_id, ConfigNature.get_release_specifics) if concept_id != 0 else []

def occurrence_specific_inlines(request, obj):
    concept_id = utils_id.get_concept_id(request, occurrence=obj)
    return get_concept_specific_inlines(concept_id, ConfigNature.get_occurrence_specifics) if concept_id != 0 else []


def release_automatic_attributes(formset, request, obj):
    concept_id = utils_id.get_concept_id(request, release=obj)

    if not obj.pk: # test if the object is already in the DB, in which case the automatic attributes are not added
        formset.initial = [{"attribute": attribute} for attribute in retrieve_automatic_attributes(concept_id)]
    else:
        formset.extra = 1


def get_or_initial_release_corresponding_entry(form, release_corresponding_list, release_corresponding_field):
    """ This function is a helper to be used when initial_data should be assigned to forms """
    """ but only if they are not corresponding to an instance saved in the DB. """
    """ see populate_occurrence_attributes() comments for a rationale """
    # Nota: the following code assumes that all forms with an instance whose release_corresponding_entry is assigned
    # will come before the forms where it is not.
    try:
        # The forms are not bound, but their 'instance' field is assigned by the FormSet's _construct_form()
        # see: https://github.com/django/django/blob/1.9/django/forms/models.py#L592-L593 
        corresponding = getattr(form.instance, release_corresponding_field)
        in_db = True
    # Since release_corresponding_field is required, a DoesNotExist exception indicates that the instance is not in the DB
    # It seems that DoesNotExist derives from AttributeError, as we can catch that type here
    # thus uniformizing with OccurrenceAnyAttribute::release_corresponding_entry that raise AttributeError
    #except release_corresponding_list[0].__class__.DoesNotExist:
    except AttributeError:
        corresponding = release_corresponding_list[0]
        form.initial[release_corresponding_field] = corresponding
        in_db = False

    release_corresponding_list.remove(corresponding)
    return corresponding, in_db

    
def populate_occurrence_attributes(formset, request, obj):
    release_id = utils_id.get_release_id(request, obj)
    
    attributes = retrieve_noncustom_custom_release_attributes(release_id)
    force_formset_size(formset, len(attributes))

    # We had to move away from always assigning the initial value for release_corresponding_entry:
    # When "changing" and existing occurrence, if the Occurrence***Attribute are not saved in the same order as the Release***Attribute of the matching Release
    # (side note: this situation is treated as an error by formset clean)
    # the value assigned to initial would override the release_corresponding_entry saved in the DB,
    # but the associated attribute value would still be the one from the DB, causing a mismatch.
    #formset.initial = [{"release_corresponding_entry": attrib} for attrib in attributes]

    # Instead, we create a list of all Release***Attribute assigned to the correponding release, and remove from this list
    # the Release***Attribute which already have a matchin Occurrence***Attribute saved to the DB.
    attribute_list = list(attributes)

    for form in formset:
        rel_attrib, in_db = get_or_initial_release_corresponding_entry(form, attribute_list, "release_corresponding_entry")

        # This is very important: by default, forms in formsets have empty_permitted set to True
        # Then, a form with no other value than the initial(s) would skip fields validation, not populating cleaned_data     
        # see: https://github.com/django/django/blob/1.8.3/django/forms/forms.py#L389
        form.empty_permitted=False 
        form.fields["value"] = enum.Attribute.Type.to_form_field[rel_attrib.attribute.value_type]
        if not in_db:
            form.initial.update({
                "attribute_type": ContentType.objects.get_for_model(rel_attrib.__class__),
                "attribute_id": rel_attrib.pk,
            })


def occurrence_composition_queryset(formset, request, obj):
    release_id = utils_id.get_release_id(request, obj)

    if release_id == 0:
        force_formset_size(formset, 0)
    else:
        release_compositions = retrieve_release_composition(release_id)
        force_formset_size(formset, len(release_compositions))
            ## Does not help with saving the emtpy forms (only with their initial values)...
        #formset.validate_min = True
        #formset.validate_max = True

        # Would not be a safe approach, see comment in populate_occurrence_attributes()
        #formset.initial = [{"release_composition": compo} for compo in release_compositions]

        release_compositions = list(release_compositions)

        for form in formset:
            release_compo, in_db = get_or_initial_release_corresponding_entry(form, release_compositions, "release_composition")

            release = release_compo.to_release
            #form.empty_permitted=False ## Does not help with empty forms either
            form.fields["to_occurrence"].queryset = (
                Occurrence.objects.filter(release=release)  # only propose occurrences of the right release
                                  .filter(Q(occurrence_composition__isnull=True) # not already nested in another occurrence
                                          | Q(occurrence_composition__from_occurrence=formset.instance)) # except if nested in this occurrence (for edit)
            )
            form.fields["to_occurrence"].label = "Nested {} occurrence".format(release.name)


##
## Formset helpers
##
def force_formset_size(formset, size):
    formset.extra   = size
    formset.max_num = size


##
def retrieve_any_attributes(AttributeModel, release_id):
    return (AttributeModel.objects.filter(release=release_id).order_by("pk")) if release_id else []

def retrieve_release_composition(release_id):
    return ReleaseComposition.objects.filter(from_release=release_id).order_by("pk") ## on the "through" table
     ## Would return Release instances, NOT ReleaseComposition objects
    #return Release.objects.get(pk=release_id).nested_releases.all()

def retrieve_automatic_attributes(concept_id):
    return ConfigNature.get_concept_automatic_attributes(Concept.objects.get(pk=concept_id)) if concept_id else []

def shared_release_attributes(release_id):
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

def retrieve_noncustom_custom_release_attributes(release_id):
    return shared_release_attributes(release_id) + list(retrieve_any_attributes(ReleaseCustomAttribute, release_id))
