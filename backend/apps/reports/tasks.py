import csv
import os
import uuid
from io import StringIO

from celery import shared_task
from django.apps import apps
from django.conf import settings
from django.utils import timezone


@shared_task
def generate_report_task(report_id):
    Report = apps.get_model('reports', 'Report')
    try:
        report = Report.objects.select_related('project', 'generated_by').get(id=report_id)
    except Report.DoesNotExist:
        return

    report_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
    os.makedirs(report_dir, exist_ok=True)

    output = StringIO()
    writer = csv.writer(output)

    if report.type == Report.ReportType.TASK_LIST:
        _generate_task_list(writer, report)
    elif report.type == Report.ReportType.BURNDOWN:
        _generate_burndown(writer, report)
    elif report.type == Report.ReportType.WORKLOG_SUMMARY:
        _generate_worklog_summary(writer, report)
    else:
        _generate_generic(writer, report)

    filename = f'{report.type}_{uuid.uuid4().hex[:8]}.csv'
    file_path = os.path.join(report_dir, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(output.getvalue())

    report.file_path = file_path
    report.save(update_fields=['file_path'])


def _generate_task_list(writer, report):
    Task = apps.get_model('tasks', 'Task')
    writer.writerow(['ID', 'Title', 'Status', 'Priority', 'Assignee', 'Start Date', 'Due Date'])

    params = report.parameters or {}
    tasks = Task.objects.none()
    if Task is not None:
        tasks = Task.objects.filter(project=report.project)
        start_date = params.get('start_date')
        end_date = params.get('end_date')
        if start_date:
            tasks = tasks.filter(created_at__gte=start_date)
        if end_date:
            tasks = tasks.filter(created_at__lte=end_date)

    for t in tasks:
        writer.writerow([
            str(t.id), getattr(t, 'title', ''), getattr(t, 'status', ''),
            getattr(t, 'priority', ''),
            getattr(t.assignee, 'username', '') if getattr(t, 'assignee', None) else '',
            getattr(t, 'start_date', '') or '',
            getattr(t, 'due_date', '') or '',
        ])


def _generate_worklog_summary(writer, report):
    WorkLog = apps.get_model('worklogs', 'WorkLog')
    writer.writerow(['Task ID', 'User', 'Hours', 'Date', 'Description'])

    logs = WorkLog.objects.none()
    if WorkLog is not None:
        logs = WorkLog.objects.filter(task__project=report.project).select_related('user', 'task')
        params = report.parameters or {}
        start_date = params.get('start_date')
        end_date = params.get('end_date')
        if start_date:
            logs = logs.filter(date__gte=start_date)
        if end_date:
            logs = logs.filter(date__lte=end_date)

    for wl in logs:
        writer.writerow([
            str(getattr(wl, 'task_id', '')),
            getattr(wl.user, 'username', '') if getattr(wl, 'user', None) else '',
            getattr(wl, 'hours', 0),
            getattr(wl, 'date', ''),
            getattr(wl, 'description', ''),
        ])


def _generate_burndown(writer, report):
    """Generate burndown data for a specific sprint."""
    params = report.parameters or {}
    sprint_id = params.get('sprint_id')

    Sprint = apps.get_model('sprints', 'Sprint')
    Task = apps.get_model('tasks', 'Task')
    writer.writerow(['Date', 'Ideal Remaining', 'Actual Remaining'])

    if Sprint is None or Task is None or not sprint_id:
        writer.writerow(['(no data)', '', ''])
        return

    try:
        sprint = Sprint.objects.get(id=sprint_id, project=report.project)
    except Sprint.DoesNotExist:
        writer.writerow(['(sprint not found)', '', ''])
        return

    from datetime import date, timedelta
    total_days = (sprint.end_date - sprint.start_date).days + 1
    total_tasks = Task.objects.filter(sprint=sprint).count()
    today = date.today()

    for i in range(total_days):
        d = sprint.start_date + timedelta(days=i)
        ideal_remaining = max(0, total_tasks - int(total_tasks * (i + 1) / total_days))

        if d <= today:
            completed = Task.objects.filter(
                sprint=sprint, status__in=['done', 'completed']
            ).count()
            actual_remaining = max(0, total_tasks - completed)
        else:
            actual_remaining = ideal_remaining

        writer.writerow([str(d), ideal_remaining, actual_remaining])


def _generate_generic(writer, report):
    writer.writerow(['Report Type', report.type])
    writer.writerow(['Project', report.project.name])
    writer.writerow(['Generated At', str(timezone.now())])
    writer.writerow([])
    writer.writerow(['(Detailed data will be available in a future version.)'])
