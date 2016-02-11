from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^ajax/concept/(?P<concept_id>[0-9]+)/admin_formsets/html/$', views.ajax_release_admin_formsets),

    url(r'^ajax/release/(?P<release_id>[0-9]+)/admin_formsets/html/$', views.ajax_occurrence_admin_formsets),

    url(r'^view_scripts/app_name.js/$', views.app_name_script),
]

