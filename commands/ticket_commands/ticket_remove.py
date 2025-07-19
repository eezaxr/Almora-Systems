
import discord
from discord.ext import commands
import config
from utils.ticket_utils import is_ticket_channel, has_staff_permissions

def setup(bot):
    @bot.command(name='remove')
    async def remove_from_ticket(ctx, member: discord.Member):
        """Remove a user from the current ticket"""
        
        if not is_ticket_channel(ctx.channel):
            await ctx.send("This command can only be used in ticket channels.")
            return
        
        if not has_staff_permissions(ctx.author):
            await ctx.send("Only staff members can remove users from tickets.")
            return
        
        # Remove user from channel
        await ctx.channel.set_permissions(member, overwrite=None)
        
        embed = discord.Embed(
            title="<:Cross:1393269948700426341> User Removed",
            description=f"{member.mention} has been removed from this ticket.",
            color=0xFFFFFF
        )
        
        await ctx.send(embed=embed)
