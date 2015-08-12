from django.shortcuts   import render
from django.template    import loader
from django.contrib     import admin
from django.http        import HttpResponse

from .admin import ReleaseAdmin, OccurrenceAdmin
from .models import *
from .requests import CollecsterAugmentedRequest

def ajax_admin_formset(request, concept_id):
    release_adm = ReleaseAdmin(Release, admin.site)

    request_with_payload = request
    request_with_payload.collecster_payload = {"concept": concept_id}

    formsets, inline_instances = release_adm._create_formsets(request_with_payload, release_adm.model(), change=False)
    formsets = release_adm.get_inline_formsets(request, formsets, inline_instances)#, **{"release_id": release_id})

    rendered_formsets = [] 
    for wrapped_formset in formsets:
        rendered_formsets.append(loader.render_to_string("admin/edit_inline/stacked.html", {"inline_admin_formset": wrapped_formset}))

    return HttpResponse("<div id={}>{}</div>".format("collecster_specifics", "\n".join(rendered_formsets)))
    #return render(request, "admin/edit_inline/tabular.html",
    #return render(request, "admin/edit_inline/stacked.html",
    #               {"inline_admin_formset": wrapped_formset})


def ajax_occurrence_specific_admin_formsets(request, release_id):
    occurrence_adm = OccurrenceAdmin(Occurrence, admin.site)

    request_with_payload = request
    release_id = int(release_id)
    request_with_payload.collecster_payload = {"concept": (Release.objects.get(pk=release_id).concept.pk) if release_id else 0}

    ## SAME AS ABOVE ##
    formsets, inline_instances = occurrence_adm._create_formsets(request_with_payload, occurrence_adm.model(), change=False)
    formsets = occurrence_adm.get_inline_formsets(request, formsets, inline_instances)#, **{"release_id": release_id})

    rendered_formsets = [] 
    for wrapped_formset in formsets:
        rendered_formsets.append(loader.render_to_string("admin/edit_inline/stacked.html", {"inline_admin_formset": wrapped_formset}))

    return HttpResponse("<div id={}>{}</div>".format("collecster_specifics", "\n".join(rendered_formsets)))

