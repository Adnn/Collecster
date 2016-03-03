#from data_manager.models import * # Absolute path import, we do not execute this one because we can do without !
## Actually, we hardly can do without: tie Concept base models are depending on ConfNature, defined per application.
with open("data_manager/models.py") as f:
        code = compile(f.read(), "data_manager/models.py", 'exec')
        exec(code)

from .configuration import OccurrenceSpecific
from . import tag
from . import utils_path

# TODO sort out the enumeration
from data_manager.enumerations import Country

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

import collections, os


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


##
## Forwarding most models
##
class ConceptNature(ConceptNatureBase):
    pass

class TagToOccurrence(TagToOccurrenceBase):
    pass

class AttributeCategory(AttributeCategoryBase):
    pass

class Attribute(AttributeBase):
    pass

class Distinction(DistinctionBase):
    pass

class ReleaseDistinction(ReleaseDistinctionBase):
    pass

class ReleaseAttributeCodeExtension(models.Model):
    class Meta:
        abstract = True
    code = models.CharField(max_length=64, blank=True)
    code_type = models.CharField(blank=True, max_length=1, choices = (("S", "Serial number"), ("C", "Catalog / Internal"), ))

    def clean(self):
        if (self.code and not self.code_type) or (not self.code and self.code_type):
            raise ValidationError("code and code type must either be both specified or both left blank.", code="invalid")

class ReleaseAttribute(ReleaseAttributeBase, ReleaseAttributeCodeExtension):
    pass

class ReleaseCustomAttribute(ReleaseCustomAttributeBase, ReleaseAttributeCodeExtension):
    pass

class ReleaseComposition(ReleaseCompositionBase):
    pass

class OccurrenceAttribute(OccurrenceAttributeBase):
    pass

class OccurrenceCustomAttribute(OccurrenceCustomAttributeBase):
    pass

class OccurrenceComposition(OccurrenceCompositionBase):
    pass

##
## Customization of the 3 base models
##

#class BlankIsNullURLField(models.URLField):
#    ## Not called when the value is left blank, which is ironic 
#    def clean(self, value, model_instance, ll):
#        cleaned = super(BlankIsNullURLField, self).clean(value, model_instance)
#        return cleaned if cleaned else None

class Concept(ConceptBase):
    """ Specialization of the Concept model, to give it deployment-specific fields without introducing """
    """ an additional DB table. """  

    developer = models.ForeignKey('Company', null=True) # Allows null but not blank, for the _COMBO concept special case

    name_scope_restriction = models.ManyToManyField("ReleaseRegion", blank=True)
    year = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)


class Release(ReleaseBase):
    """ An abstract base for the Release model, allowing to give it deployment-specific fields without introducing """
    """ an additional DB table. """  

    collecster_properties = {
        "forbidden_on_material":                ("digitally_distributed", ),
        "forbidden_on_non_material":            ("loose", "barcode", ),
        "forbidden_on_embedded_immaterial":     ("system_specification", "release_regions", "partial_date", ),
        "required_on_non_embedded_immaterial":  ("release_regions", "system_specification", ),
    }

    immaterial              = models.BooleanField(default=False) 
    digitally_distributed  = models.BooleanField(default=False) 

    loose   = models.BooleanField() 

    ## Barcode is not mandatory because some nested release will not have a barcode (eg. pad with a console)
    ## neither will immaterials
    barcode = models.CharField(max_length=20, blank=True)
    release_regions  = models.ManyToManyField("ReleaseRegion", blank=True)
    version = models.CharField(max_length=20, blank=True) 

    system_specification = models.ForeignKey("SystemSpecification", blank=True, null=True) # immaterials do not specify it

    def is_embedded_immaterial(self):
        return not self.is_material() and not self.digitally_distributed

    def is_digital_immaterial(self):
        return not self.is_material() and self.digitally_distributed

    def tag_regions(self):
        return list(collections.OrderedDict.fromkeys([region.tag_region for region in self.release_regions.all()]))
        
    def compatible_systems(self):
        keys = []
        if self.system_specification:
            keys = [pair.system.abbreviated_name
                    for pair in self.system_specification.interface_description.requires.all()]
        return list(collections.OrderedDict.fromkeys(keys))
            
        

class Occurrence(OccurrenceBase):
    collecster_material_fields = ("blister",)

    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    origin = models.CharField(max_length=OccurrenceOrigin.choices_maxlength(), choices=OccurrenceOrigin.get_choices())
    #tag = models.ImageField(upload_to=name_tag, blank=True) #TODO
    blister = models.BooleanField(help_text="Indicates whether a blister is still present.")

    note = models.CharField(max_length=256, blank=True) # Not sure if it should not be a TextField ?
    # Uses a CharField, in case some "numbers" contain alphabetic characters
    unique_number = models.CharField(max_length=32, blank=True,
                help_text="An identifier uniquely attached to this occurrence (eg. collector numbered edition).")

    tag_url = models.URLField(null=True)

    def admin_post_save(self):
        if self.is_material():
            self.tag_url = tag.generate_tag(self)
            self.save()

    def origin_color(self):
        return OccurrenceOrigin.DATA[self.origin].tag_color

##
## Extra models
##

class ConceptUrl(models.Model):
    concept = models.ForeignKey("Concept")
    url = models.URLField(unique=True)

class ReleaseUrl(models.Model):
    release = models.ForeignKey("Release")
    url = models.URLField(unique=True)

class TagRegion(models.Model):
    name = models.CharField(max_length=3, unique=True, help_text="The value printed on the occurrence tag.")

    def __str__(self):
        return self.name


class ReleaseRegion(models.Model):
    name = models.CharField(max_length=60, unique=True)
    parent_region = models.ForeignKey("self", blank=True, null=True)
    tag_region = models.ForeignKey("TagRegion")

    detail = models.CharField(max_length=20, blank=True)

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
    donator = models.ForeignKey("supervisor.Person")

#
# Pictures
#
class PictureDetail():
    GROUP = u'GRP'
    FRONT = u'FRT'
    BACK = u'BCK'
    SIDE = u'SID'
    SIDE_LABEL = u'SLB'
    INSIDE = u'INS'
    DEFECT = u'DEF'

    DICT = collections.OrderedDict((
        (GROUP,     ("Group",)),
        (FRONT,     ("Front",)),
        (BACK,      ("Back",)),
        (SIDE,      ("Side",)),
        (SIDE_LABEL, ("Side label",)),
        (INSIDE,    ("Inside",)),
        (DEFECT,    ("Defect",)),
    ))

    @classmethod
    def get_choices(cls):
        return [(key, value[0]) for key, value in cls.DICT.items()]
   
    @classmethod
    def choices_maxlength(cls):
        return 3

def name_occurrence_picture(occurrence_picture, filename):
    return os.path.join(utils_path.instance_media_dir(Occurrence, occurrence_picture.occurrence, False), "pictures", filename)

def name_bundle_picture(bundle_picture, filename):
    return os.path.join(utils_path.instance_media_dir(Bundle, bundle_picture.bundle, False), "pictures", filename)

def name_release_picture(release_picture, filename):
    return os.path.join(utils_path.instance_media_dir(Release, release_picture.release, False), "pictures", filename)


class OccurrencePicture(models.Model):
    occurrence  = models.ForeignKey("Occurrence")
    # The 3 following fields implement a "generic relation"
    #(see: https://docs.djangoproject.com/en/1.9/ref/contrib/contenttypes/#generic-relations)
    # Note that the generic relation is not mandatory: for group pictures, no attribute should be specified
    attribute_type  = models.ForeignKey(ContentType, null=True)
    attribute_id    = models.PositiveIntegerField(null=True)
    attribute_object = GenericForeignKey("attribute_type", "attribute_id")

    detail          = models.CharField(max_length=PictureDetail.choices_maxlength(), choices=PictureDetail.get_choices(), blank=False, default=PictureDetail.GROUP)
    image_file      = models.ImageField(upload_to=name_occurrence_picture)

class BundlePicture(models.Model):
    bundle      = models.ForeignKey("Bundle")
    image_file  = models.ImageField(upload_to=name_bundle_picture)

class ReleasePicture(models.Model):
    release     = models.ForeignKey("Release")
    image_file  = models.ImageField(upload_to=name_release_picture)

#
# Platform
#
class LockoutRegion(models.Model):
    region_name = models.CharField(max_length=10)
    note        = models.CharField(max_length=60)
    limit_scope = models.ManyToManyField("BaseSystem", blank=True, help_text="When specified, this lockout will be limited to the selected systems.")

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

    name = models.CharField(max_length=30, unique=True, help_text="eg. 'Mega Drive', 'NES', ...")
    brand = models.ForeignKey(Company)
    generation = models.DecimalField(max_digits=2, decimal_places=0)
    destination = models.CharField(max_length=1, choices=((ARCADE, "Arcade"), (HOME, "Home entertainment")))
    upgrade_for = models.ForeignKey("self", blank=True, null=True) # TODO: should prevent an instance from referencing itself

    abbreviated_name = models.CharField(max_length=5, unique=True, help_text="Abbreviated name for the system, independently of any interface.")

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
        return self.code

     
class InputType(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class MediaType(models.Model):
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
        
# Create your models here.
