import discord
from discord.ext import commands
import config
from datetime import timedelta
from utils.ticket_utils import is_ticket_channel, has_staff_permissions
from utils.transcript_utils import generate_transcript, get_ticket_info_from_channel

def setup(bot):
    @bot.command(name='close')
    async def close_ticket(ctx, *, reason=None):
        """Close the current ticket with an optional reason"""
        if not is_ticket_channel(ctx.channel):
            await ctx.send("This command can only be used in ticket channels.")
            return
        
        if not (ctx.channel.name == f"ticket-{ctx.author.name.lower()}" or has_staff_permissions(ctx.author)):
            await ctx.send("You don't have permission to close this ticket.")
            return
        
        close_reason = reason if reason else "No reason provided"
        
        embed = discord.Embed(
            title="<:Team:1393269975753691276> Close Ticket",
            description="Are you sure you want to close this ticket?",
            color=0xFFFFFF
        )
        
        if reason:
            embed.add_field(name="Close Reason", value=close_reason, inline=False)
        
        message = await ctx.send(embed=embed)
        await message.add_reaction("<:Tick:1393269945500045473>")
        await message.add_reaction("<:Cross:1393269948700426341>")
        
        def check(reaction, user):
            return (
                user == ctx.author and 
                str(reaction.emoji) in ["<:Tick:1393269945500045473>", "<:Cross:1393269948700426341>"] and 
                reaction.message.id == message.id
            )
        
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
            
            if str(reaction.emoji) == "<:Tick:1393269945500045473>":
                
                await ctx.send("Generating transcript and closing ticket...")
                
                
                ticket_owner, claimed_by = get_ticket_info_from_channel(ctx.channel)
                
                
                ticket_reason = "No reason provided"
                async for message in ctx.channel.history(limit=50, oldest_first=True):
                    if message.embeds and "Support Ticket" in str(message.embeds[0].title):
                        embed_desc = message.embeds[0].description
                        if "**Reason:**" in embed_desc:
                            ticket_reason = embed_desc.split("**Reason:**")[1].split("\n")[0].strip()
                        break
                
                
                transcript = await generate_transcript(ctx.channel)
                
                
                log_channel = ctx.guild.get_channel(config.LOG_CHANNEL_ID)
                if log_channel:
                    log_embed = discord.Embed(
                        title="<:Cross:1393269948700426341> Ticket Closed",
                        color=0xFFFFFF,
                        timestamp=discord.utils.utcnow()
                    )
                    log_embed.add_field(name="Ticket Owner", value=ticket_owner.mention if ticket_owner else "Unknown", inline=True)
                    log_embed.add_field(name="Closed By", value=ctx.author.mention, inline=True)
                    log_embed.add_field(name="Claimed By", value=claimed_by if claimed_by else "Unclaimed", inline=True)
                    log_embed.add_field(name="Channel", value=ctx.channel.name, inline=True)
                    log_embed.add_field(name="Original Reason", value=ticket_reason, inline=True)
                    log_embed.add_field(name="Close Reason", value=close_reason, inline=True)
                    log_embed.set_image(url="https://media.discordapp.net/attachments/1301667213131907170/1393267567925137478/Banner2.png?ex=68728d09&is=68713b89&hm=3848c521166c97401f3eaac93d3ed9b0901279cab8ae433b4a7a48600d1a000e&=&format=webp&quality=lossless&width=1318&height=63")
                    
                    await log_channel.send(embed=log_embed, file=transcript)
                
                
                if ticket_owner:
                    try:
                        dm_embed = discord.Embed(
                            title="<:Cross:1393269948700426341> Your Ticket Has Been Closed",
                            color=0xFFFFFF,
                            timestamp=discord.utils.utcnow()
                        )
                        dm_embed.add_field(name="Server", value=ctx.guild.name, inline=True)
                        dm_embed.add_field(name="Closed By", value=ctx.author.display_name, inline=True)
                        dm_embed.add_field(name="Claimed By", value=claimed_by if claimed_by else "Unclaimed", inline=True)
                        dm_embed.add_field(name="Close Reason", value=close_reason, inline=True)
                        dm_embed.set_image(url="https://media.discordapp.net/attachments/1301667213131907170/1393267567925137478/Banner2.png?ex=68728d09&is=68713b89&hm=3848c521166c97401f3eaac93d3ed9b0901279cab8ae433b4a7a48600d1a000e&=&format=webp&quality=lossless&width=1318&height=63")
                        
                        dm_transcript = await generate_transcript(ctx.channel)
                        await ticket_owner.send(embed=dm_embed, file=dm_transcript)
                    except discord.Forbidden:
                        pass 
                
                await ctx.send("Ticket will be deleted in 3 seconds...")
                await discord.utils.sleep_until(discord.utils.utcnow() + timedelta(seconds=3))
                await ctx.channel.delete(reason=f"Ticket closed by {ctx.author} - {close_reason}")
                
            else:
                await ctx.send("Ticket close cancelled.")
                
        except TimeoutError:
            await ctx.send("Ticket close timed out.")