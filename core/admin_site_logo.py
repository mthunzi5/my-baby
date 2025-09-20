from django.contrib import admin
from .models_site_logo import SiteLogo

@admin.register(SiteLogo)
class SiteLogoAdmin(admin.ModelAdmin):
    list_display = ("id", "uploaded_at", "logo")
    readonly_fields = ("uploaded_at",)
    actions = ["clear_logo_action"]

    def clear_logo_action(self, request, queryset):
        for obj in queryset:
            obj.logo.delete(save=True)
        self.message_user(request, "Selected logo(s) cleared.")
    clear_logo_action.short_description = "Clear selected logo(s)"
