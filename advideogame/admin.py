with open("data_manager/admin.py") as f:
        code = compile(f.read(), "data_manager/admin.py", 'exec')
        exec(code)

##
## Customization starts here
##

from .models import *

from django.contrib import admin

##
## Edit the data_manager admin
##
class ConceptAdminForm(forms.models.ModelForm):
    def clean(self):
        """ Enforces some uniqueness constraints : """
        """ If two concepts have the same "distinctive name" and the same "year" """
        """ their name need to have different "scopes" """
        data = self.cleaned_data
        existing_same_name = (Concept.objects.filter(distinctive_name=data["distinctive_name"]) 
                                             .exclude(pk=self.instance.pk))
        for other_concept in existing_same_name:
            if other_concept.year == data["year"]:
                if not data["name_scope_restriction"] and not other_concept.name_scope_restriction.all():
                    raise forms.ValidationError("The concept with index: %(concept_id)i, with the same year value, already uses the name '%(name)s' worldwide.",
                                                params={"concept_id": other_concept.pk,
                                                        "name": data["distinctive_name"]},
                                                code='invalid')
                else:
                    intersection = set(data["name_scope_restriction"]).intersection(other_concept.name_scope_restriction.all())
                    if intersection:
                        raise forms.ValidationError("The concept with index: %(concept_id)i, with the same year value, already uses the name '%(name)s' for regions: %(regions)s.",
                                                    params={"concept_id": other_concept.pk,
                                                            "name": data["distinctive_name"],
                                                            "regions": ["{}".format(region) for region in intersection]},
                                                    code='invalid')

        return super(ConceptAdminForm, self).clean()


# TODO just add this property, avoid auto inheriting from the same name
class ConceptAdmin(ConceptAdmin):
    form = ConceptAdminForm

OccurrenceAdmin.collecster_exclude_create = ("tag_url",)
OccurrenceAdmin.collecster_readonly_edit = OccurrenceAdmin.collecster_readonly_edit + ("tag_url",)

base_register(admin.site)


##
## Admin for extra models
## 
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

admin.site.register(Company)
admin.site.register(CompanyService)

admin.site.register(ReleaseRegion)
admin.site.register(TagRegion)

admin.site.register(Color)

admin.site.register(StorageUnit)

admin.site.register(Donation, AnyBundleAdmin)
admin.site.register(Purchase, AnyBundleAdmin)

admin.site.register(Location)
admin.site.register(PurchaseContext)

admin.site.register(LockoutRegion)
admin.site.register(BaseSystem)
admin.site.register(SystemMediaPair)
admin.site.register(SystemInterfaceDescription, SystemInterfaceDescriptionAdmin)
admin.site.register(SystemSpecification, SystemSpecificationAdmin)

## Debug
admin.site.register(TagToOccurrence)

