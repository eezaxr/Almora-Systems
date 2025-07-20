import discord
from discord.ext import commands
import config
import json
import os

def load_warnings():
    """Load warnings from JSON file"""
    if os.path.exists('data/warnings.json'):
        with open('data/warnings.json', 'r') as f:
            return json.load(f)
    return {}

def setup(bot):
    @bot.command(name='warnings')
    async def view_warnings(ctx, member: discord.Member):
        """View all warnings for a user"""
        # Check if user has moderation role
        if not any(role.id == config.MODERATION_ROLE_ID for role in ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        
        try:
            # Load warnings data
            warnings_data = load_warnings()
            
            # Find all warnings for this user
            user_warnings = []
            for warning_id, warning in warnings_data.items():
                if warning['user_id'] == member.id:
                    user_warnings.append((warning_id, warning))
            
            if not user_warnings:
                embed = discord.Embed(
                    title="<:Info:1393269947005780069> No Warnings Found",
                    description=f"No warnings found for {member.mention}",
                    color=0xFFFFFF,
                    timestamp=discord.utils.utcnow()
                )
                embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
                await ctx.send(embed=embed)
                return
            
            # Sort warnings by timestamp (newest first)
            user_warnings.sort(key=lambda x: x[1]['timestamp'], reverse=True)
            
            # Create embed
            embed = discord.Embed(
                title=f"<:Warning:1393269950188048464> Warnings for {member.display_name}",
                color=0xFFFFFF,
                timestamp=discord.utils.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="Total Warnings", value=str(len(user_warnings)), inline=True)
            embed.add_field(name="User ID", value=member.id, inline=True)
            embed.add_field(name="User", value=member.mention, inline=True)
            
            # Add warnings (limit to 10 most recent to avoid embed limits)
            warnings_text = []
            for i, (warning_id, warning) in enumerate(user_warnings[:10]):
                warning_date = warning['timestamp'][:10]  # Get just the date part
                warning_text = f"**Warning #{warning_id}** ({warning_date})\n"
                warning_text += f"By: {warning['moderator_name']}\n"
                warning_text += f"Reason: {warning['reason']}\n"
                warnings_text.append(warning_text)
            
            if warnings_text:
                # Split warnings across multiple fields if needed
                warnings_content = "\n".join(warnings_text)
                if len(warnings_content) > 1024:
                    # Split into chunks
                    chunks = []
                    current_chunk = ""
                    for warning_text in warnings_text:
                        if len(current_chunk + warning_text) > 1024:
                            chunks.append(current_chunk)
                            current_chunk = warning_text
                        else:
                            current_chunk += warning_text + "\n"
                    if current_chunk:
                        chunks.append(current_chunk)
                    
                    for i, chunk in enumerate(chunks[:3]):  # Limit to 3 fields
                        field_name = "Warnings" if i == 0 else f"Warnings (continued {i+1})"
                        embed.add_field(name=field_name, value=chunk, inline=False)
                        
                    if len(user_warnings) > 10:
                        embed.add_field(name="Note", value=f"Showing 10 most recent warnings out of {len(user_warnings)} total.", inline=False)
                else:
                    embed.add_field(name="Warnings", value=warnings_content, inline=False)
            
            embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")