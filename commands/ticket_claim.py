
import discord
from discord.ext import commands
import config
from utils.ticket_utils import is_ticket_channel, has_staff_permissions

def setup(bot):
    @bot.command(name='claim')
    async def claim_ticket(ctx):
        """Claim the current ticket"""
        
        if not is_ticket_channel(ctx.channel):
            await ctx.send("This command can only be used in ticket channels.")
            return
        
        if not has_staff_permissions(ctx.author):
            await ctx.send("Only staff members can claim tickets.")
            return
        
        # Check if ticket is already claimed
        topic = ctx.channel.topic or ""
        if "Claimed by:" in topic:
            await ctx.send("This ticket is already claimed!")
            return
        
        # Update channel topic to show who claimed it
        new_topic = f"Claimed by: {ctx.author.display_name}"
        await ctx.channel.edit(topic=new_topic)
        
        embed = discord.Embed(
            title="<:Tick:1393269945500045473> Ticket Claimed",
            description=f"This ticket has been claimed by {ctx.author.mention}",
            color=0xFFFFFF
        )
        embed.set_image(url="https://media.discordapp.net/attachments/1301667213131907170/1393267567925137478/Banner2.png?ex=68728d09&is=68713b89&hm=3848c521166c97401f3eaac93d3ed9b0901279cab8ae433b4a7a48600d1a000e&=&format=webp&quality=lossless&width=1318&height=63")

        await ctx.send(embed=embed)

    @bot.command(name='unclaim')
    async def unclaim_ticket(ctx):
        """Unclaim the current ticket"""
        
        if not is_ticket_channel(ctx.channel):
            await ctx.send("This command can only be used in ticket channels.")
            return
        
        if not has_staff_permissions(ctx.author):
            await ctx.send("Only staff members can unclaim tickets.")
            return
        
        # Check if ticket is claimed
        topic = ctx.channel.topic or ""
        if "Claimed by:" not in topic:
            await ctx.send("This ticket is not currently claimed!")
            return
        
        # Remove claim from topic
        await ctx.channel.edit(topic="")
        
        embed = discord.Embed(
            title="<:Cross:1393269948700426341> Ticket Unclaimed",
            description=f"This ticket has been unclaimed by {ctx.author.mention}",
            color=0xFFFFFF
        )
        
        await ctx.send(embed=embed)
