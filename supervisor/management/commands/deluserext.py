from ._utils import print_validationerror

from supervisor.models import UserCollection, UserExtension

from django.core.management.base import BaseCommand, CommandError
from django.core import exceptions
from django.db import transaction


##
## This is a custom management command, to delete Collecster users.
##
class Command(BaseCommand):
    help = "Deletes a user, removing its supervisor.UserCollection, and the associated supervisor.Person, supervisor.UserExtension and auth.User."

    def add_arguments(self, parser):
        parser.add_argument('username')

    def handle(self, *args, **options):
        try:
            userext = UserExtension.objects.get(user__username=options["username"])
        except UserExtension.DoesNotExist:
            raise CommandError("No UserExtension for username '{}' .".format(options["username"]))

        if userext.user.is_superuser:
            raise CommandError("User '{}' is a superuser, which cannot be deleted with this command.".format(options["username"]))

        try:
            with transaction.atomic():
                UserCollection.objects.filter(user=userext).delete()
                userext.user.delete() 
                userext.person.delete() 
                userext.delete()
        except exceptions.ValidationError as e:
            print_validationerror(self, e)
