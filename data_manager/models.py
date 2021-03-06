from .configuration import ConfigNature

from data_manager import enumerations as enum
from data_manager import fields

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# TODEL
#import wdb


##########
## Utils functions
##########

## Nota: this function would implement the material consistency checks at the DB model level.
## Sadly, there is a limitation for ManyToMany fields, which are throwing a ValueError when trying to retrieve them
## on an instance not yet saved in the DB, making those fields not enforcable at the DB model level.
## Instead, this check is now run at the form level (eg. see PropertyAwareModelForm).
def check_material_consistency(model_instance, is_material):
    errors_dict = check_property_consistency_impl(model_instance, is_material, "material", getattr, required=model_instance.required_on_material)
    errors_dict.update( check_property_consistency_impl(model_instance, not is_material, "non_material", getattr, forbidden=model_instance.forbidden_on_non_material) )
    if errors_dict:
        raise ValidationError(errors_dict)

def check_property_consistency(model_instance, property_value, property_name, data_getter, forbidden=(), required=()):
    errors_dict = {}

    if property_value and forbidden:
        for field_name in forbidden:
            field = model_instance._meta.get_field(field_name)
            #if data_getter(model_instance, field_name) not in field.empty_values:
            ## Nota: With boolean fields, we want "False" to be allowed on material fields of immaterial instances,
            ## but "False" is not an empty value.
            if data_getter(model_instance, field_name):
                errors_dict[field_name] = ValidationError("This field is not allowed on %(property)s releases.",
                                                          params = {"property": property_name}, code="invalid")

    if property_value and required:
        # see: https://github.com/django/django/blob/1.9/django/db/models/base.py#L1147-L1158
        for field_name in required:
            field = model_instance._meta.get_field(field_name)
            if data_getter(model_instance, field_name) in field.empty_values:
                errors_dict[field_name] = ValidationError("This field is required on %(property)s releases.",
                                                          params = {"property": property_name}, code="invalid")

    return errors_dict

class CollecsterPropertiesHelper(object):
    @staticmethod
    def _split_property(property_name):
        """
        Splits the property name found on the collecster_properties dictionary,
        between the sign (False if "non_" prefix, True otherwise) and the positive property name
        """
        splits = property_name.split("_", maxsplit=1)
        if (len(splits) == 2) and (splits[0] =="non"):
            return False, splits[1]
        else:
            return True, "_".join(splits)

    @staticmethod
    def is_property_known(base_instance, property_name):
        """ Checks whether the base model defines a "{property}_is_known" member, and calls it if available. """
        sign_DISCARDED, positive_property = CollecsterPropertiesHelper._split_property(property_name)
        availability_check = "{}_is_known".format(positive_property)
        if hasattr(base_instance, availability_check):
            return getattr(base_instance, availability_check)()
        else:
            return True

    @staticmethod
    def get_property_value(base_instance, property_name):
        sign, positive_property = CollecsterPropertiesHelper._split_property(property_name)
        return sign == getattr(base_instance, "is_{}".format(positive_property))()

    @classmethod
    def validate(cls, instance, base_instance, data_getter):
        errors = {}
        if hasattr(instance, "collecster_properties"):
            for key, fields in instance.collecster_properties.items():
                instruction, DISCARDED, property_name = key.split("_", maxsplit=2)
                if CollecsterPropertiesHelper.is_property_known(base_instance, property_name):
                    errors.update(check_property_consistency(instance,
                                                             cls.get_property_value(base_instance, property_name),
                                                             property_name, data_getter,
                                                             **{instruction: fields}))
        return errors


class TagToOccurrenceBase(models.Model):
    """
    This model makes the link between user occurrence IDs
    (which are identifiers -immutable accross installations- assigned to each occurrence. Only unique per user)
    And the actual application Occurrences kept in the database.
    """
    class Meta:
        abstract = True
        unique_together = ("user_creator", "user_occurrence_id") # Enforces TAGTOOCCURRENCE::2)

    # This is *NOT* the Occurrence.owner. It is the user that created the occurrence instance.
    # It is thus the same value as Occurrence.created_by.
    user_creator       = models.ForeignKey("supervisor.UserExtension", related_name="%(app_label)s_%(class)s_set")
    user_occurrence_id = fields.id_field()
    occurrence = models.OneToOneField("Occurrence") # Enforces TAGTOOCCURRENCE::1.b)

    def __str__(self):
        return "{}/{} -> {}".format(self.user_creator.user, self.user_occurrence_id, self.occurrence)


class AbstractRecordOwnership(models.Model):
    """ Abstract class adding the fields to make the inheriting model instances owned by a user """
    class Meta:
        abstract = True

    created_by  = models.ForeignKey("supervisor.UserExtension", related_name="%(app_label)s_%(class)s_created_set")


##########
## Concept
##########

class ConceptNatureBase(models.Model):
    class Meta:
        abstract = True
        unique_together = ("concept", "nature") # Enforce CONCEPT::1.a)

    concept = models.ForeignKey("Concept", related_name="additional_nature_set")
    nature  = models.CharField(max_length=ConfigNature.choices_maxlength(), choices=ConfigNature.get_choices())


class ConceptBase(AbstractRecordOwnership):
    class Meta:
        abstract = True

    distinctive_name    = models.CharField(max_length=180)
    common_name         = models.CharField(max_length= 60, blank=True)
    primary_nature      = models.CharField(max_length=ConfigNature.choices_maxlength(), choices=ConfigNature.get_choices())

    def __str__(self):
        return "{}{}".format(self.common_name if self.common_name else self.distinctive_name,
                             " ({})".format(self.year) if self.year else "")

    @property
    def all_nature_tuple(self):
        return ((self.primary_nature,) if self.primary_nature else ()) \
             + tuple([value_dict["nature"] for value_dict in self.additional_nature_set.all().values()])


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
        ordering = ("category", "name")


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


    def is_material(self):
        """
        The notion of immaterial needs to be a core concept, because some core behaviour depends on it
        eg. define application logic that an immterial cannot have nested elements
        Yet not to force having an immaterial field (for cases were there are no immaterials),
        it is abstracted through this function which implements a sensible default, but can be overriden.
        """
        if hasattr(self, "immaterial"):
            return not self.immaterial
        else:
            return True


    def display_name(self):
        return self.name if self.name else str(self.concept)

    def name_color(self):
        """
        Returns the color associated to this release, which is based on its nature
        Nota that this color will be based on the primary nature only
        """
        return ConfigNature.DATA[self.concept.primary_nature].tag_color;

    def __str__(self):
        return ("Rel #{}: {}{}".format(self.pk, "[immat] " if not self.is_material() else "", self.display_name()))

    ## Currently useless, as it is not taken into account by the form validation
    #def full_clean(self, exclude=None, validate_unique=True):
    #    """ Makes required fields not-required (excluded from validation) when the instance is immaterial and the field """
    #    """ appears in collecster_material_fields. Sadly is not working with forms, because the field is also cleaned at the form level """
    #    """ which does not take the exclusions into considerations. """
    #    """ (see: forms._cleand_fields(), https://github.com/django/django/blob/1.9/django/forms/forms.py#L366) """
    #    """ Had to introduce the 'collecster_required_on_material' model attribute, so the model fields are not marked as required """
    #    """ But Collecster can still enforce that the fields must be present on material instances (check_material_consistency_generic) """
    #    if not self.is_material() and hasattr(self, "collecster_material_fields"):
    #        exclude = exclude + list(self.collecster_material_fields)
    #    super(ReleaseBase, self).full_clean(exclude, validate_unique)

    def clean(self):
        super(ReleaseBase, self).clean()
        self._clean_partial_date()
        ## Enforces IMMATERIAL::2.a), now enforced at the form level
        #check_material_consistency(self, self.is_material())


    def _clean_partial_date(self):
        # Enforces PARTIAL_DATE::1)
        if not self.partial_date:
            self.partial_date_precision = ""
            return
        # Enforces PARTIAL_DATE:2a)
        elif not self.partial_date_precision:
            raise ValidationError({"partial_date_precision": ValidationError("The precision must be specified.", code="invalid")})

        # Enforces PARTIAL_DATE::2b)
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
    """
    Maps an Attribute to a Release, with an optional note.
    The note is manadatory if the same attribute is present multiple times on the same Release
    """

    class Meta:
        abstract = True
        unique_together = ("release", "attribute", "note") # Seems to be a bug: when ADDing the parent object, it is possible to save instances violating this constraint
                                                    # TODO: report to the Django project

    release     = models.ForeignKey("Release", related_name="attributes") # No release are attached for implicit attributes (that are determined by the Release nature), disabled
    attribute   = models.ForeignKey("Attribute")
    note       = models.CharField(max_length=60, blank=True, help_text="Distinctive remark if the attribute is repeated.")

    def __str__(self):
        return ("{} ({})" if self.note else "{}").format(self.attribute, self.note)


class ReleaseCustomAttributeBase(AbstractAttribute): # Inherits the fields of AbstractAttribute, direct composition
    """
    Inherits from AbstractAttribute: the attribute is custom to a single release
    Since it is not shared, there is no need for mapping to an external attribute:
    this is the attribute itself, mapped to a Release.
    """

    class Meta:
        abstract = True
        # Note that AttributeBase is not the parent, but it defines the right unique_together clause that we need to extend
        unique_together = AttributeBase.Meta.unique_together + ("release", "note") # Same bug than with ReleaseAttribute

    release     = models.ForeignKey("Release", related_name="custom_attributes")
    note       = models.CharField(max_length=60, blank=True, null=True, help_text="Distinctive remark if the attribute is repeated.")

    @property
    def attribute(self):
        """ Allows a unified access, copied from ReleaseAttribute class """
        return self

    def __str__(self):
        return ("{} ({})" if self.note else "{}").format(super(ReleaseCustomAttributeBase, self).__str__(), self.note)


class ReleaseCompositionBase(models.Model):
    class Meta:
        abstract = True

    from_release    = models.ForeignKey("Release", related_name="+") # "+" disable the reverse relation: not needed here,
                                                                   # because we can access it through the 'nested_releases' field.
    """ The parent in the composition relation (i.e., the container). """

    to_release      = models.ForeignKey("Release") # Reverse relation implicitly named "releasecomposition"
    """ The contained element. """

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
    owner       = models.ForeignKey("supervisor.Person", related_name="%(app_label)s_%(class)s_owned_set")

        ## Some automatic date fields
    add_date        = models.DateTimeField(auto_now_add=True)
    lastmodif_date  = models.DateTimeField(auto_now=True)

    nested_occurrences  = models.ManyToManyField("self", through="OccurrenceComposition", symmetrical=False,
                                                 through_fields = ("from_occurrence", "to_occurrence"))

    def __str__(self):
        return ("Occurrence #{} of {}".format(self.pk, self.release))

    def material_is_known(self):
        return hasattr(self, "release")

    def is_material(self):
        return self.release.is_material()

    @property
    def concept(self):
        return self.release.concept

    #def clean(self):
    #    super(OccurrenceBase, self).clean()
    #    # Enforces IMMATERIAL::2.b), now enforced at the form level
    #    if hasattr(self, "release"):
    #        check_material_consistency(self, self.release.is_material())


class AbstractReleaseAttributeRelatedBase(models.Model):
    class Meta:
        abstract = True

    @property
    def release_corresponding_entry(self):
        #return self.attribute_object # Actually works, but returns None when the value are not set, which makes it
                                      # differ from other "relation fields", that raise DoesNotExist exceptions.
        try:
            return self.attribute_type.get_object_for_this_type(pk=self.attribute_id)
        except ContentType.DoesNotExist:
            # the exact type of the "corresponding entry" is not know, as it could be any release attribute model
            # so we raise a generic AttributeError
            raise AttributeError()


class AbstractReleaseAttributeRelated(AbstractReleaseAttributeRelatedBase):
    class Meta:
        abstract = True
    # The 3 following fields implement a "generic relation"
    #(see: https://docs.djangoproject.com/en/1.9/ref/contrib/contenttypes/#generic-relations)
    attribute_type  = models.ForeignKey(ContentType, related_name="+")
    attribute_id    = models.PositiveIntegerField()
    attribute_object = GenericForeignKey("attribute_type", "attribute_id")


class AbstractReleaseAttributeRelatedOptional(AbstractReleaseAttributeRelatedBase):
    class Meta:
        abstract = True
    attribute_type  = models.ForeignKey(ContentType, null=True)
    attribute_id    = models.PositiveIntegerField(null=True)
    attribute_object = GenericForeignKey("attribute_type", "attribute_id")


class OccurrenceAnyAttributeBase(AbstractReleaseAttributeRelated):
    class Meta:
        abstract = True
        unique_together = ("occurrence", "attribute_type", "attribute_id") # Enforces ATTRIBUTES::2.b)

    occurrence          = models.ForeignKey("Occurrence", related_name="attributes")
     # The choices limitation is assigned dynamically, depending on the attribute's value type
    value               = models.CharField(max_length=enum.Attribute.Value.choices_maxlength())

    def __str__(self):
        return "{}: {}".format(self.release_corresponding_entry, self.value)

    @staticmethod
    def is_clean_value(value, release_corresponding_entry):
        form_field = enum.Attribute.Type.to_form_field[release_corresponding_entry.attribute.value_type]
        return value in [first for first, second in form_field.choices]

    def clean(self):
        # Enforces ATTRIBUTES::2.c)
        try:
            if self.release_corresponding_entry.release != self.occurrence.release:
                raise ValidationError("The attribute assigned to the Occurrence is not an attribute of the corresponding Release.", code='invalid')
        except Occurrence.DoesNotExist:
            pass # I do not know how to access the data for the occurrence that is currently added
                 # see: http://stackoverflow.com/q/33854812/1027706

        # Enforces ATTRIBUTES::3)
        if not self.is_clean_value(self.value, self.release_corresponding_entry):
            raise ValidationError("The assigned value is not allowed by the Attribute value type.", code='invalid')


class OccurrenceCompositionBase(models.Model):
    class Meta:
        abstract = True
        unique_together = ("release_composition", "from_occurrence") # Enforces COMPOSITION::2.b)

    release_composition = models.ForeignKey("ReleaseComposition")
    from_occurrence = models.ForeignKey("Occurrence", related_name="+") # "+" disable the reverse relation: not needed here,
                                                                      # because we can access it through the 'nested_occurrences' field.
     ## This one has to be optional: if a nested occurrence is absent, we store a blank to_occurrence:
     ## (We store empty composition to maintain the same order than the corresponding release compositions)
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

    def __str__(self):
        return "{}. Matched to {}".format(self.release_composition, self.to_occurrence)
