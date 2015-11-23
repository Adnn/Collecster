from .configuration import ConceptNature as ConfNature, ReleaseDeploymentBase, OccurrenceDeploymentBase, is_material
from . import enumerations as enum

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


##########
## Utils functions
##########
def check_material_consistency(model_instance):
    if hasattr(model_instance, "collecster_material_fields"):
        errors_dict = {}
        for field_name in model_instance.collecster_material_fields:
            if getattr(model_instance, field_name):
                errors_dict[field_name]=ValidationError("Not allowed on immaterial releases.", code='invalid')
        if errors_dict:
            raise ValidationError(errors_dict)

def id_field(**kwargs):
    return models.IntegerField(**kwargs) # From the documentation, it is the type of primary keys
                                          # see: https://docs.djangoproject.com/en/1.8/ref/models/fields/#autofield



##########
## User
##########

class UserExtension(models.Model):
    """ Extends Django contrib's User model, to attach a globally unique ID """
    """ (to be managed by a central repo for Collecster """
    user = models.OneToOneField(User, primary_key=True)
    guid = id_field(unique=True)
    
    def __str__(self):
        return "{} (guid: {})".format(self.user, self.guid)


class TagToOccurrence(models.Model):
    class Meta:
        unique_together = ("user", "tag_occurrence_id")

    user              = models.ForeignKey(UserExtension)
    tag_occurrence_id = id_field()
    occurrence = models.OneToOneField("Occurrence")

    def __str__(self):
        return "{}/{} -> {}".format(self.user.user, self.tag_occurrence_id, self.occurrence)


class AbstractUserOwned(models.Model):
    """ Abstract class adding the fields to make a model owned by a user """
    class Meta:
        abstract = True

    created_by  = models.ForeignKey("UserExtension")


##########
## Concept
##########

class ConceptNature(models.Model):
    concept = models.ForeignKey('Concept', related_name="additional_nature_set")
    nature  = models.CharField(max_length=ConfNature.choices_maxlength(), choices=ConfNature.get_choices())


class Concept(AbstractUserOwned):
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

class Release(ReleaseDeploymentBase, AbstractUserOwned):
    concept = models.ForeignKey(Concept)
    name    = models.CharField(max_length=180, blank=True, verbose_name="Release's name")  
    date    = models.DateField(blank=True, null=True)
    # Todo specificity (text, or list ?)
    # Todo edition ? What is that ?

    #  ## Not symmetrical: if a release B is nested in A, then A is NOT nested in B
    #nested_releases = models.ManyToManyField("self", symmetrical=False, blank=True)

    nested_releases = models.ManyToManyField("self", through="ReleaseComposition", symmetrical=False,
                                             through_fields = ("from_release", "to_release"))

    def __str__(self):
        return ("Rel #{}: {}{}".format(self.pk, "[immat] " if not is_material(self) else "", self.name if self.name else self.concept))

    def clean(self):
        super(Release, self).clean()
        if self.immaterial:
            check_material_consistency(self)


class ReleaseAttribute(models.Model):
    """ Maps an Attribute to a Release, with an optional note. """
    """ The note is manadatory if the same attribute is present multiple times on the same Release """

    class Meta:
        unique_together = ("release", "attribute", "note") # Seems to be a bug: when ADDing the parent object, it is possible to save instances violating this constraint
                                                    # TODO: report to the Django project

    release     = models.ForeignKey(Release) # No release are attached for implicit attributes (that are determined by the Release nature), disabled
    attribute   = models.ForeignKey(Attribute)
    note        = models.CharField(max_length=60, blank=True, help_text="Distinctive remark if the attribute is repeated.")

    def __str__(self):
        return ("{} ({})" if self.note else "{}").format(self.attribute, self.note)


class ReleaseCustomAttribute(AbstractAttribute):
    """ Inherits from AbstractAttribute: the attribute is custom to a single release """
    """ Since it is not shared, there is no need for mapping to an external attribute: """
    """ this is the attribute itself, mapped to a Release. """

    class Meta:
        unique_together = AbstractAttribute._meta.unique_together + ("release", "note") # Same bug than with ReleaseAttribute

    release     = models.ForeignKey(Release)
    note        = models.CharField(max_length=60, blank=True, null=True, help_text="Distinctive remark if the attribute is repeated.")

    @property
    def attribute(self):
        """ Allows a unified access, copied from ReleaseAttribute class """
        return self

    def __str__(self):
        return ("{} ({})" if self.note else "{}").format(super(ReleaseCustomAttribute, self).__str__(), self.note)


class ReleaseComposition(models.Model):
    from_release    = models.ForeignKey(Release, related_name="+") # "+" disable the reverse relation: not needed here,
                                                                   # because we can access it through the 'nested_releases' field.
    """ The parent in the composition relation (i.e., the container). """

    to_release      = models.ForeignKey(Release) # Reverse relation implicitly named "release_composition_set"
    """ The container element. """

    def __str__(self):
        return "Nested {}".format(self.to_release)



#############
## Occurrence
#############

class Occurrence(OccurrenceDeploymentBase, AbstractUserOwned):
    release     = models.ForeignKey(Release)
    #owner       = models.ForeignKey(Person) #TODO
        ## Some automatic date fields
    add_date        = models.DateTimeField(auto_now_add=True)
    lastmodif_date  = models.DateTimeField(auto_now=True)
    nested_occurrences  = models.ManyToManyField("self", through="OccurrenceComposition", symmetrical=False,
                                                 through_fields = ("from_occurrence", "to_occurrence"))

    def __str__(self):
        return ("Occurrence #{} of {}".format(self.pk, self.release))

    def clean(self):
        super(Occurrence, self).clean()
        if hasattr(self, "release") and self.release.immaterial:
            check_material_consistency(self)


class OccurrenceAnyAttributeBase(models.Model):
    class Meta:
        abstract = True

    occurrence          = models.ForeignKey(Occurrence)
     # The choices limitation is assigned dynamically, depending on the attribute's value type
    value               = models.CharField(max_length=enum.Attribute.Value.choices_maxlength())

    def __str__(self):
        # release_corresponding_entry should be added by all derived concrete models.
        return "{}: {}".format(self.release_corresponding_entry, self.value)

class OccurrenceAttribute(OccurrenceAnyAttributeBase):
    release_corresponding_entry = models.ForeignKey(ReleaseAttribute)

class OccurrenceCustomAttribute(OccurrenceAnyAttributeBase):
    release_corresponding_entry = models.ForeignKey(ReleaseCustomAttribute)


class OccurrenceComposition(models.Model):
    release_composition = models.ForeignKey(ReleaseComposition)
    from_occurrence = models.ForeignKey(Occurrence, related_name="+") # "+" disable the reverse relation: not needed here,
                                                                      # because we can access it through the 'nested_occurrences' field.
     ## This one has to be optional: if a nested occurrence is absent, we store a blank to_occurrence:
     ## (We store empty composition to maintain the same order than the corresponding release compositions)
     ## Unique, because any occurrence can be nested in at most one parent occurrence.
    to_occurrence   = models.OneToOneField(Occurrence, blank=True, null=True, related_name="occurrence_composition")
    # Note: Because of the OneToMany relation here (One parent to many nested occurrences), it would have been possible
    # to directly put a ForeignKey to the parent in Occurence. But it would complicate the occurrence composition formset.
