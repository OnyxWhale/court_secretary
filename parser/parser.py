import requests
from bs4 import BeautifulSoup
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from web.models import ForumThread, ThreadMessage, ParseProgress
from .base_parser import BaseParser

class MessageExtractor:
    """Извлекает данные из сообщений форума."""
    @staticmethod
    def extract_messages(soup: BeautifulSoup, thread_obj: ForumThread) -> list:
        """Извлекает список сообщений из HTML."""
        messages = soup.select("article.message")
        result = []
        for msg in messages:
            msg_id = msg.get("id")
            msg_url = thread_obj.url + f"#{msg_id}" if msg_id else thread_obj.url

            author_elem = msg.select_one("h4.message-name a")
            content_elem = msg.select_one("div.message-userContent article")
            time_elem = msg.select_one("time.u-dt")

            author = author_elem.text.strip() if author_elem else "Unknown"
            content = MessageExtractor._extract_content(content_elem)
            posted_at = timezone.datetime.fromisoformat(time_elem["datetime"]) if time_elem else timezone.now()

            result.append({
                "url": msg_url,
                "author": author,
                "content": content,
                "posted_at": posted_at
            })
        return result

    @staticmethod
    def _extract_content(content_elem) -> str:
        """Извлекает содержимое сообщения."""
        if not content_elem:
            return "No content found"
        content_parts = []
        for elem in content_elem.children:
            if elem.name in ['p', 'div']:
                text = elem.get_text(strip=True)
                if text:
                    content_parts.append(text)
            elif elem.name == 'br':
                content_parts.append('\n')
            elif elem.string and elem.string.strip():
                content_parts.append(elem.string.strip())
        content = '\n'.join(part for part in content_parts if part).strip()
        return content or content_elem.get_text(strip=True).strip()

class ThreadParser:
    """Парсит отдельные треды форума."""
    def __init__(self, headers: dict):
        self.headers = headers

    def parse(self, thread_obj: ForumThread, progress: ParseProgress) -> None:
        """Парсит все страницы указанного треда."""
        page = 1
        new_messages_added = False
        while True:
            page_url = thread_obj.url if page == 1 else f"{thread_obj.url}page-{page}"
            try:
                response = requests.get(page_url, headers=self.headers, timeout=10)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Failed to fetch page {page} of thread {thread_obj.url}: {e}")
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            messages = MessageExtractor.extract_messages(soup, thread_obj)

            if not messages:
                print(f"No messages found on page {page} of thread {thread_obj.url}, stopping.")
                break

            with transaction.atomic():
                for msg_data in messages:
                    message, created = ThreadMessage.objects.get_or_create(
                        thread=thread_obj,
                        url=msg_data["url"],
                        defaults={
                            "author": msg_data["author"],
                            "content": msg_data["content"],
                            "posted_at": msg_data["posted_at"]
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

class ForumParser(BaseParser):
    """Парсит форум целиком."""
    def __init__(self, headers: dict, judge_service):
        self.headers = headers
        self.thread_parser = ThreadParser(headers)
        self.judge_service = judge_service

    def parse(self, max_pages: int = 1) -> None:
        """Парсит форум на заданное количество страниц."""
        print(f"Starting parse_forum with max_pages={max_pages}...")
        progress, _ = ParseProgress.objects.get_or_create(pk=1, defaults={'status': 'running'})
        threads_to_parse = []

        for page in range(1, max_pages + 1):
            url = settings.FORUM_URL if page == 1 else f"{settings.FORUM_URL}page-{page}"
            print(f"Parsing page {page}: {url}")
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
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
                    print(f"Processing thread: {title} ({thread_url}) with prefix: {prefix_text}")
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
            self.thread_parser.parse(thread_obj, progress)

        self.judge_service.update_leading_judge_for_threads()
        progress.status = 'completed'
        progress.progress = 100
        progress.save()
        print("Finished parse_forum successfully")

def start_parse(max_pages: int = 1) -> None:
    """Запускает парсинг форума."""
    headers = {"User-Agent": settings.USER_AGENT}
    from judges.services import JudgeService
    parser = ForumParser(headers, JudgeService())
    parser.parse(max_pages)