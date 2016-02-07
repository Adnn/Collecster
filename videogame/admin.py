with open("data_manager/admin.py") as f:
        code = compile(f.read(), "data_manager/admin.py", 'exec')
        exec(code)

##
## Customization starts here
##

from .models import *

from django.contrib import admin


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
