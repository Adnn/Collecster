from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^ajax/release/(?P<release_id>[0-9]+)/admin_formset/html/$', views.ajax_admin_formset),
    url(r'^ajax/release/empty_admin_formset/html/$', views.ajax_admin_formset, {"release_id": 0}),
]
