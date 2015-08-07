# coding: utf-8

from django.contrib import admin

# Register your models here.
from workflow.models import Ftp, Outputter, PrintingPress, Phone, Grid


class PrintingPressAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name',),
        }),
        ('Размеры пластины', {
            'classes': ('wide',),
            'fields': (('plate_w', 'plate_h', 'klapan'),)
        })
    )
    list_display = ('name', 'plate_w', 'plate_h')


admin.site.register(Ftp)
admin.site.register(Outputter)
admin.site.register(PrintingPress, PrintingPressAdmin)
admin.site.register(Phone)
admin.site.register(Grid)