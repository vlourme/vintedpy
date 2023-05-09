# Vinted Alerting Bot

I decided to open-source by Vinted alerting bot. This bot will inform you via Discord message when new articles that correspond to your criteria are posted on Vinted.

## Changelog

### 09/05/2023 — Bug fixes / Important notice

I haven't updated this bot for like a year. This bot is now back working with following changes:

- Fixed major bug due to Lightbulb change in the way of making embedded messages
- Tokens are now fetched via iOS client instead of web session
- Added an interval parameter in the environments
- Removed tenacity and retrying decorators, this may create an infinite loop.

## How it works?

Once installed, your Discord server will have 3 new commands registered:

```sh
/subscriptions # Display the list of your subscribed searches with ID
/subscribe [channel] [url] # Subscribe to a new search and receive alerts in a channel
/unsubscribe [id] # Unsubscribe of an alert with its ID
```

Once you saved a subscription, the bot will fetch new articles every 30 seconds and alert you in case of new findings!

### Creating bot on Discord Developer

1. Create an application on [Discord Developer](https://discord.com/developers/applications)
2. Create a bot in your application
3. Copy the `.env.example` file to `.env` and copy/paste the token
4. Invite your bot by generating an URL (OAuth2 -> URl Generator)

**Important:** Set the following scopes:

- `bot`
- `applications.commands`

And also set the following bot permission:

- Send Messages
- Embed Links
- Read Messages/View Channels
- Use Slash Commands

### Installation

You must have `python3` and `pip3` installed, Python >3.8 is recommended.

1. Install dependencies: `pip3 install -r requirements.txt`
2. Start the bot: `python3 main.py`

If you want to stop the bot, you can just press **CTRL+C** once. Don't spam **CTRL+C**, it may take a few seconds before it completely stop because of the background thread used to sync items.

### Keeping the bot up all the time

I highly recommend running this bot via a service on Linux distributions.

Here is an example of a Linux service, you will certainly need to change paths:

```ini
[Unit]
Description=vinted_scraper
After=network.target

[Service]
ExecStart=python3 /root/vintedpy/main.py
EnvironmentFile=/root/vintedpy/.env
Restart=on-failure
SyslogIdentifier=vinted
RestartSec=5
TimeoutStartSec=infinity

[Install]
WantedBy=multi-user.target
```
