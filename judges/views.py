from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.contrib import messages
from .models import Judge, EmploymentHistory
from .forms import JudgeForm, EmploymentHistoryForm
from .utils import update_leading_judge_for_threads

def judges_list(request):
    judges = Judge.objects.all().prefetch_related('employment_history')
    return render(request, 'judges/judges_list.html', {'judges': judges})

def judge_manage(request, judge_id=None):
    judge = get_object_or_404(Judge, id=judge_id) if judge_id else None
    EmploymentHistoryFormSet = modelformset_factory(EmploymentHistory, form=EmploymentHistoryForm, extra=1, can_delete=True)

    if request.method == 'POST':
        form = JudgeForm(request.POST, instance=judge)
        formset = EmploymentHistoryFormSet(request.POST, queryset=EmploymentHistory.objects.filter(judge=judge) if judge else EmploymentHistory.objects.none())

        if form.is_valid() and formset.is_valid():
            judge = form.save()
            
            # Проверяем, нажата ли кнопка "Удалить выбранные"
            if request.POST.get('delete_selected') == 'true':
                deleted = False
                for f in formset:
                    if f.cleaned_data.get('DELETE', False) and f.instance.pk:
                        f.instance.delete()
                        deleted = True
                if deleted:
                    messages.success(request, "Выбранные записи успешно удалены.")
                else:
                    messages.warning(request, "Выберите хотя бы одну запись для удаления.")
                update_leading_judge_for_threads()
                return redirect('judge_edit', judge_id=judge.id)  # Заменили judge_manage на judge_edit
            
            # Обычное сохранение (кнопка "Сохранить")
            for f in formset:
                if f.cleaned_data and not f.cleaned_data.get('DELETE', False):
                    history = f.save(commit=False)
                    history.judge = judge
                    history.save()
            for f in formset.deleted_forms:
                if f.instance.pk:
                    f.instance.delete()
            update_leading_judge_for_threads()
            messages.success(request, "Изменения успешно сохранены.")
            return redirect('judges_list')
    else:
        form = JudgeForm(instance=judge)
        formset = EmploymentHistoryFormSet(queryset=EmploymentHistory.objects.filter(judge=judge) if judge else EmploymentHistory.objects.none())

    return render(request, 'judges/judge_manage.html', {'form': form, 'formset': formset, 'judge': judge})

def judge_delete(request, judge_id):
    judge = get_object_or_404(Judge, id=judge_id)
    if request.method == 'POST':
        judge.delete()
        update_leading_judge_for_threads()
        return redirect('judges_list')
    return render(request, 'judges/judge_confirm_delete.html', {'judge': judge})

def employment_history_delete(request, pk):
    history = get_object_or_404(EmploymentHistory, pk=pk)
    if request.method == "POST":
        history.delete()
        next_url = request.POST.get('next', reverse('judge_edit', args=[history.judge.id]))  # Заменили judge_manage на judge_edit
        return redirect(next_url)
    return redirect('judges_list')