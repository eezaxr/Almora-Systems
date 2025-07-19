import discord
from discord.ext import commands
from discord import app_commands
import config
import uuid
from datetime import datetime
import re

# Store active shifts (in a real bot, you'd use a database)
active_shifts = {}

def setup(bot):
    @bot.tree.command(name="shift-start", description="Start a new shift")
    @app_commands.describe(
        shift_type="Type of shift",
        start_time="Start time (format: HH:MM, must be in 5-minute intervals)",
        end_time="End time (format: HH:MM, must be in 5-minute intervals)"
    )
    @app_commands.choices(shift_type=[
        app_commands.Choice(name="Promotional", value="Promotional"),
        app_commands.Choice(name="General", value="General")
    ])
    async def shift_start(
        interaction: discord.Interaction,
        shift_type: str,
        start_time: str,
        end_time: str
    ):
        # Check if user has staff role
        staff_role = discord.utils.get(interaction.user.roles, id=config.STAFF_ROLE_ID)
        if not staff_role:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        # Validate time format and 5-minute intervals
        time_pattern = r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$'
        
        if not re.match(time_pattern, start_time) or not re.match(time_pattern, end_time):
            await interaction.response.send_message("Invalid time format! Please use HH:MM format (e.g., 19:45)", ephemeral=True)
            return

        # Check if minutes are in 5-minute intervals
        start_minutes = int(start_time.split(':')[1])
        end_minutes = int(end_time.split(':')[1])
        
        if start_minutes % 5 != 0 or end_minutes % 5 != 0:
            await interaction.response.send_message("Time must be in 5-minute intervals (e.g., 19:45, 20:00, 20:05)", ephemeral=True)
            return

        # Generate unique shift ID
        shift_id = str(uuid.uuid4())[:8].upper()
        
        # Create embed based on shift type
        if shift_type == "Promotional":
            embed = discord.Embed(
                title="<:Shifts:1393545049832292482> Almora Promotional Shift Starting",
                description=f"A promotional shift has now started at the Handley Chase Store. If you have any questions, please ask the shift host. See details below.",
                color=0x4A4A4A
            )
        else:
            embed = discord.Embed(
                title="<:Shifts:1393545049832292482> Almora Shift Starting",
                description=f"A shift has now started at the Handley Chase Store. If you have any questions, please ask the shift host. See details below.",
                color=0x4A4A4A
            )

        # Convert time to Discord timestamp format
        from datetime import datetime, time
        import time as time_module
        
        # Get today's date and create datetime objects
        today = datetime.now().date()
        start_datetime = datetime.combine(today, datetime.strptime(start_time, "%H:%M").time())
        end_datetime = datetime.combine(today, datetime.strptime(end_time, "%H:%M").time())
        
        # Convert to Unix timestamp
        start_timestamp = int(start_datetime.timestamp())
        end_timestamp = int(end_datetime.timestamp())

        embed.add_field(
            name="",
            value=f"**Host**: {interaction.user.mention}\n**Start Time**: <t:{start_timestamp}:t>\n**End Time**: <t:{end_timestamp}:t>",
            inline=False
        )
        embed.set_footer(text=f"Session ID: {shift_id}")
        embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")

        # Send to shift channel with link button and role ping
        shift_channel = bot.get_channel(config.SHIFT_CHANNEL_ID)
        view = MainGameView()
        message = await shift_channel.send(f"<@&1393356313173692518>", embed=embed, view=view)
        
        # Store shift data
        active_shifts[shift_id] = {
            'type': shift_type,
            'host': interaction.user.id,
            'start_time': start_time,
            'end_time': end_time,
            'message': message,
            'status': 'active'
        }
        
        await interaction.response.send_message(f"Shift started successfully! Shift ID: {shift_id}", ephemeral=True)

class MainGameView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
        # Create the link button
        link_button = discord.ui.Button(
            label="Main Game",
            style=discord.ButtonStyle.link,
            url="https://www.roblox.com/games/75586247932175"
        )
        self.add_item(link_button)