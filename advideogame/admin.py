with open("data_manager/admin.py") as f:
        code = compile(f.read(), "data_manager/admin.py", 'exec')
        exec(code)

##
## Customization starts here
##

from .models import *
from . import config_utils

from django.contrib import admin
from django.utils.html import format_html

##
## Edit the data_manager admin
##

## Concept name scoping ##
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

## Occurrence pictures relation to any attribute ##
def populate_occurrence_picture_attributes_choices(formset, request, obj):
    """ Populates the any_attribute ChoiceField of OccurrencePictureForm with all attributes (incl. CustomReleaseAttributes) """
    """ available on the Release of the related occurrence. Also populates its initial data for edition form. """
    release_id = utils.get_release_id(request, obj)
    
    choices = [("", "----")]

    attributes = utils.all_release_attributes(release_id)
    attribute_contenttype = ContentType.objects.get_for_model(ReleaseAttribute)
    choices.extend([ ("{}_{}".format(attribute_contenttype.pk, attribute.pk), "{}".format(attribute))
                     for attribute in attributes])

    custom_attributes = utils.retrieve_any_attributes(ReleaseCustomAttribute, release_id)
    custom_attribute_contenttype = ContentType.objects.get_for_model(ReleaseCustomAttribute)
    choices.extend([ ("{}_{}".format(custom_attribute_contenttype.pk, attribute.pk), "{} (custom)".format(attribute))
                     for attribute in custom_attributes])

    for form in formset:
        form.fields["any_attribute"].choices = choices
        if form.instance.attribute_id:
            form.fields["any_attribute"].initial = "{}_{}".format(form.instance.attribute_type.pk, form.instance.attribute_id)
    
class OccurrencePictureForm(forms.ModelForm):
    class Meta:
        exclude = ("attribute_type", "attribute_id")

    # Choices are populated dynamically by populate_occurrence_picture_attributes_choices
    any_attribute = forms.ChoiceField(label="Attribute", required=False)
    
    def cleaned_attribute(self):
        attribute = None
        try:
            attribute = self.cleaned_data["any_attribute"]
        except KeyError:
            pass
        return attribute

    def clean(self, *args, **kwargs):
        """ Ensures that detail==Group pictures have no attributes associated, but all other "details" have one """
        error = None
        detail = self.cleaned_data["detail"]
        attribute = self.cleaned_attribute()
        
        if detail == PictureDetail.GROUP:
            if attribute:
               error = ValidationError("This field must be blank for {} pictures.".format(PictureDetail.DICT[detail][0]),
                                       code="invalid")
        else:
            if not attribute:
               error = ValidationError("This field is mandatory for {} pictures.".format(PictureDetail.DICT[detail][0]),
                                       code="invalid")
                
        if error:
            raise ValidationError({"any_attribute": error})

        return super(OccurrencePictureForm, self).clean()

    def save(self, *args, **kwargs):
        """ Populates the model fields of the generic relation (attribute_type, attribute_id) using the selected value """
        if self.cleaned_attribute():
            attribute_type_pk, self.instance.attribute_id = self.cleaned_attribute().split("_")
            self.instance.attribute_type = ContentType.objects.get(id=attribute_type_pk)
        return super(OccurrencePictureForm, self).save(*args, **kwargs)

     
class OccurrencePictureFormSet(forms.BaseInlineFormSet):
    collecster_instance_callback = populate_occurrence_picture_attributes_choices

class OccurrencePictureInline(admin.TabularInline):
    model   = OccurrencePicture
    formset = OccurrencePictureFormSet
    form    = OccurrencePictureForm

OccurrenceAdmin.collecster_dynamic_inline_classes["pictures"] = (OccurrencePictureInline,)
OccurrenceAdmin.collecster_refresh_inline_classes.extend( ("pictures",) )

## Display the tag link as a clickable read-only url, only when editing ##
def tag_link(self, instance):
    """ By default, an UrlField does not display as a clickable link when it is read-only """
    """ so we rely on the ModelAdmin.readonly_fields ability to use a callable to output the link """
    """ see: http://stackoverflow.com/q/35708814/1027706 """
    if instance.tag_url:
        return format_html('<a href="{url}" target=_blank>{url}</a>', url=instance.tag_url)
    else:
        return "-" # What was displayed by default by the readonly UrlField when the tag was not set

OccurrenceAdmin.tag_link = tag_link # Has to be a method on the model or the ModelAdmin
OccurrenceAdmin.collecster_readonly_edit = OccurrenceAdmin.collecster_readonly_edit + ("tag_link",)
OccurrenceAdmin.exclude = OccurrenceAdmin.exclude + ("tag_url",)

## Release picture ##
class ReleasePictureInline(admin.TabularInline):
    model   = ReleasePicture
    extra   = 1

ReleaseAdmin.collecster_dynamic_inline_classes["pictures"] = (ReleasePictureInline,)

## Release attributes ##
ReleaseAttributeForm._forbidden_on_immaterial.append(config_utils.get_attribute("content", "self"))


base_register(admin.site)


##
## Admin for extra models
## 
class BundleCompositionInline(admin.TabularInline):
   model = BundleComposition
   extra = 4
       
class BundlePictureInline(admin.TabularInline):
   model = BundlePicture
   extra = 1

class AnyBundleAdmin(admin.ModelAdmin):
    inlines = (BundleCompositionInline, BundlePictureInline,)

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

