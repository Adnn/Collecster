from .admin import ReleaseAdmin, OccurrenceAdmin
from .models import *
from . import utils

from django.shortcuts   import render
from django.template    import loader
from django.contrib     import admin
from django.http        import HttpResponse


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


def render_admin_formsets(admin_formsets):
    return [loader.render_to_string(get_template(wrapped_fs), {"inline_admin_formset": wrapped_fs})
            for wrapped_fs in admin_formsets]


##
## Views
##
def ajax_release_admin_formsets(request, concept_id):
    release_adm = ReleaseAdmin(Release, admin.site)

    request_with_payload = request
    request_with_payload.collecster_payload = {
        "concept_id": int(concept_id),
    }

    ## The specifics
    request_with_payload.collecster_payload["inlines_groups"] = ("specific",)
    rendered_formsets = render_admin_formsets(get_admin_formsets(release_adm, request_with_payload))
    specifics_div = "<div id={}>{}</div>".format("collecster_specifics", "\n".join(rendered_formsets))

    ## The automatic attributes
    request_with_payload.collecster_payload["inlines_groups"] = ("attributes",)
    rendered_attributes = render_admin_formsets(get_admin_formsets(release_adm, request_with_payload))

    return HttpResponse("{}\n{}".format(specifics_div, rendered_attributes[0]))


def ajax_occurrence_admin_formsets(request, release_id):
    occurrence_adm = OccurrenceAdmin(Occurrence, admin.site)

    request.collecster_payload = { "release_id": int(release_id) }

    ## The specifics
    utils.set_request_payload(request, "inlines_groups", ("specific",))
    rendered_formsets = render_admin_formsets(get_admin_formsets(occurrence_adm, request))
    specifics_div = "<div id={}>{}</div>".format("collecster_specifics", "\n".join(rendered_formsets))

    ## The attributes and composition
    utils.set_request_payload(request, "inlines_groups", ("attributes", "custom_attributes", "composition",))
    rendered_attributes = render_admin_formsets(get_admin_formsets(occurrence_adm, request))

    return HttpResponse("{}\n{}".format("\n".join(rendered_attributes), specifics_div))


def app_name_script(request):
    return HttpResponse("window.collecster_app_name = \"{}\"".format(utils.get_app_name()))
