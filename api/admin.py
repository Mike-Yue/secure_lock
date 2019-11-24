from django.contrib import admin
from api.models import Lock, Code, LockUser

# Register your models here.

admin.site.register(Lock)
admin.site.register(Code)
admin.site.register(LockUser)