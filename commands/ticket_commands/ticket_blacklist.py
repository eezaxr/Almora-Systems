import discord
from discord.ext import commands
import json
import os

# File to store blacklisted users
BLACKLIST_FILE = "data/ticket_blacklist.json"

def load_blacklist():
    """Load the blacklist from file"""
    if not os.path.exists(BLACKLIST_FILE):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(BLACKLIST_FILE), exist_ok=True)
        return {}
    
    try:
        with open(BLACKLIST_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_blacklist(blacklist_data):
    """Save the blacklist to file"""
    os.makedirs(os.path.dirname(BLACKLIST_FILE), exist_ok=True)
    with open(BLACKLIST_FILE, 'w') as f:
        json.dump(blacklist_data, f, indent=2)

def is_user_blacklisted(user_id, guild_id):
    """Check if a user is blacklisted from creating tickets"""
    blacklist = load_blacklist()
    guild_blacklist = blacklist.get(str(guild_id), {})
    return str(user_id) in guild_blacklist

def setup(bot):

    @bot.command(name='blacklist')
    async def blacklist_user(ctx, user: discord.Member = None, *, reason: str = "No reason provided"):
        """Blacklist a user from creating tickets"""
        
        # Check if user has permission (manage channels or admin)
        if not ctx.author.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="<:Cross:1393269948700426341> Permission Denied",
                description="You don't have permission to use this command!",
                color=0xFFFFFF
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
            await ctx.send(embed=embed)
            return

        if user is None:
            embed = discord.Embed(
                title="<:Cross:1393269948700426341> Invalid Usage",
                description="Please provide a user to blacklist.\n**Usage:** `!blacklist @user [reason]`",
                color=0xFFFFFF
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
            await ctx.send(embed=embed)
            return

        # Load current blacklist
        blacklist = load_blacklist()
        guild_id = str(ctx.guild.id)
        user_id = str(user.id)

        # Initialize guild blacklist if it doesn't exist
        if guild_id not in blacklist:
            blacklist[guild_id] = {}

        # Check if user is already blacklisted
        if user_id in blacklist[guild_id]:
            embed = discord.Embed(
                title="<:Warning:1393269985031487528> Already Blacklisted",
                description=f"{user.mention} is already blacklisted from creating tickets.",
                color=0xFFFFFF
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
            await ctx.send(embed=embed)
            return

        # Add user to blacklist
        blacklist[guild_id][user_id] = {
            "username": user.name,
            "discriminator": user.discriminator,
            "reason": reason,
            "blacklisted_by": ctx.author.id,
            "blacklisted_at": ctx.message.created_at.isoformat()
        }

        # Save blacklist
        save_blacklist(blacklist)

        # Send success message
        embed = discord.Embed(
            title="<:Tick:1393269945500045473> User Blacklisted",
            description=f"{user.mention} has been blacklisted from creating tickets.",
            color=0xFFFFFF
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Blacklisted By", value=ctx.author.mention, inline=True)
        embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
        await ctx.send(embed=embed)

    @bot.command(name='unblacklist')
    async def unblacklist_user(ctx, user: discord.Member = None):
        """Remove a user from the ticket blacklist"""
        
        # Check if user has permission
        if not ctx.author.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="<:Cross:1393269948700426341> Permission Denied",
                description="You don't have permission to use this command!",
                color=0xFFFFFF
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
            await ctx.send(embed=embed)
            return

        if user is None:
            embed = discord.Embed(
                title="<:Cross:1393269948700426341> Invalid Usage",
                description="Please provide a user to unblacklist.\n**Usage:** `!unblacklist @user`",
                color=0xFFFFFF
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
            await ctx.send(embed=embed)
            return

        # Load current blacklist
        blacklist = load_blacklist()
        guild_id = str(ctx.guild.id)
        user_id = str(user.id)

        # Check if guild or user exists in blacklist
        if guild_id not in blacklist or user_id not in blacklist[guild_id]:
            embed = discord.Embed(
                title="<:Warning:1393269985031487528> Not Blacklisted",
                description=f"{user.mention} is not currently blacklisted from creating tickets.",
                color=0xFFFFFF
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
            await ctx.send(embed=embed)
            return

        # Remove user from blacklist
        del blacklist[guild_id][user_id]

        # Clean up empty guild entries
        if not blacklist[guild_id]:
            del blacklist[guild_id]

        # Save blacklist
        save_blacklist(blacklist)

        # Send success message
        embed = discord.Embed(
            title="<:Tick:1393269945500045473> User Unblacklisted",
            description=f"{user.mention} has been removed from the ticket blacklist.",
            color=0xFFFFFF
        )
        embed.add_field(name="Unblacklisted By", value=ctx.author.mention, inline=True)
        embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
        await ctx.send(embed=embed)

    @bot.command(name='blacklist_list')
    async def list_blacklisted(ctx):
        """List all blacklisted users in the server"""
        
        # Check if user has permission
        if not ctx.author.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="<:Cross:1393269948700426341> Permission Denied",
                description="You don't have permission to use this command!",
                color=0xFFFFFF
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
            await ctx.send(embed=embed)
            return

        blacklist = load_blacklist()
        guild_id = str(ctx.guild.id)

        if guild_id not in blacklist or not blacklist[guild_id]:
            embed = discord.Embed(
                title="<:Team:1393269975753691276> Ticket Blacklist",
                description="No users are currently blacklisted from creating tickets.",
                color=0xFFFFFF
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title="<:Team:1393269975753691276> Ticket Blacklist",
            description="The following users are blacklisted from creating tickets:",
            color=0xFFFFFF
        )

        guild_blacklist = blacklist[guild_id]
        for user_id, data in guild_blacklist.items():
            user = ctx.guild.get_member(int(user_id))
            username = user.mention if user else f"{data['username']}#{data['discriminator']}"
            
            embed.add_field(
                name=username,
                value=f"**Reason:** {data['reason']}\n**Blacklisted by:** <@{data['blacklisted_by']}>",
                inline=False
            )

        embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
        await ctx.send(embed=embed)