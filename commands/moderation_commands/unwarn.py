import discord
from discord.ext import commands
import config
import json
import os
from datetime import datetime, timezone

def load_warnings():
    """Load warnings from JSON file"""
    if os.path.exists('data/warnings.json'):
        with open('data/warnings.json', 'r') as f:
            return json.load(f)
    return {}

def save_warnings(warnings_data):
    """Save warnings to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open('data/warnings.json', 'w') as f:
        json.dump(warnings_data, f, indent=2)

def load_unwarns():
    """Load unwarns from JSON file"""
    if os.path.exists('data/unwarns.json'):
        with open('data/unwarns.json', 'r') as f:
            return json.load(f)
    return {}

def save_unwarns(unwarns_data):
    """Save unwarns to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open('data/unwarns.json', 'w') as f:
        json.dump(unwarns_data, f, indent=2)

def setup(bot):
    @bot.command(name='unwarn')
    async def unwarn_user(ctx, warning_id: str, *, reason="No reason provided"):
        """Remove a warning from a user"""
        # Check if user has moderation role
        if not any(role.id == config.MODERATION_ROLE_ID for role in ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        
        try:
            # Load warnings data
            warnings_data = load_warnings()
            
            # Check if warning exists
            if warning_id not in warnings_data:
                await ctx.send(f"Warning with ID `{warning_id}` not found.")
                return
            
            warning_record = warnings_data[warning_id]
            
            # Get the user from the warning record
            try:
                user = bot.get_user(warning_record['user_id'])
                if user is None:
                    user = await bot.fetch_user(warning_record['user_id'])
            except:
                user = None
            
            # Load existing unwarns
            unwarns_data = load_unwarns()
            
            # Create unwarn record
            unwarn_id = str(len(unwarns_data) + 1)
            unwarn_record = {
                'warning_id': warning_id,
                'user_id': warning_record['user_id'],
                'user_name': warning_record['user_name'],
                'original_reason': warning_record['reason'],
                'moderator_id': ctx.author.id,
                'moderator_name': str(ctx.author),
                'reason': reason,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'guild_id': ctx.guild.id
            }
            
            # Save unwarn record
            unwarns_data[unwarn_id] = unwarn_record
            save_unwarns(unwarns_data)
            
            # Remove the warning
            del warnings_data[warning_id]
            save_warnings(warnings_data)
            
            # Try to DM the user
            if user:
                try:
                    dm_embed = discord.Embed(
                        title="<:Tick:1393269945500045473> Warning Removed",
                        color=0xFFFFFF,
                        timestamp=discord.utils.utcnow()
                    )
                    dm_embed.add_field(name="Server", value=ctx.guild.name, inline=True)
                    dm_embed.add_field(name="Moderator", value=ctx.author.display_name, inline=True)
                    dm_embed.add_field(name="Warning ID", value=warning_id, inline=True)
                    dm_embed.add_field(name="Original Reason", value=warning_record['reason'], inline=False)
                    dm_embed.add_field(name="Removal Reason", value=reason, inline=False)
                    dm_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
                    
                    await user.send(embed=dm_embed)
                except discord.Forbidden:
                    pass  # User has DMs disabled
            
            # Send confirmation
            success_embed = discord.Embed(
                title="<:Tick:1393269945500045473> Warning Removed",
                color=0xFFFFFF,
                timestamp=discord.utils.utcnow()
            )
            success_embed.add_field(name="Warning ID", value=warning_id, inline=True)
            success_embed.add_field(name="User", value=warning_record['user_name'], inline=True)
            success_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            success_embed.add_field(name="Original Reason", value=warning_record['reason'], inline=False)
            success_embed.add_field(name="Removal Reason", value=reason, inline=False)
            success_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
            
            await ctx.send(embed=success_embed)
            
            # Log to moderation channel
            mod_channel = bot.get_channel(config.MODERATION_CHANNEL_ID)
            if mod_channel:
                log_embed = discord.Embed(
                    title="<:Tick:1393269945500045473> Warning Removed",
                    color=0xFFFFFF,
                    timestamp=discord.utils.utcnow()
                )
                log_embed.add_field(name="Warning ID", value=warning_id, inline=True)
                log_embed.add_field(name="User", value=warning_record['user_name'], inline=True)
                log_embed.add_field(name="User ID", value=warning_record['user_id'], inline=True)
                log_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
                log_embed.add_field(name="Channel", value=ctx.channel.mention, inline=True)
                log_embed.add_field(name="Unwarn ID", value=unwarn_id, inline=True)
                log_embed.add_field(name="Original Reason", value=warning_record['reason'], inline=False)
                log_embed.add_field(name="Removal Reason", value=reason, inline=False)
                log_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
                
                await mod_channel.send(embed=log_embed)
                
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")