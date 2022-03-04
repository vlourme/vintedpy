# Vinted article scraper for Discord
This bot is heavily inspired from [vinted-bot-discord](https://github.com/Androz2091/vinted-discord-bot) with major issues fixed.
The goal of this bot is to be:
- Easy to install (standalone python 3.x or Docker)
- Easy to maintain and patch, the code is very light with less than 300 LoC
- Able to handle networking issues (automatic retries on HTTP) and proxies in future releases

## Important notes
- This is a work in progress, it was not intensively tested yet.
- Working only on `vinted.fr` domain.

## How it works?
Once installed, your Discord server will have 3 new commands registered:
```sh
/subscriptions # Display the list of your subscribed searches with ID
/subscribe [channel] [url] # Subscribe to a new search and receive alerts in a channel
/unsubscribe [id] # Unsubscribe of an alert with its ID
```

Once you saved a subscription, the bot will fetch new articles every 30 seconds and alert you in case of new findings!

## Installation
There are two ways of installing this Vinted bot:
- Standalone Python
- Docker

The standalone installation is most the of the time easier for most users.

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

### Database setup
The program uses SQLite to store subscriptions and synced items.
Once the first launch, it will create the database automatically, however, you'll need to create a **data directory**
in the project root.
In order to do this, you can just use your graphical interface to make a directory or run `mkdir data` in your terminal.

*Note:* You may want to use a external database such as MySQL or PostgreSQL, for this, you can specify the database credentials in the beginning of the `main.py` file. This can be useful if you want to run replicas of the bot like on Kubernetes.

### Standalone installation
You must have `python3` and `pip3` installed, Python >3.8 is recommended.

1. Install dependencies: `pip3 install -r requirements.txt`
2. Start the bot: `python3 main.py`

If you want to stop the bot, you can just press **CTRL+C** once. Don't spam **CTRL+C**, it may take a few seconds before it completely stop because of the background thread used to sync items.

*Note:* The bot will run on main thread, if the connection to the server closes, the bot will end. You can use `screen` or `jobs` to handle this. 

### Docker installation
You must have docker installed.

1. Build the image: `docker build -t vinted .`
2. Start the bot: `docker run --env-file=.env -d vinted`

If you want to stop the bot:
1. Run `docker ps` to get container ID
2. Then, run `docker stop <container_id>`

In case of problem, you can get logs using `docker logs <container_id>`.