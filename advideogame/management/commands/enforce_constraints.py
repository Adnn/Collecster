from django.core.management.base import BaseCommand, CommandError

from .constraints_enforcer import enforce_main

##
## This is a wrapper around constraints_enforcer.py
##
class Command(BaseCommand):
    help = "Checks that the data stored with advideogame is consistent with the constraints."

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        enforce_main(self)

    def warn(self, message):
        self.stdout.write("[Warning] {}".format(message))

    def error(self, message):
        self.stderr.write("[Error] {}".format(message))
