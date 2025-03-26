from celery import shared_task
from django.utils import timezone
from web.models import ParseProgress
from parser.parser import start_parse

@shared_task
def auto_parse_task():
    progress = ParseProgress.objects.first()
    if progress and progress.auto_parse_enabled and progress.status != 'running':
        start_parse(max_pages=progress.auto_parse_pages)
        progress.update_next_parse_time()