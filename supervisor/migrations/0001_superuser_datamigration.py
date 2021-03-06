import os
from django.db import migrations


class Migration(migrations.Migration):

    # Could be empty, this does not actually depend on any migration in this application
    # But that will avoid this migratin being considered initial
    # see: https://docs.djangoproject.com/en/2.2/topics/migrations/#initial-migrations
    dependencies = [
        # Will ensure the required "auth" migrations are run
        ('supervisor', '0001_initial'),
    ] 

    def generate_superuser(apps, schema_editor):
        from django.contrib.auth.models import User

        DJANGO_SU_NAME = os.environ.get('DJANGO_SU_NAME')
        DJANGO_SU_EMAIL = os.environ.get('DJANGO_SU_EMAIL')
        DJANGO_SU_PASSWORD = os.environ.get('DJANGO_SU_PASSWORD')

        superuser = User.objects.create_superuser(
            username=DJANGO_SU_NAME,
            email=DJANGO_SU_EMAIL,
            password=DJANGO_SU_PASSWORD)

        superuser.save()

    operations = [
        migrations.RunPython(generate_superuser),
    ]
