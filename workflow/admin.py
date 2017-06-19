# coding: utf-8

from django.contrib import admin
from workflow.models import Ftp, Ctpbureau, PrintingPress, Grid

class GridAdmin(admin.ModelAdmin):
    list_display = ('order', 'datetime', 'pdfname', 'machine', 'total_pages', 'total_plates', 'contractor')

    def has_add_permission(self, request):
        return False


class OutputterAdmin(admin.ModelAdmin):
    list_display = ('name', 'ftp_account')


class FtpAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip', 'port', 'login', 'passw', 'todir', 'passive_mode')


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





admin.site.register(Ftp, FtpAdmin)
admin.site.register(Ctpbureau, OutputterAdmin)
admin.site.register(PrintingPress, PrintingPressAdmin)
admin.site.register(Grid, GridAdmin)

