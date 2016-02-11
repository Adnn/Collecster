from django.db import models

def id_field(**kwargs):
    return models.IntegerField(**kwargs) # From the documentation, it is the type of primary keys
                                          # see: https://docs.djangoproject.com/en/1.8/ref/models/fields/#autofield



