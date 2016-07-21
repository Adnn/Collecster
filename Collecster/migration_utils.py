from django.core.management import call_command
import django

from functools import partial
import os

##
## Those utilities are used to load initial data from fixtures through a migrations
## see: http://stackoverflow.com/a/25981899/1027706
## see: https://docs.djangoproject.com/en/1.9/topics/migrations/#data-migrations
## see: https://github.com/alexhayes/django-migration-fixture/blob/0.5.1/django_migration_fixture/__init__.py#L73-L93
##
class app_patcher(object):
    def __init__(self, apps):
        self.original_serializer_apps = django.core.serializers.python.apps
        self.context_apps = apps
        
    def __enter__(self):
        django.core.serializers.python.apps = self.context_apps
        return self

    def __exit__(self, type, value, traceback):
        django.core.serializers.python.apps = self.original_serializer_apps


def list_initial_fixtures(app_name):
    fixture_dir = "{}/fixtures".format(app_name)
    return [base for base, ext
                 in [os.path.splitext(fixture) for fixture in os.listdir(fixture_dir)
                                               if os.path.isfile(os.path.join(fixture_dir, fixture))]
                 if ext==".json" and base.startswith("initial_")]
    
        
def _load_initial_fixtures_impl(app_name, apps, schema_editor):
    with app_patcher(apps):
        call_command('loaddata', *list_initial_fixtures(app_name), app_label=app_name) 

def load_initial_fixtures_func(app_name):
    """ 
    The public interface to those utilities 
    This method should be invoked inside a migration "operations" list, with a syntax: 
        migrations.RunPython(load_initial_fixtures_func("app_name_here")) 
    """
    return partial(_load_initial_fixtures_impl, app_name)
