from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Count
from web.models import ForumThread, ParseProgress
from parser.parser import start_parse  # Изменяем импорт на parser.parser

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
    if request.method == 'POST':
        print("Triggering parse via POST request")
        max_pages = int(request.POST.get('max_pages', 1))
        start_parse(max_pages=max_pages)  # Используем start_parse из parser/parser.py
        return redirect('web:trigger_parse')
    print("Rendering parse page")
    return render(request, 'web/parse.html', {})

def thread_detail(request, thread_id):
    print(f"Rendering thread detail page for thread_id={thread_id}")
    thread = get_object_or_404(ForumThread, id=thread_id)
    messages = thread.messages.all().order_by('posted_at')
    return render(request, 'web/thread_detail.html', {'thread': thread, 'messages': messages})