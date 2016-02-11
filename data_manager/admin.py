from . import utils
from .forms_admins import SaveInitialDataModelForm, CustomSaveModelAdmin, CollecsterModelAdmin

from .models import *
from supervisor.models import Person

from data_manager import widgets 
from data_manager import enumerations as enums

from django import forms
from django.contrib import admin
from django.core.exceptions import FieldDoesNotExist
from django.forms.models import modelform_factory

from functools import partial, partialmethod
from collections import OrderedDict

## TODEL ##
#import wdb


##########
## Concept
##########

class ConceptNatureInline(admin.TabularInline):
    extra = 0
    model = ConceptNature
    can_delete = False


class ConceptAdmin(CustomSaveModelAdmin):
    exclude = ("created_by",)
    inlines = (ConceptNatureInline,)


##########
## Release
##########

class OnlyOnMaterialFormSet(forms.BaseInlineFormSet):
    def clean(self):
        if not self.instance.is_material():
            for form in self:
                if form.has_changed(): # This is the criterion used by BaseModelfFormSet.save_new_object() to decide whether to save the object
                    raise forms.ValidationError("Immaterial release cannot be attached those inlines.",
                                                code='invalid')


class ReleaseDistinctionInline(admin.TabularInline):
    extra = 1
    model = ReleaseDistinction

class ReleaseAttributeFormset(OnlyOnMaterialFormSet):
    collecster_instance_callback = utils.release_automatic_attributes

class ReleaseAttributeInline(admin.TabularInline):
    extra = 3
    model = ReleaseAttribute
    can_delete = False
    formset = ReleaseAttributeFormset
    form = modelform_factory(ReleaseAttribute, form=SaveInitialDataModelForm, fields="__all__")

class ReleaseCustomAttributeInline(admin.TabularInline):
    extra = 0
    model = ReleaseCustomAttribute
    can_delete = False
    formset = OnlyOnMaterialFormSet


class ReleaseCompositionInline(admin.TabularInline):
    verbose_name = verbose_name_plural = "Release composition"
    model = Release.nested_releases.through
    fk_name = 'from_release' # This seems to be the hardcoded name automatically given by Django 
    formset = OnlyOnMaterialFormSet


class ReleaseForm(forms.ModelForm):
    ## Override the partial_date_precision field for two customizations :
    ## 1) Changes the use widget to be a RadioSelect (customized for single line rendering)
    ## 2) Do not display an emtpy value even though the model field allows blank (the choices do not contain the emtpy value)
    partial_date_precision = forms.ChoiceField(choices=ReleaseBase._meta.get_field("partial_date_precision").choices, required=False,
                                               widget=widgets.RadioSelectOneLine)
        
    ## Would be less intrusive, but does not allow to control the choices proposed by the widget
    #class Meta:
    #    widgets = {"partial_date_precision": widgets.RadioSelectOneLine} 


def get_release_readonlyedit():
    """ The immaterial field is not mandatory on Release, but if it is present is should not be changeable """
    try:
        Release._meta.get_field("immaterial")
        return ("concept", "immaterial",)
    except FieldDoesNotExist:
        return ("concept",)

class ReleaseAdmin(CollecsterModelAdmin):
    exclude = ("created_by",)
    #fieldsets = (
    #    (None, {"fields": (("concept", "immaterial"),)}),
    #)
    #inlines = (ReleaseAttributeInline, ReleaseCustomAttributeInline, ReleaseCompositionInline)
    collecster_dynamic_inline_classes = OrderedDict((
        ("specific",             utils.release_specific_inlines),
        ("distinctions",         (ReleaseDistinctionInline,)),
        ("attributes",           (ReleaseAttributeInline,)),
        ("custom_attributes",    (ReleaseCustomAttributeInline,)),
        ("composition",          (ReleaseCompositionInline,)),
    )) 
    collecster_readonly_edit = get_release_readonlyedit()
    form = ReleaseForm


#############
## Occurrence
#############

#class OccurrenceAttributeForm(forms.ModelForm):
#    class Meta:
#        widgets={"release_corresponding_entry": widgets.labelwidget_factory(ReleaseAttribute)}

class BaseAttributeFormset(forms.BaseInlineFormSet):
    def clean(self):
        if hasattr(self.instance, "release"):
            release_attributes = self.retrieve_function(self.instance.release)

            forms_count = len(self)
            if forms_count != len(release_attributes):
                raise forms.ValidationError("Instanciated release expects %(total_attr)i attributes (%(count)i provided).",
                                            params={"total_attr": len(release_attributes), "count": forms_count},
                                            code='invalid')

            errors = []
            for id, (form, release_attr) in enumerate( zip(self, release_attributes) ):
                if form.cleaned_data["release_corresponding_entry"] != release_attr:
                    # \todo Internationalize (see: https://docs.djangoproject.com/en/1.8/ref/forms/validation/#using-validation-in-practice)
                    errors.append(forms.ValidationError("Instanciated release expects %(expected_attr)s attribute at index %(index)s.",
                                                        params={'expected_attr': release_attr, 'index': id},
                                                        code='invalid'))

            if errors:
                raise errors


def AnyAttributeFormset_factory(classname, retr_func):
    return type(classname, (BaseAttributeFormset,),
                {"retrieve_function": staticmethod(retr_func), #the retr_func should be called without implicit self
                 "collecster_instance_callback": partialmethod(utils.populate_occurrence_attributes,
                                                         retrieve_function = retr_func)})



class OccurrenceAttributeInline(admin.TabularInline):
    model = OccurrenceAttribute
    formset = AnyAttributeFormset_factory("OccurrenceAttributeFormset", utils.all_release_attributes)
    #form = OccurrenceAttributeForm
    form = modelform_factory(OccurrenceAttribute, fields=("release_corresponding_entry", "value"),
                             widgets={"release_corresponding_entry": widgets.labelwidget_factory(ReleaseAttribute)})
    can_delete = False


class OccurrenceCustomAttributeInline(admin.TabularInline):
    model = OccurrenceCustomAttribute
    formset = AnyAttributeFormset_factory("OccurrenceCustomAttributeFormset", partial(utils.retrieve_any_attributes, ReleaseCustomAttribute))
    #form = OccurrenceAttributeForm
    form = modelform_factory(OccurrenceCustomAttribute, fields=("release_corresponding_entry", "value"),
                             widgets={"release_corresponding_entry": widgets.labelwidget_factory(ReleaseCustomAttribute)})
    can_delete = False


class OccurrenceCompositionFormset(forms.BaseInlineFormSet):
    collecster_instance_callback = utils.occurrence_composition_queryset


class OccurrenceCompositionInline(admin.TabularInline):
    #model = Occurrence.nested_occurrences.through # Allowd to get the model when it is automatically created by Django
    model = OccurrenceComposition
    #verbose_name = verbose_name_plural = "Occurrence composition" # The default name is machine-friendly
    fk_name = 'from_occurrence' # This seems to be the hardcoded name automatically given by Django 
    extra   = 0 # on first load, none shown
    max_num = 0 # and no "+" button
    formset = OccurrenceCompositionFormset # required to specify the "form population" callback
    ## required to specify the lable widget on release_composition and to force saving empty compositions
    form = modelform_factory(OccurrenceComposition, form=SaveInitialDataModelForm, fields="__all__",
                             widgets={"release_composition": widgets.labelwidget_factory(ReleaseComposition)})
    can_delete = False #Remove the delete checkbox on each composition form (on edit page)


class OccurrenceAdmin(CollecsterModelAdmin):
    exclude = ("created_by",)
    collecster_dynamic_inline_classes = OrderedDict((
        ("specific",             (utils.occurrence_specific_inlines)),
        ("attributes",           (OccurrenceAttributeInline,)),
        ("custom_attributes",    (OccurrenceCustomAttributeInline,)),
        ("composition",          (OccurrenceCompositionInline,)),
    ))

    collecster_readonly_edit = ("release",)


    def post_save_model(self, request, obj, form, change):
        if not change:
            TagToOccurrence(user_creator=obj.created_by, user_occurrence_id=obj.pk, occurrence=obj).save()

    def get_changeform_initial_data(self, request):
        """ Pre-populates the owner field with the Person corresponding to the logged-in user """
        """ But does not override this value in case it was provided as GET data """
        initial = super(OccurrenceAdmin, self).get_changeform_initial_data(request)
        if "owner" not in initial:
            initial["owner"] = Person.objects.get(userextension__user=request.user)
        return initial


################
## Registrations
################

def base_register(site):
    site.register(Concept,    ConceptAdmin)
    site.register(Release,    ReleaseAdmin)
    site.register(Occurrence, OccurrenceAdmin)

    site.register(Attribute)
    site.register(AttributeCategory)

    site.register(Distinction)

# For readonly debug
#admin.site.register(ConceptNature)
#admin.site.register(TagToOccurrence)
