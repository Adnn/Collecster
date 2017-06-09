with open("data_manager/admin.py") as f:
        code = compile(f.read(), "data_manager/admin.py", 'exec')
        exec(code)

##
## Customization starts here
##

from .models import *

from django.contrib import admin

##
## Edit the data_manager admin
##
class ConceptAdmin(ConceptAdmin):
    inlines = () # Disable additional natures

base_register(admin.site)


##
## Admin for extra models
## 
admin.site.register(Artist)
admin.site.register(Label)
