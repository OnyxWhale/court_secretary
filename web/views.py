from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Count
from web.models import ForumThread, ParseProgress
from parser.parser import start_parse
from court_secretary.celery import app as celery_app  # Импортируем приложение Celery
from django_celery_beat.models import PeriodicTask, IntervalSchedule

def index(request):
    print("Rendering index page")
    return render(request, 'web/index.html')

def stats(request):
    print("Rendering stats page")
    threads = ForumThread.objects.annotate(message_count=Count('messages')).order_by('-created_at')
    total_messages = sum(t.message_count for t in threads)
    print(f"Found {threads.count()} threads, total messages: {total_messages}")
    return render(request, 'web/stats.html', {'threads': threads, 'total_messages': total_messages})

def trigger_parse(request):
    progress = ParseProgress.objects.first()
    if not progress:
        progress = ParseProgress.objects.create()

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'start_parse':
            max_pages = int(request.POST.get('max_pages', 1))
            start_parse(max_pages=max_pages)
            progress.update_next_parse_time()
            return redirect('web:trigger_parse')
        
        elif action == 'update_auto_parse':
            auto_enabled = request.POST.get('auto_parse_enabled') == 'on'
            interval = int(request.POST.get('auto_parse_interval', 60))
            pages = int(request.POST.get('auto_parse_pages', 1))
            progress.auto_parse_enabled = auto_enabled
            progress.auto_parse_interval = interval
            progress.auto_parse_pages = pages
            if auto_enabled:
                # Обновляем задачу в Celery Beat
                schedule, _ = IntervalSchedule.objects.get_or_create(every=interval, period=IntervalSchedule.MINUTES)
                task, _ = PeriodicTask.objects.get_or_create(name='auto-parse', defaults={'task': 'web.tasks.auto_parse_task'})
                task.interval = schedule
                task.enabled = True
                task.save()
                progress.update_next_parse_time()
            else:
                # Отключаем задачу
                PeriodicTask.objects.filter(name='auto-parse').update(enabled=False)
                progress.next_parse_time = None
            progress.save()
            return redirect('web:trigger_parse')
        
        elif action == 'stop_auto_parse':
            progress.auto_parse_enabled = False
            progress.status = 'stopped'
            progress.next_parse_time = None
            PeriodicTask.objects.filter(name='auto-parse').update(enabled=False)
            # Если нужно отозвать запущенные задачи (опционально)
            # task_id = PeriodicTask.objects.filter(name='auto-parse').first().task
            # if task_id:
            #     celery_app.control.revoke(task_id, terminate=True)
            progress.save()
            return redirect('web:trigger_parse')

    return render(request, 'web/parse.html', {'progress': progress})

def thread_detail(request, thread_id):
    print(f"Rendering thread detail page for thread_id={thread_id}")
    thread = get_object_or_404(ForumThread, id=thread_id)
    messages = thread.messages.all().order_by('posted_at')
    return render(request, 'web/thread_detail.html', {'thread': thread, 'messages': messages})