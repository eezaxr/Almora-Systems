import discord
from discord.ext import commands
import config
import json
import os

def load_notes():
    """Load notes from JSON file"""
    if os.path.exists('data/notes.json'):
        with open('data/notes.json', 'r') as f:
            return json.load(f)
    return {}

def setup(bot):
    @bot.command(name='notes')
    async def view_notes(ctx, member: discord.Member):
        """View all notes for a user"""
        # Check if user has moderation role
        if not any(role.id == config.MODERATION_ROLE_ID for role in ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        
        try:
            # Load notes data
            notes_data = load_notes()
            
            # Find all notes for this user
            user_notes = [note for note in notes_data.values() if note['user_id'] == member.id]
            
            if not user_notes:
                embed = discord.Embed(
                    title="<:Info:1393269947005780069> No Notes Found",
                    description=f"No notes found for {member.mention}",
                    color=0xFFFFFF,
                    timestamp=discord.utils.utcnow()
                )
                embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
                await ctx.send(embed=embed)
                return
            
            # Sort notes by timestamp (newest first)
            user_notes.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Create embed
            embed = discord.Embed(
                title=f"<:Info:1393269947005780069> Notes for {member.display_name}",
                color=0xFFFFFF,
                timestamp=discord.utils.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="Total Notes", value=str(len(user_notes)), inline=True)
            embed.add_field(name="User ID", value=member.id, inline=True)
            embed.add_field(name="User", value=member.mention, inline=True)
            
            # Add notes (limit to 10 most recent to avoid embed limits)
            notes_text = []
            for i, note in enumerate(user_notes[:10]):
                note_date = note['timestamp'][:10]  # Get just the date part
                note_text = f"**Note #{list(notes_data.keys())[list(notes_data.values()).index(note)]}** ({note_date})\n"
                note_text += f"By: {note['moderator_name']}\n"
                note_text += f"Note: {note['note']}\n"
                notes_text.append(note_text)
            
            if notes_text:
                # Split notes across multiple fields if needed
                notes_content = "\n".join(notes_text)
                if len(notes_content) > 1024:
                    # Split into chunks
                    chunks = []
                    current_chunk = ""
                    for note_text in notes_text:
                        if len(current_chunk + note_text) > 1024:
                            chunks.append(current_chunk)
                            current_chunk = note_text
                        else:
                            current_chunk += note_text + "\n"
                    if current_chunk:
                        chunks.append(current_chunk)
                    
                    for i, chunk in enumerate(chunks[:3]):  # Limit to 3 fields
                        field_name = "Notes" if i == 0 else f"Notes (continued {i+1})"
                        embed.add_field(name=field_name, value=chunk, inline=False)
                        
                    if len(user_notes) > 10:
                        embed.add_field(name="Note", value=f"Showing 10 most recent notes out of {len(user_notes)} total.", inline=False)
                else:
                    embed.add_field(name="Notes", value=notes_content, inline=False)
            
            embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")