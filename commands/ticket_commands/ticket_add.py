
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
        embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")


        await ctx.send(embed=embed)
