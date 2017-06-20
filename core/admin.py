from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from core.models import Employee
from core.models import Customer
#from workflow.models import Employee

admin.site.site_header = 'TES: Управление данными'

class EmployeeInline(admin.TabularInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'Доп. инфо'


class UserAdmin(BaseUserAdmin):
    inlines = (EmployeeInline, )


class EmployeeAdmin(admin.ModelAdmin):
    model = Employee
    list_display = ('get_username', 'user', 'phone', 'sms_notify','telegram_id', 'telegram_notify')

    def get_username(self, obj):
        return ' '.join([obj.user.first_name, obj.user.last_name])
    get_username.short_description = 'ФИО'

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'fio', 'phone', 'remarks')

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Customer, CustomerAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)