from django.contrib import admin
from .models import NudgeTemplate, Nudge


@admin.register(NudgeTemplate)
class NudgeTemplateAdmin(admin.ModelAdmin):
    list_display = ('message', 'category')
    list_filter = ('category',)
    search_fields = ('message',)


@admin.register(Nudge)
class NudgeAdmin(admin.ModelAdmin):
    list_display = ('pod', 'sender', 'recipient', 'template', 'date', 'is_read', 'sent_at')
    list_filter = ('is_read', 'date', 'pod')
    search_fields = ('sender__username', 'recipient__username', 'template__message')
