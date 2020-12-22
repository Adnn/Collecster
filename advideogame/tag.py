import advideogame

from . import utils_path

from supervisor.models import * # for generate_qr_code

from django.conf import settings
from django.template import loader

import pyqrcode

import os, struct


def generate_qrcode(occurrence, tag_to_occurrence, tag_version):
    magic_number = 86 # Identifies a Collecster tag
    application_id = 3 # Id for ADVG, lets reserve a few values just in case
    #user_guid   = UserExtension.objects.get(person=occurrence.owner).guid
    # The globally unique id (i.e. cross installations) for the user who created the occurrence
    user_guid = tag_to_occurrence.user_creator.guid
    deployment = Deployment.objects.get(configuration=advideogame.utils_path.get_app_name())
    # The collection_id that the user chose for this collection (which is also cross installations)
    user_collection_id = UserCollection.objects.get(user__guid=user_guid, deployment=deployment).user_collection_id
    #TODO Handle the object type when other types will be allowed
    objecttype_id = 1 # There is a single object type at the moment: the occurrence
    user_occurrence_id = tag_to_occurrence.user_occurrence_id

    # Magicnumber, tag version, application id, user_collection_id, objecttype_id, user_guid, user_occurrence_id
    # 1 + 1 + 1 + 2 + 1 + 2 + 4 = 12 bytes
    # Note: application_id is redundant with user_collection_id, since the user collection identifies a specific application
    #   Since we have up to 14 bytes, lets keep the application id for the moment, allowing some consistency checks
    #   Future versions of the tag will be able to remove it if the room is needed
    data = struct.pack("<BBBHBHI", magic_number, tag_version, application_id, user_collection_id, objecttype_id, user_guid, user_occurrence_id)

    # This method will call date.decode(encoding). Default encoding being utf-8, it fails with some bytes
    # Uses latin_1, which should not alter the byte sequence.
    # QR code version 1 error M offer 14 bytes of user data, see: https://www.qrcode.com/en/about/version.html
    return pyqrcode.create(data, version=1, error="M", mode="binary", encoding="latin_1")


def generate_tag(occurrence):
    tag_version = 2
    qr_filename = "qr_v{}.svg".format(tag_version)

    tag_to_occurrence = advideogame.models.TagToOccurrence.objects.get(occurrence=occurrence)

    # Some Concept Natures do not have associate an OperationanOcc with the OccurrenceCategory (see Configuration.py)
    try:
        working = advideogame.models.OccurrenceSpecific.OperationalOcc.objects.get(occurrence=occurrence.pk).working_condition
    except advideogame.models.OccurrenceSpecific.OperationalOcc.DoesNotExist:
        working = None

    template_file = "v2.html"
    template = loader.get_template("tag/{}".format(template_file))
    context = {
        "release": occurrence.release,
        "tag": {"version": tag_version, "file": qr_filename},
        "collection": {"shortname": "VG", "objecttype": "OCC"},
        "occurrence": occurrence,
        "working": working,
    }

    # Here, uses the occurrence PK in the DB, not the tag_occurrence id, because we see this part of the filesystem
    # like a direct extension of the DB.
    # As a consequence, a potential migration of a collection would impose to rename those folders to map to the DB.
    directory = os.path.join(utils_path.instance_media_dir(occurrence, True), "tags")
    if not os.path.exists(directory):
        os.makedirs(directory)

    # The QR code is 25 "dots" on each dimension (21 data plus 2 in each quiet zone)
    # There is a 838px tall zone to fit it. floor(838/25) = 33, resulting size 33*25 = 825px
    QR_MODULE_SIZE=33
    qr = generate_qrcode(occurrence, tag_to_occurrence, tag_version)
    qr.svg(os.path.join(directory, qr_filename), scale=QR_MODULE_SIZE, quiet_zone=2)

    tag_filename = os.path.join(directory, "v{}.html".format(tag_version))
    with open(tag_filename, "w", encoding="utf-8") as f: #TODO some date and time ?
        f.write(template.render(context))

    # Prune the media root, if any, from the returned filename.
    result = tag_filename[len(settings.MEDIA_ROOT)+1:] if settings.MEDIA_ROOT else tag_filename # +1 for the '/'
    return result
