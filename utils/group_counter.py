import aiohttp
import asyncio
import discord
from discord.ext import commands
from typing import Optional, Dict, Any
import json
import os
from datetime import datetime
import logging

# Set up logging for better debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RobloxGroupCounter:
    def __init__(self, bot: commands.Bot, group_id: int, channel_id: int, check_interval: int = 60):
        """
        Initialize the Roblox Group Counter
        
        Args:
            bot: Discord bot instance (commands.Bot)
            group_id: Roblox group ID to monitor
            channel_id: Discord channel ID to send notifications
            check_interval: How often to check for new members (seconds)
        """
        self.bot = bot
        self.group_id = group_id
        self.channel_id = channel_id
        self.check_interval = check_interval
        self.last_member_count = None
        self.milestones = [50, 100, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 7500, 10000, 15000, 20000, 25000, 50000, 75000, 100000]
        self.session = None
        self.is_running = False
        
    async def get_group_info(self) -> Optional[Dict[Any, Any]]:
        """Fetch group information from Roblox API"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            url = f"https://groups.roblox.com/v1/groups/{self.group_id}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Successfully fetched group info. Member count: {data.get('memberCount', 'Unknown')}")
                    return data
                else:
                    logger.error(f"Error fetching group info: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Exception while fetching group info: {e}")
            return None
    
    def get_next_milestone(self, current_count: int) -> int:
        """Get the next milestone based on current member count"""
        for milestone in self.milestones:
            if current_count < milestone:
                return milestone
        # If we're past all predefined milestones, calculate next round number
        if current_count < 100000:
            return ((current_count // 10000) + 1) * 10000
        else:
            return ((current_count // 25000) + 1) * 25000
    
    def should_celebrate_milestone(self, old_count: int, new_count: int) -> bool:
        """Check if we've reached a milestone worth celebrating"""
        if old_count is None:
            return False
            
        logger.info(f"Checking milestone: {old_count} -> {new_count}")
            
        # Check if we crossed any predefined milestones
        for milestone in self.milestones:
            if old_count < milestone <= new_count:
                logger.info(f"Milestone reached: {milestone}")
                return True
                
        # Check for every 100 members if under 1000
        if new_count < 1000 and (new_count // 100) > (old_count // 100):
            logger.info(f"100-member milestone reached: {new_count}")
            return True
            
        # Check for every 500 members if over 1000
        if new_count >= 1000 and (new_count // 500) > (old_count // 500):
            logger.info(f"500-member milestone reached: {new_count}")
            return True
            
        return False
    
    async def send_member_update(self, group_info: Dict[Any, Any]) -> None:
        """Send member count update to Discord"""
        try:
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                logger.error(f"Channel {self.channel_id} not found")
                return
                
            current_count = group_info.get("memberCount", 0)
            group_name = group_info.get("name", "Unknown Group")
            next_milestone = self.get_next_milestone(current_count)
            members_until_milestone = next_milestone - current_count
            
            # Create embed
            embed = discord.Embed(
                title="🎉 Group Milestone!",
                description=f"We've reached **{current_count:,}** members! We are **{members_until_milestone:,}** away from **{next_milestone:,}**.",
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="Group",
                value=group_name,
                inline=True
            )
            
            embed.add_field(
                name="Current Members",
                value=f"{current_count:,}",
                inline=True
            )
            
            embed.add_field(
                name="Next Milestone",
                value=f"{next_milestone:,}",
                inline=True
            )
            
            # Fixed thumbnail URL - this was incorrect in original code
            embed.set_thumbnail(url=f"https://thumbnails.roblox.com/v1/groups/icons?groupIds={self.group_id}&size=150x150&format=Png&isCircular=false")
            embed.set_footer(text="Roblox Group Monitor")
            
            await channel.send(embed=embed)
            logger.info(f"Sent milestone notification for {current_count} members")
            
        except Exception as e:
            logger.error(f"Error sending Discord message: {e}")
    
    async def send_regular_update(self, group_info: Dict[Any, Any]) -> None:
        """Send regular member count update (non-milestone)"""
        try:
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                logger.error(f"Channel {self.channel_id} not found")
                return
                
            current_count = group_info.get("memberCount", 0)
            group_name = group_info.get("name", "Unknown Group")
            next_milestone = self.get_next_milestone(current_count)
            members_until_milestone = next_milestone - current_count
            
            message = f"📈 **{group_name}** now has **{current_count:,}** members! Only **{members_until_milestone:,}** more until **{next_milestone:,}**!"
            
            await channel.send(message)
            logger.info(f"Sent regular update for {current_count} members")
            
        except Exception as e:
            logger.error(f"Error sending regular update: {e}")
    
    async def send_member_join_notification(self, group_info: Dict[Any, Any], members_gained: int) -> None:
        """Send notification when someone joins (but not a milestone)"""
        try:
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                logger.error(f"Channel {self.channel_id} not found")
                return
                
            current_count = group_info.get("memberCount", 0)
            group_name = group_info.get("name", "Unknown Group")
            next_milestone = self.get_next_milestone(current_count)
            members_until_milestone = next_milestone - current_count
            
            if members_gained == 1:
                message = f"🎊 We have reached  **{current_count:,}** members, **only {members_until_milestone:,}** more until **{next_milestone:,}**"
            else:
                message = f"🎊 **{members_gained}** new members joined! We now have **{current_count:,}** members, **{members_until_milestone:,}** more until **{next_milestone:,}**"
            
            await channel.send(message)
            logger.info(f"Sent join notification: +{members_gained} members (now {current_count})")
            
        except Exception as e:
            logger.error(f"Error sending join notification: {e}")
    
    async def check_member_count(self) -> None:
        """Check for member count changes and send updates"""
        group_info = await self.get_group_info()
        
        if not group_info:
            logger.warning("Failed to get group info, skipping check")
            return
            
        current_count = group_info.get("memberCount", 0)
        
        if self.last_member_count is not None:
            if current_count > self.last_member_count:
                # Members increased
                members_gained = current_count - self.last_member_count
                logger.info(f"Member count increased: {self.last_member_count} -> {current_count} (+{members_gained})")
                
                if self.should_celebrate_milestone(self.last_member_count, current_count):
                    await self.send_member_update(group_info)
                else:
                    # Send notification for any member join
                    await self.send_member_join_notification(group_info, members_gained)
                    
            elif current_count < self.last_member_count:
                # Members decreased
                members_lost = self.last_member_count - current_count
                logger.info(f"Member count decreased: {self.last_member_count} -> {current_count} (-{members_lost})")
            else:
                # No change
                logger.info(f"No change in member count: {current_count}")
        else:
            logger.info(f"Setting initial member count: {current_count}")
                
        self.last_member_count = current_count
    
    async def start_monitoring(self) -> None:
        """Start the monitoring loop"""
        if self.is_running:
            logger.warning("Group monitoring is already running")
            return
            
        self.is_running = True
        logger.info(f"Started monitoring Roblox group {self.group_id}")
        
        # Wait for bot to be ready
        await self.bot.wait_until_ready()
        
        # Initial check to set baseline
        group_info = await self.get_group_info()
        if group_info:
            self.last_member_count = group_info.get("memberCount", 0)
            logger.info(f"Initial member count: {self.last_member_count}")
        else:
            logger.error("Failed to get initial group info")
        
        while self.is_running:
            try:
                await self.check_member_count()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(30)  # Wait a bit before retrying
    
    async def stop_monitoring(self) -> None:
        """Stop the monitoring loop"""
        self.is_running = False
        if self.session:
            await self.session.close()
        logger.info("Stopped group monitoring")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the monitor"""
        return {
            "is_running": self.is_running,
            "group_id": self.group_id,
            "channel_id": self.channel_id,
            "last_member_count": self.last_member_count,
            "check_interval": self.check_interval
        }


# Convenience function to set up group monitoring
async def setup_group_monitoring(bot: commands.Bot, group_id: int, channel_id: int, check_interval: int = 60) -> RobloxGroupCounter:
    """
    Set up and start group monitoring
    
    Args:
        bot: Discord bot instance (commands.Bot)
        group_id: Roblox group ID to monitor
        channel_id: Discord channel ID to send notifications
        check_interval: How often to check for new members (seconds)
    
    Returns:
        RobloxGroupCounter instance
    """
    counter = RobloxGroupCounter(bot, group_id, channel_id, check_interval)
    
    # Start monitoring in the background
    asyncio.create_task(counter.start_monitoring())
    
    return counter


# Example usage for your main bot file:
"""
from utils.group_counter import setup_group_monitoring

# In your bot's on_ready event or similar:
@bot.event
async def on_ready():
    # Replace with your actual group ID and channel ID
    group_counter = await setup_group_monitoring(
        bot=bot,
        group_id=YOUR_GROUP_ID,
        channel_id=YOUR_CHANNEL_ID,
        check_interval=120  # Check every 2 minutes
    )
"""