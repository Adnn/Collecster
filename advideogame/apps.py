from django.apps import AppConfig, apps
from django.core import checks, exceptions
from django.core.checks import register, Tags


def check_material_fields(app_configs, **kwargs):
    """ Custom system check, see: https://docs.djangoproject.com/en/1.9/topics/checks/ """
    errors = []
    if app_configs is None:
        models = apps.get_models()
    else:
        models = chain.from_iterable(app_config.get_models() for app_config in app_configs)
    for model in models:
        if hasattr(model, "collecster_material_fields"):
            for material_field in model.collecster_material_fields : 
                try:
                    field = model._meta.get_field(material_field)
                except exceptions.FieldDoesNotExist:
                    errors.append(checks.Error(
                                                  "'{}' is not a model field, it cannot appear in 'collecster_material_fields'.".format(material_field),
                                                  hint="Remove this entry from 'collecster_material_fields'.",
                                                  obj=model,
                                                  id='Collecster.E010',
                                 ))
                if field.many_to_many:
                    errors.append(checks.Error(
                                                  "Many-to-many field '{}' cannot appear in 'collecster_material_fields'.".format(field),
                                                  hint="Make a through model for the field, and have this model implement the check.",
                                                  obj=model,
                                                  id='Collecster.E010',
                                 ))
    return errors

class AdvideogameConfig(AppConfig):
    name = 'advideogame'

    def ready(self):
        super(AdvideogameConfig, self).ready() # Probably useless, as it is a hook
        #register(Tags.models)(check_material_fields)
