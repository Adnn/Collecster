from django.conf import settings

import os


def get_app_name():
    #return string(models.__dict__["__package__"])
    return globals()["__package__"]


def instance_media_dir(instance, prepend_media_root):
    """ prepend_media_root is a boolean value, indicating if the media root should prefix the returned value. """
    class_name = type(instance)._meta.verbose_name_plural.replace(" ", "_")
    from_media_root = os.path.join(get_app_name(), class_name, "{}".format(instance.pk))
    return os.path.join(settings.MEDIA_ROOT, from_media_root) if prepend_media_root else from_media_root


