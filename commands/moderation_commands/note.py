import discord
from discord.ext import commands
import config
import json
import os
from datetime import datetime, timezone

def load_notes():
    """Load notes from JSON file"""
    if os.path.exists('data/notes.json'):
        with open('data/notes.json', 'r') as f:
            return json.load(f)
    return {}

def save_notes(notes_data):
    """Save notes to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open('data/notes.json', 'w') as f:
        json.dump(notes_data, f, indent=2)

def setup(bot):
    @bot.command(name='note')
    async def add_note(ctx, member: discord.Member, *, note_content):
        """Add a note about a user"""
        # Check if user has moderation role
        if not any(role.id == config.MODERATION_ROLE_ID for role in ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        
        try:
            # Load existing notes
            notes_data = load_notes()
            
            # Create note record
            note_id = str(len(notes_data) + 1)
            note_record = {
                'user_id': member.id,
                'user_name': str(member),
                'moderator_id': ctx.author.id,
                'moderator_name': str(ctx.author),
                'note': note_content,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'guild_id': ctx.guild.id
            }
            
            # Save note record
            notes_data[note_id] = note_record
            save_notes(notes_data)
            
            # Send confirmation
            success_embed = discord.Embed(
                title="<:Tick:1393269945500045473> Note Added",
                color=0xFFFFFF,
                timestamp=discord.utils.utcnow()
            )
            success_embed.add_field(name="User", value=f"{member.mention} ({member})", inline=True)
            success_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            success_embed.add_field(name="Note ID", value=note_id, inline=True)
            success_embed.add_field(name="Note", value=note_content, inline=False)
            success_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
            
            await ctx.send(embed=success_embed)
            
            # Log to moderation channel
            mod_channel = bot.get_channel(config.MODERATION_CHANNEL_ID)
            if mod_channel:
                log_embed = discord.Embed(
                    title="<:Info:1393269947005780069> Note Added",
                    color=0xFFFFFF,
                    timestamp=discord.utils.utcnow()
                )
                log_embed.add_field(name="User", value=f"{member.mention} ({member})", inline=True)
                log_embed.add_field(name="User ID", value=member.id, inline=True)
                log_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
                log_embed.add_field(name="Channel", value=ctx.channel.mention, inline=True)
                log_embed.add_field(name="Note ID", value=note_id, inline=True)
                log_embed.add_field(name="Note", value=note_content, inline=False)
                log_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
                
                await mod_channel.send(embed=log_embed)
                
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")