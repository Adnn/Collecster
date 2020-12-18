from advideogame.models import Occurrence
from advideogame import tag

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from distutils.dir_util import copy_tree
from functools import partial
import os


def regenerate(occurrence, occurence_id):
    if occurrence.is_taggable():
        occurrence.tag_file = tag.generate_tag(occurrence)
        occurrence.save()


def copy(occurrence, occurrence_id, destination):
    tagfolder = os.path.join(destination, str(occurrence_id))
    copy_tree(
        os.path.dirname(os.path.join(settings.MEDIA_ROOT, occurrence.tag_file.name)),
        tagfolder)


OpMap = {
    "copy": copy,
    #"render": render,
}


class Command(BaseCommand):
    help = "Different commands to manipulated tags of specified Occurrence instances."


    def foreach_occurrence(self, first_id, last_id, operation):
        for occurrence_id in range(first_id, last_id+1):
            try:
                try:
                    occurrence = Occurrence.objects.get(id=occurrence_id)
                except ObjectDoesNotExist:
                    pass # It is okay that some ids are "not assigned"
                operation(occurrence, occurrence_id)
            except Exception as e:
                self.stdout.write("Exception below for occurrence id: {}".format(occurrence_id))
                raise e


    def add_arguments(self, parser):
        parser.add_argument("command", choices=["copy", "regenerate"],
                            help="The operation, to regenerate tags or copy them to separate folders")
        parser.add_argument("occurrence_id", type=int,
                            help="first occurrence to operate, the only one if --until is not specified")
        parser.add_argument("--until", type=int,
                            help="apply command on the interval from occurrence_id until this optional id inclusive")
        parser.add_argument("--destination",
                            help="destination folder for copy command")

    def handle(self, *args, **options):
        """ Command entry point """
        command = options["command"]
        first_id = options["occurrence_id"]
        last_id = options["until"] if options["until"] else first_id

        self.stdout.write("{} tag for occurrences ({}..{})".format(command, first_id, last_id))

        if command == "regenerate":
            if options["destination"]:
                raise CommandError("--destination is not available for regenerate")
            self.foreach_occurrence(first_id, last_id, regenerate)
        elif command in ("copy",): #Expandable
            if not options["destination"] or not os.path.exists(options["destination"]):
                raise CommandError("--destination is required, and pointing to an existing folder")
            self.foreach_occurrence(first_id, last_id,
                                    partial(OpMap[command], destination=options["destination"]))
        else:
            raise CommandError("Unhandled command '{}'".format(command))
