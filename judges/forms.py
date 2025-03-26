from django import forms
from .models import Judge, EmploymentHistory
from court_secretary.utils.date_utils import validate_date_range, get_min_date

class JudgeForm(forms.ModelForm):
    """Форма для управления судьями."""
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
    """Форма для истории приёма/увольнения."""
    hire_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'custom-date-input',
            'min': get_min_date(),
        }),
        label="Дата приёма на работу",
        input_formats=['%Y-%m-%d'],
    )
    dismissal_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'custom-date-input',
            'min': get_min_date(),
        }),
        label="Дата увольнения",
        required=False,
        input_formats=['%Y-%m-%d'],
    )

    class Meta:
        model = EmploymentHistory
        fields = ['hire_date', 'dismissal_date']

    def clean(self):
        """Валидация дат."""
        cleaned_data = super().clean()
        hire_date = cleaned_data.get('hire_date')
        dismissal_date = cleaned_data.get('dismissal_date')
        validate_date_range(hire_date, dismissal_date)
        return cleaned_data