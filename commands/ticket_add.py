
import discord
from discord.ext import commands
import config
from utils.ticket_utils import is_ticket_channel, has_staff_permissions

def setup(bot):
    @bot.command(name='add')
    async def add_to_ticket(ctx, member: discord.Member):
        """Add a user to the current ticket"""
        
        if not is_ticket_channel(ctx.channel):
            await ctx.send("This command can only be used in ticket channels.")
            return
        
        if not has_staff_permissions(ctx.author):
            await ctx.send("Only staff members can add users to tickets.")
            return
        
        # Add user to channel
        overwrite = discord.PermissionOverwrite(
            read_messages=True,
            send_messages=True,
            attach_files=True,
            embed_links=True
        )
        
        await ctx.channel.set_permissions(member, overwrite=overwrite)
        
        embed = discord.Embed(
            title="<:Tick:1393269945500045473> User Added",
            description=f"{member.mention} has been added to this ticket!",
            color=0xFFFFFF
        )
        embed.set_image(url="https://media.discordapp.net/attachments/1301667213131907170/1393267567925137478/Banner2.png?ex=68728d09&is=68713b89&hm=3848c521166c97401f3eaac93d3ed9b0901279cab8ae433b4a7a48600d1a000e&=&format=webp&quality=lossless&width=1318&height=63")


        await ctx.send(embed=embed)
