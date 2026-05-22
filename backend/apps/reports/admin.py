from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'project', 'generated_by', 'created_at']
    list_filter = ['type']
