import requests
from bs4 import BeautifulSoup
from django.utils import timezone
from django.db import transaction
from web.models import ForumThread, ThreadMessage, ParseProgress
from judges.utils import update_leading_judge_for_threads

FORUM_URL = "https://forum.gta5rp.com/forums/federalnyj-sud.1745/"

def parse_thread(thread_obj, progress, headers):
    print(f"Starting parse_thread for {thread_obj.url}")
    page = 1
    new_messages_added = False
    while True:
        page_url = thread_obj.url if page == 1 else f"{thread_obj.url}page-{page}"
        print(f"Parsing page {page} of thread: {page_url}")
        try:
            response = requests.get(page_url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch page {page} of thread {thread_obj.url}: {e}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.select("article.message")
        print(f"Found {len(messages)} messages on page {page} of thread {thread_obj.url}")

        if not messages:
            print(f"No messages found on page {page} of thread {thread_obj.url}, stopping pagination.")
            break

        with transaction.atomic():
            for msg in messages:
                msg_id = msg.get("id")
                msg_url = thread_obj.url + f"#{msg_id}" if msg_id else thread_obj.url

                author_elem = msg.select_one("h4.message-name a")
                content_elem = msg.select_one("div.message-userContent article")
                time_elem = msg.select_one("time.u-dt")

                author = author_elem.text.strip() if author_elem else "Unknown"
                if content_elem:
                    content_parts = []
                    for elem in content_elem.children:
                        if elem.name == 'p' or elem.name == 'div':
                            text = elem.get_text(strip=True)
                            if text:
                                content_parts.append(text)
                        elif elem.name == 'br':
                            content_parts.append('\n')
                        elif elem.string and elem.string.strip():
                            content_parts.append(elem.string.strip())
                    content = '\n'.join(part for part in content_parts if part).strip()
                    if not content:
                        content = content_elem.get_text(strip=True).strip()
                else:
                    content = "No content found"
                posted_at = timezone.datetime.fromisoformat(time_elem["datetime"]) if time_elem else timezone.now()

                print(f"Saving message from {author} at {posted_at} with content: {content[:50]}...")
                message, created = ThreadMessage.objects.get_or_create(
                    thread=thread_obj,
                    url=msg_url,
                    defaults={
                        "author": author,
                        "content": content,
                        "posted_at": posted_at
                    }
                )
                if created:
                    new_messages_added = True

        next_page = soup.select_one(".pageNav-jump--next")
        if not next_page:
            print(f"No next page found for thread {thread_obj.url}, stopping.")
            break
        page += 1

    if new_messages_added:
        thread_obj.last_parsed_at = timezone.now()
        thread_obj.save()
        print(f"Updated last_parsed_at for thread {thread_obj.url} to {thread_obj.last_parsed_at}")

    progress.processed_threads += 1
    progress.progress = (progress.processed_threads / progress.total_threads) * 100 if progress.total_threads > 0 else 0
    progress.save()
    print(f"Finished parse_thread for {thread_obj.url}")

def parse_forum(max_pages=1):
    print(f"Starting parse_forum with max_pages={max_pages}...")
    progress, _ = ParseProgress.objects.get_or_create(pk=1, defaults={'status': 'running'})
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        threads_to_parse = []
        for page in range(1, max_pages + 1):
            url = FORUM_URL if page == 1 else f"{FORUM_URL}page-{page}"
            print(f"Parsing page {page}: {url}")
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Failed to fetch page {page} ({url}): {e}")
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            threads = soup.select(".structItem--thread")
            print(f"Found {len(threads)} threads on page {page}")

            if not threads:
                print(f"No threads found on page {page}, stopping pagination.")
                break

            for thread in threads:
                title_elem = thread.select_one(".structItem-title")
                prefix = title_elem.select_one(".label")
                prefix_text = prefix.text.strip() if prefix else None

                title_link = title_elem.select_one("a[data-xf-init='preview-tooltip']")
                title = title_link.text.strip() if title_link else "Без названия"
                thread_url = "https://forum.gta5rp.com" + title_link["href"] if title_link else None

                time_elem = thread.select_one(".structItem-startDate time")
                created_at = timezone.datetime.fromisoformat(time_elem["datetime"]) if time_elem else timezone.now()

                if thread_url:
                    print(f"Processing thread: {title} ({thread_url}) with prefix: {prefix_text}, created at: {created_at}")
                    with transaction.atomic():
                        thread_obj, created = ForumThread.objects.get_or_create(
                            url=thread_url,
                            defaults={
                                "title": title,
                                "prefix": prefix_text,
                                "created_at": created_at,
                                "last_parsed_at": timezone.now()
                            }
                        )
                    if created or not thread_obj.messages.exists():
                        threads_to_parse.append(thread_obj)

        progress.total_threads = len(threads_to_parse)
        progress.processed_threads = 0
        progress.progress = 0
        progress.status = 'running'
        progress.save()
        print(f"Total threads to parse: {progress.total_threads}")

        for thread_obj in threads_to_parse:
            parse_thread(thread_obj, progress, headers)

        # Обновляем ведущих судей после парсинга
        update_leading_judge_for_threads()

        progress.status = 'completed'
        progress.progress = 100
        progress.save()
        print("Finished parse_forum successfully")
    except Exception as e:
        progress.status = 'failed'
        progress.save()
        print(f"parse_forum failed with error: {str(e)}")
        raise e

def start_parse(max_pages=1):
    parse_forum(max_pages=max_pages)