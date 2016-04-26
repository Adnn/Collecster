from . import utils
from .forms_admins import SaveInitialDataModelForm, PropertyAwareModelForm, CustomSaveModelAdmin, CollecsterModelAdmin, EditLinkToInlineObject

from .models import *
from supervisor.models import Person, Deployment, UserCollection, UserExtension

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


class ConceptAdmin(CollecsterModelAdmin):
    exclude = ("created_by",)
    collecster_dynamic_inline_classes = OrderedDict((
        ("additional_natures",  (ConceptNatureInline,)),
        ("specific",            utils.concept_specific_inlines),
    ))

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
        return super(OnlyOnMaterialFormSet, self).clean()


class ReleaseAnyAttributeFormset(forms.BaseInlineFormSet):
    """ The unique_together constraint of any Attribute class includes the Release PK """
    """ Creating the Release, it is not yet saved into the DB when the Attribute model validate_unique() method is called """
    """ To avoid a DB exception ruining usability, we must validate this uniqueness at the formset level """
    def clean(self):
        super(ReleaseAnyAttributeFormset, self).clean()
        errors = []
        attribute_note = {}

        for id, form in enumerate(self):
            data = form.cleaned_data

            # Note: this formset should work with both ReleaseAttribute and ReleaseCustomAttribute, which do not have the same "attribute" definition
            # We first try to retrieve the attribute definition from a ReleaseCustomAttribute, and if empty we try for a ReleaseAttribute
            # This order is important, as ("", "") does not evaluat false, but "" does.
            attribute = (data.get("category", ""), data.get("name", ""))
            if attribute == ("", ""):
                attribute = data.get("attribute", "")

            # If an attribute is found in the form (i.e., not left blank), check that the note makes it unique, using dictionary lookup
            if attribute:
                pair = (attribute, data.get("note", ""))
                if pair not in attribute_note:
                    attribute_note[pair] = None
                else:
                    errors.append(forms.ValidationError("Uniqueness violation for attribute %(attribute)s. Use a distinctive 'note'.",
                                                        params={"attribute": attribute},
                                                        code="invalid"))
        if errors:
            raise forms.ValidationError(errors)
            

class ReleaseDistinctionInline(admin.TabularInline):
    extra = 1
    model = ReleaseDistinction


# Must derive from SaveInitialDataModelFrom, or unchanged automatic attributes would not be saved
class ReleaseAttributeForm(SaveInitialDataModelForm):
    _forbidden_on_immaterial = [] # Ad-hoc solution, so an app could extend this to prevent specific attributes on immaterials.

    def extra_clean_for_immaterial(self):
        forbidden_attributes = [Attribute.objects.get(q_obj) for q_obj in self._forbidden_on_immaterial]
        if self.instance.attribute in forbidden_attributes:
            self.add_error("attribute", forms.ValidationError("This attribute is not allowed on immaterial releases.",
                                                              code="invalid"))
 
class ReleaseAttributeFormset(ReleaseAnyAttributeFormset):
    collecster_instance_callback = utils.release_automatic_attributes

    def clean(self):
        if not self.instance.is_material():
            for form in self:
                if form.has_changed(): # This is the criterion used by BaseModelfFormSet.save_new_object() to decide whether to save the object
                    form.extra_clean_for_immaterial() 
        return super(ReleaseAttributeFormset, self).clean()
   
class ReleaseAttributeInline(admin.TabularInline):
    extra = 3
    model = ReleaseAttribute
    can_delete = False
    formset = ReleaseAttributeFormset  #Enforces ATTRIBUTES::1) and IMMATERIAL::6)
    form = ReleaseAttributeForm

class ReleaseCustomAttributeInline(admin.TabularInline):
    extra = 0
    model = ReleaseCustomAttribute
    can_delete = False
    formset = ReleaseAnyAttributeFormset #Enforces ATTRIBUTES::1) and IMMATERIAL::6)


class ReleaseCompositionInline(admin.TabularInline):
    verbose_name = verbose_name_plural = "Release composition"
    model = Release.nested_releases.through
    fk_name = 'from_release' # This seems to be the hardcoded name automatically given by Django 
    formset = OnlyOnMaterialFormSet #Enforces IMMATERIAL::5)


class ReleaseForm(PropertyAwareModelForm):
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
    collecster_refresh_inline_classes = ["attributes",] ## For the automatic attributes, depending on the nature(s)
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
                raise forms.ValidationError(errors)


def AnyAttributeFormset_factory(classname, retr_func):
    return type(classname, (BaseAttributeFormset,),
                {"retrieve_function": staticmethod(retr_func), #the retr_func should be called without implicit self
                 "collecster_instance_callback": partialmethod(utils.populate_occurrence_attributes,
                                                         retrieve_function = retr_func)})


class OccurrenceAnyAttributeInline(EditLinkToInlineObject, admin.TabularInline):
    can_delete = False
    readonly_fields = ("edit_link",)
    link_text = "edit defects"

class OccurrenceAttributeInline(OccurrenceAnyAttributeInline):
    model = OccurrenceAttribute
    formset = AnyAttributeFormset_factory("OccurrenceAttributeFormset", utils.all_release_attributes)
    #form = OccurrenceAttributeForm
    form = modelform_factory(OccurrenceAttribute, fields=("release_corresponding_entry", "value"),
                             widgets={"release_corresponding_entry": widgets.labelwidget_factory(ReleaseAttribute)})


class OccurrenceCustomAttributeInline(OccurrenceAnyAttributeInline):
    model = OccurrenceCustomAttribute
    formset = AnyAttributeFormset_factory("OccurrenceCustomAttributeFormset", partial(utils.retrieve_any_attributes, ReleaseCustomAttribute))
    #form = OccurrenceAttributeForm
    form = modelform_factory(OccurrenceCustomAttribute, fields=("release_corresponding_entry", "value"),
                             widgets={"release_corresponding_entry": widgets.labelwidget_factory(ReleaseCustomAttribute)})


class OccurrenceAttributeDefectInline(admin.TabularInline):
    model = OccurrenceAttributeDefect
    extra = 2

class OccurrenceCustomAttributeDefectInline(admin.TabularInline):
    model = OccurrenceCustomAttributeDefect
    extra = 2

class OccurrenceAnyAttributeAdminBase(admin.ModelAdmin):
    readonly_fields = ("occurrence", "release_corresponding_entry", ) 

class OccurrenceAttributeAdmin(OccurrenceAnyAttributeAdminBase):
    inlines = (OccurrenceAttributeDefectInline, )

class OccurrenceCustomAttributeAdmin(OccurrenceAnyAttributeAdminBase):
    inlines = (OccurrenceCustomAttributeDefectInline, )

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


class OccurrenceAdminForm(PropertyAwareModelForm):
    def clean(self):
        self.clean_tag_to_occurrence()
    
    def clean_tag_to_occurrence(self):
        """ Ensures that the proper configuration is in place in Supervisor : """
        """ * That there is a Deployment for the current application """
        """ * That this Deployment is associated to a UserCollection for the logged-in user """
        try:
            deployment = Deployment.objects.get(configuration=utils_path.get_app_name())
        except Deployment.DoesNotExist:
            self.add_error(None, ValidationError("The current application '%(app_name)s' does not have a corresponding Deployment in Supervisor.",
                                            params={"app_name": utils_path.get_app_name()}, code="invalid"))
            return

        try:
            UserCollection.objects.get(user=self.collecster_user_extension, deployment=deployment)
        except UserCollection.DoesNotExist:
            self.add_error(None, ValidationError("The logged-in user '%(user)s' does not have a UserCollection for '%(deployment)s' in Supervisor.",
                                                 params={"user": self.collecster_user_extension.user,
                                                         "deployment": deployment},
                                                 code="invalid"))

class OccurrenceAdmin(CollecsterModelAdmin):
    exclude = ("created_by",)
    collecster_dynamic_inline_classes = OrderedDict((
        ("specific",             (utils.occurrence_specific_inlines)),
        ("attributes",           (OccurrenceAttributeInline,)),
        ("custom_attributes",    (OccurrenceCustomAttributeInline,)),
        ("composition",          (OccurrenceCompositionInline,)),
    ))
    collecster_refresh_inline_classes = ["attributes", "custom_attributes", "composition",] ## Each determined by the release

    collecster_readonly_edit = ("release",)
    form = OccurrenceAdminForm

    def post_save_model(self, request, obj, form, change):
        if not change:
            # TODO The user_occurrence_id could be made more compact, by taking the next id available
            # for the corresponding creator, not the local occurrence id.
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

    site.register(OccurrenceAttribute, OccurrenceAttributeAdmin)
    site.register(OccurrenceCustomAttribute, OccurrenceCustomAttributeAdmin)


# For readonly debug
#admin.site.register(ConceptNature)
#admin.site.register(TagToOccurrence)
