from django.shortcuts import render
from django.db.models import Q, Min, Max
from web.models import ForumThread
from judges.models import Judge
from datetime import datetime, timedelta
from django.utils import timezone

def calculate_urgent_threads(threads, judges_list):
    urgent_ids = []
    for thread in threads:
        if thread.prefix in ["Рассмотрено", "Отказано"]:
            continue
        first_judge_message = thread.messages.filter(author__in=judges_list).order_by('posted_at').first()
        if not first_judge_message:
            time_delta = timezone.now() - thread.created_at
            total_hours = time_delta.total_seconds() / 3600
            if total_hours > 50:
                urgent_ids.append(thread.id)
        else:
            end_time = timezone.now()
            last_judge_message = thread.messages.filter(author__in=judges_list).order_by('-posted_at').first()
            if thread.prefix in ["Отказано", "Рассмотрено"] and last_judge_message:
                end_time = last_judge_message.posted_at
            trial_duration_hours = (end_time - first_judge_message.posted_at).total_seconds() / 3600
            if trial_duration_hours > 120:
                urgent_ids.append(thread.id)
    return urgent_ids

def summary_table(request):
    judge_filter = request.GET.get('judge', '')
    prefix_filter = request.GET.get('prefix', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    urgent_filter = request.GET.get('urgent', '')

    threads = ForumThread.objects.annotate(
        first_judge_msg=Min('messages__posted_at', filter=Q(messages__author__in=Judge.objects.values_list('forum_account', flat=True))),
        last_judge_msg=Max('messages__posted_at', filter=Q(messages__author__in=Judge.objects.values_list('forum_account', flat=True)))
    )

    if judge_filter:
        threads = threads.filter(leading_judge=judge_filter)
    if prefix_filter:
        if prefix_filter == "no_prefix":
            threads = threads.filter(prefix__isnull=True)
        else:
            threads = threads.filter(prefix=prefix_filter)
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            threads = threads.filter(created_at__gte=date_from_obj)
        except ValueError:
            pass
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            threads = threads.filter(created_at__lt=date_to_obj)
        except ValueError:
            pass
    if urgent_filter:
        judges_list = Judge.objects.values_list('forum_account', flat=True)
        urgent_ids = calculate_urgent_threads(threads, judges_list)
        threads = threads.filter(id__in=urgent_ids)

    threads = threads.order_by('-created_at')
    judges = ForumThread.objects.exclude(leading_judge__isnull=True).values_list('leading_judge', flat=True).distinct()
    prefixes = ForumThread.objects.exclude(prefix__isnull=True).values_list('prefix', flat=True).distinct()
    judges_list = Judge.objects.values_list('forum_account', flat=True)

    today = timezone.now().date()
    last_21_days = [(today - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(21)]

    thread_data = []
    for thread in threads:
        last_post = thread.messages.order_by('-posted_at').first()
        time_to_first_judge_message = None
        time_to_first_judge_class = None
        if thread.first_judge_msg:
            time_delta = thread.first_judge_msg - thread.created_at
            days = time_delta.days
            hours, remainder = divmod(time_delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            time_to_first_judge_message = f"{days} дн. {hours} ч. {minutes} мин."
            total_hours = days * 24 + hours + minutes / 60
            if total_hours >= 70:
                time_to_first_judge_class = "first-very-strong-indication"
            elif total_hours >= 60:
                time_to_first_judge_class = "first-strong-indication"
            # ... остальные условия ...

        trial_duration = None
        trial_duration_class = None
        if thread.first_judge_msg:
            end_time = timezone.now()
            if thread.prefix in ["Отказано", "Рассмотрено"] and thread.last_judge_msg:
                end_time = thread.last_judge_msg
            time_delta = end_time - thread.first_judge_msg
            days = time_delta.days
            hours, remainder = divmod(time_delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            trial_duration = f"{days} дн. {hours} ч. {minutes} мин."
            total_hours = days * 24 + hours + minutes / 60
            if total_hours >= 170:
                trial_duration_class = "trial-very-strong-indication"
            # ... остальные условия ...

        thread_data.append({
            'thread': thread,
            'last_post_date': last_post.posted_at if last_post else None,
            'time_to_first_judge_message': time_to_first_judge_message,
            'time_to_first_judge_class': time_to_first_judge_class,
            'trial_duration': trial_duration,
            'trial_duration_class': trial_duration_class,
        })

    return render(request, 'summary/summary_table.html', {
        'thread_data': thread_data,
        'judges': judges,
        'prefixes': prefixes,
        'selected_judge': judge_filter,
        'selected_prefix': prefix_filter,
        'date_from': date_from,
        'date_to': date_to,
        'urgent_filter': urgent_filter,
        'last_21_days': last_21_days,
    })