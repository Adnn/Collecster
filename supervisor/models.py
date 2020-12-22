from data_manager import fields

from django.db import models
from django.contrib.auth.models import User


#############
## Deployment
#############
class Deployment(models.Model):
    """
    Records which configurations are deployed on the current Django installation, in which version.

    .. note::
       We do not authorize several version of the same config for the moment.
    """
    configuration = models.CharField(max_length=20, unique=True)
    version = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)

    def __str__(self):
        return "{} v.{}".format(self.configuration, self.version)


class UserCollection(models.Model):
    """
    Used to assign a ``user_collection_id`` to the association of a :instance:`user` and a :instance:`deployment`.

    Thus allows to link from a user plus a user_collection_id (both kept stable accross any installation, thanks to user's guid),
    to a deployment on the local Django installation.

    .. note::
       This ``user_collection_id`` is chosen and managed by the user itself,
       and must be kept consistent accross all installations the user can access.
    """
    class Meta:
        unique_together = (("user", "user_collection_id"), ("user", "deployment"),)

    user = models.ForeignKey("UserExtension")
    user_collection_id = fields.id_field() #TODO ensure it cannot exceed 2 bytes, as it is encoded in the QR as unsigned short
    deployment = models.ForeignKey(Deployment)

    def __str__(self):
        return "{}(collection: {}) -> {}".format(self.user.person.nickname, self.user_collection_id, self.deployment)


##########
## User
##########
class Person(models.Model):
    """
    A class to identify a person, separate from the built-in User model.

    It is usefull for cases when a model needs a relation ship to a person that is not necessarily a user on the system
    (eg. a donator of an Occurrence)
    """
    first_name = models.CharField(max_length=20)
    last_name  = models.CharField(max_length=20)
    nickname   = models.CharField(max_length=20, unique=True) # Required, because it is printed on the tag

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


class UserExtension(models.Model):
    """
    Extends Django contrib's User model, to attach a globally unique user ID, which allows to unambiguously
    identify a user accross separate installations.

    .. note::
       ``guid`` should be assigned and managed by a central authority for Collecster, to globally avoid collisions.

    .. warning::
       A given ``guid`` should be active on a single Django installation at a time.
       This is because the ``user_occurrence_id``, recorded in ``TagToOccurrence``, are assigned locally,
       but the the pairs <``guid``-``user_occurrence_id``> should be globally unique to later allow merging.

    In the case the same person wants to be a user on several distinct installation at the same time,
    it has to use a different ``guid`` on each installation :

    * Since the same :instance:`person` can be assigned to different :instance:`UserExtension`,
      the same logic person can use a different user ``guid`` on each distinct Django installation running the same configuration,
      and will still be able to merge them later (having several :instance:`UserExtension` on the destination installation).
    * It would **not possible** to do it by keeping the same ``guid`` but using different ``user_collection_id`` on each installation:
      it would make merging impossible (the <``guid``-``deployment``> pair must be unique on a given installation).

    .. note::
       A conservative approach to simplify things is to always have a logic person only using a **single** installation
       (potentially migrating, but never having access to two at the same time).
    """

    user = models.OneToOneField(User, primary_key=True)
    guid = fields.id_field(unique=True)
    person = models.ForeignKey("Person") # Several users can correspond to the same person

    def __str__(self):
        return "{} (guid: {})".format(self.user, self.guid)
