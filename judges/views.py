from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from django.core.paginator import Paginator
from django.urls import reverse  # Добавляем импорт reverse
from .models import Judge, EmploymentHistory
from .forms import JudgeForm, EmploymentHistoryForm
from .utils import update_leading_judge_for_threads

def judges_list(request):
    query = request.GET.get('q', '')
    judges = Judge.objects.filter(
        Q(full_name__icontains=query) | Q(forum_account__icontains=query)
    ).prefetch_related('employment_history')
    paginator = Paginator(judges, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'judges/judges_list.html', {'page_obj': page_obj, 'query': query})

def judge_add(request):
    EmploymentHistoryFormSet = modelformset_factory(EmploymentHistory, form=EmploymentHistoryForm, extra=1, can_delete=True)
    if request.method == 'POST':
        form = JudgeForm(request.POST)
        formset = EmploymentHistoryFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            judge = form.save()
            for f in formset:
                if f.cleaned_data and not f.cleaned_data.get('DELETE', False):
                    history = f.save(commit=False)
                    history.judge = judge
                    history.save()
            update_leading_judge_for_threads()
            messages.success(request, "Судья успешно добавлен.")
            return redirect('judges:judges_list')
    else:
        form = JudgeForm()
        formset = EmploymentHistoryFormSet(queryset=EmploymentHistory.objects.none())
    return render(request, 'judges/judge_manage.html', {'form': form, 'formset': formset, 'judge': None})

def judge_edit(request, judge_id):
    judge = get_object_or_404(Judge, id=judge_id)
    EmploymentHistoryFormSet = modelformset_factory(EmploymentHistory, form=EmploymentHistoryForm, extra=1, can_delete=True)
    if request.method == 'POST':
        form = JudgeForm(request.POST, instance=judge)
        formset = EmploymentHistoryFormSet(request.POST, queryset=EmploymentHistory.objects.filter(judge=judge))
        if form.is_valid() and formset.is_valid():
            judge = form.save()
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
            return redirect('judges:judges_list')
    else:
        form = JudgeForm(instance=judge)
        formset = EmploymentHistoryFormSet(queryset=EmploymentHistory.objects.filter(judge=judge))
    return render(request, 'judges/judge_manage.html', {'form': form, 'formset': formset, 'judge': judge})

def judge_delete(request, judge_id):
    judge = get_object_or_404(Judge, id=judge_id)
    if request.method == 'POST':
        judge.delete()
        update_leading_judge_for_threads()
        return redirect('judges:judges_list')
    return render(request, 'judges/judge_confirm_delete.html', {'judge': judge})

@csrf_protect
def employment_history_delete(request, pk):
    history = get_object_or_404(EmploymentHistory, pk=pk)
    if request.method == "POST":
        history.delete()
        next_url = request.POST.get('next', reverse('judges:judge_edit', args=[history.judge.id]))
        return redirect(next_url)
    return redirect('judges:judges_list')