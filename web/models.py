from django.db import models
from django.utils import timezone

class ForumThread(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField(unique=True)
    prefix = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    last_parsed_at = models.DateTimeField(null=True, blank=True)
    leading_judge = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ведущий судья")

class ThreadMessage(models.Model):
    thread = models.ForeignKey(ForumThread, related_name='messages', on_delete=models.CASCADE)
    url = models.URLField(unique=True)
    author = models.CharField(max_length=100)
    content = models.TextField()
    posted_at = models.DateTimeField(default=timezone.now)

class ParseProgress(models.Model):
    status = models.CharField(max_length=50, default='idle')
    progress = models.FloatField(default=0.0)
    total_threads = models.IntegerField(default=0)
    processed_threads = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)