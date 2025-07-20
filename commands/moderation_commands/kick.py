import discord
from discord.ext import commands
import config
import json
import os
from datetime import datetime, timezone

def load_kicks():
    """Load kicks from JSON file"""
    if os.path.exists('data/kicks.json'):
        with open('data/kicks.json', 'r') as f:
            return json.load(f)
    return {}

def save_kicks(kicks_data):
    """Save kicks to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open('data/kicks.json', 'w') as f:
        json.dump(kicks_data, f, indent=2)

def setup(bot):
    @bot.command(name='kick')
    async def kick_user(ctx, member: discord.Member, *, reason="No reason provided"):
        """Kick a user from the server"""
        # Check if user has moderation role
        if not any(role.id == config.MODERATION_ROLE_ID for role in ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        
        # Check if trying to kick themselves
        if member == ctx.author:
            await ctx.send("You cannot kick yourself.")
            return
        
        # Check if trying to kick a user with higher or equal role
        if member.top_role >= ctx.author.top_role:
            await ctx.send("You cannot kick a user with equal or higher permissions.")
            return
        
        # Check if trying to kick the bot
        if member == bot.user:
            await ctx.send("I cannot kick myself.")
            return
        
        try:
            # Load existing kicks
            kicks_data = load_kicks()
            
            # Create kick record
            kick_id = str(len(kicks_data) + 1)
            kick_record = {
                'user_id': member.id,
                'user_name': str(member),
                'moderator_id': ctx.author.id,
                'moderator_name': str(ctx.author),
                'reason': reason,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'guild_id': ctx.guild.id
            }
            
            # Save kick record
            kicks_data[kick_id] = kick_record
            save_kicks(kicks_data)
            
            # Try to DM the user before kicking
            try:
                dm_embed = discord.Embed(
                    title="<:Cross:1393269948700426341> You Have Been Kicked",
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
            
            # Kick the user
            await member.kick(reason=f"{reason} - Kicked by {ctx.author}")
            
            # Send confirmation
            success_embed = discord.Embed(
                title="<:Tick:1393269945500045473> User Kicked",
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
                    title="<:Cross:1393269948700426341> User Kicked",
                    color=0xFFFFFF,
                    timestamp=discord.utils.utcnow()
                )
                log_embed.add_field(name="User", value=f"{member.mention} ({member})", inline=True)
                log_embed.add_field(name="User ID", value=member.id, inline=True)
                log_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
                log_embed.add_field(name="Channel", value=ctx.channel.mention, inline=True)
                log_embed.add_field(name="Kick ID", value=kick_id, inline=True)
                log_embed.add_field(name="Reason", value=reason, inline=False)
                log_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
                
                await mod_channel.send(embed=log_embed)
        
        except discord.Forbidden:
            await ctx.send("I don't have permission to kick this user.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")