from django.db import models
from django.utils import timezone

class ForumThread(models.Model):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=255)
    prefix = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(db_index=True)
    last_parsed_at = models.DateTimeField(null=True, blank=True)
    leading_judge = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ведущий судья")

    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
        ]

class ThreadMessage(models.Model):
    thread = models.ForeignKey(ForumThread, related_name='messages', on_delete=models.CASCADE)
    url = models.URLField(unique=True)
    author = models.CharField(max_length=255)
    content = models.TextField()
    posted_at = models.DateTimeField(db_index=True)

    def __str__(self):
        return f"{self.author}: {self.content[:50]}"

    class Meta:
        indexes = [
            models.Index(fields=['posted_at']),
        ]

class ParseProgress(models.Model):
    processed_threads = models.IntegerField(default=0)
    total_threads = models.IntegerField(default=0)
    progress = models.FloatField(default=0.0)
    status = models.CharField(max_length=50, default='not_started')
    auto_parse_enabled = models.BooleanField(default=False, verbose_name="Автоматический парсинг включен")
    auto_parse_interval = models.PositiveIntegerField(default=60, verbose_name="Интервал (минуты)")
    auto_parse_pages = models.PositiveIntegerField(default=1, verbose_name="Количество страниц")
    next_parse_time = models.DateTimeField(null=True, blank=True, verbose_name="Время следующего запуска")

    def __str__(self):
        return f"Progress: {self.progress}%"

    def update_next_parse_time(self):
        """Обновляет время следующего запуска."""
        if self.auto_parse_enabled:
            self.next_parse_time = timezone.now() + timezone.timedelta(minutes=self.auto_parse_interval)
            self.save()