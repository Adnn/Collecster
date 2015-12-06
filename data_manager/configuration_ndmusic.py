from .config_utils import *

from django.db import models

import data_manager.models
from .enumerations import Country


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


def register_custom_models():
    admin.site.register(Artist)
    admin.site.register(Label)


##
## Categories for specifics
##
class ReleaseCategory:
    EMPTY       = ()

class OccurrenceCategory:
    EMPTY       = ()


##
## Defines the natures and all their associeted data
##
def automatic_any():
    return (
        get_attribute("content", "media"),
        get_attribute("packaging", "sleeve"),
    )


class ConceptNature(ConceptNature):
    class UIGroup:
        _HIDDEN         = "_HIDDEN"
        _TOPLEVEL       = ""

    COMBO = "_COMBO"

    RECORD = "REC"

    DataTuple = collections.namedtuple("DataTuple", ["ui_value", "ui_group", "release_category", "occurrence_category", "automatic_attributes"])
    DATA = collections.OrderedDict((
        (COMBO,     DataTuple(COMBO,    UIGroup._HIDDEN,    ReleaseCategory.EMPTY,     OccurrenceCategory.EMPTY,    (),             )),

        (RECORD,    DataTuple('Record', UIGroup._TOPLEVEL,  ReleaseCategory.EMPTY,     OccurrenceCategory.EMPTY,        automatic_any )),
    ))
