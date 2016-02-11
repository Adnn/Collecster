from data_manager import fields

from django.db import models
from django.contrib.auth.models import User


#############
## Deployment
#############
class Deployment(models.Model):
    """ Deployment allows to keep track of which configurations are deployed on the Django installation """
    """ and in which version. """
    # We do not authorize several version of the same config for the moment
    configuration = models.CharField(max_length=20, unique=True)
    version = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    
    def __str__(self):
        return "{} v.{}".format(self.configuration, self.version)


class UserCollection(models.Model):
    """ Makes the link from a user plus a user collection id, to a deployment on the local Django installation """
    class Meta:
        unique_together = (("user", "user_collection_id"), ("user", "deployment"),)

    user = models.ForeignKey("UserExtension")
    user_collection_id = fields.id_field() #TODO ensure it cannot exceede 4 bytes, as it is encoded in the QR
    deployment = models.ForeignKey(Deployment)

    def __str__(self):
        return "{}(collection: {}) -> {}".format(self.user.person.nickname, self.user_collection_id, self.deployment)


##########
## User
##########
class Person(models.Model):
    """ A class to identify a person, separate from the built-in User model. """
    """ It is usefull for cases when a model needs a relation ship to a person that is not necessarily a user on the system """ 
    """ (eg. a donator of an Occurrence) """
    first_name = models.CharField(max_length=20)
    last_name  = models.CharField(max_length=20)
    nickname   = models.CharField(max_length=20, unique=True) # Required, because it is printed on the tag

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


class UserExtension(models.Model):
    """ Extends Django contrib's User model, to attach a globally unique ID """
    """ (to be managed by a central repo for Collecster) """
    user = models.OneToOneField(User, primary_key=True)
    guid = fields.id_field(unique=True)
    person = models.OneToOneField("Person")
    
    def __str__(self):
        return "{} (guid: {})".format(self.user, self.guid)
