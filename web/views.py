from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from web.models import ForumThread, ParseProgress
from parser.utils import run_parser_in_background

def index(request):
    print("Rendering index page")
    return render(request, 'index.html')

def stats(request):
    print("Rendering stats page")
    threads = ForumThread.objects.all().order_by('-created_at')  # Сортировка по убыванию created_at
    total_messages = sum(thread.messages.count() for thread in threads)
    print(f"Found {threads.count()} threads, total messages: {total_messages}")
    return render(request, 'stats.html', {'threads': threads, 'total_messages': total_messages})

def trigger_parse(request):
    if request.method == 'POST':
        print("Triggering parse via POST request")
        max_pages = int(request.POST.get('max_pages', 1))
        run_parser_in_background(max_pages=max_pages)
        return redirect('progress')
    print("Invalid request method for trigger_parse")
    return HttpResponse(status=405)

def parse_progress(request):
    print("Rendering parse progress page")
    progress = ParseProgress.objects.first()
    return render(request, 'progress.html', {'progress': progress})

def thread_detail(request, thread_id):
    print(f"Rendering thread detail page for thread_id={thread_id}")
    thread = get_object_or_404(ForumThread, id=thread_id)
    messages = thread.messages.all().order_by('posted_at')
    return render(request, 'thread_detail.html', {'thread': thread, 'messages': messages})