from .config_utils import *

from .enumerations import Country

from django.db import models
from django.contrib import admin
from django.core.exceptions import ValidationError

import collections

import data_manager.models


class Region:
    FREE = "none"
    ASIA = "NTSC-J"
    CHINA = "NTSC-C"
    NORTH_AMERICA = "NTSC-U/C"
    PAL = "PAL"

    class Nes:
        NTSC = "NES-NTSC"
        PAL_A = "NES-PALA"
        PAL_B = "NES-PALB"

    DATA = (
        (FREE, "Region free"),
        (PAL, "Pal regions"),
        (NORTH_AMERICA, "North America"),
        (ASIA, "Japan and Asia"),
        (CHINA, "China"),
        ("NES",
            ((Nes.NTSC, "NTSC"),
            (Nes.PAL_A, "PAL-A"),
            (Nes.PAL_B, "PAL-B"),)
        ),
    )
    
    @classmethod
    def get_choices(cls):
        return cls.DATA
    
    @classmethod
    def choices_maxlength(cls):
        return 8


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
    # Can be left blank, meaning it is unknown (there is a value for "region free")
    region  = models.CharField(max_length=Region.choices_maxlength(), choices=Region.get_choices(), blank=True)
    version = models.CharField(max_length=20, blank=True) 

    ## Barcode is not mandatory because some nested release will not have a barcode (eg. pad with a console)

    system_specification = models.ForeignKey("SystemSpecification", blank=True, null=True) # immaterials do not specify it


class OccurrenceDeploymentBase(models.Model):
    class Meta:
        abstract = True

    collecster_material_fields = ("blister",)

    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    origin = models.CharField(max_length=OccurrenceOrigin.choices_maxlength(), choices=OccurrenceOrigin.get_choices())
    #tag = models.ImageField(upload_to=name_tag, blank=True) #TODO
    blister = models.BooleanField(help_text="Indicates whether a blister is still present.")

    note = models.CharField(max_length=256, blank=True) # Not sure if it should not be a TextField ?

##
## Extra models
##

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
    nickname   = models.CharField(max_length=20, blank=True)

    def __str__(self):
            return "{} {}".format(self.first_name, self.last_name)

#
# 
#
class SystemSpecification(models.Model):
    pass


class Color(models.Model):
    """ Color is a table listing available color choices (populated by fixture). """
    """ It appears as a more general solution over the fixed choice field in models, because it allows """
    """ ManyToOne and ManyToMany relationships very easily"""
    name = models.CharField(max_length=30, unique=True)

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

def register_custom_models(site):
   site.register(Company)
   site.register(StorageUnit)
   site.register(Location)
   site.register(Person)

   site.register(Donation, AnyBundleAdmin)
   site.register(Purchase, AnyBundleAdmin)

   site.register(PurchaseContext)

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

#
#
#    class Console(AbstractBase):
#       pass
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
    DEMO        = compose(SOFTWARE, (RelSp.Demo,))
    MEMORY      = compose(HARDWARE, (RelSp.Memory,))
    DIR_INPUT   = compose(HARDWARE, (RelSp.DirectionalController,))


class OccurrenceSpecific(object):
    """ OccurrenceSpecific classes are added to Occurrence instances depending on their nature(s) """

    class AbstractBase(models.Model):
        class Meta:
            abstract = True
        release = models.ForeignKey('Occurrence')

    class Operational(AbstractBase):
        YES = "Y"
        NO = "N"
        UNKNOWN = "?"

        CHOICES = (
            (UNKNOWN, "N/A"),
            (YES, "Yes"),
            (NO, "No"),
        )
        working_condition = models.CharField(max_length=1, choices=CHOICES, default=UNKNOWN)

    class Console(AbstractBase):
        region_modded = models.BooleanField()
        copy_modded = models.BooleanField()


OccSp = OccurrenceSpecific


class OccurrenceCategory:
    EMPTY       = ()
    OPERATIONAL = (OccSp.Operational,)
    CONSOLE     = (OccSp.Operational, OccSp.Console,)


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

    DataTuple = collections.namedtuple("DataTuple", ["ui_value", "ui_group", "release_category", "occurrence_category", "automatic_attributes"])
    DATA = collections.OrderedDict((
        (COMBO,     DataTuple(COMBO,        UIGroup._HIDDEN,    ReleaseCategory.COMBO,     OccurrenceCategory.EMPTY,    (),             )),

        (CONSOLE,   DataTuple('Console',    UIGroup._TOPLEVEL,  ReleaseCategory.HARDWARE,  OccurrenceCategory.CONSOLE,      automatic_self )),
        (GAME,      DataTuple('Game',       UIGroup.SOFT,       ReleaseCategory.SOFTWARE,  OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (DEMO,      DataTuple('Demo',       UIGroup.SOFT,       ReleaseCategory.DEMO,      OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (GUN,       DataTuple('Gun',        UIGroup.ACCESSORY,  ReleaseCategory.HARDWARE,  OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (PAD,       DataTuple('Pad',        UIGroup.ACCESSORY,  ReleaseCategory.DIR_INPUT, OccurrenceCategory.OPERATIONAL,  automatic_self )),
    ))
