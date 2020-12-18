from django.contrib import admin
from django import forms

from .models import *

# see: https://groups.google.com/d/msg/django-users/xu2Ef7y4DPQ/u3z30vl_BwAJ
class ElementFormset(forms.BaseInlineFormSet):
    def __init__(self, data=None, files=None, instance=None,
                 save_as_new=False, prefix=None, queryset=None, **kwargs):
        super(ElementFormset,self).__init__(data, files, instance, save_as_new, prefix, queryset, **kwargs)
        self.validate_min = True
        self.validate_max = True
    
class ElementInline(admin.StackedInline):
    model = Element
    extra = 0
    min_num = 2
    validate_min = True # Seems not to be forwarded anyway
    max_num = 2

    formset = ElementFormset


class ContainerAdmin(admin.ModelAdmin):
    model = Container
    inlines = [ElementInline, ]

admin.site.register(Container, ContainerAdmin)
