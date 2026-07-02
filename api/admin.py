from django.contrib import admin

from .models import ApplicationHistory


@admin.register(ApplicationHistory)
class ApplicationHistoryAdmin(admin.ModelAdmin):
    list_display = ("recipient_email", "role", "status", "sent_at")
    list_filter = ("status", "role")
    search_fields = ("recipient_email",)
