from django.db import models
from django.core.exceptions import ValidationError

import collections

import data_manager.models
from .enumerations import Country

#TODEL
#import wdb

def compose(*args):
    """ Used to compose category from by extending another category """
    return tuple([element for tupl in args for element in tupl])


def is_material(release):
    """ The notion of immaterial needs to be a core concept, because some core behaviour depends on it"""
    """ eg. define application logic that an immterial cannot have attribute nor nested elements """
    """ Yet not to force having an immaterial field (for cases were there are no immaterials), it is abstracted through this function """
    return True 


##
## Customization of the 3 base models
##
class ConceptDeploymentBase(models.Model):
    """ An abstract base for the Concept model, allowing to give it deployment-specific fields without introducing """
    """ an additional DB table. """  
    class Meta:
        abstract = True

    discogs_mrelease_code  = models.CharField(max_length= 60, blank=True)  
    # Must allow null for the special concepts (like _COMBO), but the user should not be allowed to leave them blank
    artist   = models.ForeignKey("Artist", null=True)
    year    = models.DecimalField(max_digits=4, decimal_places=0, null=True) 
    
 
class ReleaseDeploymentBase(models.Model):
    """ An abstract base for the Release model, allowing to give it deployment-specific fields without introducing """
    """ an additional DB table. """  
    class Meta:
        abstract = True
    
    discogs_release_code  = models.CharField(max_length= 60, blank=True)  

    barcode = models.CharField(max_length=20, blank=True)
    number  = models.CharField(max_length=40, blank=True)
    country = models.CharField(max_length=Country.choices_maxlength(), choices=Country.get_choices(), blank=True)
    #year    = models.DecimalField(max_digits=4, decimal_places=0) 
    label   = models.ForeignKey("Label")
                    
    VINYL_STANDARD  = "VI_STD"
    VINYL_AUDIO     = "VI_180"
    CD_STANDARD     = "CD_STD"
    CD_SHM          = "CD_SHM"
    _support_choices = (
        ("Vinyl", ( (VINYL_STANDARD, "Standard"), (VINYL_AUDIO, "Audiophile"), )),
        ("CD", ( (CD_STANDARD, "Standard"), (CD_SHM, "SHM-CD"), )),
    )
    support = models.CharField(max_length=6, choices=_support_choices)
            
    SINGLE  = "SG"
    EP      = "EP"
    LP      = "LP"
    type    = models.CharField(max_length=2, choices=((SINGLE, "Single"), (EP, "EP"), (LP, "LP"),) )


class OccurrenceDeploymentBase(models.Model):
    class Meta:
        abstract = True

    purchase_price  = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    purchase_date   = models.DateField(blank=True, null=True)


##
## Additional models
##
class Artist(models.Model):
    name = models.CharField(max_length= 60)  

    def __str__(self):
        return "{}".format(self.name)


class Label(models.Model):
    name = models.CharField(max_length= 60)  

    def __str__(self):
        return "{}".format(self.name)


##
## Specific
##

class ReleaseCategory:
    EMPTY       = ()

class OccurrenceCategory:
    EMPTY       = ()


def get_attribute_category(category_name):
    models = data_manager.models
    return models.AttributeCategory.objects.get(name=category_name)

def get_attribute(category_name, attribute_name):
    models = data_manager.models
    return models.Attribute.objects.get(category=get_attribute_category(category_name), name=attribute_name)


def automatic_any():
    return (
        get_attribute("content", "media"),
        get_attribute("packaging", "sleeve"),
    )

# Intended to be used for implicit occurence attributes (unused now)
def self_software(release):
    try:
        material = not ReleaseSpecific.Software.objects.get(release=release).immaterial
    except ReleaseSpecific.Software.DoesNotExist:
        # The Software specific is not created id its form stayed empty (=> 'immaterial' was not checked)
        material = True
    return implicit_self(release) if material else ()


class ConceptNature:
    class UIGroup:
        _HIDDEN         = "_HIDDEN"
        _TOPLEVEL       = ""

    COMBO = "_COMBO"

    RECORD = "REC"

    DataTuple = collections.namedtuple("DataTuple", ["ui_value", "ui_group", "release_category", "occurrence_category", "automatic_attributes"])
    DATA = ((
        (COMBO,     DataTuple(COMBO,    UIGroup._HIDDEN,    ReleaseCategory.EMPTY,     OccurrenceCategory.EMPTY,    (),             )),

        (RECORD,    DataTuple('Record', UIGroup._TOPLEVEL,  ReleaseCategory.EMPTY,     OccurrenceCategory.EMPTY,        automatic_any )),
    ))


##
## Generic methods (no need for customization)
##
    @classmethod
    def choices_maxlength(cls):
        """ Returns the number of characters required to store any Nature into the DB """
        return max ([len(db_value) for db_value in cls.DATA])

    @classmethod
    def get_choices(cls):
        """ Returns the Nature choices for Concepts """
        #grouped = [(group, tuple([(line[0], line[1]) for line in tupl])) for group, tupl in cls.DATA.items() if group]
        #toplevel = [(line[0], line[1]) for line in [tupl for tupl in cls.DATA.get(cls.UIGroup._TOPLEVEL, ())]]
        #return tuple(toplevel) + tuple(grouped)
        toplevel = []
        sorted_groups = collections.defaultdict(list)
        for db_value, data in cls.DATA.items():
            pair = (db_value, data.ui_value)
            (toplevel if (data.ui_group is cls.UIGroup._TOPLEVEL) else sorted_groups[data.ui_group]).append(pair)
        return tuple(toplevel + [(ui_group, tuple(pairs)) for ui_group, pairs in sorted_groups.items() if ui_group != cls.UIGroup._HIDDEN])

        #return (
        #    ("console", "console"),
        #    ( "ACCESSORY", (("pad", "pad"), ("gun", "gun")) ),
        #)


    @classmethod
    def _get_specifics(cls, nature_set, model_name):
        unique_specific_set = collections.OrderedDict()
        for nature in nature_set:
            for specific in getattr(cls.DATA[nature], "{}_category".format(model_name)):
                unique_specific_set[specific] = None
        return unique_specific_set.keys()    
        
    @classmethod
    def get_release_specifics(cls, nature_set):
        return cls._get_specifics(nature_set, "release")

    @classmethod
    def get_occurrence_specifics(cls, nature_set):
        return cls._get_specifics(nature_set, "occurrence")

    @classmethod
    def get_concept_automatic_attributes(cls, concept):
        unique_automatic_attribs = collections.OrderedDict()
        models = data_manager.models

        for nature in concept.all_nature_tuple:
            automatics = cls.DATA[nature].automatic_attributes 
            if callable(automatics):
                automatics = automatics()
            for attribute in automatics:
                 unique_automatic_attribs[attribute] = None

        return list(unique_automatic_attribs.keys())

    ##
    ## Note: This method implemented proper implicit attributes, that are not shown on the Release add page
    ## but are then attributes attached to each Occurence instantiated from the Release.
    ## Implicit attributes are is disabled for the moment.
    ## To re-enable, it requires to allow ReleaseAttribute.release to be nullable
    ## and to make utils.all_release_attributes() to call this function.
    ##
    #@classmethod
    #def get_release_implicit_attributes(cls, release):
    #    unique_implicit_attribs = collections.OrderedDict()
    #    models = data_manager.models

    #    for nature in release.concept.all_nature_tuple:
    #        implicits = cls.DATA[nature].implicit_attributes 
    #        if callable(implicits):
    #            implicits = implicits(release)

    #        for attribute in implicits:
    #            release_attribute = models.ReleaseAttribute.objects.get_or_create(release=None, attribute=attribute)[0]
    #            unique_implicit_attribs[release_attribute] = None

    #    return list(unique_implicit_attribs.keys())
