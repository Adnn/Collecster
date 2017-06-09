from django.shortcuts import render

from django.http import HttpResponse
from django.shortcuts import render
from django.forms.models import inlineformset_factory, modelformset_factory, modelform_factory
from django.template import RequestContext, loader
from django import forms

import simplejson
import traceback

from .models import *
from .admin import InstanceAttributeFormset, InstanceAdmin
from .admin import *


def retrieve_attributes(release_id):
    return ReleaseAttribute.objects.filter(release=release_id)

def assign_attribute_names(attribute_formset, release_attributes):
    for form, attribute in zip(attribute_formset, release_attributes):
        form.fields['value'].label = "{} {}".format(attribute, form.fields['value'].label)


#
# Ad-hoc serving static files
#
def index(request):
    return render(request, "OOModel/index.html")


##
## Custom view examples
##
def add_instance(request):
    InstanceForm = modelform_factory(Instance, exclude=("release_attributes",))
    InstanceAttributeFormset = inlineformset_factory(Instance, InstanceAttribute, fields=("value",),
                                                     can_delete=False, extra=0, validate_min=True)

    if request.method == "POST":
        instance_form = InstanceForm(request.POST)
        instance_form.is_valid()

        if "release" in instance_form.cleaned_data:
            attributes = retrieve_attributes(instance_form.cleaned_data["release"])
            InstanceAttributeFormset.min_num=len(attributes)
            attribute_formset = InstanceAttributeFormset(request.POST, prefix="instance_attributes")
            assign_attribute_names(attribute_formset, attributes)
        else:
            attribute_formset = InstanceAttributeFormset(prefix="instance_attributes")

        # Save to DB
        if instance_form.is_valid() and attribute_formset.is_valid():
            saved_instance = instance_form.save()
            attribute_formset.instance = saved_instance
            instance_attributes = attribute_formset.save(commit=False)
            for instance_attr, release_attr in zip(instance_attributes, attributes):
                instance_attr.release_attribute = release_attr
                instance_attr.save()
    else:
        instance_form = InstanceForm()
        attribute_formset = InstanceAttributeFormset(prefix="instance_attributes")

    return render(request, "OOModel/instance_ajax.html",
                  {"instance_form": instance_form, "attribute_formset": attribute_formset})

    
##
## AJAX
##
def ajax(request, release_id):
    values = list(ReleaseAttribute.objects.filter(release=release_id).values('attribute__name', 'note'))
    return HttpResponse(simplejson.dumps(values))


def ajax_form(request, release_id):
    release_attributes = retrieve_attributes(release_id)
    InstanceAttributeFormset = inlineformset_factory(Instance, InstanceAttribute, fields=("value",), can_delete=False, extra=len(release_attributes))
    formset = InstanceAttributeFormset(prefix="instance_attributes")
    assign_attribute_names(formset, release_attributes)
    return HttpResponse(formset.as_p())


def ajax_admin_formset(request, release_id):
    """ Implements all that is required to render an inline formset using admin templates """

        ## Initial data for the formset
    release_attributes = retrieve_attributes(release_id)
    initial_attributes = [ {"release_attribute": val} for val in [attribute.id for attribute in release_attributes]]

        ## It is not enough to render the correct formset class directly !
    #formset = FormsetClass( initial=initial_attributes )
    #formset = FormsetClass()
    #assign_attribute_names(formset, release_attributes)
    #return HttpResponse(formset.as_p())

        ## Getting the formset returned by the inline is not better
    #inline = InstanceAttributeInline(Instance, admin.site)
    #formset = inline.get_formset(request)
    ##formset = inline.get_inline_formsets(request)

        ## Retrieves the correct instance to be rendered
    inst_adm = InstanceAdmin(Instance, admin.site)
    formsets, inline_instances = inst_adm._create_formsets(request, inst_adm.model(), change=False)
    formsets = inst_adm.get_inline_formsets(request, formsets, inline_instances)
    wrapped_formset = formsets[0]

    # Done on the formset instance, not on the class (because on the class would take effect until ovewritten)
    wrapped_formset.formset.extra = len(release_attributes)
    wrapped_formset.formset.max_num = len(release_attributes)
    wrapped_formset.formset.initial = initial_attributes

    return render(request, "admin/edit_inline/stacked.html",
                  {"inline_admin_formset": wrapped_formset})


def ajax_empty_admin_formset(request):
    inst_adm = InstanceAdmin(Instance, admin.site)
    inst_adm.inlines[0].extra = 0
    inst_adm.inlines[0].max_num = 0
    formsets, inline_instances = inst_adm._create_formsets(request, inst_adm.model(), change=False)
    formsets = inst_adm.get_inline_formsets(request, formsets, inline_instances)
    formset = formsets[0]

    return render(request, "admin/edit_inline/stacked.html",
                  {"inline_admin_formset": formset})
