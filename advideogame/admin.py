from data_manager.collecster_exec import collecster_exec

collecster_exec("data_manager/admin.py")

##
## Customization starts here
##

from .models import *
from . import config_utils
from .forms_admins import SaveEmptyDataModelForm

from data_manager import utils_id

from django.utils.html import format_html
from django.contrib import admin

##
## Edit the data_manager admin
##

## Concept name scoping ##
class ConceptAdminForm(forms.models.ModelForm):
    def clean(self):
        """
        Enforces some uniqueness constraints : 
        If two concepts have the same "distinctive name" and the same "year" 
        their name need to have different "scopes"
        """
        data = self.cleaned_data
        if "distinctive_name" not in data:
            return
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

ConceptAdmin.form = ConceptAdminForm

class ConceptUrlInline(admin.TabularInline):
    extra = 1
    model = ConceptUrl

class ConceptRelationInline(admin.TabularInline):
    extra = 0
    model = ConceptRelation
    fk_name = "concept"

ConceptAdmin.collecster_dynamic_inline_classes["urls"] = (ConceptUrlInline,)
ConceptAdmin.collecster_dynamic_inline_classes["relations"] = (ConceptRelationInline,)

## Occurrence pictures relation to any attribute ##
def populate_occurrence_picture_attributes_choices(formset, request, obj):
    """
    Populates the any_attribute ChoiceField of OccurrencePictureForm with all attributes (incl. CustomReleaseAttributes) 
    available on the Release of the related occurrence. Also populates its initial data for edition form. 
    """
    release_id = utils_id.get_release_id(request, obj)
    
    choices = [("", "----")]

    attributes = utils.retrieve_noncustom_custom_release_attributes(release_id)
    choices.extend([ ("{}_{}".format(ContentType.objects.get_for_model(attribute.__class__).pk, attribute.pk),
                      "{}".format(attribute),)
                     for attribute in attributes])

    for form in formset:
        form.fields["any_attribute"].choices = choices
        if form.instance.attribute_id:
            form.fields["any_attribute"].initial = "{}_{}".format(form.instance.attribute_type.pk, form.instance.attribute_id)

    def empty_form(self):
        form = super(OccurrencePictureFormSet, self).empty_form
        form.fields["any_attribute"].choices = choices
        return form

    # The empty_formset property is used when clicking the "Add another Occurrence picture" in the web interface
    # "patches" the property by subclassing, as described on SO: http://stackoverflow.com/a/31591589/1027706
    class PatchedFormset(formset.__class__):
        @property
        def empty_form(self):
            form = super(PatchedFormset, self).empty_form
            form.fields["any_attribute"].choices = choices
            return form
    formset.__class__ = PatchedFormset

    
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


class OccurrenceAnyAttributeInline_advg(EditLinkToInlineObject, OccurrenceAnyAttributeInline):
    readonly_fields = ("edit_link",)
    link_text = "edit defects"

class OccurrenceAnyAttributeDefectInline(admin.TabularInline):
    model = OccurrenceAnyAttributeDefect
    extra = 2

class OccurrenceAnyAttributeAdmin(admin.ModelAdmin):
    readonly_fields = ("occurrence",) 
    inlines = (OccurrenceAnyAttributeDefectInline, )
    form = OccurrenceAnyAttributeForm

OccurrenceAdmin.collecster_dynamic_inline_classes["attributes"] = (OccurrenceAnyAttributeInline_advg,)


## Display the tag link as a clickable read-only url, only when editing ##
def tag_link(self, instance):
    """
    By default, an UrlField does not display as a clickable link when it is read-only
    so we rely on the ModelAdmin.readonly_fields ability to use a callable to output the link 
    see: http://stackoverflow.com/q/35708814/1027706 
    """
    if instance.tag_url:
        return format_html('<a href="{url}" target=_blank>{url}</a>', url=instance.tag_url)
    else:
        return "-" # What was displayed by default by the readonly UrlField when the tag was not set

## Not usefull anymore since tag_url UrlField is now tag_file FileField
#OccurrenceAdmin.tag_link = tag_link # Has to be a method on the model or the ModelAdmin
OccurrenceAdmin.collecster_readonly_edit = OccurrenceAdmin.collecster_readonly_edit + ("tag_file",)
OccurrenceAdmin.exclude = OccurrenceAdmin.exclude + ("tag_file",)

## Release picture ##
class ReleasePictureInline(admin.TabularInline):
    model   = ReleasePicture
    extra   = 1

ReleaseAdmin.collecster_dynamic_inline_classes["pictures"] = (ReleasePictureInline,)

## Release attributes ##
ReleaseAttributeForm._forbidden_on_immaterial.append(models.Q(category__name="content", name="self"))

## Release urls ##
class ReleaseUrlInline(admin.TabularInline):
    extra = 1
    model = ReleaseUrl

#ReleaseAdmin.inlines = (ReleaseUrlInline,) + ReleaseAdmin.inlines
ReleaseAdmin.collecster_dynamic_inline_classes["urls"] = (ReleaseUrlInline,)
ReleaseAdmin.collecster_dynamic_inline_classes.move_to_end("urls", last=False)

## Validates the selected regions ##
class ReleaseFormRegions(ReleaseForm):
    """ 
    Inherit from ReleaseForm and assign it as the ReleaseAdmin form 
    We could have defined a free function instead, and assigned it to ReleaseForm.clean, but it would override 
    a potential clean member already present on ReleaseForm 
    """
    def clean(self):
        super(ReleaseFormRegions, self).clean()
        regions = self.cleaned_data.get("release_regions")
        for region in regions:
            if region.parent_region in regions:
                self.add_error("release_regions",
                               forms.ValidationError("Release regions cannot contain the region %(nested_region)s "
                                                     "and its parent region %(parent_region)s at the same time.",
                                                     params={"nested_region": region, "parent_region": region.parent_region},
                                                     code="invalid"))

ReleaseAdmin.form = ReleaseFormRegions

base_register(admin.site)

admin.site.register(OccurrenceAnyAttribute, OccurrenceAnyAttributeAdmin)


##
## Admin for extra models
## 
class BundleCompositionInline(admin.TabularInline):
   model = BundleComposition
   extra = 4
       
class BundlePictureInline(admin.TabularInline):
   model = BundlePicture
   extra = 1

class AnyBundleAdmin(CollecsterModelAdmin):
    exclude = ("created_by",)
    inlines = (BundleCompositionInline, BundlePictureInline,)


## System specifications ##
class ProvidedInterfaceInline(admin.TabularInline):
   model = ProvidedInterface
   extra = 1

class RequiredInterfaceInline(admin.TabularInline):
   model = RequiredInterface
   extra = 1

class SystemInterfaceDetailAdmin(admin.ModelAdmin):
    inlines = (ProvidedInterfaceInline, RequiredInterfaceInline,)
    readonly_fields = ("interfaces_specification", "advertised_system",) 

class SystemInterfaceDetailFormset(forms.BaseInlineFormSet):
    def clean(self):
        super(SystemInterfaceDetailFormset, self).clean()
        systems_set = set()

        for form in self:
            advertised_system = form.cleaned_data.get("advertised_system")
            if advertised_system and (advertised_system in systems_set):
                form.add_error("advertised_system", forms.ValidationError("This advertised system is already present, and does not allow duplicates.",
                                                                          code="invalid"))
            else:
                systems_set.add(advertised_system)

class SystemInterfaceDetailInline(EditLinkToInlineObject, admin.TabularInline):
    model = SystemInterfaceDetail
    extra = 2
    readonly_fields = ("edit_link",)
    link_text = "edit interfaces"
    formset = SystemInterfaceDetailFormset

class CommonInterfaceDetailAdmin(admin.ModelAdmin):
    inlines = (ProvidedInterfaceInline, RequiredInterfaceInline,)
    readonly_fields = ("interfaces_specification",) 

class CommonInterfaceDetailInline(EditLinkToInlineObject, admin.TabularInline):
    model = CommonInterfaceDetail
    readonly_fields = ("edit_link",)
    link_text = "edit interfaces"
    form = SaveEmptyDataModelForm


class InterfacesSpecificationAdmin(admin.ModelAdmin):
    inlines = (SystemInterfaceDetailInline, CommonInterfaceDetailInline,)
 

class SystemSpecificationForm(forms.ModelForm):
    def clean(self):
        """
        Makes sure the selected lockout regions are available to the reference system 
        If the reference system has specific regions associeted to it, then only those regions are allowed 
        Otherwise, only non-scoped regions are allowed 
        """
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

admin.site.register(Currency)

admin.site.register(StorageUnit)

admin.site.register(Donation, AnyBundleAdmin)
admin.site.register(Purchase, AnyBundleAdmin)

admin.site.register(Location)
admin.site.register(PurchaseContext)

admin.site.register(LockoutRegion)
admin.site.register(BaseSystem)
admin.site.register(SystemMediaPair)

admin.site.register(CommonInterfaceDetail, CommonInterfaceDetailAdmin)
admin.site.register(SystemInterfaceDetail, SystemInterfaceDetailAdmin)
admin.site.register(InterfacesSpecification, InterfacesSpecificationAdmin)
#admin.site.register(SystemInterfaceDetail, SystemInterfaceDetailAdmin)
admin.site.register(SystemSpecification, SystemSpecificationAdmin)

admin.site.register(SystemVariant)

## Debug
admin.site.register(TagToOccurrence)

