import discord
from discord.ext import commands
from discord import app_commands
import config
from commands.shift_commands.shift_start import active_shifts

def setup(bot):
    @bot.tree.command(name="shift-cancel", description="Cancel an active shift")
    @app_commands.describe(shift_id="The ID of the shift to cancel")
    async def shift_cancel(interaction: discord.Interaction, shift_id: str):
        # Check if user has staff role
        staff_role = discord.utils.get(interaction.user.roles, id=config.STAFF_ROLE_ID)
        if not staff_role:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        # Check if shift exists
        shift_id = shift_id.upper()
        if shift_id not in active_shifts:
            await interaction.response.send_message("Shift ID not found or shift is not active.", ephemeral=True)
            return

        shift_data = active_shifts[shift_id]
        
        # Check if user is the host or has staff permissions
        if shift_data['host'] != interaction.user.id and not staff_role:
            await interaction.response.send_message("You can only cancel shifts that you started.", ephemeral=True)
            return

        # Check if shift is still active
        if shift_data['status'] != 'active':
            await interaction.response.send_message("This shift is no longer active.", ephemeral=True)
            return

        # Create cancelled embed
        embed = discord.Embed(
            title="<:Shifts:1393545049832292482> Almora Shift Cancelled",
            description=f"Our {shift_data['end_time']} shift was cancelled, we're sorry for any inconveniences\ncaused. Our next session will be",
            color=0x4A4A4A
        )
        
        # Get host user
        host_user = bot.get_user(shift_data['host'])
        host_mention = host_user.mention if host_user else "Unknown"
        
        # Convert time to Discord timestamp format
        from datetime import datetime, time
        import time as time_module
        
        # Get today's date and create datetime objects
        today = datetime.now().date()
        start_datetime = datetime.combine(today, datetime.strptime(shift_data['start_time'], "%H:%M").time())
        end_datetime = datetime.combine(today, datetime.strptime(shift_data['end_time'], "%H:%M").time())
        
        # Convert to Unix timestamp
        start_timestamp = int(start_datetime.timestamp())
        end_timestamp = int(end_datetime.timestamp())

        embed.add_field(
            name="",
            value=f"**Host**: {host_mention}\n**Start Time**: <t:{start_timestamp}:t>\n**End Time**: <t:{end_timestamp}:t>",
            inline=False
        )
        embed.set_footer(text=f"Session ID: {shift_id}")
        embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")

        # Update the original message (without buttons)
        try:
            await shift_data['message'].edit(embed=embed)
        except:
            await interaction.response.send_message("Could not update the original shift message.", ephemeral=True)
            return

        # Update shift status
        active_shifts[shift_id]['status'] = 'cancelled'
        
        await interaction.response.send_message(f"Shift {shift_id} has been cancelled successfully!", ephemeral=True)