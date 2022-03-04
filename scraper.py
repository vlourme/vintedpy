from typing import Any, Dict, List

import hikari
from lightbulb import BotApp
from datetime import datetime
from api import search


def scrape(params: Dict[str, str]) -> List:
    """
    Scrape items and filter by new results

    Args:
        params (Dict[str, str]): Row of database

    Returns:
        List: list of new items
    """
    response = search(params['url'], {
        'per_page': 20
    })

    # Remove promoted items
    items = [item for item in response['items'] if item['promoted'] == False]

    # Skip null
    if not len(items):
        return []

    # Ignore items for first sync
    if params['synced'] == False:
        return [items[0]]

    # Filter date
    items = [item for item in items if item['photo']
             ['high_resolution']['timestamp'] > params['last_sync']]

    return items


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
    embed.title = item['title']
    embed.url = item['url']
    embed.set_image(item['photo']['url'])
    embed.color = hikari.Color(0x09b1ba)
    embed.add_field('Price', item['price'] + ' €', inline=True)
    embed.add_field('Size', item['size_title'], inline=True)

    date = datetime.utcfromtimestamp(
        int(item['photo']['high_resolution']['timestamp'])).strftime('%d/%m/%Y, %H:%M:%S')
    embed.set_footer(f'Published on {date} • Subscription #{str(sub_id)}')
    embed.set_author(name='Posted by ' + item['user']['login'],
                     url=item['user']['profile_url'])

    return embed


def generate_row(bot: BotApp, item: Any, link: str) -> Any:
    """
    Generate a component row with a button
    to redirect user on Vinted

    Args:
        bot (BotApp): Bot instance
        item (Any): Item
        link (str): Original search link

    Returns:
        Any: Generated row
    """
    row = bot.rest.build_action_row()
    (
        row.add_button(hikari.ButtonStyle.LINK, item['url'])
        .set_label('View article')
        .set_emoji('🛍')
        .add_to_container()
    )
    (
        row.add_button(hikari.ButtonStyle.LINK, link)
        .set_label('Search list')
        .set_emoji('🔍')
        .add_to_container()
    )
    (
        row.add_button(
            hikari.ButtonStyle.LINK,
            'https://www.vinted.fr/transaction/buy/new?source_screen=item&transaction%5Bitem_id%5D=' +
            str(item['id'])
        )
        .set_label('Buy')
        .set_emoji('💵')
        .add_to_container()
    )

    return row
