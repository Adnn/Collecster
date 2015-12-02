from django.shortcuts   import render
from django.template    import loader
from django.contrib     import admin
from django.http        import HttpResponse

from .admin import ReleaseAdmin, OccurrenceAdmin
from .models import *


##
## Utilities
##
def get_admin_formsets(admin, request):
    formsets, inline_instances = admin._create_formsets(request, admin.model(), change=False)
    admin_formsets = admin.get_inline_formsets(request, formsets, inline_instances)#, **{"release_id": release_id}) Alternative way to forward the id
    return admin_formsets


def get_template(wrapped_formset):
    #return "admin/edit_inline/{}.html".format("tabular" if issubclass(wrapped_formset.opts.__class__, admin.TabularInline)
    #                                          else "stacked")
    return wrapped_formset.opts.template

##
## Views
##
def ajax_release_specific_admin_formsets(request, concept_id):
    release_adm = ReleaseAdmin(Release, admin.site)

    request_with_payload = request
    request_with_payload.collecster_payload = {
        "concept_id": int(concept_id),
    }

    ## The specifics
    request_with_payload.collecster_payload["inlines_groups"] = ("specific",)
    admin_formsets = get_admin_formsets(release_adm, request_with_payload)

    rendered_formsets = [loader.render_to_string(get_template(wrapped_fs), {"inline_admin_formset": wrapped_fs})
                         for wrapped_fs in admin_formsets]

    specifics_div = "<div id={}>{}</div>".format("collecster_specifics", "\n".join(rendered_formsets))

    ## The automatic attributes
    request_with_payload.collecster_payload["inlines_groups"] = ("attributes",)
    formsets = get_admin_formsets(release_adm, request_with_payload)

    rendered_formsets = [] 
    for wrapped_formset in formsets:
    #for inline, wrapped_formset in zip(inline_instances, formsets):
        template_file = get_template(wrapped_formset)
        rendered_formsets.append(loader.render_to_string(template_file, {"inline_admin_formset": wrapped_formset}))
    attributes_formset = rendered_formsets[0]

    return HttpResponse("{}\n{}".format(specifics_div, attributes_formset))


def ajax_occurrence_specific_admin_formsets(request, release_id):
    occurrence_adm = OccurrenceAdmin(Occurrence, admin.site)

    request_with_payload = request
    release_id = int(release_id)
    request_with_payload.collecster_payload = {
        "concept_id": (Release.objects.get(pk=release_id).concept.pk) if release_id else 0,
        "inlines_groups": ("specific",) 
    }

    ## SAME AS ABOVE ##
    rendered_formsets = [loader.render_to_string(get_template(wrapped_fs), {"inline_admin_formset": wrapped_fs})
                         for wrapped_fs in get_admin_formsets(occurrence_adm, request_with_payload)]

    return HttpResponse("<div id={}>{}</div>".format("collecster_specifics", "\n".join(rendered_formsets)))


def ajax_occurrence_attributes_admin_formsets(request, release_id):
    occurrence_adm = OccurrenceAdmin(Occurrence, admin.site)

    request.collecster_payload = { "release_id": int(release_id) }

    formsets, inline_instances = occurrence_adm._create_formsets(request, occurrence_adm.model(), change=False)
    formsets = occurrence_adm.get_inline_formsets(request, formsets, inline_instances)

    rendered_formsets = [] 
    for inline, wrapped_formset in zip(inline_instances, formsets):
        rendered_formsets.append(loader.render_to_string(inline.template, {"inline_admin_formset": wrapped_formset}))

    return HttpResponse("{}".format("\n".join(rendered_formsets)))
