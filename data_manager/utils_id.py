from data_manager import utils_payload

def get_concept_id(request, release=None, occurrence=None):
    # Even if the forwarded object is not None, it could not have its related field not populated:
    # Eg. On creation of the empty form for a Release, a default constructed Release instance is forwarded to formsets
    # see: https://github.com/django/django/blob/1.8.3/django/contrib/admin/options.py#L1480

    # See forms_admins.py _collecster_fixup_request()
    release = release if release else utils_payload.get_request_payload(request, "release")
    occurrence = occurrence if occurrence else utils_payload.get_request_payload(request, "occurrence")

    if release and hasattr(release, "concept"):
        return release.concept.pk
    elif occurrence and hasattr(occurrence, "release"):
        return occurrence.release.concept.pk
    else:
        concept_id = utils_payload.get_request_payload(request, "concept_id", 0)
        ## This is not possible anymore if we want to make this file not include the models
        #if not concept_id:
        #    release_id = utils_payload.get_request_payload(request, "release_id", 0)
        #    if release_id:
        #        concept_id = Release.objects.get(pk=release_id).concept.pk
        return concept_id


def get_release_id(request, occurrence=None):
    # Even if the forwarded object is not None, it could not have its related field not populated
    if occurrence is not None and hasattr(occurrence, "release"):
        return occurrence.release.pk
    else:
        return utils_payload.get_request_payload(request, "release_id", 0)



