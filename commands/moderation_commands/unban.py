import discord
from discord.ext import commands
import config
import json
import os
from datetime import datetime, timezone

def load_bans():
    """Load bans from JSON file"""
    if os.path.exists('data/bans.json'):
        with open('data/bans.json', 'r') as f:
            return json.load(f)
    return {}

def save_bans(bans_data):
    """Save bans to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open('data/bans.json', 'w') as f:
        json.dump(bans_data, f, indent=2)

def load_unbans():
    """Load unbans from JSON file"""
    if os.path.exists('data/unbans.json'):
        with open('data/unbans.json', 'r') as f:
            return json.load(f)
    return {}

def save_unbans(unbans_data):
    """Save unbans to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open('data/unbans.json', 'w') as f:
        json.dump(unbans_data, f, indent=2)

def setup(bot):
    @bot.command(name='unban')
    async def unban_user(ctx, user_id: int, *, reason="No reason provided"):
        """Unban a user from the server"""
        # Check if user has moderation role
        if not any(role.id == config.MODERATION_ROLE_ID for role in ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        
        try:
            # Get banned users
            banned_users = [entry async for entry in ctx.guild.bans(limit=2000)]
            banned_user = None
            
            for ban_entry in banned_users:
                if ban_entry.user.id == user_id:
                    banned_user = ban_entry.user
                    break
            
            if not banned_user:
                await ctx.send(f"User with ID {user_id} is not banned from this server.")
                return
            
            # Load existing unbans
            unbans_data = load_unbans()
            
            # Create unban record
            unban_id = str(len(unbans_data) + 1)
            unban_record = {
                'user_id': user_id,
                'user_name': str(banned_user),
                'moderator_id': ctx.author.id,
                'moderator_name': str(ctx.author),
                'reason': reason,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'guild_id': ctx.guild.id
            }
            
            # Save unban record
            unbans_data[unban_id] = unban_record
            save_unbans(unbans_data)
            
            # Unban the user
            await ctx.guild.unban(banned_user, reason=f"{reason} - Unbanned by {ctx.author}")
            
            # Send confirmation
            success_embed = discord.Embed(
                title="<:Tick:1393269945500045473> User Unbanned",
                color=0xFFFFFF,
                timestamp=discord.utils.utcnow()
            )
            success_embed.add_field(name="User", value=f"{banned_user.mention} ({banned_user})", inline=True)
            success_embed.add_field(name="User ID", value=user_id, inline=True)
            success_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            success_embed.add_field(name="Reason", value=reason, inline=False)
            success_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
            
            await ctx.send(embed=success_embed)
            
            # Log to moderation channel
            mod_channel = bot.get_channel(config.MODERATION_CHANNEL_ID)
            if mod_channel:
                log_embed = discord.Embed(
                    title="<:Tick:1393269945500045473> User Unbanned",
                    color=0xFFFFFF,
                    timestamp=discord.utils.utcnow()
                )
                log_embed.add_field(name="User", value=f"{banned_user.mention} ({banned_user})", inline=True)
                log_embed.add_field(name="User ID", value=user_id, inline=True)
                log_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
                log_embed.add_field(name="Channel", value=ctx.channel.mention, inline=True)
                log_embed.add_field(name="Unban ID", value=unban_id, inline=True)
                log_embed.add_field(name="Reason", value=reason, inline=False)
                log_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
                
                await mod_channel.send(embed=log_embed)
            
        except discord.Forbidden:
            await ctx.send("I don't have permission to unban users.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")