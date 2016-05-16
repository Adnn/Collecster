from ._utils import print_validationerror

from supervisor.models import UserCollection, UserExtension, Deployment

from django.core.management.base import BaseCommand, CommandError
from django.core import exceptions
from django.db import transaction
from django.contrib.auth.models import Group


##
## This is a custom management command, creating a new supervisor.UserCollection for existing user and deployment.
##
class Command(BaseCommand):
    help = "Adds supervisor.UserCollection for the given user."

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('deployed_configuration')
        parser.add_argument('user_collection_id')

    def handle(self, *args, **options):
        try:
            userext = UserExtension.objects.get(user__username=options["username"])
        except UserExtension.DoesNotExist:
            raise CommandError("No UserExtension for username '{}' .".format(options["username"]))

        try:
            deployment = Deployment.objects.get(configuration=options["deployed_configuration"])
        except Deployment.DoesNotExist:
            raise CommandError("No Deployment for configuration '{}' .".format(options["deployed_configuration"]))

        GroupModel = Group
        target_group = "{}_users".format(options["deployed_configuration"])
        try:

            group = GroupModel.objects.get(name=target_group)
        except GroupModel.DoesNotExist:
            raise CommandError("No auth.Group with name '{}' .".format(target_group))


        user_collection = UserCollection(user=userext, user_collection_id=options["user_collection_id"],
                                         deployment=deployment)

        try:
            with transaction.atomic():
                user_collection.full_clean() 
                user_collection.save()

                user = userext.user
                user.groups.add(group)
                user.full_clean()
                user.save()

        except exceptions.ValidationError as e:
            print_validationerror(self, e)
