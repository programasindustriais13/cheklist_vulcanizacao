from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Machine, ChecklistSession, ChecklistTimelineLog, ChecklistItemValue

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('specialty', 'partner_user')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('specialty', 'partner_user')}),
    )
    list_display = ('username', 'email', 'specialty', 'partner_user', 'is_staff')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'partner_user' in form.base_fields:
            qs = User.objects.filter(specialty__in=['Eletricista', 'Mecânico', 'Eletromecânico'], is_active=True)
            if obj:
                qs = qs.exclude(id=obj.id)
            form.base_fields['partner_user'].queryset = qs
        return form

class MachineAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

class ChecklistSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'machine', 'inspector', 'co_inspector', 'leader', 'status', 'created_at')
    list_filter = ('status', 'machine', 'inspector', 'co_inspector')
    search_fields = ('leader__username', 'leader__first_name', 'leader__last_name')

class ChecklistTimelineLogAdmin(admin.ModelAdmin):
    list_display = ('session', 'user', 'action', 'pause_reason', 'timestamp')
    list_filter = ('action', 'user')

class ChecklistItemValueAdmin(admin.ModelAdmin):
    list_display = ('session', 'section', 'item_name', 'status')
    list_filter = ('section', 'status')
    search_fields = ('item_name',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Machine, MachineAdmin)
admin.site.register(ChecklistSession, ChecklistSessionAdmin)
admin.site.register(ChecklistTimelineLog, ChecklistTimelineLogAdmin)
admin.site.register(ChecklistItemValue, ChecklistItemValueAdmin)
