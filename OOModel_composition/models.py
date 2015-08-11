from django.db import models


#class ObjectDescription(models.Model):
#    common_note = models.CharField(max_length=60, blank=True, null=True)
#
#    def __str__(self):
#        return "Object: " + self.common_note
#
#
#class SubObject(ObjectDescription):
#    description = models.CharField(max_length=60)
#
#    def __str__(self):
#        return "Object: " + self.description


    ##
    ## Note: The ObjectDescription approach was having SubObject and Release both inherits from the concrete ObjectDescription
    ##  It was decided it was too complicated to introduce polymorphism on this central model for the rare cases when it will be needed.
    ##  Just make a special hardcoded edge case "_subobject" to be set as the Release of an Instance that is logically a SubObject.
    ##
class Release(models.Model):
    name = models.CharField(max_length=60)
    #composition = models.ManyToManyField(ObjectDescription, through='ReleaseComposition', related_name='ObjectDescription_composition')
    composition = models.ManyToManyField('self', through='ReleaseComposition', symmetrical=False)

    def __str__(self):
        return self.name


class ReleaseComposition(models.Model):
    container_release = models.ForeignKey(Release, related_name='container_of_set')
    nested_object = models.ForeignKey(Release, related_name='element_of_set')


class Instance(models.Model):
    release = models.ForeignKey(Release)
    name    = models.CharField(max_length=60)
    #release_attributes  = models.ManyToManyField(ReleaseAttribute, through='InstanceAttribute')

    def __str__(self):
        return self.name


class InstanceComposition(models.Model):
    container = models.ForeignKey(Instance, related_name="container_of_set")
    nested_instance = models.OneToOneField(Instance, related_name="element_of")
