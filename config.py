from dotenv import load_dotenv
import os

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
TICKET_CATEGORY_ID = int(os.getenv("TICKET_CATEGORY_ID"))
STAFF_ROLE_ID = int(os.getenv("STAFF_ROLE_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
INVITE_CHANNEL = int(os.getenv("INVITE_CHANNEL"))
REACTION_ROLE_CHANNEL = int(os.getenv("REACTION_ROLE_CHANNEL"))
INVITE_CHANNEL_ID = int(os.getenv("INVITE_CHANNEL_ID"))
SHIFT_CHANNEL_ID = int(os.getenv("SHIFT_CHANNEL_ID"))
TRAINING_CHANNEL_ID = int(os.getenv("TRAINING_CHANNEL_ID"))