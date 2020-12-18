from django.db import models


class Attribute(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name

    
class UniqueAttribute(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class Release(models.Model):
    name = models.CharField(max_length=60)
    attributes = models.ManyToManyField(Attribute, through='ReleaseAttribute')
    unique_attributes = models.ManyToManyField(UniqueAttribute, blank=True) # To show how m2m fields are shown in the admin when there is no "through"

    def __str__(self):
        return self.name


class ReleaseAttribute(models.Model):
    release = models.ForeignKey(Release)
    attribute = models.ForeignKey(Attribute)
    note = models.CharField(max_length=120, blank=True, null=True)

    def __str__(self):
        return ("{}.{} ({})" if self.note else "{}.{}").format(self.release, self.attribute, self.note)


class Instance(models.Model):
    release = models.ForeignKey(Release)
    name    = models.CharField(max_length=60)
    release_attributes  = models.ManyToManyField(ReleaseAttribute, through='InstanceAttribute')

    def __str__(self):
        return self.name


class InstanceAttribute(models.Model):
    VALUES = (
        ("A", "A"),
        ("B", "B"),
    )

    instance = models.ForeignKey(Instance)
    release_attribute = models.ForeignKey(ReleaseAttribute)
    value = models.CharField(max_length=1, choices = VALUES)

    def __str__(self):
        return "{}: {}".format(self.release_attribute, self.value)

