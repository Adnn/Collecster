from .config_utils import *

from .enumerations import Country

import data_manager.models

from django import forms
from django.db import models
from django.contrib import admin
from django.conf import settings
from django.core.exceptions import ValidationError
from django.template import RequestContext, loader
from django.shortcuts import render

import pyqrcode

import collections, os, struct


configuration_name = "advg"

class OccurrenceOrigin():
    ORIGINAL = u'OR'
    BUY_USAGE = u'BU'
    BUY_COLLEC = u'BC'
    #For lost/stolen original elements...
    BUY_AGAIN = u'BA'
    GIFT = u'GF'

    DataTuple = collections.namedtuple("OriginDataTuple", ["ui_value", "tag_color"])
    #colors, see : http://www.w3schools.com/html/html_colornames.asp
    DATA = collections.OrderedDict((
        (ORIGINAL,    DataTuple(u'Original',        'red')),
        (BUY_USAGE,   DataTuple(u'Buy usage',       'royalblue')),
        (BUY_COLLEC,  DataTuple(u'Buy collection',  'green')),
        (BUY_AGAIN,   DataTuple(u'Buy back',        'gold')),
        (GIFT,        DataTuple(u'Gift',            'hotpink')),
    ))

    @classmethod
    def get_choices(cls):
        return [(key, value.ui_value) for key, value in cls.DATA.items()]

    @classmethod
    def choices_maxlength(cls):
        return max ([len(db_value) for db_value in cls.DATA])


def is_material(release):
    """ The notion of immaterial needs to be a core concept, because some core behaviour depends on it"""
    """ eg. define application logic that an immterial cannot have attribute nor nested elements """
    """ Yet not to force having an immaterial field (for cases were there are no immaterials), it is abstracted through this function """
    return not release.immaterial


def generate_qrcode(occurrence, tag_to_occurrence):
    reserved = 0 #For later use
    #user_guid   = UserExtension.objects.get(person=occurrence.owner).guid
    user_guid = tag_to_occurrence.user.guid
    deployment = data_manager.models.Deployment.objects.get(configuration=configuration_name)
    collection_id = data_manager.models.UserCollection.objects.get(user=user_guid, deployment=deployment).collection_local_id 
    #TODO Handle the object type when other types will be allowed
    objecttype_id = 1 # There is a single object type at the moment: the occurrence
    tag_occurrence_id = tag_to_occurrence.tag_occurrence_id 
    data = struct.pack("<BHBII", reserved, collection_id, objecttype_id, user_guid, tag_occurrence_id)

    return pyqrcode.create(data, version=1, error="M", mode="binary")


def generate_tag(occurrence):
    tag_version = 2
    qr_filename = "qr_v{}.png".format(tag_version)

    tag_to_occurrence = data_manager.models.TagToOccurrence.objects.get(occurrence=occurrence)
    
    working = OccurrenceSpecific.OperationalOcc.objects.get(occurrence=occurrence.pk).working_condition

    template = loader.get_template('tag/v2.html')
    context = {
        "release": occurrence.release,
        "tag": {"version": tag_version, "file": qr_filename},
        "collection": {"shortname": "VG", "objecttype": "OCC"},
        "occurrence": occurrence,
        "working": working,
    }
    
    # Here, uses the occurrence PK in the DB, not the tag_occurrence id, because we see this part of the filesystem
    # like a direct extension to the DB
    # As a consequence, a potential migration of a collection would need to rename those folder to map to the DB.
    directory = "{}/data_manager/occurrences/{}/tags/".format(settings.MEDIA_ROOT, occurrence.pk)
    if not os.path.exists(directory):
        os.makedirs(directory)

    QR_MODULE_SIZE=8*4
    qr = generate_qrcode(occurrence, tag_to_occurrence)
    qr.png(os.path.join(directory, qr_filename), scale=QR_MODULE_SIZE, quiet_zone=2)

    f = open(os.path.join(directory, "v{}.html".format(tag_version)), "w") #TODO some date and time ?
    f.write(template.render(context))
    f.close()

##
## Customization of the 3 base models
##

#class BlankIsNullURLField(models.URLField):
#    ## Not called when the value is left blank, which is ironic 
#    def clean(self, value, model_instance, ll):
#        cleaned = super(BlankIsNullURLField, self).clean(value, model_instance)
#        return cleaned if cleaned else None

class ConceptDeploymentBase(models.Model):
    """ An abstract base for the Concept model, allowing to give it deployment-specific fields without introducing """
    """ an additional DB table. """  
    class Meta:
        abstract = True

    url = models.URLField(blank=True) # Ideally, it should be unique, except for the "blank" value.
                                      # But that poses a problem because the blank is empty string (see: http://stackoverflow.com/a/1400046/1027706)

    developer = models.ForeignKey('Company')

class ReleaseDeploymentBase(models.Model):
    """ An abstract base for the Release model, allowing to give it deployment-specific fields without introducing """
    """ an additional DB table. """  
    class Meta:
        abstract = True
    
    collecster_material_fields = ("loose", "barcode", "region", "system_specification")

    immaterial  = models.BooleanField(default=False) 

    url = models.URLField(blank=True) # Ideally, it should be unique, except for the "blank" value.
    loose   = models.BooleanField() 

    barcode = models.CharField(max_length=20, blank=True)
    release_regions  = models.ManyToManyField("ReleaseRegion")
    version = models.CharField(max_length=20, blank=True) 

    ## Barcode is not mandatory because some nested release will not have a barcode (eg. pad with a console)

    system_specification = models.ForeignKey("SystemSpecification", blank=True, null=True) # immaterials do not specify it

    def tag_regions(self):
        return list(collections.OrderedDict.fromkeys([region.tag_region for region in self.release_regions.all()]))
        
    def compatible_systems(self):
        keys = []
        if self.system_specification:
            keys = [pair.system.abbreviated_name
                    for pair in self.system_specification.interface_description.requires.all()]
        return list(collections.OrderedDict.fromkeys(keys))
            
        
            

class OccurrenceDeploymentBase(models.Model):
    class Meta:
        abstract = True

    collecster_material_fields = ("blister",)

    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    origin = models.CharField(max_length=OccurrenceOrigin.choices_maxlength(), choices=OccurrenceOrigin.get_choices())
    #tag = models.ImageField(upload_to=name_tag, blank=True) #TODO
    blister = models.BooleanField(help_text="Indicates whether a blister is still present.")

    note = models.CharField(max_length=256, blank=True) # Not sure if it should not be a TextField ?

    def admin_post_save(self):
        generate_tag(self)

    def origin_color(self):
        return OccurrenceOrigin.DATA[self.origin].tag_color

##
## Extra models
##

class TagRegion(models.Model):
    name = models.CharField(max_length=3, unique=True, help_text="The value printed on the occurrence tag.")

    def __str__(self):
        return self.name


class ReleaseRegion(models.Model):
    name = models.CharField(max_length=60, unique=True)
    parent_region = models.ForeignKey("self", blank=True, null=True)
    tag_region = models.ForeignKey("TagRegion")

    detail = models.CharField(max_length=20, unique=True)

    def __str__(self):
        display = "{}".format(self.name)
        if self.parent_region:
            display = "{}/{}".format(self.parent_region, display)
        return display

#
# Company
#
class CompanyService(models.Model):
    name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.name

class Company(models.Model):
    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Companies"

    name = models.CharField(max_length=60, unique=True)
    services = models.ManyToManyField(CompanyService)
    # Perhaps there is actually a field that give the "type" of the structure, which could be a group, a person, a studio...
    is_individual = models.BooleanField(default=False, verbose_name="Is it a single person name ?")

    def __str__(self):
        return self.name

#
# Bundles
#
class Bundle(models.Model):
    arrival_date = models.DateField()
    note = models.CharField(max_length=256, blank=True) # Not sure if it should not be a TextField ?

#class BundlePicture(models.Model):
#    bundle = models.ForeignKey(Bundle)
#    image = models.ImageField(upload_to=name_bundlepicture)

class BundleComposition(models.Model):
    bundle     = models.ForeignKey(Bundle)
    occurrence = models.OneToOneField("Occurrence")
    brand_new  = models.BooleanField(default=False)

    #@classmethod
    #def get_content_string(cls, bundle, limit=10):
    #    return "({})".format(', '.join(x.instance.instanciated_release.get_display_name()
    #                                   for x in cls.objects.filter(bundle=bundle)[:limit]))


class Location(models.Model):
    """ A country, and optionaly a city """
    class Meta:
        unique_together = ("country", "city", "post_code",)

    country = models.CharField(max_length=2, choices=Country.CHOICES)

    city      = models.CharField(max_length=60, blank=True)
    post_code = models.CharField(max_length=8,  blank=True)

    def __str__(self):
        return '['+self.country+'] ' + self.city + ("("+self.post_code+")") if self.post_code else ""
 

class PurchaseContextCategory:
    INTERNET_SHOP = "NET"
    INTERNET_ADS  = "ADS"
    SHOP = "SHP"
    SECONDHAND = "SEC"
    WORD_MOUTH = "WOM" # Bouche à oreille, en discutant quoi

    DATA = collections.OrderedDict((
        ("Online", (
            (INTERNET_SHOP, "e-shop"),
            (INTERNET_ADS, "Advertisements"),
        )),
        ("Offline", (
            (SHOP, "Shop"),
            (SECONDHAND, "Secondhand sale"),
            (WORD_MOUTH, "Word of mouth"),
        ))
    ))

    @classmethod
    def get_choices(cls):
        base = [("Online", cls.DATA["Online"])]
        base.extend(cls.DATA["Offline"])
        return base

    @classmethod
    def choices_maxlength(cls):
        return 3

    @classmethod
    def is_online(cls, value):
        return value in [db_value for db_value, ui_value in cls.DATA["Online"]]

def clean_complement(instance, errors):
    if instance.address_complement and not instance.location:
        errors["location"] =  ValidationError("An address must complement a location.", code="invalid")


class PurchaseContext(models.Model):
    category = models.CharField(max_length=PurchaseContextCategory.choices_maxlength(),
                                choices=PurchaseContextCategory.get_choices())
    name = models.CharField(max_length=60)

    location = models.ForeignKey(Location, blank=True, null=True)
    address_complement  = models.CharField(max_length=60, blank=True)

    url = models.URLField(blank=True)

    def clean(self):
        """ Online contexts cannot specify a location nor address complement """
        """ Only contexts with a location can provide an address complement """
        errors = {} 
        if PurchaseContextCategory.is_online(self.category):
            if not self.url:
                errors["url"] = ValidationError("This field is mandatory for online contexts.",
                                                 code="mandatory")
            if self.location:
                errors["location"] = ValidationError("Field not available for online contexts.",
                                                     code="invalid")
            if self.address_complement:
                errors["address_complement"] = ValidationError("Field not available for online contexts.",
                                                               code="invalid")
        else:
            clean_complement(self, errors)

        if errors:
            raise ValidationError(errors)


    def __str__(self):
        value = self.name
        if self.address_complement:
            value += ", {}".format(self.address_complement)
        if self.location:
            value += ", {}".format(self.location)
        return value


class Purchase(Bundle):
    price   = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    context = models.ForeignKey(PurchaseContext)

    shipping_cost = models.DecimalField(max_digits=6,  decimal_places=2, blank=True, null=True)

    PICKUP = "P"
    MAIL = "M"
    retrieval          = models.CharField(max_length=1, choices=((PICKUP, "Local pickup"),(MAIL, "Shipped")), blank=True)
    location           = models.ForeignKey(Location, blank=True, null=True, help_text="The location the object shipped from, or the pickup location.")
    address_complement = models.CharField(max_length=60, blank=True)

    def clean(self):
        # The only way I found to check if the context was set
        try:
            self.context
        except PurchaseContext.DoesNotExist:
            return

        errors = {}
        if self.context.category != PurchaseContextCategory.INTERNET_ADS:
            def forbidden_field(field_name):
                if getattr(self, field_name):
                    errors[field_name] = ValidationError("Field only available for internet advertisements context.", code="invalid")

            #map(forbidden_field, ("retrieval", "location", "address_complement")) # TODO why does not that work ???
            for field in ("retrieval", "location", "address_complement"):
                forbidden_field(field)
        else:
            if not self.retrieval:
                errors["retrieval"] = ValidationError("This field is mandatory for internet advertisements context.",
                                                     code="mandatory")
            clean_complement(self, errors)

        if errors:
            raise ValidationError(errors)


    def __str__(self):
        #return "{} {} {}".format(self.acquisition_date, self.context, BundleComposition.get_content_string(self))
        return "{} {} {}".format(self.arrival_date, self.context, "TODO content")


class Donation(Bundle):
    donator = models.ForeignKey("Person")

#
# Person
#
class Person(models.Model):
    first_name = models.CharField(max_length=20)
    last_name  = models.CharField(max_length=20)
    nickname   = models.CharField(max_length=20, unique=True) # Required, because it is printed on the tag

    def __str__(self):
            return "{} {}".format(self.first_name, self.last_name)

#
# Platform
#
class LockoutRegion(models.Model):
    region_name = models.CharField(max_length=10)
    note        = models.CharField(max_length=60)
    limit_scope = models.ManyToManyField("BaseSystem", blank=True)

    def __str__(self):
        display = "{}".format(self.region_name)
        if self.limit_scope.count():
            display = "({}) {}".format("/".join(["{}".format(scope.abbreviated_name) for scope in self.limit_scope.all()]), display)
        return display

    #FREE = "_none"
    #ASIA = "NTSC-J"
    #CHINA = "NTSC-C"
    #NORTH_AMERICA = "NTSC-U/C"
    #PAL = "PAL"

    #class Nes:
    #    NTSC = "NES-NTSC"
    #    PAL_A = "NES-PALA"
    #    PAL_B = "NES-PALB"

    #DATA = (
    #    (FREE, "Region free"),
    #    (PAL, "Pal regions"),
    #    (NORTH_AMERICA, "North America"),
    #    (ASIA, "Japan and Asia"),
    #    (CHINA, "China"),
    #    ("NES",
    #        ((Nes.NTSC, "NTSC"),
    #        (Nes.PAL_A, "PAL-A"),
    #        (Nes.PAL_B, "PAL-B"),)
    #    ),
    #)
    #
    #@classmethod
    #def get_choices(cls):
    #    return cls.DATA
    #
    #@classmethod
    #def choices_maxlength(cls):
    #    return 8


class BaseSystem(models.Model):
    ARCADE = "A"
    HOME   = "H"

    name = models.CharField(max_length=30, unique=True)
    brand = models.ForeignKey(Company)
    generation = models.DecimalField(max_digits=2, decimal_places=0)
    destination = models.CharField(max_length=1, choices=((ARCADE, "Arcade"), (HOME, "Home entertainment")))
    upgrade_for = models.ForeignKey("self", blank=True, null=True) # TODO: should prevent an instance from referencing itself

    abbreviated_name = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return "{} {}".format(self.brand, self.name)

class SystemMediaPair(models.Model):
    class Meta:
        unique_together = ("system", "media")

    system = models.ForeignKey(BaseSystem) 
    media  = models.CharField(max_length=10)
    wireless = models.BooleanField(default=False)

    abbreviated_name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return "{}--{} ({})".format(self.system, self.media, self.abbreviated_name)


class SystemInterfaceDescription(models.Model):
    class Meta:
        unique_together = ("reference_system", "internal_name")

    # Useful for console on chip for example
    reference_system = models.ForeignKey(BaseSystem)
    internal_name = models.CharField(max_length=60)
    provides = models.ManyToManyField(SystemMediaPair, through="ProvidedInterface", related_name="provided_to_set")
    requires = models.ManyToManyField(SystemMediaPair, through="RequiredInterface", related_name="required_by_set")

    def __str__(self):
        return "{}: {}".format(self.reference_system, self.internal_name)

# Need to separate as two tables, because Django would not be able to know if it is a provided or required otherwise
class BaseSpecificationInterface(models.Model):
    class Meta:
        abstract = True

    specification = models.ForeignKey(SystemInterfaceDescription)
    interface = models.ForeignKey(SystemMediaPair)
    cardinality = models.PositiveSmallIntegerField(default=1)
    regional_lockout_override = models.ManyToManyField(LockoutRegion, blank=True)

class ProvidedInterface(BaseSpecificationInterface):
    pass

class RequiredInterface(BaseSpecificationInterface):
    pass

class SystemSpecification(models.Model):
    # TODO M2M not allowed in unique_together clause, how to enforce ?
    #class Meta:
    #    unique_together = ("regional_lockout", "bios_version", "interface")

    regional_lockout     = models.ManyToManyField(LockoutRegion)
    bios_version         = models.CharField(max_length=10, blank=True)
    interface_description = models.ForeignKey(SystemInterfaceDescription)

    def __str__(self):
        display = "{}".format(self.interface_description)
        if self.regional_lockout.count():
           display = "{} [{}]".format(display,
                                      ", ".join(["{}".format(lockout) for lockout in self.regional_lockout.all()]))
        if self.bios_version:
           display = "{} (bios: {})".format(display, self.bios_version)
        return display 


#
# Misc
#
class Color(models.Model):
    """ Color is a table listing available color choices (populated by fixture). """
    """ It appears as a more general solution over the fixed choice field in models, because it allows """
    """ ManyToOne and ManyToMany relationships very easily"""
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class BatteryType(models.Model):
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name

     
class InputType(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class StorageUnit(models.Model):
    class Meta:
        unique_together = ("name", "brand")

    name = models.CharField(max_length=20)
    symbol = models.CharField(max_length=5, blank=True)

    #prorietary = models.BooleanField()
    brand = models.ForeignKey(Company, blank=True, null=True)

    #def clean(self):
    #    if self.prorietary and not self.brand:
    #        raise ValidationError({"brand": ValidationError("Proprietary units cannot leave this field blank.", code="invalid")})
    def validate_unique(self, exclude=None):
        """ Needed to prevent adding several brandless units with the same name """
        """ because a NULL foreign key does not compare equal to NULL """
        if not self.brand: #if there is a brand, we can rely on the unique_together constraint
            qs = StorageUnit.objects.filter(name=self.name).filter(brand=None)
            if not self._state.adding:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError("A non-proprietary unit with this name already exists.", code="invalid")
        super(StorageUnit, self).validate_unique(exclude)
                

    def __str__(self):
        if self.brand:
            return "[{}] {}".format(self.brand, self.name)
        else:
            return self.name
        

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
##
## Specifics
##
class ReleaseSpecific(object):
    """ ReleaseSpecific classes are added to Release instances depending on their nature(s) """

    class AbstractBase(models.Model):
        class Meta:
            abstract = True
        release = models.ForeignKey('Release')

    class Combo(AbstractBase):
        brand = models.ForeignKey('Company', blank=True, null=True)

    class Hardware(AbstractBase):
        color = models.ManyToManyField("Color")
        manufacturer = models.ForeignKey('Company', blank=True, null=True)
        wireless = models.BooleanField(default=False)
        battery_type = models.ForeignKey(BatteryType, blank=True, null=True)
        #model = models.CharField(max_length=20, blank=True)  ## Probably useless, since there is already 'version'

        def __str__(self):
           return "Hardware specific for release: {}".format(self.release)

    class DirectionalController(AbstractBase):
        direction_input_type = models.ManyToManyField(InputType)

    class Software(AbstractBase):
        publisher   = models.ForeignKey("Company", blank=True, null=True, related_name="published_software_set")
        porter      = models.ForeignKey("Company", blank=True, null=True, related_name="ported_software_set", verbose_name="Company realizing the port")
        collection_label = models.CharField(max_length=120, blank=True, verbose_name="Released in collection")

    class Accessory(AbstractBase):
        wireless        = models.BooleanField()
        force_feedback  = models.BooleanField()
        rumble_feedback = models.BooleanField()

        #turbo    = models.BooleanField() ## same thing as autofire, is not it ?
        autofire = models.BooleanField()
        slow     = models.BooleanField()

    class Console(AbstractBase):
       console_on_chip = models.BooleanField(default=False, help_text="Is this a (re-)implementation of a system on a single chip ?")
#
#
#    class Game(AbstractBase):
#        pass

    class Demo(AbstractBase):
        issue_number    = models.PositiveIntegerField(blank=True, null=True)
        games_playable  = models.ManyToManyField('Concept', blank=True, related_name='playable_demo_set')
        games_video     = models.ManyToManyField('Concept', blank=True, related_name='video_demo_set')

            ## Not sure if it is possible to query the M2M relationship (ValueError wether there is a provided value or not)
        #def clean(self):
        #    wdb.set_trace()
        #    if not self.games_playable and not self.games_video:
        #        raise ValidationError("The demo must have at least one game, video or playalbe.")

    class Memory(AbstractBase):
        capacity    = models.PositiveIntegerField()
        unit        = models.ForeignKey(StorageUnit)


RelSp = ReleaseSpecific


class ReleaseCategory:
    EMPTY       = ()
    COMBO       = (RelSp.Combo,)
    SOFTWARE    = (RelSp.Software,)
    HARDWARE    = (RelSp.Hardware,)
    CONSOLE     = compose(HARDWARE, (RelSp.Console,))
    DEMO        = compose(SOFTWARE, (RelSp.Demo,))
    MEMORY      = compose(HARDWARE, (RelSp.Memory,))
    DIR_INPUT   = compose(HARDWARE, (RelSp.DirectionalController,))


class OccurrenceSpecific(object):
    """ OccurrenceSpecific classes are added to Occurrence instances depending on their nature(s) """

    class AbstractBase(models.Model):
        class Meta:
            abstract = True
        occurrence = models.ForeignKey('Occurrence')

    class OperationalOcc(AbstractBase):
        YES = "Y"
        NO = "N"
        UNKNOWN = "?"

        CHOICES = (
            (UNKNOWN, "N/A"),
            (YES, "Yes"),
            (NO, "No"),
        )
        working_condition = models.CharField(max_length=1, choices=CHOICES, default=UNKNOWN)

    class ConsoleOcc(AbstractBase):
        region_modded = models.BooleanField()
        copy_modded = models.BooleanField()


OccSp = OccurrenceSpecific


class OccurrenceCategory:
    EMPTY       = ()
    OPERATIONAL = (OccSp.OperationalOcc,)
    CONSOLE     = (OccSp.OperationalOcc, OccSp.ConsoleOcc,)


def automatic_self():
    return (get_attribute("content", "self"), )

# Intended to be used for implicit occurence attributes (unused now)
def self_software(release):
    try:
        material = not ReleaseSpecific.Software.objects.get(release=release).immaterial
    except ReleaseSpecific.Software.DoesNotExist:
        # The Software specific is not created id its form stayed empty (=> 'immaterial' was not checked)
        material = True
    return implicit_self(release) if material else ()


##
## Defines the natures and all their associeted data
##
class ConceptNature(ConceptNature):
    class UIGroup:
        _HIDDEN         = "_HIDDEN"
        _TOPLEVEL       = ""
        ACCESSORY       = "Accessory"
        SOFT            = "Software"

    COMBO = "_COMBO"

    CONSOLE = "CONSOLE"
    DEMO = "DEMO"
    GAME = "GAME"
    OS = "OS"

    PAD = "PAD"
    GUN = "GUN"

    DataTuple = collections.namedtuple("DataTuple", ["ui_value", "ui_group", "tag_color", "release_category", "occurrence_category", "automatic_attributes"])
    DATA = collections.OrderedDict((
        (COMBO,     DataTuple(COMBO,        UIGroup._HIDDEN,    "grey",     ReleaseCategory.COMBO,     OccurrenceCategory.EMPTY,    (),             )),

        (CONSOLE,   DataTuple('Console',    UIGroup._TOPLEVEL,  "red",      ReleaseCategory.CONSOLE,   OccurrenceCategory.CONSOLE,      automatic_self )),
        (GAME,      DataTuple('Game',       UIGroup.SOFT,       "green",    ReleaseCategory.SOFTWARE,  OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (DEMO,      DataTuple('Demo',       UIGroup.SOFT,       "palegreen",ReleaseCategory.DEMO,      OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (GUN,       DataTuple('Gun',        UIGroup.ACCESSORY,  "blue",     ReleaseCategory.HARDWARE,  OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (PAD,       DataTuple('Pad',        UIGroup.ACCESSORY,  "blue",     ReleaseCategory.DIR_INPUT, OccurrenceCategory.OPERATIONAL,  automatic_self )),
        # application -> purple
    ))
