import discord
from discord.ext import commands
from discord import app_commands
import config
from commands.training_commands.training_start import active_trainings
from datetime import datetime, timedelta

async def training_end_command(interaction: discord.Interaction, training_id: str):
    """Handle the training end command"""
    # Check if user has staff role
    staff_role = discord.utils.get(interaction.user.roles, id=config.STAFF_ROLE_ID)
    if not staff_role:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    # Check if training exists
    training_id = training_id.upper()
    if training_id not in active_trainings:
        await interaction.response.send_message("Training ID not found or training is not active.", ephemeral=True)
        return

    training_data = active_trainings[training_id]
    
    # Check if user is the host or has staff permissions
    if training_data['host'] != interaction.user.id and not staff_role:
        await interaction.response.send_message("You can only end trainings that you started.", ephemeral=True)
        return

    # Check if training is still active
    if training_data['status'] != 'active':
        await interaction.response.send_message("This training is no longer active.", ephemeral=True)
        return

    # Create ended embed
    embed = discord.Embed(
        title=f"<:Retail:1393269955260055702> Almora {training_data['type']} Training Ended",
        description=f"Our {training_data['type']} training has now ended, well done to everyone who has passed.",
        color=0x2b2d31
    )
    
    # Get host user
    host_user = interaction.guild.get_member(training_data['host'])
    host_mention = host_user.mention if host_user else "Unknown"
    
    # Convert time to Discord timestamp format
    today = datetime.now().date()
    start_datetime = datetime.combine(today, datetime.strptime(training_data['start_time'], "%H:%M").time())
    end_datetime = datetime.combine(today, datetime.strptime(training_data['end_time'], "%H:%M").time())
    
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


    # Update the original message
    try:
        await training_data['message'].edit(embed=embed)
    except:
        await interaction.response.send_message("Could not update the original training message.", ephemeral=True)
        return

    # Update training status in memory
    active_trainings[training_id]['status'] = 'ended'
    
    await interaction.response.send_message(f"Training {training_id} has been ended successfully!", ephemeral=True)

def setup(bot):
    @bot.tree.command(name="training_end", description="End an active training session")
    @app_commands.describe(
        training_id="Training ID to end (generated when starting a session)"
    )
    async def training_end(
        interaction: discord.Interaction, 
        training_id: str
    ):
        await training_end_command(interaction, training_id)