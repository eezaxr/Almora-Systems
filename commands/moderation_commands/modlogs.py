import discord
from discord.ext import commands
import config
import json
import os

def load_bans():
    """Load bans from JSON file"""
    if os.path.exists('data/bans.json'):
        with open('data/bans.json', 'r') as f:
            return json.load(f)
    return {}

def load_kicks():
    """Load kicks from JSON file"""
    if os.path.exists('data/kicks.json'):
        with open('data/kicks.json', 'r') as f:
            return json.load(f)
    return {}

def load_mutes():
    """Load mutes from JSON file"""
    if os.path.exists('data/mutes.json'):
        with open('data/mutes.json', 'r') as f:
            return json.load(f)
    return {}

def load_warnings():
    """Load warnings from JSON file"""
    if os.path.exists('data/warnings.json'):
        with open('data/warnings.json', 'r') as f:
            return json.load(f)
    return {}

def setup(bot):
    @bot.command(name='modlogs')
    async def modlogs(ctx, member: discord.Member = None):
        """View moderation logs for a user"""
        # Check if user has moderation role
        if not any(role.id == config.MODERATION_ROLE_ID for role in ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        
        # If no member specified, use command author
        if member is None:
            member = ctx.author
        
        try:
            # Load all moderation data
            bans_data = load_bans()
            kicks_data = load_kicks()
            mutes_data = load_mutes()
            warnings_data = load_warnings()
            
            # Find all actions for this user
            user_bans = [ban for ban in bans_data.values() if ban['user_id'] == member.id]
            user_kicks = [kick for kick in kicks_data.values() if kick['user_id'] == member.id]
            user_mutes = [mute for mute in mutes_data.values() if mute['user_id'] == member.id]
            user_warnings = [warning for warning in warnings_data.values() if warning['user_id'] == member.id]
            
            # Create embed
            embed = discord.Embed(
                title=f"<:Info:1393269947005780069> Moderation Logs for {member.display_name}",
                color=0xFFFFFF,
                timestamp=discord.utils.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            
            # Add fields for each type of action
            embed.add_field(name="Bans", value=str(len(user_bans)), inline=True)
            embed.add_field(name="Kicks", value=str(len(user_kicks)), inline=True)
            embed.add_field(name="Mutes", value=str(len(user_mutes)), inline=True)
            embed.add_field(name="Warnings", value=str(len(user_warnings)), inline=True)
            embed.add_field(name="Total Actions", value=str(len(user_bans) + len(user_kicks) + len(user_mutes) + len(user_warnings)), inline=True)
            embed.add_field(name="User ID", value=member.id, inline=True)
            
            # Recent actions (last 5)
            all_actions = []
            for ban in user_bans:
                all_actions.append(f"🔨 **Ban** - {ban['reason']} ({ban['timestamp'][:10]})")
            for kick in user_kicks:
                all_actions.append(f"👢 **Kick** - {kick['reason']} ({kick['timestamp'][:10]})")
            for mute in user_mutes:
                all_actions.append(f"🔇 **Mute** - {mute['reason']} ({mute['timestamp'][:10]})")
            for warning in user_warnings:
                all_actions.append(f"⚠️ **Warning** - {warning['reason']} ({warning['timestamp'][:10]})")
            
            # Sort by timestamp and get last 5
            if all_actions:
                recent_actions = all_actions[-5:] if len(all_actions) > 5 else all_actions
                embed.add_field(name="Recent Actions", value="\n".join(recent_actions), inline=False)
            else:
                embed.add_field(name="Recent Actions", value="No moderation actions found.", inline=False)
            
            embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")