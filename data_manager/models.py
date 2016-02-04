#from advg.configuration_advg import ConceptNature as ConfNature, is_material
from . import enumerations as enum

# TODO remove
#from videogame.configuration import ConceptNature as ConfNature#, is_material

#import shared
#from shared import ConfNature

from django.db import models
from django.core.exceptions import ValidationError

# TODEL
#import wdb

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

# TODO factorize with supervisor
def id_field(**kwargs):
    return models.IntegerField(**kwargs) # From the documentation, it is the type of primary keys
                                          # see: https://docs.djangoproject.com/en/1.8/ref/models/fields/#autofield



class TagToOccurrenceBase(models.Model):
    class Meta:
        abstract = True
        unique_together = ("user", "tag_occurrence_id") # Enforces USER::3)

    # This is a duplication of the Occurrence.owner. Perhaps remove it on Occurrence ?
    user              = models.ForeignKey("supervisor.UserExtension")
    tag_occurrence_id = id_field()
    occurrence = models.OneToOneField("Occurrence") # Enforces USER::2.b)

    def __str__(self):
        return "{}/{} -> {}".format(self.user.user, self.tag_occurrence_id, self.occurrence)


class AbstractRecordOwnership(models.Model):
    """ Abstract class adding the fields to make a model owned by a user """
    class Meta:
        abstract = True

    created_by  = models.ForeignKey("supervisor.UserExtension")


##########
## Concept
##########

#class ConceptNatureBase(models.Model):
#    class Meta:
#        abstract = True
#        unique_together = ("concept", "nature") # Enforce CONCEPT::1.a)
#
#    concept = models.ForeignKey("Concept", related_name="additional_nature_set")
#    nature  = models.CharField(max_length=ConfNature.choices_maxlength(), choices=ConfNature.get_choices())
#
#
#class ConceptBase(AbstractRecordOwnership):
#    class Meta:
#        abstract = True
#
#    distinctive_name    = models.CharField(max_length=180)  
#    common_name         = models.CharField(max_length= 60, blank=True)  
#    primary_nature      = models.CharField(max_length=ConfNature.choices_maxlength(), choices=ConfNature.get_choices())
#
#    def __str__(self):
#        return "{}{}".format(self.common_name if self.common_name else self.distinctive_name,
#                             " ({})".format(self.year) if self.year else "")
#
#    @property
#    def all_nature_tuple(self):
#        return (self.primary_nature,) \
#             + (self.additional_nature_set.all().values_list("nature")[0] if self.additional_nature_set.all() else ())
#    

############
## Attribute
############

class AttributeCategoryBase(models.Model):
    class Meta:
        abstract = True
        verbose_name_plural = "Attribute categories"

    name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.name


class AbstractAttribute(models.Model):
    """ Abstract class containing all the field for an attribute, to be used by Attribute an ReleaseCustomAttribute """
    class Meta:
        abstract = True

    category    = models.ForeignKey("AttributeCategory")
    name        = models.CharField(max_length=60)
    description = models.CharField(max_length=180, blank=True)
    value_type  = models.CharField(max_length=enum.Attribute.Type.choices_maxlength(),
                                   choices=enum.Attribute.Type.get_choices())

    def __str__(self):
        return "[{}]{}".format(self.category, self.name)


class AttributeBase(AbstractAttribute):
    class Meta:
        abstract = True
        unique_together = ("category", "name")


##########
## Release
##########

class ReleaseBase(AbstractRecordOwnership):
    class Meta:
        abstract = True
    
    concept = models.ForeignKey("Concept")
    name    = models.CharField(max_length=180, blank=True, verbose_name="Release's name")  

    partial_date = models.DateField("Date", blank=True, null=True)
    partial_date_precision = models.CharField("Date precision",
                                              choices=enum.PartialDate.get_choices(),
                                              max_length=enum.PartialDate.choices_maxlength(),
                                              default=enum.PartialDate.DAY,
                                              blank=True)

    distinctions = models.ManyToManyField("Distinction", through="ReleaseDistinction")

    # Not symmetrical: if a release B is nested in A, then A is NOT nested in B
    nested_releases = models.ManyToManyField("self", through="ReleaseComposition", symmetrical=False,
                                             through_fields = ("from_release", "to_release"))

    def display_name(self):
        return self.name if self.name else self.concept

    def name_color(self):
        """ Returns the color associated to this release, which is based on its nature """
        """ Nota that this color will be based on the primary nature only """
        return ConfNature.DATA[self.concept.primary_nature].tag_color;

    def __str__(self):
        return ("Rel #{}: {}{}".format(self.pk, "[immat] " if not is_material(self) else "", self.display_name()))

    def clean(self):
        super(ReleaseBase, self).clean()
        # Enforces IMMATERIAL::2.a)
        if not is_material(self):
            check_material_consistency(self)

        self._clean_partial_date()

    def _clean_partial_date(self):
        # Implements PARTIAL DATE::1)
        if not self.partial_date:
            self.partial_date_precision = ""
            return
        # Enforces PARTIAL DATE:2a)
        elif not self.partial_date_precision:
            raise ValidationError({"partial_date_precision": ValidationError("The precision must be specified.", code="invalid")})

        # Enforces PARTIAL DATE::2b)
        errors = {"partial_date": []} 
        if ((self.partial_date_precision == enum.PartialDate.YEAR or self.partial_date_precision == enum.PartialDate.MONTH)
            and self.partial_date.day != 1):
            print(self.partial_date.day)
            errors["partial_date"].append(ValidationError("Day should be set to '1' with precision %(precision)s.",
                                                     params={"precision":enum.PartialDate.DATA[self.partial_date_precision]},
                                                     code="inconsistent"))
        if (self.partial_date_precision == enum.PartialDate.YEAR
            and self.partial_date.day != 1):
            errors["partial_date"].append(ValidationError("Month should be set to '1' with precision %(precision)s.",
                                                     params={"precision":enum.PartialDate.DATA[self.partial_date_precision]},
                                                     code="inconsistent"))
        if errors["partial_date"]:
            raise ValidationError(errors)
        
        
class DistinctionBase(models.Model):
    class Meta:
        abstract = True
        
    name  = models.CharField(max_length=20, unique=True)
    note = models.CharField(max_length=64, blank=True, help_text="Optional details about the meaning of this distinction.")

    def __str__(self):
        return self.name

class ReleaseDistinctionBase(models.Model):
    class Meta:
        abstract = True
        
    release     = models.ForeignKey("Release")
    distinction = models.ForeignKey("Distinction")
    value       = models.CharField(max_length=30)


class ReleaseAttributeBase(models.Model):
    """ Maps an Attribute to a Release, with an optional note. """
    """ The note is manadatory if the same attribute is present multiple times on the same Release """

    class Meta:
        abstract = True
        unique_together = ("release", "attribute", "note") # Seems to be a bug: when ADDing the parent object, it is possible to save instances violating this constraint
                                                    # TODO: report to the Django project

    release     = models.ForeignKey("Release") # No release are attached for implicit attributes (that are determined by the Release nature), disabled
    attribute   = models.ForeignKey("Attribute")
    note       = models.CharField(max_length=60, blank=True, help_text="Distinctive remark if the attribute is repeated.")

    def __str__(self):
        return ("{} ({})" if self.note else "{}").format(self.attribute, self.note)


class ReleaseCustomAttributeBase(AbstractAttribute): # Inherits the fields of AbstractAttribute, direct composition
    """ Inherits from AbstractAttribute: the attribute is custom to a single release """
    """ Since it is not shared, there is no need for mapping to an external attribute: """
    """ this is the attribute itself, mapped to a Release. """

    class Meta:
        abstract = True
        unique_together = AbstractAttribute._meta.unique_together + ("release", "note") # Same bug than with ReleaseAttribute

    release     = models.ForeignKey("Release")
    note       = models.CharField(max_length=60, blank=True, null=True, help_text="Distinctive remark if the attribute is repeated.")

    @property
    def attribute(self):
        """ Allows a unified access, copied from ReleaseAttribute class """
        return self

    def __str__(self):
        return ("{} ({})" if self.note else "{}").format(super(ReleaseCustomAttribute, self).__str__(), self.note)


class ReleaseCompositionBase(models.Model):
    class Meta:
        abstract = True
        
    from_release    = models.ForeignKey("Release", related_name="+") # "+" disable the reverse relation: not needed here,
                                                                   # because we can access it through the 'nested_releases' field.
    """ The parent in the composition relation (i.e., the container). """

    to_release      = models.ForeignKey("Release") # Reverse relation implicitly named "release_composition_set"
    """ The container element. """

    def clean(self):
        # Enforces COMPOSITION::1)
        try:
            target = self.from_release
        except Release.DoesNotExist:
            return # If the from_release is not yet saved in the DB, no other path could lead to it
        self.check_circular_dependencies(target, self.to_release)

    def __str__(self):
        return "Nested {}".format(self.to_release)

    @staticmethod
    def check_circular_dependencies(target, to_release):
        if to_release == target:
            raise ValidationError("This composition would introduce a circular dependency.", code='invalid')
        for indirect_composition in ReleaseComposition.objects.filter(from_release=to_release):
            ReleaseComposition.check_circular_dependencies(target, indirect_composition.to_release)
        



#############
## Occurrence
#############

class OccurrenceBase(AbstractRecordOwnership):
    class Meta:
        abstract = True

    release     = models.ForeignKey("Release")
    owner       = models.ForeignKey("supervisor.Person")

        ## Some automatic date fields
    add_date        = models.DateTimeField(auto_now_add=True)
    lastmodif_date  = models.DateTimeField(auto_now=True)

    nested_occurrences  = models.ManyToManyField("self", through="OccurrenceComposition", symmetrical=False,
                                                 through_fields = ("from_occurrence", "to_occurrence"))

    def __str__(self):
        return ("Occurrence #{} of {}".format(self.pk, self.release))

    def clean(self):
        super(OccurrenceBase, self).clean()
        # Enforces IMMATERIAL::2.b)
        if hasattr(self, "release") and not is_material(self.release):
            check_material_consistency(self)


class OccurrenceAnyAttributeBase(models.Model):
    class Meta:
        abstract = True
        unique_together = ("occurrence", "release_corresponding_entry") # Enforces ATTRIBUTES::2.b)

    occurrence          = models.ForeignKey("Occurrence")
     # The choices limitation is assigned dynamically, depending on the attribute's value type
    value               = models.CharField(max_length=enum.Attribute.Value.choices_maxlength())

    def __str__(self):
        # release_corresponding_entry should be added by all derived concrete models.
        return "{}: {}".format(self.release_corresponding_entry, self.value)

    def clean(self):
        # Enforces ATTRIBUTES::2.c)
        try:
            if self.release_corresponding_entry.release != self.occurrence.release:
                raise ValidationError("The attribute assigned to the Occurrence is not an attribute of the corresponding Release.", code='invalid')
        except Occurrence.DoesNotExist:
            pass # I do not know how to access the data for the occurrence that is currently added
                 # see: http://stackoverflow.com/q/33854812/1027706

        # Enforces ATTRIBUTES::3)
        form_field = enum.Attribute.Type.to_form_field[self.release_corresponding_entry.attribute.value_type]
        if self.value not in [first for first, second in form_field.choices]:
            raise ValidationError("The assigned value is not allowed by the Attribute value type.", code='invalid')


class OccurrenceAttributeBase(OccurrenceAnyAttributeBase):
    class Meta:
        abstract = True
        
    release_corresponding_entry = models.ForeignKey("ReleaseAttribute")

class OccurrenceCustomAttributeBase(OccurrenceAnyAttributeBase):
    class Meta:
        abstract = True
        
    release_corresponding_entry = models.ForeignKey("ReleaseCustomAttribute")


class OccurrenceCompositionBase(models.Model):
    class Meta:
        abstract = True
        unique_together = ("release_composition", "from_occurrence") # Enforces COMPOSITION::2.b)

    release_composition = models.ForeignKey("ReleaseComposition")
    from_occurrence = models.ForeignKey("Occurrence", related_name="+") # "+" disable the reverse relation: not needed here,
                                                                      # because we can access it through the 'nested_occurrences' field.
     ## This one has to be optional: if a nested occurrence is absent, we store a blank to_occurrence:
     ## (We store empty composition to maintain the same order than the corresponding release compositions)
     ## Unique, because any occurrence can be nested in at most one parent occurrence.
    to_occurrence   = models.OneToOneField("Occurrence", blank=True, null=True, related_name="occurrence_composition")
    # Note: Because of the OneToMany relation here (One parent to many nested occurrences), it would have been possible
    # to directly put a ForeignKey to the parent in Occurence. But it would complicate the occurrence composition formset.

    def clean(self):
        try:
            if self.release_composition.from_release != self.from_occurrence.release:
                raise ValidationError("The release composition container-release does not match the container-occurrence corresponding release.", code='invalid')
        except Occurrence.DoesNotExist:
            pass # I do not know how to access the data for the occurrence that is currently added
                 # see: http://stackoverflow.com/q/33854812/1027706
        if (self.to_occurrence) and (self.release_composition.to_release != self.to_occurrence.release):
            raise ValidationError("The nested-occurrence corresponding release does not match the nested-release in the ReleaseComposition.", code='invalid')
