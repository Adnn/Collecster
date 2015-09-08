from django.db import models

from .configuration import ConceptNature as ConfNature, ReleaseDeploymentBase
from . import enumerations as enum


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
    

############
## Attribute
############

class AttributeCategory(models.Model):
    name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.name


class AbstractAttribute(models.Model):
    """ Abstract class containing all the field for an attribute, to be used by Attribute an ReleaseCustomAttribute """
    class Meta:
        abstract = True

    category    = models.ForeignKey(AttributeCategory)
    name        = models.CharField(max_length=60)
    description = models.CharField(max_length=180, blank=True)
    value_type  = models.CharField(max_length=enum.Attribute.Type.choices_maxlength(),
                                   choices=enum.Attribute.Type.get_choices())

    def __str__(self):
        return "[{}]{}".format(self.category, self.name)


class Attribute(AbstractAttribute):
    class Meta:
        unique_together = ("category", "name")


##########
## Release
##########

class Release(ReleaseDeploymentBase):
    concept = models.ForeignKey(Concept)
    name    = models.CharField(max_length=180, blank=True, verbose_name="Release's name")  
    date    = models.DateField(blank=True, null=True)
     ## Barcode is not mandatory because some nested release will not have a barcode (eg. pad with a console)
    barcode = models.CharField(max_length=20, blank=True)
    # Todo specificity (text, or list ?)
    # Todo edition ? What is that ?

    def __str__(self):
        return ("{}".format(self.name if self.name else self.concept))


class ReleaseAttribute(models.Model):
    release     = models.ForeignKey(Release)
    attribute   = models.ForeignKey(Attribute)
    note        = models.CharField(max_length=60, blank=True, null=True, help_text="Distinctive remark if the attribute is repeated.")

    def __str__(self):
        return ("{} ({})" if self.note else "{}").format(self.attribute, self.note)


class ReleaseCustomAttribute(AbstractAttribute):
    """ Inherits from AbstractAttribute: the attribute is custom to a single release """
    release     = models.ForeignKey(Release)
    note        = models.CharField(max_length=60, blank=True, null=True, help_text="Distinctive remark if the attribute is repeated.")

    @property
    def attribute(self):
        """ Allows a unified access, copied from ReleaseAttribute class """
        return self

    def __str__(self):
        return ("{} ({})" if self.note else "{}").format(super(ReleaseCustomAttribute, self).__str__(), self.note)


#############
## Occurrence
#############

class Occurrence(models.Model):
    release     = models.ForeignKey(Release)
    #owner       = models.ForeignKey(Person) #TODO
        ## Some automatic date fields
    add_date        = models.DateTimeField(auto_now_add=True)
    lastmodif_date  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return ("Occurrence: {}".format(self.release))


class OccurenceAnyAttributeBase(models.Model):
    class Meta:
        abstract = True

    occurrence          = models.ForeignKey(Occurrence)
     # The choices limitation is assigned dynamically, depending on the attribute's value type
    value               = models.CharField(max_length=enum.Attribute.Value.choices_maxlength())

    def __str__(self):
        # release_corresponding_entry should be added by all derived concrete models.
        return "{}: {}".format(self.release_corresponding_entry, self.value)

class OccurenceAttribute(OccurenceAnyAttributeBase):
    release_corresponding_entry = models.ForeignKey(ReleaseAttribute)

class OccurenceCustomAttribute(OccurenceAnyAttributeBase):
    release_corresponding_entry = models.ForeignKey(ReleaseCustomAttribute)
