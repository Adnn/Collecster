from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^ajax/concept_admin_formsets/html/$', views.ajax_concept_admin_formsets),

    url(r'^ajax/concept/(?P<concept_id>[0-9]+)/admin_formsets/html/$', views.ajax_release_admin_formsets),

    url(r'^ajax/release/(?P<release_id>[0-9]+)/admin_formsets/html/$', views.ajax_occurrence_admin_formsets),

    url(r'^view_scripts/app_name.js$', views.app_name_script),

    # Those urls were added to allow writting data-import code. Commented until another use could be found for them.
    #url(r'^import_help/release_specific_classes/concept/$', views.release_specific_classes),
    #url(r'^import_help/occurrence_specific_classes/concept/$', views.occurrence_specific_classes),
]

