from django.db import models
from django.core.validators import RegexValidator

class Judge(models.Model):
    """Модель судьи."""
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    forum_account = models.CharField(max_length=100, verbose_name="Форумный аккаунт")
    discord_id = models.CharField(
        max_length=18, blank=True, verbose_name="ID Discord",
        validators=[RegexValidator(r'^\d{17,18}$', 'Неверный формат ID Discord')]
    )
    telegram = models.CharField(max_length=100, blank=True, verbose_name="Telegram")
    email = models.EmailField(blank=True, verbose_name="Почта")
    additional_info = models.TextField(blank=True, verbose_name="Дополнительно")

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Судья"
        verbose_name_plural = "Судьи"
        indexes = [
            models.Index(fields=['forum_account']),
        ]

class EmploymentHistory(models.Model):
    """Модель истории приёма/увольнения."""
    judge = models.ForeignKey(Judge, related_name='employment_history', on_delete=models.CASCADE, verbose_name="Судья")
    hire_date = models.DateField(verbose_name="Дата приёма на работу", db_index=True)
    dismissal_date = models.DateField(null=True, blank=True, verbose_name="Дата увольнения", db_index=True)

    class Meta:
        verbose_name = "История приёма/увольнения"
        verbose_name_plural = "История приёмов/увольнений"
        indexes = [
            models.Index(fields=['hire_date', 'dismissal_date']),
        ]