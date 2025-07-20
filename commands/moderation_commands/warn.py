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

def get_user_warnings(user_id, warnings_data):
    """Get all warnings for a specific user"""
    user_warnings = []
    for warn_id, warning in warnings_data.items():
        if warning['user_id'] == user_id and warning.get('active', True):
            user_warnings.append(warning)
    return user_warnings

def setup(bot):
    @bot.command(name='warn')
    async def warn_user(ctx, member: discord.Member, *, reason="No reason provided"):
        """Warn a user"""
        # Check if user has moderation role
        if not any(role.id == config.MODERATION_ROLE_ID for role in ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        
        # Check if trying to warn themselves
        if member == ctx.author:
            await ctx.send("You cannot warn yourself.")
            return
        
        # Check if trying to warn the bot
        if member == bot.user:
            await ctx.send("I cannot warn myself.")
            return
        
        try:
            # Load existing warnings
            warnings_data = load_warnings()
            
            # Create warning record
            warn_id = str(len(warnings_data) + 1)
            warning_record = {
                'user_id': member.id,
                'user_name': str(member),
                'moderator_id': ctx.author.id,
                'moderator_name': str(ctx.author),
                'reason': reason,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'guild_id': ctx.guild.id,
                'active': True
            }
            
            # Save warning record
            warnings_data[warn_id] = warning_record
            save_warnings(warnings_data)
            
            # Get user's total warnings
            user_warnings = get_user_warnings(member.id, warnings_data)
            warning_count = len(user_warnings)
            
            # Try to DM the user
            try:
                dm_embed = discord.Embed(
                    title="<:Cross:1393269948700426341> You Have Been Warned",
                    color=0xFFFFFF,
                    timestamp=discord.utils.utcnow()
                )
                dm_embed.add_field(name="Server", value=ctx.guild.name, inline=True)
                dm_embed.add_field(name="Moderator", value=ctx.author.display_name, inline=True)
                dm_embed.add_field(name="Warning Count", value=f"{warning_count} warning(s)", inline=True)
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
                
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # User has DMs disabled
            
            # Send confirmation
            success_embed = discord.Embed(
                title="<:Tick:1393269945500045473> User Warned",
                color=0xFFFFFF,
                timestamp=discord.utils.utcnow()
            )
            success_embed.add_field(name="User", value=f"{member.mention} ({member})", inline=True)
            success_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            success_embed.add_field(name="Warning Count", value=f"{warning_count} warning(s)", inline=True)
            success_embed.add_field(name="Reason", value=reason, inline=False)
            success_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
            
            await ctx.send(embed=success_embed)
            
            # Log to moderation channel
            mod_channel = bot.get_channel(config.MODERATION_CHANNEL_ID)
            if mod_channel:
                log_embed = discord.Embed(
                    title="<:Cross:1393269948700426341> User Warned",
                    color=0xFFFFFF,
                    timestamp=discord.utils.utcnow()
                )
                log_embed.add_field(name="User", value=f"{member.mention} ({member})", inline=True)
                log_embed.add_field(name="User ID", value=member.id, inline=True)
                log_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
                log_embed.add_field(name="Channel", value=ctx.channel.mention, inline=True)
                log_embed.add_field(name="Warning ID", value=warn_id, inline=True)
                log_embed.add_field(name="Warning Count", value=f"{warning_count} warning(s)", inline=True)
                log_embed.add_field(name="Reason", value=reason, inline=False)
                log_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
                
                await mod_channel.send(embed=log_embed)
        
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")