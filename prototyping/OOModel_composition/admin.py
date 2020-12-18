from django.contrib import admin
from django import forms, utils

from django.forms.models import BaseInlineFormSet
from .models import *
from .utils import composition_queryset

import traceback
import itertools

class CollecsterModelAdmin(admin.ModelAdmin):
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


##
## Release
##
class ReleaseCompositionForm(forms.ModelForm):
    pass
    

class CompositionInline(admin.StackedInline):
    model = ReleaseComposition
    fk_name = 'container_release'
    form = ReleaseCompositionForm


class ReleaseAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    inlines = (CompositionInline,)


##
## Instance
##
class InstanceCompositionFormset(BaseInlineFormSet):
    collecster_instance_callback = composition_queryset

class InstanceCompositionInline(admin.StackedInline):
    model = InstanceComposition
    fk_name = 'container'
    extra   = 0 # on first load, none shown
    max_num = 0 # an no "+" button
    formset = InstanceCompositionFormset
    can_delete = False #Remove the delete checkbox on each composition form (on edit page)
                       # Could also be set on the formset in its __init__ method


class InstanceAdmin(CollecsterModelAdmin):
    class Media:
        # Loads the custom javascript
        js = ("//ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js",
              "OOModel_attributes/ajax.js",)

    exclude = ['container',]
    inlines = (InstanceCompositionInline,)

    collecster_readonly_edit = ("release",)
    fields = ("release", "name") # By default, the readonly fields are displayed after all editable fields


##
## Registrations
##
admin.site.register(Release, ReleaseAdmin)
admin.site.register(Instance, InstanceAdmin)
