import discord
from discord.ext import commands
import config

# Ticket commands imports
from commands.ticket_commands.ticket_close import setup as setup_ticket_close
from commands.ticket_commands.ticket_add import setup as setup_ticket_add
from commands.ticket_commands.ticket_remove import setup as setup_ticket_remove
from commands.ticket_commands.ticket_panel import setup as setup_ticket_panel
from commands.ticket_commands.ticket_claim import setup as setup_ticket_claim
from commands.ticket_commands.ticket_blacklist import setup as setup_ticket_blacklist
from commands.ticket_commands.patience import setup as setup_patience

# Shift commands imports
from commands.shift_commands.shift_start import setup as setup_shift_start
from commands.shift_commands.shift_cancel import setup as setup_shift_cancel
from commands.shift_commands.shift_end import setup as setup_shift_end

# Training commands imports
from commands.training_commands.training_start import setup as setup_training_start
from commands.training_commands.training_cancel import setup as setup_training_cancel
from commands.training_commands.training_end import setup as setup_training_end

# Reaction commands imports
from commands.reaction_commands.reaction_panel import setup as setup_reaction_panel

# Moderation commands imports
from commands.moderation_commands.kick import setup as setup_kick
from commands.moderation_commands.ban import setup as setup_ban
from commands.moderation_commands.unban import setup as setup_unban
from commands.moderation_commands.warn import setup as setup_warn
from commands.moderation_commands.unwarn import setup as setup_unwarn
from commands.moderation_commands.mute import setup as setup_mute
from commands.moderation_commands.unmute import setup as setup_unmute
from commands.moderation_commands.lockdown import setup as setup_lockdown
from commands.moderation_commands.note import setup as setup_note
from commands.moderation_commands.notes import setup as setup_notes
from commands.moderation_commands.warnings import setup as setup_warnings
from commands.moderation_commands.modlogs import setup as setup_modlogs
from commands.moderation_commands.members import setup as setup_members

# Import views and utilities
from commands.ticket_commands.ticket_panel import TicketPanelView
from utils.reaction_panel import GeneralRolesView, PronounsRolesView
from utils.invite_utils import setup_invite_tracking, handle_member_join, cache_invites_for_guild, setup_invite_commands
from utils.group_counter import setup_group_monitoring
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.invites = True  # Required for invite tracking

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord')
    print(f'Bot is ready in {len(bot.guilds)} guilds')
    
    # Add persistent views
    bot.add_view(TicketPanelView())
    bot.add_view(GeneralRolesView())
    bot.add_view(PronounsRolesView())
    
    # Update presence
    await bot.change_presence(activity=discord.CustomActivity(name="Indexing tickets"))
    await asyncio.sleep(5)
    await bot.change_presence(activity=discord.CustomActivity(name="Answering your tickets"))
    
    print('Persistent ticket panel view loaded')
    print('Persistent reaction role view loaded')
    
    # Cache invites for all guilds
    for guild in bot.guilds:
        await cache_invites_for_guild(guild)
    print('Invite tracking initialized')
    
    # Setup Roblox group monitoring
    # Replace these with your actual values
    if hasattr(config, 'ROBLOX_GROUP_ID') and hasattr(config, 'GROUP_COUNTER_CHANNEL_ID'):
        try:
            group_counter = await setup_group_monitoring(
                bot=bot,
                group_id=config.ROBLOX_GROUP_ID,
                channel_id=config.GROUP_COUNTER_CHANNEL_ID,
                check_interval=120  # Check every 2 minutes
            )
            print('Roblox group monitoring started')
        except Exception as e:
            print(f'Failed to start group monitoring: {e}')
    else:
        print('Roblox group monitoring not configured - add ROBLOX_GROUP_ID and GROUP_COUNTER_CHANNEL_ID to config.py')
    
    # Sync slash commands - this reloads/updates all slash commands
    try:
        print("Syncing slash commands...")
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

@bot.event
async def on_member_join(member):
    """Handle member join - includes invite tracking"""
    # Your existing member join logic can go here
    
    # Handle invite tracking
    await handle_member_join(member)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.CommandRegistrationError):
        print(f"Command registration error: {error}")
        await ctx.send("There was an issue with command registration. Please contact an administrator.")
    else:
        await ctx.send(f"An error occurred: {error}")
        print(f"Unhandled error: {error}")

@bot.command(name="a_say")
async def say(ctx, *, message: str):
    """Repeats the message sent by the user (staff only)."""
    staff_role = discord.utils.get(ctx.author.roles, id=config.STAFF_ROLE_ID)
    if not staff_role:
        await ctx.send("You don't have permission to use this command.")
        return
    await ctx.send(message)

# Function to safely setup commands with error handling
def safe_setup(setup_func, name):
    """Safely setup a command with error handling"""
    try:
        setup_func(bot)
        print(f"✓ {name} commands loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load {name} commands: {e}")

# Setup all commands with error handling
print("Loading commands...")

# Setup ticket commands
safe_setup(setup_ticket_close, "ticket_close")
safe_setup(setup_ticket_add, "ticket_add")
safe_setup(setup_ticket_remove, "ticket_remove")
safe_setup(setup_ticket_panel, "ticket_panel")
safe_setup(setup_ticket_claim, "ticket_claim")
safe_setup(setup_ticket_blacklist, "ticket_blacklist")
safe_setup(setup_patience, "patience")

# Setup shift commands
safe_setup(setup_shift_start, "shift_start")
safe_setup(setup_shift_cancel, "shift_cancel")
safe_setup(setup_shift_end, "shift_end")

# Setup training commands
safe_setup(setup_training_start, "training_start")
safe_setup(setup_training_cancel, "training_cancel")
safe_setup(setup_training_end, "training_end")

# Setup reaction commands
safe_setup(setup_reaction_panel, "reaction_panel")

# Setup invite tracking
safe_setup(setup_invite_tracking, "invite_tracking")
safe_setup(setup_invite_commands, "invite_commands")

# Setup moderation commands
safe_setup(setup_kick, "kick")
safe_setup(setup_ban, "ban")
safe_setup(setup_unban, "unban")
safe_setup(setup_warn, "warn")
safe_setup(setup_unwarn, "unwarn")
safe_setup(setup_mute, "mute")
safe_setup(setup_unmute, "unmute")  # This is where the duplicate command error occurs
safe_setup(setup_lockdown, "lockdown")
safe_setup(setup_note, "note")
safe_setup(setup_notes, "notes")
safe_setup(setup_warnings, "warnings")
safe_setup(setup_modlogs, "modlogs")
safe_setup(setup_members, "members")

print("Command loading complete!")

if __name__ == "__main__":
    bot.run(config.DISCORD_TOKEN)