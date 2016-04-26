# coding: utf-8

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from workflow.models import Ftp, Ctpbureau, PrintingPress, Employee, Grid


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


class EmployeeInline(admin.TabularInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'Доп. инфо'


class UserAdmin(BaseUserAdmin):
    inlines = (EmployeeInline, )


admin.site.register(Ftp, FtpAdmin)
admin.site.register(Ctpbureau, OutputterAdmin)
admin.site.register(PrintingPress, PrintingPressAdmin)
admin.site.register(Grid, GridAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
