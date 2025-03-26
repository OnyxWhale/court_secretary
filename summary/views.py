from django.shortcuts import render
from django.db.models import Q, Min, Max, Case, When, Value, BooleanField, F
from django.core.paginator import Paginator
from datetime import timedelta
from django.utils import timezone
from web.models import ForumThread
from judges.models import Judge
from court_secretary.utils.date_utils import parse_date

def summary_table(request):
    judge_filter = request.GET.get('judge', '')
    prefix_filter = request.GET.get('prefix', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    urgent_filter = request.GET.get('urgent', '')

    judges_list = Judge.objects.values_list('forum_account', flat=True)
    threads = ForumThread.objects.select_related().prefetch_related('messages').annotate(
        first_judge_msg=Min('messages__posted_at', filter=Q(messages__author__in=judges_list)),
        last_judge_msg=Max('messages__posted_at', filter=Q(messages__author__in=judges_list)),
        is_urgent=Case(
            When(
                Q(prefix__in=["Рассмотрено", "Отказано"]), then=Value(False)
            ),
            When(
                Q(first_judge_msg__isnull=True) & Q(created_at__lte=timezone.now() - timedelta(hours=50)),
                then=Value(True)
            ),
            When(
                Q(first_judge_msg__isnull=False) & Q(last_judge_msg__isnull=False) & 
                Q(last_judge_msg__gte=F('first_judge_msg') + timedelta(hours=120)),
                then=Value(True)
            ),
            default=Value(False),
            output_field=BooleanField()
        )
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
            threads = threads.filter(created_at__gte=parse_date(date_from))
        except ValueError:
            pass
    if date_to:
        try:
            date_to_obj = parse_date(date_to) + timedelta(days=1)
            threads = threads.filter(created_at__lt=date_to_obj)
        except ValueError:
            pass
    if urgent_filter:
        threads = threads.filter(is_urgent=True)

    threads = threads.order_by('-created_at')
    paginator = Paginator(threads, 100)  # 100 записей на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    judges = ForumThread.objects.exclude(leading_judge__isnull=True).values_list('leading_judge', flat=True).distinct()
    prefixes = ForumThread.objects.exclude(prefix__isnull=True).values_list('prefix', flat=True).distinct()

    today = timezone.now().date()
    last_21_days = [(today - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(21)]

    thread_data = []
    for thread in page_obj:
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
        'page_obj': page_obj,
        'judges': judges,
        'prefixes': prefixes,
        'selected_judge': judge_filter,
        'selected_prefix': prefix_filter,
        'date_from': date_from,
        'date_to': date_to,
        'urgent_filter': urgent_filter,
        'last_21_days': last_21_days,
    })