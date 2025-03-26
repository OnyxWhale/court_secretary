from django.db import models

class ForumThread(models.Model):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=255)
    prefix = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(db_index=True)  # Индекс для фильтрации
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
    posted_at = models.DateTimeField(db_index=True)  # Индекс для сортировки

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

    def __str__(self):
        return f"Progress: {self.progress}%"