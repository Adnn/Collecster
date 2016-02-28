import advideogame

from . import utils_path

from supervisor.models import * # for generate_qr_code 

from django.template import loader

import pyqrcode

import os, struct


def generate_qrcode(occurrence, tag_to_occurrence):
    reserved = 0 #For later use
    #user_guid   = UserExtension.objects.get(person=occurrence.owner).guid
    user_guid = tag_to_occurrence.user_creator.guid
    deployment = Deployment.objects.get(configuration=advideogame.utils_path.get_app_name())
    user_collection_id = UserCollection.objects.get(user__guid=user_guid, deployment=deployment).user_collection_id 
    #TODO Handle the object type when other types will be allowed
    objecttype_id = 1 # There is a single object type at the moment: the occurrence
    user_occurrence_id = tag_to_occurrence.user_occurrence_id 
    data = struct.pack("<BHBII", reserved, user_collection_id, objecttype_id, user_guid, user_occurrence_id)

    return pyqrcode.create(data, version=1, error="M", mode="binary")


def generate_tag(occurrence):
    tag_version = 2
    qr_filename = "qr_v{}.png".format(tag_version)

    tag_to_occurrence = advideogame.models.TagToOccurrence.objects.get(occurrence=occurrence)
    
    working = advideogame.models.OccurrenceSpecific.OperationalOcc.objects.get(occurrence=occurrence.pk).working_condition

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
    directory = os.path.join(utils_path.instance_media_dir(Occurrence, occurrence, True), "tags")
    if not os.path.exists(directory):
        os.makedirs(directory)

    QR_MODULE_SIZE=8*4
    qr = generate_qrcode(occurrence, tag_to_occurrence)
    qr.png(os.path.join(directory, qr_filename), scale=QR_MODULE_SIZE, quiet_zone=2)

    with open(os.path.join(directory, "v{}.html".format(tag_version)), "w") as f: #TODO some date and time ?
        f.write(template.render(context))

    return "/{}".format(os.path.join(directory, template_file))
