from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^ajax/concept/(?P<concept_id>[0-9]+)/specific_admin_formset/html/$', views.ajax_release_specific_admin_formsets),

    url(r'^ajax/release/(?P<release_id>[0-9]+)/specific_admin_formset/html/$', views.ajax_occurrence_specific_admin_formsets),
    url(r'^ajax/release/(?P<release_id>[0-9]+)/attributes_admin_formset/html/$', views.ajax_occurrence_attributes_admin_formsets),
]

