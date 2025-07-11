
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
        embed.set_image(url="https://media.discordapp.net/attachments/1301667213131907170/1393267567925137478/Banner2.png?ex=68728d09&is=68713b89&hm=3848c521166c97401f3eaac93d3ed9b0901279cab8ae433b4a7a48600d1a000e&=&format=webp&quality=lossless&width=1318&height=63")
        
        # Send to all ticket channels
        sent_count = 0
        for channel in ticket_channels:
            try:
                await channel.send(embed=embed)
                sent_count += 1
            except discord.Forbidden:
                continue  # Skip channels where bot doesn't have permission
        
        await ctx.send(f"Patience message sent to {sent_count} ticket channels.")
