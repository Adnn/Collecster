from ._utils import print_validationerror

import supervisor

from django.core.management.base import BaseCommand, CommandError
from django.core import exceptions
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.text import capfirst
from django.db import transaction

import getpass, sys

##
## This is a custom management command, creating a new auth User, plus a supervisor.UserExtension and supervisor.Person
## the code is derived from createsuperuser command.
##  see: https://github.com/django/django/blob/1.9/django/contrib/auth/management/commands/createsuperuser.py
##
class Command(BaseCommand):
    help = "Adds a auth.User, associating it to a supervisor.UserExtension and supervisor.Person."

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.UserModel = get_user_model()

    def add_arguments(self, parser):
        parser.add_argument('username')

    def execute(self, *args, **options):
        self.stdin = options.get('stdin', sys.stdin)  # Used for testing
        return super(Command, self).execute(*args, **options)

    def handle(self, *args, **options):
        if hasattr(self.stdin, 'isatty') and not self.stdin.isatty():
            raise CommandError("'adduserext' must be run in a TTY.")

        if self.UserModel.objects.filter(username=options["username"]).exists():
            raise CommandError("Username '{}' already exists.".format(options["username"]))

        try:
            person = self.interactive_create_object(supervisor.models.Person)
            user_ext = self.interactive_create_object(supervisor.models.UserExtension)

            user = self.UserModel(username=options["username"], is_staff=True)
            user.set_password(self.get_password(user))

            # The order in which we have to save the models and assign the related fields is quite strict
            # see: http://stackoverflow.com/a/13249363/1027706
            try:
                with transaction.atomic():
                    user.full_clean()
                    person.full_clean()
                    user.save()
                    person.save()

                    user_ext.person = person
                    user_ext.user = user
                    user_ext.full_clean()
                    user_ext.save()

            except exceptions.ValidationError as e:
                print_validationerror(self, e)

        except KeyboardInterrupt:
            self.stderr.write("\nOperation cancelled.")
            sys.exit(1)


    def interactive_create_object(self, model_class):
        model_data = {}
        for field in [f for f in model_class._meta.get_fields() if not (f.auto_created or f.is_relation)]:
            while model_data.get(field.name) is None:
                model_data[field.name] = self.get_input_data(field, "{}: ".format(capfirst(field.verbose_name)))

        return model_class(**model_data)

                
    def get_password(self, user=None):
        password = None
        while password is None:
            password = getpass.getpass()
            password2 = getpass.getpass("Password (again): ")
            if password != password2:
                self.stderr.write("Error: Your passwords didn't match.")
                password = None
                # Don't validate passwords that don't match.
                continue

            if password.strip() == '':
                self.stderr.write("Error: Blank passwords aren't allowed.")
                password = None
                # Don't validate blank passwords.
                continue

            try:
                validate_password(password2, user)
            except exceptions.ValidationError as err:
                self.stderr.write('\n'.join(err.messages))
                password = None
        return password


    def get_input_data(self, field, message, default=None):
        """
        Override this method if you want to customize data inputs or
        validation exceptions.
        """
        raw_value = input(message)
        if default and raw_value == '':
            raw_value = default
        try:
            val = field.clean(raw_value, None)
        except exceptions.ValidationError as e:
            self.stderr.write("Error: %s" % '; '.join(e.messages))
            val = None

        return val
