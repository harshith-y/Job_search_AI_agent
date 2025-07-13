import discord
from apscheduler.schedulers.blocking import BlockingScheduler
from agent import summarize_job  

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)
scheduler = BlockingScheduler()

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    scheduler.add_job(send_new_jobs, 'cron', hour=8)  # Every day at 8AM
    scheduler.start()

async def send_new_jobs():
    new_jobs = check_new_jobs()  # Return a list of new job strings
    channel = client.get_channel(CHANNEL_ID)
    if not new_jobs:
        await channel.send("No new jobs today.")
    else:
        for job in new_jobs:
            await channel.send(f"📌 {job}")

async def on_message(message):
    if message.content == "!testjobs" and message.channel.id == CHANNEL_ID:
        await send_new_jobs()

client.run(TOKEN)
