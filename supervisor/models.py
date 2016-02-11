from data_manager import fields

from django.db import models
from django.contrib.auth.models import User


#############
## Deployment
#############
class Deployment(models.Model):
        
    # We do not authorize several version of the same config for the moment
    configuration = models.CharField(max_length=20, unique=True)
    version = models.PositiveSmallIntegerField(default=1)
    
    def __str__(self):
        return "{} v.{}".format(self.configuration, self.version)


class UserCollection(models.Model):
    class Meta:
        unique_together = (("user", "collection_local_id"), ("user", "deployment"),)
        

    user = models.ForeignKey("UserExtension")
    collection_local_id = fields.id_field() #TODO ensure it cannot exceede 4 bytes, as it is encoded in the QR
    deployment = models.ForeignKey(Deployment)

    def __str__(self):
        return "{}(collection: {}) -> {}".format(self.user.person.nickname, self.collection_local_id, self.deployment)


##########
## User
##########
class Person(models.Model):
        
    first_name = models.CharField(max_length=20)
    last_name  = models.CharField(max_length=20)
    nickname   = models.CharField(max_length=20, unique=True) # Required, because it is printed on the tag

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


class UserExtension(models.Model):
        
    """ Extends Django contrib's User model, to attach a globally unique ID """
    """ (to be managed by a central repo for Collecster """
    user = models.OneToOneField(User, primary_key=True)
    guid = fields.id_field(unique=True)
    person = models.OneToOneField("Person")
    
    def __str__(self):
        return "{} (guid: {})".format(self.user, self.guid)
