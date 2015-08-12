from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^ajax/concept/(?P<concept_id>[0-9]+)/admin_formset/html/$', views.ajax_admin_formset),
    url(r'^ajax/concept/empty_admin_formset/html/$', views.ajax_admin_formset, {"concept_id": 0}),
    url(r'^ajax/release/(?P<release_id>[0-9]+)/admin_formset/html/$', views.ajax_occurrence_specific_admin_formsets),
]

