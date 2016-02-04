from django.contrib import admin

from .models import *

admin.site.register(UserExtension)
admin.site.register(Person)
admin.site.register(Deployment)
admin.site.register(UserCollection)

# Register your models here.
