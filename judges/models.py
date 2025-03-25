from django.db import models

class Judge(models.Model):
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    forum_account = models.CharField(max_length=100, verbose_name="Форумный аккаунт")
    discord_id = models.CharField(max_length=100, blank=True, verbose_name="ID Discord")
    telegram = models.CharField(max_length=100, blank=True, verbose_name="Telegram")
    email = models.EmailField(blank=True, verbose_name="Почта")
    additional_info = models.TextField(blank=True, verbose_name="Дополнительно")

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Судья"
        verbose_name_plural = "Судьи"

class EmploymentHistory(models.Model):
    judge = models.ForeignKey(Judge, related_name='employment_history', on_delete=models.CASCADE, verbose_name="Судья")
    hire_date = models.DateField(verbose_name="Дата приёма на работу")
    dismissal_date = models.DateField(null=True, blank=True, verbose_name="Дата увольнения")

    class Meta:
        verbose_name = "История приёма/увольнения"
        verbose_name_plural = "История приёмов/увольнений"