import asyncio
import os
from time import time
import dataset
import dotenv
import hikari
import lightbulb
from loguru import logger as log

from scraper import generate_embed, generate_row, scrape

dotenv.load_dotenv()

bot = lightbulb.BotApp(token=os.getenv('TOKEN'))
db = dataset.connect('sqlite:///data/data.db')
table = db['subscriptions']


async def run_background() -> None:
    log.info("Scraper started.")

    while True:
        for sub in table:
            items = scrape(db, sub)
            log.debug("{items} found for {id}",
                      items=len(items), id=str(sub['id']))
            for item in items:
                embed = generate_embed(item, sub['id'])
                row = generate_row(bot, item, sub['url'])

                await bot.rest.create_message(sub['channel_id'], embed=embed, components=[row])

            if len(items) > 0:
                # Update table by using last in date item timestamp
                table.update(
                    dict(id=sub['id'],
                         synced=True,
                         last_sync=int(items[0]['photo']
                                       ['high_resolution']['timestamp'])
                         ),
                    ['id'])

        await asyncio.sleep(30)


@bot.listen(hikari.ShardReadyEvent)
async def ready_listener(_):
    log.info("Bot is ready")
    asyncio.create_task(run_background())


@bot.command()
@lightbulb.option('url', 'URL to vinted search', type=str, required=True)
@lightbulb.option('channel', 'Channel to receive alerts', type=hikari.TextableChannel, required=True)
@lightbulb.command('subscribe', 'Subscribe to a Vinted search')
@lightbulb.implements(lightbulb.SlashCommand)
async def subscribe(ctx: lightbulb.Context) -> None:
    table.insert({
        'url': ctx.options.url,
        'channel_id': ctx.options.channel.id,
        'synced': False,
        'last_sync': int(time())
    })
    log.info("Subscription created for {url}", url=ctx.options.url)
    await ctx.respond('✅ Created subscription')


@bot.command()
@lightbulb.command('subscriptions', 'Get a list of subscription')
@lightbulb.implements(lightbulb.SlashCommand)
async def subscriptions(ctx: lightbulb.Context) -> None:
    embed = hikari.Embed(title='Subscriptions')

    for sub in table:
        embed.add_field(
            name='#' + str(sub['id']),
            value=sub['url']
        )

    await ctx.respond(embed)


@bot.command()
@lightbulb.option('id', 'ID of the subscription', type=int, required=True)
@lightbulb.command('unsubscribe', 'Stop following a subscription')
@lightbulb.implements(lightbulb.SlashCommand)
async def unsubscribe(ctx: lightbulb.Context) -> None:
    table.delete(id=ctx.options.id)
    log.info("Deleted subscription #{id}", id=str(ctx.options.id))
    await ctx.respond(f'🗑 Deleted subscription #{str(ctx.options.id)}.')

if __name__ == "__main__":
    if os.name != "nt":
        import uvloop

        uvloop.install()

bot.run(activity=hikari.Activity(
    name='Vinted articles!',
    type=hikari.ActivityType.WATCHING,
    url='https://github.com/vlourme/vintedpy'))
