with open("data_manager/admin.py") as f:
        code = compile(f.read(), "data_manager/admin.py", 'exec')
        exec(code)

##
## Customization starts here
##

from django.contrib import admin

from .configuration import is_material
from .models import *

admin.site.register(Company)
admin.site.register(CompanyService)
