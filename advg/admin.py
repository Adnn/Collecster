from .models import *

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.template import RequestContext, loader
from django.shortcuts import render

class BundleCompositionInline(admin.TabularInline):
   model = BundleComposition
   extra = 4
       
class AnyBundleAdmin(admin.ModelAdmin):
    inlines = [BundleCompositionInline]

class ProvidedInterfaceInline(admin.TabularInline):
   model = ProvidedInterface
   extra = 3

class RequiredInterfaceInline(admin.TabularInline):
   model = RequiredInterface
   extra = 3

class SystemInterfaceDescriptionAdmin(admin.ModelAdmin):
    inlines = (ProvidedInterfaceInline, RequiredInterfaceInline,)


class SystemSpecificationForm(forms.ModelForm):
    def clean(self):
        """ Makes sure the selected lockout regions are available to the reference system """
        """ If the reference system has specific regions associeted to it, then only those regions are allowed """
        """ Otherwise, only non-scoped regions are allowed """
        super(SystemSpecificationForm, self).clean()

        if not "interface_description" in self.cleaned_data or not "regional_lockout" in self.cleaned_data:
            return

        allowed_lockout_regions = [region for region in LockoutRegion.objects.all() 
                                          if self.cleaned_data["interface_description"].reference_system in region.limit_scope.all()]
        if not allowed_lockout_regions:
            allowed_lockout_regions = [region for region in LockoutRegion.objects.all() if region.limit_scope.count()==0]

        for lockout in self.cleaned_data["regional_lockout"]:
            if lockout not in allowed_lockout_regions:
                raise ValidationError({
                        "regional_lockout": ValidationError("Only lockout with the correct scope are allowed here.",
                                                             code="mandatory")
                       })



class SystemSpecificationAdmin(admin.ModelAdmin):
    form = SystemSpecificationForm


def register_custom_models(site):
    site.register(Concept,    ConceptAdmin)
    site.register(Release,    ReleaseAdmin)
    site.register(Occurrence, OccurrenceAdmin)
    
    site.register(ReleaseRegion)

    site.register(TagRegion)

    site.register(Person)

    site.register(Color)

    site.register(Donation, AnyBundleAdmin)
    site.register(Purchase, AnyBundleAdmin)

    site.register(Location)
    site.register(StorageUnit)
    site.register(PurchaseContext)

    site.register(LockoutRegion)
    site.register(BaseSystem)
    site.register(SystemMediaPair)
    site.register(SystemInterfaceDescription, SystemInterfaceDescriptionAdmin)
    site.register(SystemSpecification, SystemSpecificationAdmin)

    site.register(Location) ## For some reason, the models registered after it do not show up ...
# Register your models here.
