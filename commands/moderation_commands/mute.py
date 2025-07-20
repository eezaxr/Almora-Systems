import discord
from discord.ext import commands
import config
import json
import os
from datetime import datetime, timezone, timedelta
import asyncio

def load_mutes():
    """Load mutes from JSON file"""
    if os.path.exists('data/mutes.json'):
        with open('data/mutes.json', 'r') as f:
            return json.load(f)
    return {}

def save_mutes(mutes_data):
    """Save mutes to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open('data/mutes.json', 'w') as f:
        json.dump(mutes_data, f, indent=2)

def parse_duration(duration_str):
    """Parse duration string like '1h', '30m', '1d' into seconds"""
    if not duration_str:
        return None
    
    duration_str = duration_str.lower()
    multipliers = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
        'w': 604800
    }
    
    for suffix, multiplier in multipliers.items():
        if duration_str.endswith(suffix):
            try:
                number = int(duration_str[:-1])
                return number * multiplier
            except ValueError:
                return None
    
    # Try to parse as just a number (assume minutes)
    try:
        return int(duration_str) * 60
    except ValueError:
        return None

def format_duration(seconds):
    """Format seconds into readable duration"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds//60}m"
    elif seconds < 86400:
        return f"{seconds//3600}h {(seconds%3600)//60}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"

def setup(bot):
    @bot.command(name='mute')
    async def mute_user(ctx, member: discord.Member, duration=None, *, reason="No reason provided"):
        """Mute a user for a specified duration"""
        # Check if user has moderation role
        if not any(role.id == config.MODERATION_ROLE_ID for role in ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        
        # Check if trying to mute themselves
        if member == ctx.author:
            await ctx.send("You cannot mute yourself.")
            return
        
        # Check if trying to mute a user with higher or equal role
        if member.top_role >= ctx.author.top_role:
            await ctx.send("You cannot mute a user with equal or higher permissions.")
            return
        
        # Check if trying to mute the bot
        if member == bot.user:
            await ctx.send("I cannot mute myself.")
            return
        
        # Parse duration
        duration_seconds = None
        if duration:
            duration_seconds = parse_duration(duration)
            if duration_seconds is None:
                await ctx.send("Invalid duration format. Use formats like: 1h, 30m, 2d, 1w")
                return
            if duration_seconds > 2419200:  # 28 days max
                await ctx.send("Mute duration cannot exceed 28 days.")
                return
        
        try:
            # Load existing mutes
            mutes_data = load_mutes()
            
            # Create timeout duration
            until = None
            if duration_seconds:
                until = discord.utils.utcnow() + timedelta(seconds=duration_seconds)
            
            # Apply timeout
            await member.timeout(until, reason=f"{reason} - Muted by {ctx.author}")
            
            # Create mute record
            mute_id = str(len(mutes_data) + 1)
            mute_record = {
                'user_id': member.id,
                'user_name': str(member),
                'moderator_id': ctx.author.id,
                'moderator_name': str(ctx.author),
                'reason': reason,
                'duration': duration_seconds,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'expires_at': until.isoformat() if until else None,
                'guild_id': ctx.guild.id,
                'active': True
            }
            
            # Save mute record
            mutes_data[mute_id] = mute_record
            save_mutes(mutes_data)
            
            # Try to DM the user
            try:
                dm_embed = discord.Embed(
                    title="<:Cross:1393269948700426341> You Have Been Muted",
                    color=0xFFFFFF,
                    timestamp=discord.utils.utcnow()
                )
                dm_embed.add_field(name="Server", value=ctx.guild.name, inline=True)
                dm_embed.add_field(name="Moderator", value=ctx.author.display_name, inline=True)
                if duration_seconds:
                    dm_embed.add_field(name="Duration", value=format_duration(duration_seconds), inline=True)
                else:
                    dm_embed.add_field(name="Duration", value="Permanent", inline=True)
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
                
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # User has DMs disabled
            
            # Send confirmation
            success_embed = discord.Embed(
                title="<:Tick:1393269945500045473> User Muted",
                color=0xFFFFFF,
                timestamp=discord.utils.utcnow()
            )
            success_embed.add_field(name="User", value=f"{member.mention} ({member})", inline=True)
            success_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            if duration_seconds:
                success_embed.add_field(name="Duration", value=format_duration(duration_seconds), inline=True)
                success_embed.add_field(name="Expires", value=f"<t:{int(until.timestamp())}:R>", inline=True)
            else:
                success_embed.add_field(name="Duration", value="Permanent", inline=True)
            success_embed.add_field(name="Reason", value=reason, inline=False)
            success_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
            
            await ctx.send(embed=success_embed)
            
            # Log to moderation channel
            mod_channel = bot.get_channel(config.MODERATION_CHANNEL_ID)
            if mod_channel:
                log_embed = discord.Embed(
                    title="<:Cross:1393269948700426341> User Muted",
                    color=0xFFFFFF,
                    timestamp=discord.utils.utcnow()
                )
                log_embed.add_field(name="User", value=f"{member.mention} ({member})", inline=True)
                log_embed.add_field(name="User ID", value=member.id, inline=True)
                log_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
                log_embed.add_field(name="Channel", value=ctx.channel.mention, inline=True)
                log_embed.add_field(name="Mute ID", value=mute_id, inline=True)
                if duration_seconds:
                    log_embed.add_field(name="Duration", value=format_duration(duration_seconds), inline=True)
                    log_embed.add_field(name="Expires", value=f"<t:{int(until.timestamp())}:R>", inline=True)
                else:
                    log_embed.add_field(name="Duration", value="Permanent", inline=True)
                log_embed.add_field(name="Reason", value=reason, inline=False)
                log_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
                
                await mod_channel.send(embed=log_embed)
        
        except discord.Forbidden:
            await ctx.send("I don't have permission to mute this user.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    @bot.command(name='unmute')
    async def unmute_user(ctx, member: discord.Member, *, reason="No reason provided"):
        """Unmute a user"""
        # Check if user has moderation role
        if not any(role.id == config.MODERATION_ROLE_ID for role in ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        
        try:
            # Remove timeout
            await member.timeout(None, reason=f"{reason} - Unmuted by {ctx.author}")
            
            # Update mute records
            mutes_data = load_mutes()
            for mute_id, mute_record in mutes_data.items():
                if mute_record['user_id'] == member.id and mute_record.get('active', True):
                    mute_record['active'] = False
                    mute_record['unmuted_by'] = ctx.author.id
                    mute_record['unmuted_at'] = datetime.now(timezone.utc).isoformat()
                    mute_record['unmute_reason'] = reason
            save_mutes(mutes_data)
            
            # Send confirmation
            success_embed = discord.Embed(
                title="<:Tick:1393269945500045473> User Unmuted",
                color=0xFFFFFF,
                timestamp=discord.utils.utcnow()
            )
            success_embed.add_field(name="User", value=f"{member.mention} ({member})", inline=True)
            success_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            success_embed.add_field(name="Reason", value=reason, inline=False)
            success_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
            
            await ctx.send(embed=success_embed)
            
            # Log to moderation channel
            mod_channel = bot.get_channel(config.MODERATION_CHANNEL_ID)
            if mod_channel:
                log_embed = discord.Embed(
                    title="<:Tick:1393269945500045473> User Unmuted",
                    color=0xFFFFFF,
                    timestamp=discord.utils.utcnow()
                )
                log_embed.add_field(name="User", value=f"{member.mention} ({member})", inline=True)
                log_embed.add_field(name="User ID", value=member.id, inline=True)
                log_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
                log_embed.add_field(name="Channel", value=ctx.channel.mention, inline=True)
                log_embed.add_field(name="Reason", value=reason, inline=False)
                log_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
                
                await mod_channel.send(embed=log_embed)
        
        except discord.Forbidden:
            await ctx.send("I don't have permission to unmute this user.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")