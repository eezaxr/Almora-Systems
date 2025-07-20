import discord
from discord.ext import commands
import config
import json
import os
from datetime import datetime, timezone

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

def load_unmutes():
    """Load unmutes from JSON file"""
    if os.path.exists('data/unmutes.json'):
        with open('data/unmutes.json', 'r') as f:
            return json.load(f)
    return {}

def save_unmutes(unmutes_data):
    """Save unmutes to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open('data/unmutes.json', 'w') as f:
        json.dump(unmutes_data, f, indent=2)

def setup(bot):
    @bot.command(name='unmute')
    async def unmute_user(ctx, member: discord.Member, *, reason="No reason provided"):
        """Unmute a user in the server"""
        # Check if user has moderation role
        if not any(role.id == config.MODERATION_ROLE_ID for role in ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        
        # Check if trying to unmute themselves
        if member == ctx.author:
            await ctx.send("You cannot unmute yourself.")
            return
        
        # Check if trying to unmute the bot
        if member == bot.user:
            await ctx.send("I cannot unmute myself.")
            return
        
        try:
            # Check if user is actually muted (has timeout)
            if member.timed_out_until is None:
                await ctx.send(f"{member.mention} is not currently muted.")
                return
            
            # Load existing unmutes
            unmutes_data = load_unmutes()
            
            # Create unmute record
            unmute_id = str(len(unmutes_data) + 1)
            unmute_record = {
                'user_id': member.id,
                'user_name': str(member),
                'moderator_id': ctx.author.id,
                'moderator_name': str(ctx.author),
                'reason': reason,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'guild_id': ctx.guild.id
            }
            
            # Save unmute record
            unmutes_data[unmute_id] = unmute_record
            save_unmutes(unmutes_data)
            
            # Try to DM the user before unmuting
            try:
                dm_embed = discord.Embed(
                    title="<:Tick:1393269945500045473> You Have Been Unmuted",
                    color=0xFFFFFF,
                    timestamp=discord.utils.utcnow()
                )
                dm_embed.add_field(name="Server", value=ctx.guild.name, inline=True)
                dm_embed.add_field(name="Moderator", value=ctx.author.display_name, inline=True)
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
                
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # User has DMs disabled
            
            # Remove timeout (unmute the user)
            await member.edit(timed_out_until=None, reason=f"{reason} - Unmuted by {ctx.author}")
            
            # Send confirmation
            success_embed = discord.Embed(
                title="<:Tick:1393269945500045473> User Unmuted",
                color=0xFFFFFF,
                timestamp=discord.utils.utcnow()
            )
            success_embed.add_field(name="User", value=f"{member.mention} ({member})", inline=True)
            success_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            success_embed.add_field(name="Unmute ID", value=unmute_id, inline=True)
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
                log_embed.add_field(name="Unmute ID", value=unmute_id, inline=True)
                log_embed.add_field(name="Reason", value=reason, inline=False)
                log_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
                
                await mod_channel.send(embed=log_embed)
        
        except discord.Forbidden:
            await ctx.send("I don't have permission to unmute this user.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")