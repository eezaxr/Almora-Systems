import discord
from discord.ext import commands
from discord import app_commands
import config
from datetime import datetime, timedelta
import re
import random
import string

# Dictionary to store active training sessions
active_trainings = {}

def validate_time_format(time_str):
    """Validate time format and check if it's in 5-minute intervals"""
    # Check if time matches HH:MM format
    if not re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', time_str):
        return False, "Invalid time format. Use HH:MM format (e.g., 14:30)"
    
    # Check if minutes are in 5-minute intervals
    minutes = int(time_str.split(':')[1])
    if minutes % 5 != 0:
        return False, "Time must be in 5-minute intervals (e.g., 14:30, 14:35, not 14:32)"
    
    return True, None

def generate_training_id():
    """Generate a unique training ID"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def create_training_embed(training_type, start_time, end_time, host_mention, training_id):
    """Create the training session embed"""
    embed = discord.Embed(
        title=f"<:Retail:1393269955260055702> Almora {training_type} Training Session",
        description=f"Our {training_type} training has now started, please may all attendees join the game via the button below.",
        color=0x2b2d31
    )
    
    # Convert time to Discord timestamp format
    today = datetime.now().date()
    start_datetime = datetime.combine(today, datetime.strptime(start_time, "%H:%M").time())
    end_datetime = datetime.combine(today, datetime.strptime(end_time, "%H:%M").time())
    
    # If end time is before start time, assume it's next day
    if end_datetime <= start_datetime:
        end_datetime += timedelta(days=1)
    
    # Convert to Unix timestamp
    start_timestamp = int(start_datetime.timestamp())
    end_timestamp = int(end_datetime.timestamp())
    
    embed.add_field(
        name="",
        value=f"**Host**: {host_mention}\n**Start Time**: <t:{start_timestamp}:t>\n**End Time**: <t:{end_timestamp}:t>",
        inline=False
    )
    
    embed.set_footer(text=f"Session ID: {training_id}")
    embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")

    
    return embed

async def training_start_command(interaction: discord.Interaction, training_type: str, start_time: str, end_time: str):
    """Handle the training start command"""
    
    # Check if user has staff role
    staff_role = discord.utils.get(interaction.user.roles, id=config.STAFF_ROLE_ID)
    if not staff_role:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    
    # Validate time formats
    start_valid, start_error = validate_time_format(start_time)
    if not start_valid:
        await interaction.response.send_message(f"Start time error: {start_error}", ephemeral=True)
        return
    
    end_valid, end_error = validate_time_format(end_time)
    if not end_valid:
        await interaction.response.send_message(f"End time error: {end_error}", ephemeral=True)
        return
    
    # Check if end time is after start time
    try:
        start_dt = datetime.strptime(start_time, "%H:%M")
        end_dt = datetime.strptime(end_time, "%H:%M")
        
        # If end time is before start time, assume it's next day
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)
        
    except ValueError:
        await interaction.response.send_message("Invalid time format. Use HH:MM format.", ephemeral=True)
        return
    
    # Generate training ID
    training_id = generate_training_id()
    
    # Create embed
    embed = create_training_embed(training_type, start_time, end_time, interaction.user.mention, training_id)
    
    # Get training channel
    training_channel = interaction.guild.get_channel(config.TRAINING_CHANNEL_ID)
    if not training_channel:
        await interaction.response.send_message("Training channel not found.", ephemeral=True)
        return
    
    # Send embed to training channel
    message = await training_channel.send(embed=embed)
    
    # Store training session data in memory
    active_trainings[training_id] = {
        "type": training_type,
        "start_time": start_time,
        "end_time": end_time,
        "host": interaction.user.id,
        "host_mention": interaction.user.mention,
        "message": message,
        "status": "active",
        "created_at": datetime.now().isoformat()
    }
    
    await interaction.response.send_message(f"Training session started! Training ID: `{training_id}`", ephemeral=True)

def setup(bot):
    @bot.tree.command(name="training_start", description="Start a new training session")
    @app_commands.describe(
        training_type="Type of training to start",
        start_time="Start time in HH:MM format (5-minute intervals)",
        end_time="End time in HH:MM format (5-minute intervals)"
    )
    @app_commands.choices(training_type=[
        app_commands.Choice(name="Store Colleague", value="Store Colleague"),
        app_commands.Choice(name="Security", value="Security")
    ])
    async def training_start(
        interaction: discord.Interaction, 
        training_type: str,
        start_time: str,
        end_time: str
    ):
        await training_start_command(interaction, training_type, start_time, end_time)