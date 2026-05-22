from django.contrib import admin
from .models import KanbanBoard, KanbanColumn, TaskColumn

@admin.register(KanbanBoard)
class KanbanBoardAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'type', 'created_at']

@admin.register(KanbanColumn)
class KanbanColumnAdmin(admin.ModelAdmin):
    list_display = ['name', 'board', 'order', 'wip_limit']

@admin.register(TaskColumn)
class TaskColumnAdmin(admin.ModelAdmin):
    list_display = ['task_id', 'column', 'order']
