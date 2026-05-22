from django.contrib import admin
from .models import Task, TaskDependency, Comment, Mention

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status', 'priority', 'assignee', 'due_date']
    list_filter = ['status', 'priority', 'type']
    search_fields = ['title']

@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    list_display = ['predecessor', 'successor', 'relation_type']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'content', 'created_at']

@admin.register(Mention)
class MentionAdmin(admin.ModelAdmin):
    list_display = ['mentioned_user', 'comment', 'is_read']
