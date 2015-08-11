from django.contrib import admin
from django import forms, utils

from .models import *

import traceback
import itertools

##
## Release
##
class ReleaseAttributeForm(forms.ModelForm):
    class Meta:
        model = ReleaseAttribute
        fields = ("attribute",)


class ReleaseAttributeInline(admin.TabularInline):
    model = ReleaseAttribute
    form = ReleaseAttributeForm


class ReleaseAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    inlines = (ReleaseAttributeInline,)


##
## Instance
##
class LabelWidget(forms.widgets.Select):
    """ Custom widget class, implementing a label instead of a user input """
        ## Alternative way to hide the select
    #def __init__(self, attrs=None, choices=()):
    #    #attrs["hidden"] = "1"
    #    super(LabelWidget, self).__init__({"hidden": "1"}, choices)

    def __init__(self, attrs=None, choices=()):
        super(LabelWidget, self).__init__(attrs, choices)
        self.can_add_related = False
        
    def render(self, name, value, attrs):
        html = u"<p hidden>{}</p>\n".format(super(LabelWidget, self).render(name, value, attrs))
        if value is None:
            html += u"LABEL WIDGET RENDER"
        else:
            html += u"{}".format(ReleaseAttribute.objects.get(pk=value))
        return utils.safestring.SafeText(html)


class InstanceAttributeForm(forms.ModelForm):
    class Meta:
        widgets = {"release_attribute": LabelWidget,}

    def __init__(self, *args, **kwargs):
        super(InstanceAttributeForm, self).__init__(*args, **kwargs)


def retrieve_release_attributes(release_id):
    return ReleaseAttribute.objects.filter(release=release_id)

class InstanceAttributeFormset(forms.BaseInlineFormSet):
    """ Notably implements validation of the attributes composition """ 
    def __init__(self, *args, **kwargs):
        super(InstanceAttributeFormset, self).__init__(*args, **kwargs)
        self.can_delete = False #Remove the delete checkbox in the 'Instance' edit form.

    def clean(self):
        if hasattr(self.instance, "release"):
            release_attributes = retrieve_release_attributes(self.instance.release)

            if len(self) != len(release_attributes):
                raise forms.ValidationError("Instanciated release expects %(total_attr)s attributes.",
                                            params={'total_attr': len(release_attributes)},
                                            code='invalid')

            for form, release_attr, id in zip(self, release_attributes, itertools.count()):
                if form.cleaned_data["release_attribute"] != release_attr:
                    # \todo Internationalize (see: https://docs.djangoproject.com/en/1.8/ref/forms/validation/#using-validation-in-practice)
                    raise forms.ValidationError("Instanciated release expects %(expected_attr)s attribute at index %(index)s.",
                                                params={'expected_attr': release_attr, 'index': id},
                                                code='invalid')
        else:
            # \todo not sure it should be displayed: parent form will already complain that release must be selected.
            raise forms.ValidationError("Release must be selected to determine its attributes.")


#class InstanceAttributeInline(admin.TabularInline):
class InstanceAttributeInline(admin.StackedInline):
    model = InstanceAttribute
    formset = InstanceAttributeFormset
    form =  InstanceAttributeForm
    extra = 0
    max_num = 0


    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Prevent the green "plus" button on Foreign key fields """
        """ Has to be done here, when the widget is already wrapped in widgets.RelatedFieldWidgetWrapper """
        formfield = super(InstanceAttributeInline,self).formfield_for_dbfield(db_field, **kwargs)
        if formfield:
            formfield.widget.can_add_related = False
        return formfield


class InstanceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(InstanceForm, self).__init__(*args, **kwargs)


class InstanceAdmin(admin.ModelAdmin):
    class Media:
        # Loads the custom javascript
        js = ("//ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js",
              "OOModel_attributes/ajax.js",)

    model = Instance
    inlines = (InstanceAttributeInline,)
    form = InstanceForm

    def get_readonly_fields(self, request, obj=None):
        """ Make the 'release' field read-only when editing an existing object """
        if obj:
            return self.readonly_fields + ('release',)
        else:
            return self.readonly_fields

##
## Registrations
##
admin.site.register(Attribute)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(ReleaseAttribute)
admin.site.register(Instance, InstanceAdmin)
admin.site.register(InstanceAttribute)
