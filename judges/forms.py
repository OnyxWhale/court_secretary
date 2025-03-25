from django import forms
from .models import Judge, EmploymentHistory

class JudgeForm(forms.ModelForm):
    class Meta:
        model = Judge
        fields = ['full_name', 'forum_account', 'discord_id', 'telegram', 'email', 'additional_info']
        labels = {
            'full_name': 'ФИО',
            'forum_account': 'Форумный аккаунт',
            'discord_id': 'ID Discord',
            'telegram': 'Telegram',
            'email': 'Почта',
            'additional_info': 'Дополнительно',
        }
        widgets = {
            'additional_info': forms.Textarea(attrs={'rows': 3}),
        }

class EmploymentHistoryForm(forms.ModelForm):
    hire_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'custom-date-input',  # Класс для стилизации
            'min': '2024-08-01',  # Ограничение с августа 2024
        }),
        label="Дата приёма на работу",
        input_formats=['%Y-%m-%d'],
    )
    dismissal_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'custom-date-input',  # Класс для стилизации
            'min': '2024-08-01',  # Ограничение с августа 2024
        }),
        label="Дата увольнения",
        required=False,
        input_formats=['%Y-%m-%d'],
    )

    class Meta:
        model = EmploymentHistory
        fields = ['hire_date', 'dismissal_date']