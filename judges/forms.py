from django import forms
from django.utils import timezone
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
            'class': 'custom-date-input',
            'min': timezone.now().strftime('%Y-%m-%d'),  # Динамическая минимальная дата
        }),
        label="Дата приёма на работу",
        input_formats=['%Y-%m-%d'],
    )
    dismissal_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'custom-date-input',
            'min': timezone.now().strftime('%Y-%m-%d'),  # Динамическая минимальная дата
        }),
        label="Дата увольнения",
        required=False,
        input_formats=['%Y-%m-%d'],
    )

    class Meta:
        model = EmploymentHistory
        fields = ['hire_date', 'dismissal_date']

    def clean(self):
        cleaned_data = super().clean()
        hire_date = cleaned_data.get('hire_date')
        dismissal_date = cleaned_data.get('dismissal_date')
        if dismissal_date and hire_date and dismissal_date < hire_date:
            raise forms.ValidationError("Дата увольнения не может быть раньше даты приема.")
        return cleaned_data