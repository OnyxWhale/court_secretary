from django.shortcuts import render
from web.models import ForumThread
from judges.models import Judge
from datetime import datetime, timedelta
from django.utils import timezone

def summary_table(request):
    # Получаем параметры фильтрации из GET-запроса
    judge_filter = request.GET.get('judge', '')
    prefix_filter = request.GET.get('prefix', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    urgent_filter = request.GET.get('urgent', '')

    # Базовый запрос
    threads = ForumThread.objects.all().prefetch_related('messages')

    # Применяем фильтры
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
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            date_to_obj = date_to_obj + timedelta(days=1)
            threads = threads.filter(created_at__lt=date_to_obj)
        except ValueError:
            pass

    # Фильтр "Срочное"
    urgent_threads = []
    if urgent_filter:
        judges_list = Judge.objects.all().values_list('forum_account', flat=True)
        for thread in threads:
            # Исключаем темы с префиксами "Рассмотрено" или "Отказано"
            if thread.prefix in ["Рассмотрено", "Отказано"]:
                continue

            first_judge_message = None
            for message in thread.messages.order_by('posted_at'):
                if message.author in judges_list:
                    first_judge_message = message
                    break

            # Проверяем, если нет ответа судьи и прошло более 50 часов
            time_to_first_judge_hours = None
            if not first_judge_message:
                time_delta = timezone.now() - thread.created_at
                days = time_delta.days
                hours, remainder = divmod(time_delta.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                time_to_first_judge_hours = days * 24 + hours + minutes / 60

            # Время судопроизводства
            trial_duration_hours = None
            if first_judge_message:
                end_time = timezone.now()
                last_judge_message = None
                for message in thread.messages.order_by('posted_at'):
                    if message.author in judges_list:
                        last_judge_message = message
                if thread.prefix in ["Отказано", "Рассмотрено"] and last_judge_message:
                    end_time = last_judge_message.posted_at
                time_delta = end_time - first_judge_message.posted_at
                days = time_delta.days
                hours, remainder = divmod(time_delta.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                trial_duration_hours = days * 24 + hours + minutes / 60

            # Проверяем условия для "Срочное"
            if (time_to_first_judge_hours and time_to_first_judge_hours > 50) or (trial_duration_hours and trial_duration_hours > 120):
                urgent_threads.append(thread.id)

        threads = threads.filter(id__in=urgent_threads)

    # Сортировка по дате создания
    threads = threads.order_by('-created_at')

    # Получаем уникальные значения для фильтров
    judges = ForumThread.objects.exclude(leading_judge__isnull=True).values_list('leading_judge', flat=True).distinct()
    prefixes = ForumThread.objects.exclude(prefix__isnull=True).values_list('prefix', flat=True).distinct()
    judges_list = Judge.objects.all().values_list('forum_account', flat=True)

    # Генерируем список последних 21 дня для автоподсказок
    today = timezone.now().date()
    last_21_days = [(today - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(21)]

    # Обрабатываем данные для таблицы
    thread_data = []
    for thread in threads:
        last_post = thread.messages.order_by('-posted_at').first()
        first_judge_message = None
        last_judge_message = None

        for message in thread.messages.order_by('posted_at'):
            if message.author in judges_list:
                if not first_judge_message:
                    first_judge_message = message
                last_judge_message = message

        time_to_first_judge_message = None
        time_to_first_judge_class = None
        if first_judge_message:
            time_delta = first_judge_message.posted_at - thread.created_at
            days = time_delta.days
            hours, remainder = divmod(time_delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            time_to_first_judge_message = f"{days} дн. {hours} ч. {minutes} мин."

            total_hours = days * 24 + hours + minutes / 60
            if total_hours >= 70:
                time_to_first_judge_class = "first-very-strong-indication"
            elif total_hours >= 60:
                time_to_first_judge_class = "first-strong-indication"
            elif total_hours >= 50:
                time_to_first_judge_class = "first-medium-indication"
            elif total_hours >= 40:
                time_to_first_judge_class = "first-less-medium-indication"
            elif total_hours >= 30:
                time_to_first_judge_class = "first-weak-indication"
            elif total_hours >= 20:
                time_to_first_judge_class = "first-less-weak-indication"
            elif total_hours >= 10:
                time_to_first_judge_class = "first-very-weak-indication"

        trial_duration = None
        trial_duration_class = None
        if first_judge_message:
            end_time = timezone.now()
            if thread.prefix in ["Отказано", "Рассмотрено"] and last_judge_message:
                end_time = last_judge_message.posted_at

            time_delta = end_time - first_judge_message.posted_at
            days = time_delta.days
            hours, remainder = divmod(time_delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            trial_duration = f"{days} дн. {hours} ч. {minutes} мин."

            total_hours = days * 24 + hours + minutes / 60
            if total_hours >= 170:
                trial_duration_class = "trial-very-strong-indication"
            elif total_hours >= 120:
                trial_duration_class = "trial-strong-indication"
            elif total_hours >= 100:
                trial_duration_class = "trial-medium-indication"
            elif total_hours >= 80:
                trial_duration_class = "trial-less-medium-indication"
            elif total_hours >= 60:
                trial_duration_class = "trial-weak-indication"
            elif total_hours >= 40:
                trial_duration_class = "trial-less-weak-indication"
            elif total_hours >= 20:
                trial_duration_class = "trial-very-weak-indication"

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