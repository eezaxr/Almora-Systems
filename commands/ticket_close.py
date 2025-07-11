import discord
from discord.ext import commands
import config
from datetime import timedelta
from utils.ticket_utils import is_ticket_channel, has_staff_permissions
from utils.transcript_utils import generate_transcript, get_ticket_info_from_channel

class TicketCloseView(discord.ui.View):
    def __init__(self, ctx, close_reason):
        super().__init__(timeout=30.0)
        self.ctx = ctx
        self.close_reason = close_reason
        self.responded = False
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success, emoji="<:Tick:1393269945500045473>")
    async def confirm_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("Only the command user can use this button.", ephemeral=True)
            return
        
        self.responded = True
        await interaction.response.send_message("Generating transcript and closing ticket...")
        
        # Get ticket information
        ticket_owner, claimed_by = get_ticket_info_from_channel(self.ctx.channel)
        
        # Get original ticket reason
        ticket_reason = "No reason provided"
        async for message in self.ctx.channel.history(limit=50, oldest_first=True):
            if message.embeds and "Support Ticket" in str(message.embeds[0].title):
                embed_desc = message.embeds[0].description
                if "**Reason:**" in embed_desc:
                    ticket_reason = embed_desc.split("**Reason:**")[1].split("\n")[0].strip()
                break
        
        # Generate transcript
        transcript = await generate_transcript(self.ctx.channel)
        
        # Log to log channel
        log_channel = self.ctx.guild.get_channel(config.LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="<:Cross:1393269948700426341> Ticket Closed",
                color=0xFFFFFF,
                timestamp=discord.utils.utcnow()
            )
            log_embed.add_field(name="Ticket Owner", value=ticket_owner.mention if ticket_owner else "Unknown", inline=True)
            log_embed.add_field(name="Closed By", value=self.ctx.author.mention, inline=True)
            log_embed.add_field(name="Claimed By", value=claimed_by if claimed_by else "Unclaimed", inline=True)
            log_embed.add_field(name="Channel", value=self.ctx.channel.name, inline=True)
            log_embed.add_field(name="Original Reason", value=ticket_reason, inline=True)
            log_embed.add_field(name="Close Reason", value=self.close_reason, inline=True)
            log_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
            
            await log_channel.send(embed=log_embed, file=transcript)
        
        # Send DM to ticket owner
        if ticket_owner:
            try:
                dm_embed = discord.Embed(
                    title="<:Cross:1393269948700426341> Your Ticket Has Been Closed",
                    color=0xFFFFFF,
                    timestamp=discord.utils.utcnow()
                )
                dm_embed.add_field(name="Server", value=self.ctx.guild.name, inline=True)
                dm_embed.add_field(name="Closed By", value=self.ctx.author.display_name, inline=True)
                dm_embed.add_field(name="Claimed By", value=claimed_by if claimed_by else "Unclaimed", inline=True)
                dm_embed.add_field(name="Close Reason", value=self.close_reason, inline=True)
                dm_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
                
                dm_transcript = await generate_transcript(self.ctx.channel)
                await ticket_owner.send(embed=dm_embed, file=dm_transcript)
            except discord.Forbidden:
                pass
        
        await interaction.followup.send("Ticket will be deleted in 3 seconds...")
        await discord.utils.sleep_until(discord.utils.utcnow() + timedelta(seconds=3))
        await self.ctx.channel.delete(reason=f"Ticket closed by {self.ctx.author} - {self.close_reason}")
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji="<:Cross:1393269948700426341>")
    async def cancel_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("Only the command user can use this button.", ephemeral=True)
            return
        
        self.responded = True
        await interaction.response.send_message("Ticket close cancelled.")
        self.stop()
    
    async def on_timeout(self):
        if not self.responded:
            # Disable all buttons
            for item in self.children:
                item.disabled = True
            
            # Try to edit the original message
            try:
                await self.message.edit(view=self)
                await self.ctx.send("Ticket close timed out.")
            except:
                pass

def setup(bot):
    @bot.command(name='close')
    async def close_ticket(ctx, *, reason=None):
        """Close the current ticket with an optional reason"""
        if not is_ticket_channel(ctx.channel):
            await ctx.send("This command can only be used in ticket channels.")
            return
        
        if not (ctx.channel.name == f"ticket-{ctx.author.name.lower()}" or has_staff_permissions(ctx.author)):
            await ctx.send("You don't have permission to close this ticket.")
            return
        
        close_reason = reason if reason else "No reason provided"
        
        embed = discord.Embed(
            title="<:Team:1393269975753691276> Close Ticket",
            description="Are you sure you want to close this ticket?",
            color=0xFFFFFF
        )
        
        if reason:
            embed.add_field(name="Close Reason", value=close_reason, inline=False)
        
        view = TicketCloseView(ctx, close_reason)
        message = await ctx.send(embed=embed, view=view)
        view.message = message  # Store message reference for timeout handling