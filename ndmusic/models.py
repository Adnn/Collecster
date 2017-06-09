# Need to be executed too: the Concept base models are depending on ConfNature, defined per application.
with open("data_manager/models.py") as f:
        code = compile(f.read(), "data_manager/models.py", 'exec')
        exec(code)

from data_manager import enumerations

from django.dispatch import receiver
from django.db.models import signals

import collections


##
## Forwarding most base models
##

# Does not allow for additional natures.
# Yet this class name is used by some of the data_manager code, so it is still defined, but as abstract.
class ConceptNature(ConceptNatureBase):
    class Meta:
        abstract = True

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

class ReleaseAttribute(ReleaseAttributeBase):
    pass

class ReleaseCustomAttribute(ReleaseCustomAttributeBase):
    pass

class ReleaseComposition(ReleaseCompositionBase):
    pass

class OccurrenceAnyAttribute(OccurrenceAnyAttributeBase):
    pass

class OccurrenceComposition(OccurrenceCompositionBase):
    pass


##
## Customization of the 3 base models
##
class Concept(ConceptBase):
    class Meta:
        unique_together =  ("distinctive_name", "year")

    """ 
    Concret Concept, deriving from abstract ConceptBase, to give it deployment-specific fields 
    without introducing an additional DB table. 
    """  
    discogs_mrelease_code   = models.CharField(max_length= 60, blank=True)  

    # Must allow null for the special concepts (like _COMBO), but the user should not be allowed to leave them blank
    artist  = models.ForeignKey("Artist", null=True)
    year    = models.DecimalField(max_digits=4, decimal_places=0, null=True) 
    
 
Concept._meta.get_field('primary_nature').default = ConfigNature.RECORD


class Release(ReleaseBase):
    barcode = models.CharField(max_length=20, blank=True)
    number  = models.CharField(max_length=40, blank=True)
    country = models.CharField(max_length=enumerations.Country.choices_maxlength(),
                               choices=enumerations.Country.get_choices(),blank=True)
    label   = models.ForeignKey("Label")
    #year    = models.DecimalField(max_digits=4, decimal_places=0) 
                    
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


class Occurrence(OccurrenceBase):
    purchase_price  = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    purchase_date   = models.DateField(blank=True, null=True)


##
## Extra models
##
class Artist(models.Model):
    name = models.CharField(max_length= 60)  

    def __str__(self):
        return "{}".format(self.name)


class Label(models.Model):
    name = models.CharField(max_length= 60)  

    def __str__(self):
        return "{}".format(self.name)
