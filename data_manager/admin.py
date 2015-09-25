from django.contrib import admin
from django import forms
from django.forms.models import modelform_factory

from .models import *
from . import utils
from . import widgets 
from . import enumerations as enums

from functools import partial, partialmethod

## TODEL ##
from .configuration import ReleaseSpecific
import wdb

class CollecsterModelAdmin(admin.ModelAdmin):
    class Media:
        js = ("//ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js",
              "data_manager/scripts/form_ajax.js",)


    def get_readonly_fields(self, request, obj=None):
        """ Make the given fields read-only when editing an existing object """
        AdminClass = self.__class__
        if obj and hasattr(AdminClass, "collecster_readonly_edit"):
            return self.readonly_fields + AdminClass.collecster_readonly_edit
        else:
            return self.readonly_fields

        # Nota: Sadly, this happends too lat: after the formset validation. 
        # Yet, in cases where the callback would change some fields on the form, it is important that the new fields
        # would be used for validation !
    #def get_inline_formsets(self, request, formsets, inline_instances, obj=None):
    #    """ Override allowing to insert a potential callback on each formset """
    #    """ The callback is assigned to the custom formset class, under the attribute 'collecster_instance_callback' """
    #    """ It is usefull to customize a static formset (number of forms, initial data, ...) """
    #    inline_admin_formsets = super(CollecsterModelAdmin, self).get_inline_formsets(request, formsets,
    #                                                                                  inline_instances, obj)
    #    for wrapped_formset in inline_admin_formsets: 
    #        formset = wrapped_formset.formset
    #        FormSet = formset.__class__
    #        if hasattr(FormSet, "collecster_instance_callback"):
    #            FormSet.collecster_instance_callback(formset, request, obj) 
    #    
    #    return inline_admin_formsets

        # Nota: this one happens before formset validation... but it is expected to return FormSet classes
        # but we want to be able to change the formset instances.
    #def get_formsets_with_inlines(self, request, obj=None):
        ## The method in the parent yields
        #(FormSet, inline) = next(super(CollecsterModelAdmin, self).get_formsets_with_inlines(request, obj))
        ##FormSet = formset.__class__
        #if hasattr(FormSet, "collecster_instance_callback"):
        #    FormSet.collecster_instance_callback(formset, request, obj) 
        #yield formset, inline

 


    def _create_formsets(self, request, obj, change):
        """ It would be best not to need to override this 'private' method, the rationale is obj propagation """
        """ _create_formsets does not propagate the object when ADDing it (even if it partially or totally exists) """
        """ see: https://github.com/django/django/blob/1.8.3/django/contrib/admin/options.py#L1794-L1795 """
        """ Yet we need to save its value (at least the concept) for 'collecster_instance_callback' callback """
        # TODO make that generic, instead of hardcoding potential attributes
        if obj and hasattr(obj, "concept"):
            request.collecster_payload = {"concept_id": obj.concept.pk}
        if obj and hasattr(obj, "release"):
            request.collecster_payload = {"release_id": obj.release.pk}

            # Nota: it is now where we execute formset callback (see notes above)
        #return super(CollecsterModelAdmin, self)._create_formsets(request, obj, change)
        formsets, inlines = super(CollecsterModelAdmin, self)._create_formsets(request, obj, change)
        for formset in formsets:
            #FormSet = formset.__class__
            #if hasattr(FormSet, "collecster_instance_callback"):
            if hasattr(formset, "collecster_instance_callback"):
                #FormSet.collecster_instance_callback(formset, request, obj) 
                formset.collecster_instance_callback(request, obj) 
        return formsets, inlines
        

    def get_inline_instances(self, request, obj=None):
        """ Override allowing to dynamically generate AdminInline instances """
        """ It is usefull to add formsets to a given admin form at runtime """
        AdminClass = self.__class__
        added = []
        requested_inlines = utils.get_request_payload(request, "inlines_groups")
        if hasattr(AdminClass, "collecster_dynamic_inline_classes"):
            filter_func = (lambda x: x in requested_inlines) if requested_inlines else (lambda x: True)
            for func in [func for group, func in AdminClass.collecster_dynamic_inline_classes.items() if filter_func(group)]:
                for AdminInline in func(request, obj):
                    added.append(AdminInline(self.model, self.admin_site))

        if requested_inlines:
            return added
        else:
            return super(CollecsterModelAdmin, self).get_inline_instances(request, obj) + added


##########
## Concept
##########

class ConceptNatureInline(admin.TabularInline):
    extra = 0
    model = ConceptNature
    can_delete = False


class ConceptAdmin(admin.ModelAdmin):
    inlines = (ConceptNatureInline,)


##########
## Release
##########

class ReleaseAttributeInline(admin.TabularInline):
    extra = 3
    model = ReleaseAttribute
    can_delete = False

class ReleaseCustomAttributeInline(admin.TabularInline):
    extra = 0
    model = ReleaseCustomAttribute
    can_delete = False


class ReleaseAdmin(CollecsterModelAdmin):
    inlines = (ReleaseAttributeInline, ReleaseCustomAttributeInline)
    collecster_dynamic_inline_classes = {"specific": utils.release_specific_inlines}
    collecster_readonly_edit = ("concept",)


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
                {"retrieve_function": retr_func,
                 "collecster_instance_callback": partialmethod(utils.populate_occurrence_attributes,
                                                         retrieve_function = retr_func)})



class OccurrenceAttributeInline(admin.TabularInline):
    formset = AnyAttributeFormset_factory("OccurrenceAttributeFormset", partial(utils.retrieve_any_attributes, ReleaseAttribute))
    model = OccurenceAttribute
    #form = OccurrenceAttributeForm
    form = modelform_factory(OccurenceAttribute, fields=("release_corresponding_entry", "value"),
                             widgets={"release_corresponding_entry": widgets.labelwidget_factory(ReleaseAttribute)})
    can_delete = False


class OccurrenceCustomAttributeInline(admin.TabularInline):
    formset = AnyAttributeFormset_factory("OccurrenceCustomAttributeFormset", partial(utils.retrieve_any_attributes, ReleaseCustomAttribute))
    model = OccurenceCustomAttribute
    #form = OccurrenceAttributeForm
    form = modelform_factory(OccurenceCustomAttribute, fields=("release_corresponding_entry", "value"),
                             widgets={"release_corresponding_entry": widgets.labelwidget_factory(ReleaseCustomAttribute)})
    can_delete = False


class OccurrenceAdmin(CollecsterModelAdmin):
    collecster_dynamic_inline_classes = {"specific": utils.occurrence_specific_inlines}
    collecster_readonly_edit = ("release",)

    inlines = (OccurrenceAttributeInline, OccurrenceCustomAttributeInline)


################
## Registrations
################

admin.site.register(Concept,    ConceptAdmin)
admin.site.register(Release,    ReleaseAdmin)
admin.site.register(Occurrence, OccurrenceAdmin)

admin.site.register(Attribute)
admin.site.register(AttributeCategory)

# For readonly debug
admin.site.register(ConceptNature)
admin.site.register(ReleaseSpecific.Hardware)
