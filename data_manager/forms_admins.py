from . import utils
from .models import AbstractRecordOwnership, UserExtension, OccurrenceBase, ReleaseBase

from django.contrib import admin
from django import forms

#TODEL
import wdb


##########
## Forms
##########
class SaveInitialDataModelForm(forms.ModelForm):
    """ Changes the meaning of the "initial" member to mean "default": values saved even in the absence of any user-initiated change to the form """
    """ Details : when a form only has its initial values, I could not find a way to force it to be saved, even by setting empty_permitted = false, """
    """ nor by setting validate_min and validate_max. What works is to have has_changed() always return True."""
    """ Edit: it evolved to change the meaning of 'initial' to 'default', see: http://stackoverflow.com/a/33354303/1027706 """
    def has_changed(self):
        for name, field in self.fields.items():
            prefixed_name = self.add_prefix(name)
            data_value = field.widget.value_from_datadict(self.data, self.files, prefixed_name)

            # When editing a parent object, all the forms of the formset are assigned its primary_key
            # (even the totally empty ones, without any initial data)
            if data_value and not issubclass(field.__class__, forms.models.InlineForeignKeyField):
                return True
        return False


##########
## ModelAdmins
##########
class CustomSaveModelAdmin(admin.ModelAdmin):
    """ Saves the User that ADDed the instance if its model derives from AbstractRecordOwnership (-> it has a created_by field) """
    """ Also introduces a post_model_save() hook, called after saving the model, but before saving the related models """
    """ Plus attempt to call an "admin_post_save" method on the model instance, after itself and its related instances were saved """

    def save_model(self, request, obj, form, change):
        # If obj has a "created_by" field provided by AbstractRecordOwnership, and this is adding a new object (not editing one)
        if issubclass(obj.__class__, AbstractRecordOwnership) and not change:
            obj.created_by = UserExtension.objects.get(user=request.user)
        super(CustomSaveModelAdmin, self).save_model(request, obj, form, change)
        self.post_save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        self._obj_post_save(obj);
        return super(CustomSaveModelAdmin, self).response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        self._obj_post_save(obj);
        return super(CustomSaveModelAdmin, self).response_change(request, obj)

    def _obj_post_save(self, obj):
        if hasattr(obj, "admin_post_save"):
            obj.admin_post_save()

    def post_save_model(self, request, obj, form, change):
        pass


class CollecsterModelAdmin(CustomSaveModelAdmin):
    """ A derived ModelAdmin that allows for custom behaviour needed by Collecster : """
    """ * making fields read-only for edition, writtable for addition (fields listed in "collecster_readonly_edit" member) """
    """ * dynamic (ajax based) inline formsets: """
    """ ** editing an already present formset before presentation (calling formset's "collecster_instance_callback" method) """
    """ ** generate new AdminInline instances, to add new formsets ("collecster_dynamic_inline_classes" member) """

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

        # Nota: Sadly, this happend too late: after the formset validation. 
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


    def _collecster_fixup_request(self, request, obj, change):
        """ Implementation detail, allows to forward some data from 'obj' into the request """
        if type(obj) is OccurrenceBase and hasattr(obj, "release"):
            utils.set_request_payload(request, "release_id", obj.release.id)
        elif type(obj) is ReleaseBase and hasattr(obj, "concept"):
            utils.set_request_payload(request, "concept_id", obj.concept.id)


    def _create_formsets(self, request, obj, change):
        """ Used to customize a static formset (number of forms, initial data, ...). """
        """ Each formset will have its "collecster_instance_callback" method run on creation """
        """ """
        """ It would be best not to need to override this 'private' method, the rationale is obj propagation """
        """ _create_formsets does not propagate the object to get_formsets_with_inlines() when ADDing it (even if it partially or totally exists) """
        """ see: https://github.com/django/django/blob/1.8.3/django/contrib/admin/options.py#L1794-L1795 """
        """ Yet we need its value (at least the concept or release): """
        """   * for 'collecster_instance_callback' callback """
        """   * when invoking callable dynamic inline classes (see get_inline_instances) """
        self._collecster_fixup_request(request, obj, change)
        formsets, inlines = super(CollecsterModelAdmin, self)._create_formsets(request, obj, change)
        for formset in formsets:
            if hasattr(formset, "collecster_instance_callback"):
                formset.collecster_instance_callback(request, obj) 
        return formsets, inlines
        

    def get_inline_instances(self, request, obj=None):
        """ Override allowing to dynamically generate AdminInline instances. """
        """ It is usefull to add formsets to a given admin form at runtime. """
        """ """
        """ The method expects "collecster_dynamic_inline_classes" member to be a dictionary mapping group names to either: """
        """ * A callable that returns a collection of AdminInline classes (for the dynamic behaviour) """
        """ * A static collection of AdminInline classes (similar behaviour to the default "inlines" attribute behaviour) """
        """ All the AdminInlines for all groups are returned, except if the payload limits groups using its "collecster_inlines_group" entry """
        AdminClass = self.__class__
        added = []
        requested_inlines = utils.get_request_payload(request, "inlines_groups")
        if hasattr(AdminClass, "collecster_dynamic_inline_classes"):
            filter_func = (lambda x: x in requested_inlines) if requested_inlines else (lambda x: True)
            for inlines in [inlines for group, inlines in self.collecster_dynamic_inline_classes.items() if filter_func(group)]:
                for AdminInline in (inlines(request, obj) if callable(inlines) else inlines):
                    added.append(AdminInline(self.model, self.admin_site))

        if requested_inlines:
            return added
        else:
            return super(CollecsterModelAdmin, self).get_inline_instances(request, obj) + added
