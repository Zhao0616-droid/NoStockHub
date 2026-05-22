from django.contrib import admin
from .models import WorkLog, HourlyRate

@admin.register(WorkLog)
class WorkLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'date', 'hours', 'description']

@admin.register(HourlyRate)
class HourlyRateAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'rate', 'effective_from']
