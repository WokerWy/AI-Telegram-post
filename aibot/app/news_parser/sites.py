import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional

from django.db.models.expressions import result
from sqlalchemy.orm import Session

from app import models

# --- Single Site parsing config ---
class SiteConfig:
    def __init__(
            self,
            name: str,
            base_url: str,
            list_selector: str,
            title_selector: str,
            link_selector: str,
            summary_selector: Optional[str] = None
    ):
        self.name = name
        self.base_url = base_url
        self.list_selector = list_selector
        self.title_selector = title_selector
        self.link_selector = link_selector
        self.summary_selector = summary_selector


# --- Site config ---
SITE_CONFIGS = {
    "example-news": SiteConfig(
        name="Example News",
        base_url="https://example.com/news",
        list_selector="article",
        title_selector="h2",
        link_selector="a",
        summary_selector="p"
    )
}


# --- Universal site parsing config ---
def parse_site(source: models.Source, db: Session) -> int:
    """
    Парсит сайт и сохраняет новости.
    Возвращает количество добавленных новостей.
    """
    config = SITE_CONFIGS.get(source.name.lower().replace(" ", "-"))
    if not config:
        return 0

    response = requests.get(source.url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select(config.list_selector)

    created_count = 0

    for item in items:
        title_el = item.select_one(config.title_selector)
        link_el = item.select_one(config.link_selector)

        if not title_el or not link_el:
            continue

        title = title_el.get_text(strip=True)
        url = link_el.get("href")

        if url and url.startswith("/"):
            url = config.base_url.rstrip("/") + url

        summary = None
        if config.summary_selector:
            summary_el = item.select_one(config.summary_selector)
            if summary_el:
                summary = summary_el.get_text(strip=True)

        # --- Secure of duplicate
        exists = db.query(models.NewsItem).filter(
            models.NewsItem.title == title,
            models.NewsItem.url == url
        ).first()

        if exists:
            continue

        news = models.NewsItem(
            title=title,
            url=url,
            summary=summary,
            source_id=source.id,
            published_at=datetime.utcnow()
        )

        db.add(news)
        created_count += 1

    db.commit()
    return created_count


def parse_all_sites(db: Session) -> dict:
    """
     Парсит все включённые site-источники.
    """
    sources = db.query(models.Source).filter(
        models.Source.type == "site",
        models.Source.enabled == True
    ).all()

    result = {}

    for source in sources:
        try:
            count = parse_site(source, db)
            result[source.name] = count
        except Exception as e:
            result[source.name] = f"error: {e}"

    return result
