from django.shortcuts import render
from django.conf import settings

from .admin import *
from .models import *



def ajax_admin_formset(request, release_id):
    inst_adm = InstanceAdmin(Instance, admin.site)

    formsets, inline_instances = inst_adm._create_formsets(request, inst_adm.model(), change=False)
    formsets = inst_adm.get_inline_formsets(request, formsets, inline_instances, **{"release_id": release_id})

    wrapped_formset = formsets[0]

    #return render(request, "admin/edit_inline/tabular.html",
    return render(request, "admin/edit_inline/stacked.html",
                   {"inline_admin_formset": wrapped_formset})


    ## Edge case factorized in utils.composition_queryset, when id==0
#def ajax_empty_admin_formset(request):
#    inst_adm = InstanceAdmin(Instance, admin.site)
#    inst_adm.inlines[0].extra = 0
#    inst_adm.inlines[0].max_num = 0
#    formsets, inline_instances = inst_adm._create_formsets(request, inst_adm.model(), change=False)
#    formsets = inst_adm.get_inline_formsets(request, formsets, inline_instances)
#    formset = formsets[0]
#
#    return render(request, "admin/edit_inline/stacked.html",
#                  {"inline_admin_formset": formset})
