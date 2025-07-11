import discord
from discord.ext import commands
import config
from commands.ticket_close import setup as setup_ticket_close
from commands.ticket_add import setup as setup_ticket_add
from commands.ticket_remove import setup as setup_ticket_remove
from commands.ticket_panel import setup as setup_ticket_panel
from commands.ticket_claim import setup as setup_ticket_claim
from commands.patience import setup as setup_patience
from commands.reaction_panel import setup as setup_reaction_panel
from commands.ticket_panel import TicketPanelView
from utils.reaction_panel import ReactionRoleView
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is ready in {len(bot.guilds)} guilds')
    bot.add_view(TicketPanelView())
    bot.add_view(ReactionRoleView())
    await bot.change_presence(activity=discord.CustomActivity(name="Indexing tickets"))
    await asyncio.sleep(5)
    await bot.change_presence(activity=discord.CustomActivity(name="Answering your tickets"))
    print('Persistent ticket panel view loaded!')
    print('Persistent reaction role view loaded!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found! Use `!help` to see available commands.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    else:
        await ctx.send(f"An error occurred: {error}")

@bot.command(name="a_say")
async def say(ctx, *, message: str):
    """Repeats the message sent by the user (staff only)."""
    staff_role = discord.utils.get(ctx.author.roles, id=config.STAFF_ROLE_ID)
    if not staff_role:
        await ctx.send("You don't have permission to use this command.")
        return
    await ctx.send(message)

setup_ticket_close(bot)
setup_ticket_add(bot)
setup_ticket_remove(bot)
setup_ticket_panel(bot)
setup_ticket_claim(bot)
setup_patience(bot)
setup_reaction_panel(bot)

if __name__ == "__main__":
    bot.run(config.DISCORD_TOKEN)