from django.contrib import admin

# Register your models here.
from workflow.models import Ftp, Outputter, PrintingPress, Phone, Grid

admin.site.register(Ftp)
admin.site.register(Outputter)
admin.site.register(PrintingPress)
admin.site.register(Phone)
admin.site.register(Grid)