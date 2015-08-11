from django.conf.urls import url

from . import views
from . import formset_views

urlpatterns = [
    # A basic example, retrieving the list of attributes for the 2 first releases
    url(r'^$',      views.index),
    # Returns the JSON used by the example above
    url(r'^ajax/release/(?P<release_id>[0-9]+)/$',  views.ajax),

    # Add instance example in a custom view:
    # querying the list of existing Releases, and dynamically creating a formset with corresponding attributes
    url(r'^instance/add/$',  views.add_instance),
    # Returns the HTML formset used by the example above
    url(r'^ajax/release/(?P<release_id>[0-9]+)/attribute_form/html/$', views.ajax_form, name="ajax_html_formset"),

    # An example showing that the formset level validation is actually run,
    # but the error must be explicitly displayed in the template
    url(r'^formset_error_test/$',  formset_views.formset_error_bkp),

    #
    # Used in the contrib.Admin
    #
    url(r'^ajax/release/(?P<release_id>[0-9]+)/admin_formset/html/$', views.ajax_admin_formset),
    url(r'^ajax/release/empty_admin_formset/html/$', views.ajax_empty_admin_formset),
]
