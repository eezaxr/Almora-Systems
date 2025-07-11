
import discord
from discord.ext import commands
import config
from utils.ticket_utils import has_staff_permissions

def setup(bot):
    @bot.command(name='patience')
    async def patience_command(ctx):
        """Send patience message to all ticket channels"""
        
        if not has_staff_permissions(ctx.author):
            await ctx.send("Only staff members can use this command.")
            return
        
        # Get all ticket channels
        ticket_channels = [channel for channel in ctx.guild.channels 
                          if isinstance(channel, discord.TextChannel) and channel.name.startswith("ticket-")]
        
        if not ticket_channels:
            await ctx.send("No ticket channels found.")
            return
        
        # Create the patience embed
        embed = discord.Embed(
            title="Please be patient",
            description="We're currently experiencing high ticket volume. Please be patient while we get to your ticket. We will respond as soon as possible",
            color=0xFFFFFF
        )
        embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
        
        # Send to all ticket channels
        sent_count = 0
        for channel in ticket_channels:
            try:
                await channel.send(embed=embed)
                sent_count += 1
            except discord.Forbidden:
                continue  # Skip channels where bot doesn't have permission
        
        await ctx.send(f"Patience message sent to {sent_count} ticket channels.")
