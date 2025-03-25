from web.models import ForumThread
from .models import Judge

def update_leading_judge_for_threads():
    judges = Judge.objects.all().prefetch_related('employment_history')
    threads = ForumThread.objects.all().prefetch_related('messages')

    for thread in threads:
        leading_judge = None
        for message in thread.messages.all():
            for judge in judges:
                if message.author != judge.forum_account:
                    continue
                for history in judge.employment_history.all():
                    hire_date = history.hire_date
                    dismissal_date = history.dismissal_date
                    message_date = message.posted_at.date()

                    # Проверяем, попадает ли дата сообщения в период работы судьи
                    if message_date >= hire_date and (dismissal_date is None or message_date <= dismissal_date):
                        leading_judge = judge.full_name
                        break
                if leading_judge:
                    break
            if leading_judge:
                break
        thread.leading_judge = leading_judge
        thread.save()