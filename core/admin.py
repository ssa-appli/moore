from django.contrib import admin
from .models import AcceptationAudit, Sharehol, Branche, Manager

# Register your models here.
admin.site.register(AcceptationAudit)
admin.site.register(Sharehol)
admin.site.register(Branche)
admin.site.register(Manager)