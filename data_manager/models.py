from django.db import models

from .configuration import ConceptNature as ConfNature, ReleaseDeploymentBase


##########
## Concept
##########

class ConceptNature(models.Model):
    concept = models.ForeignKey('Concept', related_name="additional_nature_set")
    nature  = models.CharField(max_length=ConfNature.choices_maxlength(), choices=ConfNature.get_choices())


class Concept(models.Model):
    common_name         = models.CharField(max_length= 60, blank=True)  
    distinctive_name    = models.CharField(max_length=180, unique=True)  
    primary_nature      = models.CharField(max_length=ConfNature.choices_maxlength(), choices=ConfNature.get_choices())
    # Todo: url optional

    def __str__(self):
        return self.common_name if self.common_name else self.distinctive_name

    @property
    def all_nature_tuple(self):
        return (self.primary_nature,) \
             + (self.additional_nature_set.all().values_list("nature")[0] if self.additional_nature_set.all() else ())
    

##########
## Release
##########

class Release(ReleaseDeploymentBase):
    ## Barcode is not mandatory because some nested release will not have a barcode (eg. pad with a console)
    concept = models.ForeignKey(Concept)
    name    = models.CharField(max_length=180, blank=True, verbose_name="Release's name")  
    date    = models.DateField(blank=True, null=True)
    barcode = models.CharField(max_length=20, blank=True)
    # Todo specificity (text, or list ?)
    # Todo edition ? What is that ?

    def __str__(self):
        return ("{}".format(self.name if self.name else self.concept))


#############
## Occurrence
#############

class Occurrence(models.Model):
    release     = models.ForeignKey(Release)
    #owner       = models.ForeignKey(Person) #TODO
        ## Some automatic date fields
    add_date        = models.DateTimeField(auto_now_add=True)
    lastmodif_date  = models.DateTimeField(auto_now=True)

