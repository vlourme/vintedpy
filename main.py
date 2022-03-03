import asyncio
import os
from time import time
import dataset
import dotenv
import hikari
import lightbulb

from scraper import generate_embed, generate_row, scrape

dotenv.load_dotenv()

bot = lightbulb.BotApp(token=os.getenv('TOKEN'))
db = dataset.connect('sqlite:///data/data.db')
table = db['subscriptions']


async def run_background() -> None:
    while True:
        for sub in table:
            items = scrape(sub)
            print(f'Found {len(items)} items for #' + str(sub['id']))
            for item in items:
                embed = generate_embed(item)
                row = generate_row(bot, item)

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
    print("The bot is ready!")
    asyncio.create_task(run_background())


@bot.command()
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option('url', 'URL to vinted search')
@lightbulb.option('channel', 'Channel to receive alerts', hikari.TextableChannel)
@lightbulb.command('subscribe', 'Subscribe to a Vinted search')
@lightbulb.implements(lightbulb.SlashCommand)
async def subscribe(ctx: lightbulb.Context) -> None:
    table.insert({
        'url': ctx.options.url,
        'channel_id': ctx.options.channel.id,
        'synced': False,
        'last_sync': int(time())
    })
    await ctx.respond('✅ Created subscription')


@bot.command()
@lightbulb.add_checks(lightbulb.owner_only)
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
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option('id', 'ID of the subscription')
@lightbulb.command('unsubscribe', 'Stop following a subscription')
@lightbulb.implements(lightbulb.SlashCommand)
async def unsubscribe(ctx: lightbulb.Context) -> None:
    table.delete(id=ctx.options.id)
    await ctx.respond(f'🗑 Deleted subscription #{ctx.options.id}.')

if __name__ == "__main__":
    if os.name != "nt":
        import uvloop

        uvloop.install()

bot.run(activity=hikari.Activity(name='Scraping SB Dunks!'))
