import discord
from discord.ext import commands
import config
import json
import os
from datetime import datetime, timezone

def load_lockdowns():
    """Load lockdowns from JSON file"""
    if os.path.exists('data/lockdowns.json'):
        with open('data/lockdowns.json', 'r') as f:
            return json.load(f)
    return {}

def save_lockdowns(lockdowns_data):
    """Save lockdowns to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open('data/lockdowns.json', 'w') as f:
        json.dump(lockdowns_data, f, indent=2)

def setup(bot):
    @bot.command(name='lockdown')
    async def lockdown_channel(ctx, channel: discord.TextChannel = None, *, reason="No reason provided"):
        """Lock down a channel"""
        # Check if user has moderation role
        if not any(role.id == config.MODERATION_ROLE_ID for role in ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        
        target_channel = channel or ctx.channel
        
        try:
            # Get the @everyone role
            everyone_role = ctx.guild.default_role
            
            # Store original permissions
            original_perms = target_channel.overwrites_for(everyone_role)
            
            # Load existing lockdowns
            lockdowns_data = load_lockdowns()
            
            # Create lockdown record
            lockdown_id = str(len(lockdowns_data) + 1)
            lockdown_record = {
                'channel_id': target_channel.id,
                'channel_name': target_channel.name,
                'moderator_id': ctx.author.id,
                'moderator_name': str(ctx.author),
                'reason': reason,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'guild_id': ctx.guild.id,
                'original_send_messages': original_perms.send_messages,
                'active': True
            }
            
            # Save lockdown record
            lockdowns_data[lockdown_id] = lockdown_record
            save_lockdowns(lockdowns_data)
            
            # Apply lockdown (deny send_messages for @everyone)
            await target_channel.set_permissions(
                everyone_role, 
                send_messages=False,
                reason=f"Channel locked down by {ctx.author} - {reason}"
            )
            
            # Send confirmation
            success_embed = discord.Embed(
                title="<:Cross:1393269948700426341> Channel Locked Down",
                color=0xFFFFFF,
                timestamp=discord.utils.utcnow()
            )
            success_embed.add_field(name="Channel", value=target_channel.mention, inline=True)
            success_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            success_embed.add_field(name="Lockdown ID", value=lockdown_id, inline=True)
            success_embed.add_field(name="Reason", value=reason, inline=False)
            success_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
            
            await ctx.send(embed=success_embed)
            
            # Send lockdown message to the locked channel if it's not the current channel
            if target_channel != ctx.channel:
                lockdown_notice = discord.Embed(
                    title="🔒 Channel Locked Down",
                    description=f"This channel has been locked down by {ctx.author.mention}",
                    color=0xFFFFFF,
                    timestamp=discord.utils.utcnow()
                )
                lockdown_notice.add_field(name="Reason", value=reason, inline=False)
                await target_channel.send(embed=lockdown_notice)
            
            # Log to moderation channel
            mod_channel = bot.get_channel(config.MODERATION_CHANNEL_ID)
            if mod_channel:
                log_embed = discord.Embed(
                    title="🔒 Channel Locked Down",
                    color=0xFFFFFF,
                    timestamp=discord.utils.utcnow()
                )
                log_embed.add_field(name="Channel", value=target_channel.mention, inline=True)
                log_embed.add_field(name="Channel ID", value=target_channel.id, inline=True)
                log_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
                log_embed.add_field(name="Command Channel", value=ctx.channel.mention, inline=True)
                log_embed.add_field(name="Lockdown ID", value=lockdown_id, inline=True)
                log_embed.add_field(name="Reason", value=reason, inline=False)
                log_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
                
                await mod_channel.send(embed=log_embed)
        
        except discord.Forbidden:
            await ctx.send("I don't have permission to modify this channel's permissions.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    @bot.command(name='unlockdown', aliases=['unlock'])
    async def unlock_channel(ctx, channel: discord.TextChannel = None, *, reason="No reason provided"):
        """Unlock a channel"""
        # Check if user has moderation role
        if not any(role.id == config.MODERATION_ROLE_ID for role in ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        
        target_channel = channel or ctx.channel
        
        try:
            # Load lockdowns
            lockdowns_data = load_lockdowns()
            
            # Find active lockdown for this channel
            lockdown_record = None
            lockdown_id = None
            for lid, record in lockdowns_data.items():
                if record['channel_id'] == target_channel.id and record.get('active', True):
                    lockdown_record = record
                    lockdown_id = lid
                    break
            
            if not lockdown_record:
                await ctx.send("This channel is not currently locked down.")
                return
            
            # Get the @everyone role
            everyone_role = ctx.guild.default_role
            
            # Restore original permissions
            original_send_messages = lockdown_record.get('original_send_messages')
            
            await target_channel.set_permissions(
                everyone_role,
                send_messages=original_send_messages,
                reason=f"Channel unlocked by {ctx.author} - {reason}"
            )
            
            # Update lockdown record
            lockdown_record['active'] = False
            lockdown_record['unlocked_by'] = ctx.author.id
            lockdown_record['unlocked_at'] = datetime.now(timezone.utc).isoformat()
            lockdown_record['unlock_reason'] = reason
            save_lockdowns(lockdowns_data)
            
            # Send confirmation
            success_embed = discord.Embed(
                title="<:Tick:1393269945500045473> Channel Unlocked",
                color=0xFFFFFF,
                timestamp=discord.utils.utcnow()
            )
            success_embed.add_field(name="Channel", value=target_channel.mention, inline=True)
            success_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            success_embed.add_field(name="Lockdown ID", value=lockdown_id, inline=True)
            success_embed.add_field(name="Reason", value=reason, inline=False)
            success_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
            
            await ctx.send(embed=success_embed)
            
            # Send unlock message to the unlocked channel if it's not the current channel
            if target_channel != ctx.channel:
                unlock_notice = discord.Embed(
                    title="🔓 Channel Unlocked",
                    description=f"This channel has been unlocked by {ctx.author.mention}",
                    color=0xFFFFFF,
                    timestamp=discord.utils.utcnow()
                )
                unlock_notice.add_field(name="Reason", value=reason, inline=False)
                await target_channel.send(embed=unlock_notice)
            
            # Log to moderation channel
            mod_channel = bot.get_channel(config.MODERATION_CHANNEL_ID)
            if mod_channel:
                log_embed = discord.Embed(
                    title="🔓 Channel Unlocked",
                    color=0xFFFFFF,
                    timestamp=discord.utils.utcnow()
                )
                log_embed.add_field(name="Channel", value=target_channel.mention, inline=True)
                log_embed.add_field(name="Channel ID", value=target_channel.id, inline=True)
                log_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
                log_embed.add_field(name="Command Channel", value=ctx.channel.mention, inline=True)
                log_embed.add_field(name="Lockdown ID", value=lockdown_id, inline=True)
                log_embed.add_field(name="Reason", value=reason, inline=False)
                log_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
                
                await mod_channel.send(embed=log_embed)
        
        except discord.Forbidden:
            await ctx.send("I don't have permission to modify this channel's permissions.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")