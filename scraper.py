from typing import Any, Dict, List
from dataset import Database
import hikari
from lightbulb import BotApp
from datetime import datetime

from api import search
from loguru import logger as log


def scrape(db: Database, params: Dict[str, str]) -> List:
    """
    Scrape items and filter by new results

    Args:
        params (Dict[str, str]): Row of database

    Returns:
        List: list of new items
    """
    response = search(params["url"], {"per_page": 20})

    # Remove promoted items
    try:
        items = [item for item in response["items"] if item["promoted"] == False]
    except KeyError:
        return []

    # Skip null
    if not len(items):
        return []

    # Ignore items for first sync
    if params["last_sync"] == -1:
        return [items[0]]

    table = db["items"]

    # Filter date and by existing
    results = []
    for item in items:
        try:
            timestamp = item["photo"]["high_resolution"]["timestamp"]
        except:
            log.warning("Empty timestamp found")
            print(item)
            continue

        if timestamp > params["last_sync"] and "id" in item:
            results.append(item)

    for item in results:
        saved = table.find_one(id=item["id"])
        log.debug(saved)

        if saved:
            # Already known
            log.debug("Removing result {id}, already known", id=item["id"])
            results.remove(item)
        else:
            log.debug("Inserting item #{id}", id=item["id"])
            table.insert({"id": item["id"]})

    return results


def generate_embed(item: Any, sub_id: int) -> hikari.Embed:
    """
    Generate an embed with item details

    Args:
        item (Any): Scraped item
        sub_id (int): Subscription ID

    Returns:
        hikari.Embed: Generated embed
    """
    embed = hikari.Embed()
    embed.title = item["title"] or "Unknown"
    embed.url = item["url"] or "Unknown"
    embed.set_image(item["photo"]["url"] or "Unknown")
    embed.color = hikari.Color(0x09B1BA)
    embed.add_field("Price", str(item["price"]) or "-1" + " €", inline=True)
    embed.add_field("Size", item["size_title"] or "-1", inline=True)

    date = datetime.utcfromtimestamp(
        int(item["photo"]["high_resolution"]["timestamp"])
    ).strftime("%d/%m/%Y, %H:%M:%S")
    embed.set_footer(f'Published on {date or "unknown"} • Subscription #{str(sub_id)}')
    embed.set_author(
        name="Posted by " + item["user"]["login"] or "unknown",
        url=item["user"]["profile_url"] or "unknown",
    )

    return embed
