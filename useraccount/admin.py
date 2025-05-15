from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin, StackedInline
from unfold.forms import AdminPasswordChangeForm, UserCreationForm, UserChangeForm
#from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser, AdminUser, Agent, FleetManager, Driver, EmergencyContact, Address

admin.site.unregister(Group)

class AddressInline(StackedInline):
    model = Address
    can_delete = False
    verbose_name_plural = 'Address'
    ordering = ('-id',)


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    change_password_form = AdminPasswordChangeForm
    model = CustomUser
    list_display = ("email","first_name","last_name","is_staff","is_active",)
    list_filter = ("email","first_name","last_name","is_staff","is_active",)
    fieldsets = (
        (None, {"fields": ( "first_name", "last_name", "email", "password")}),
        ("Permissions", {"fields": ( "is_staff", "is_active", "groups", "user_permissions")}),)
    add_fieldsets = (
        (None, {"fields": ( "first_name", "last_name", "email", "password1", "password2", "is_staff", 
                           "is_active", "groups", "user_permissions")}),)
    search_fields = ["email"]
    ordering = ("email",)

    inlines = [AddressInline]


@admin.register(AdminUser)
class AdminUserAdmin(ModelAdmin):
    list_display = ('user', 'service_region')
    search_fields = ['user__email', 'department']


@admin.register(Agent)
class AgentAdmin(ModelAdmin):
    list_display = ('user', 'service_region')
    search_fields = ['user__email']
    list_filter = ['service_region']


@admin.register(FleetManager)
class FleetManagerAdmin(ModelAdmin):
    list_display = ('user', 'service_region')
    search_fields = ['user__email']
    list_filter = ['service_region']


@admin.register(Driver)
class DriverAdminClass(ModelAdmin):
    list_display = ('user', 'license_number')


@admin.register(EmergencyContact)
class EmergencyContactAdmin(ModelAdmin):
    list_display = ("user", "name", "phone_number", "relationship")
    search_fields = ["user__email", "name", "phone_number", "relationship"]


@admin.register(Address)
class AddressAdmin(ModelAdmin):
    list_display = ('user', 'city', 'state', 'country')
    search_fields = ['user__email', 'city', 'state', 'country']


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
