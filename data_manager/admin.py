from django.contrib import admin

from .models import *
from . import utils

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

    def get_inline_formsets(self, request, formsets, inline_instances, obj=None, **kwargs):
        inline_admin_formsets = super(CollecsterModelAdmin, self).get_inline_formsets(request, formsets,
                                                                                      inline_instances, obj)
        for wrapped_formset in inline_admin_formsets: 
            formset = wrapped_formset.formset
            FormSet = formset.__class__
            if hasattr(FormSet, "collecster_instance_callback"):
                FormSet.collecster_instance_callback(formset, obj, **kwargs) 

        return inline_admin_formsets

    def _create_formsets(self, request, obj, change):
        """ It would be best not to need to override this 'private' method, the rationale is obj propagation """
        """ _create_formsets does not propagate the object when ADDing it (even if it partially or totally exists) """
        """ see: https://github.com/django/django/blob/1.8.3/django/contrib/admin/options.py#L1794-L1795 """
        """ Yet we need to save its value (at least the concept) for 'collecster_dynamic_formset_func' callback """
        if obj and hasattr(obj, "concept"):
            request.collecster_payload = {"concept": obj.concept.pk}
        return super(CollecsterModelAdmin, self)._create_formsets(request, obj, change)
        

    def get_inline_instances(self, request, obj=None):
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


class ReleaseAdmin(CollecsterModelAdmin):
    inlines = (ReleaseAttributeInline,)
    collecster_dynamic_inline_classes = {"specific": utils.release_specific_inlines}
    collecster_readonly_edit = ("concept",)


#############
## Occurrence
#############

class OccurrenceAdmin(CollecsterModelAdmin):
    collecster_dynamic_inline_classes = {"specific": utils.occurrence_specific_inlines}
    collecster_readonly_edit = ("release",)


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
