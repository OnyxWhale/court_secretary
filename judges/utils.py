import logging
from django.db.models import Q
from web.models import ForumThread
from .models import Judge

logger = logging.getLogger('court_secretary')

def update_leading_judge_for_threads():
    try:
        judges = Judge.objects.prefetch_related('employment_history')
        judge_periods = {}
        for judge in judges:
            for history in judge.employment_history.all():
                judge_periods.setdefault(judge.forum_account, []).append(
                    (history.hire_date, history.dismissal_date)
                )
        
        threads = ForumThread.objects.prefetch_related('messages')
        for thread in threads:
            for message in thread.messages.all():
                if message.author in judge_periods:
                    for hire_date, dismissal_date in judge_periods[message.author]:
                        msg_date = message.posted_at.date()
                        if msg_date >= hire_date and (dismissal_date is None or msg_date <= dismissal_date):
                            thread.leading_judge = Judge.objects.get(forum_account=message.author).full_name
                            thread.save()
                            logger.info(f"Updated leading judge for thread {thread.url} to {thread.leading_judge}")
                            break
                    if thread.leading_judge:
                        break
    except Exception as e:
        logger.error(f"Ошибка в update_leading_judge_for_threads: {e}")
        raise