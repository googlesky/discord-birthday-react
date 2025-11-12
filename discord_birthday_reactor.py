#!/usr/bin/env python3
"""
Discord Birthday Message Reactor
Automatically reacts to messages containing "birthday" and mentioning "Hieu Le"

WARNING: Using personal tokens for automation violates Discord's Terms of Service
and may result in account suspension. Use at your own risk.
"""

import requests
import time
import json
import sys
import os
from typing import List, Dict, Optional
from urllib.parse import quote
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

class DiscordReactor:
    def __init__(self, token: str, reaction_emojis: List[str] = None, delay_min: float = 1.0, delay_max: float = 2.0):
        self.token = token
        self.base_url = "https://discord.com/api/v10"
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        # Emoji encodings for reactions (configurable)
        if reaction_emojis is None:
            reaction_emojis = ["❤️", "💖", "🚀"]

        # Create emoji mapping with names
        emoji_names = ["heart", "rainbow_heart", "rocket", "star", "fire", "sparkles", "tada", "balloon"]
        self.emojis = {}
        for i, emoji in enumerate(reaction_emojis):
            name = emoji_names[i] if i < len(emoji_names) else f"emoji_{i+1}"
            self.emojis[name] = emoji

        self.delay_min = delay_min
        self.delay_max = delay_max

    def get_user_id(self) -> Optional[str]:
        """Get the current user's ID"""
        try:
            response = requests.get(
                f"{self.base_url}/users/@me",
                headers=self.headers
            )
            response.raise_for_status()
            user_data = response.json()
            print(f"✓ Logged in as: {user_data['username']}#{user_data['discriminator']}")
            return user_data['id']
        except Exception as e:
            print(f"✗ Failed to get user info: {e}")
            return None

    def get_guilds(self) -> List[Dict]:
        """Get all guilds (servers) the user is in"""
        try:
            response = requests.get(
                f"{self.base_url}/users/@me/guilds",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"✗ Failed to get guilds: {e}")
            return []

    def get_channels(self, guild_id: str) -> List[Dict]:
        """Get all channels in a guild"""
        try:
            response = requests.get(
                f"{self.base_url}/guilds/{guild_id}/channels",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"✗ Failed to get channels for guild {guild_id}: {e}")
            return []

    def get_dm_channels(self) -> List[Dict]:
        """Get all DM channels"""
        try:
            response = requests.get(
                f"{self.base_url}/users/@me/channels",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"✗ Failed to get DM channels: {e}")
            return []

    def search_messages_in_channel(self, channel_id: str, query: str, user_id: str = None, debug: bool = True, date_filter: Optional[str] = None, keywords: List[str] = None) -> List[Dict]:
        """Search for messages in a specific channel

        Args:
            keywords: List of keywords to search for (case-insensitive)
        """
        messages = []

        # Default keywords if not provided
        if keywords is None:
            keywords = ["birthday"]

        try:
            # Fetch recent messages (last 100)
            response = requests.get(
                f"{self.base_url}/channels/{channel_id}/messages",
                headers=self.headers,
                params={"limit": 100}
            )
            response.raise_for_status()
            all_messages = response.json()

            if debug:
                print(f"  ℹ Fetched {len(all_messages)} messages from channel")
                print(f"  ℹ Searching for keywords: {', '.join(keywords)}")

            # Parse date filter if provided
            target_date = None
            if date_filter:
                if date_filter.lower() == "today":
                    target_date = datetime.now(timezone.utc).date()
                else:
                    try:
                        target_date = datetime.fromisoformat(date_filter).date()
                    except Exception as e:
                        print(f"  ⚠ Invalid date format: {date_filter}, expected YYYY-MM-DD or 'today'")

                if target_date and debug:
                    print(f"  ℹ Filtering messages from: {target_date}")

            birthday_messages = []
            # Filter messages containing any of the keywords and mentioning the user
            for msg in all_messages:
                content = msg.get('content', '')
                content_lower = content.lower()

                # Check if message contains any of the keywords
                contains_keyword = False
                matched_keyword = None
                for keyword in keywords:
                    if keyword.lower() in content_lower:
                        contains_keyword = True
                        matched_keyword = keyword
                        break

                if not contains_keyword:
                    continue

                # Check date filter if specified
                if target_date:
                    timestamp = msg.get('timestamp')
                    if timestamp:
                        try:
                            msg_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).date()
                            if msg_date != target_date:
                                continue  # Skip messages not from target date
                        except Exception as e:
                            print(f"  ⚠ Failed to parse timestamp: {e}")
                            continue

                birthday_messages.append(msg)

                # Check if user is mentioned in the message
                user_mentioned = False

                # Method 1: Check mentions array
                mentions = msg.get('mentions', [])
                if user_id:
                    for mention in mentions:
                        if mention.get('id') == user_id:
                            user_mentioned = True
                            break

                # Method 2: Check for plain text "Hieu Le"
                if 'hieu le' in content_lower:
                    user_mentioned = True

                # Method 3: Check for Discord mention format <@user_id>
                if user_id and f'<@{user_id}>' in content:
                    user_mentioned = True
                if user_id and f'<@!{user_id}>' in content:  # Nickname mention format
                    user_mentioned = True

                if user_mentioned:
                    if debug:
                        # Show preview of matching message
                        preview = content[:100] + '...' if len(content) > 100 else content
                        print(f"  ✓ Match (keyword: '{matched_keyword}'): '{preview}'")
                    messages.append(msg)

            # Show debug info about birthday messages
            if debug and birthday_messages and not messages:
                print(f"  ⚠ Found {len(birthday_messages)} message(s) with keywords but NONE mention you")
                print(f"  ℹ Showing first few messages:")
                for i, msg in enumerate(birthday_messages[:3]):
                    content = msg.get('content', '')
                    preview = content[:150] + '...' if len(content) > 150 else content
                    mentions = msg.get('mentions', [])
                    mention_names = [m.get('username', 'Unknown') for m in mentions]
                    print(f"    {i+1}. '{preview}'")
                    if mentions:
                        print(f"       Mentions: {', '.join(mention_names)}")
                    else:
                        print(f"       Mentions: (none)")

            time.sleep(1)  # Rate limiting
            return messages

        except Exception as e:
            print(f"  ✗ Failed to search messages in channel {channel_id}: {e}")
            return []

    def search_messages_in_guild(self, guild_id: str) -> List[Dict]:
        """Search for messages in a guild using Discord's search API"""
        messages = []
        try:
            # Use Discord's native search endpoint for guilds
            response = requests.get(
                f"{self.base_url}/guilds/{guild_id}/messages/search",
                headers=self.headers,
                params={
                    "content": "birthday Hieu Le",
                    "include_nsfw": "true"
                }
            )

            if response.status_code == 200:
                data = response.json()
                # Extract messages from search results
                for result in data.get('messages', []):
                    # Each result is an array of messages
                    if isinstance(result, list):
                        messages.extend(result)
                    else:
                        messages.append(result)
            elif response.status_code == 403:
                print(f"  ⚠ No search permission in this guild")
            else:
                print(f"  ⚠ Search returned status {response.status_code}")

            time.sleep(1)
            return messages

        except Exception as e:
            print(f"  ✗ Failed to search in guild {guild_id}: {e}")
            return []

    def add_reaction(self, channel_id: str, message_id: str, emoji: str) -> bool:
        """Add a reaction to a message"""
        try:
            # URL encode the emoji
            encoded_emoji = quote(emoji)
            url = f"{self.base_url}/channels/{channel_id}/messages/{message_id}/reactions/{encoded_emoji}/@me"

            response = requests.put(url, headers=self.headers)

            if response.status_code == 204:
                return True
            elif response.status_code == 429:
                # Rate limited
                retry_after = response.json().get('retry_after', 2)
                print(f"  ⚠ Rate limited, waiting {retry_after}s...")
                time.sleep(retry_after)
                return False
            else:
                print(f"  ✗ Failed to add reaction: {response.status_code}")
                return False

        except Exception as e:
            print(f"  ✗ Error adding reaction: {e}")
            return False

    def get_message(self, channel_id: str, message_id: str) -> Optional[Dict]:
        """Get a specific message with its reactions"""
        try:
            response = requests.get(
                f"{self.base_url}/channels/{channel_id}/messages/{message_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"  ✗ Failed to get message: {e}")
            return None

    def check_user_reactions(self, message: Dict, user_id: str) -> Dict[str, bool]:
        """Check which reactions the user has already added to a message"""
        user_reactions = {}

        for emoji_name, emoji in self.emojis.items():
            user_reactions[emoji_name] = False

        reactions = message.get('reactions', [])
        for reaction in reactions:
            emoji = reaction.get('emoji', {})
            emoji_name_or_id = emoji.get('name')

            # Check if this is one of our emojis
            for our_emoji_name, our_emoji in self.emojis.items():
                if emoji_name_or_id == our_emoji:
                    # Check if current user reacted
                    if reaction.get('me', False):
                        user_reactions[our_emoji_name] = True
                    break

        return user_reactions

    def react_to_message(self, channel_id: str, message_id: str, message_link: str, message: Optional[Dict] = None, user_id: Optional[str] = None):
        """Add all three reactions to a message, skipping ones already added"""
        print(f"\n  → Processing: {message_link}")

        # Get message if not provided
        if message is None:
            message = self.get_message(channel_id, message_id)
            if message is None:
                print(f"    ✗ Could not retrieve message")
                return

        # Check existing reactions if we have user_id
        if user_id:
            existing_reactions = self.check_user_reactions(message, user_id)
            all_reacted = all(existing_reactions.values())

            if all_reacted:
                print(f"    ℹ Already reacted with all emojis - skipping")
                return

            # Show which reactions already exist
            already_added = [name for name, exists in existing_reactions.items() if exists]
            if already_added:
                print(f"    ℹ Already have: {', '.join(already_added)}")
        else:
            existing_reactions = {name: False for name in self.emojis.keys()}

        # Add missing reactions
        added_count = 0
        for emoji_name, emoji in self.emojis.items():
            if existing_reactions.get(emoji_name, False):
                continue  # Skip already added reactions

            success = self.add_reaction(channel_id, message_id, emoji)
            if success:
                print(f"    ✓ Added {emoji_name} {emoji}")
                added_count += 1
            else:
                print(f"    ✗ Failed to add {emoji_name} {emoji}")

            # Random delay between configured min and max seconds
            import random
            delay = random.uniform(self.delay_min, self.delay_max)
            time.sleep(delay)

        if added_count == 0 and not all(existing_reactions.values()):
            print(f"    ⚠ No new reactions added")

    def process_guild(self, guild: Dict, user_id: str):
        """Process all channels in a guild"""
        guild_id = guild['id']
        guild_name = guild['name']
        print(f"\n📁 Searching in guild: {guild_name}")

        # Try guild-wide search first
        messages = self.search_messages_in_guild(guild_id)

        if messages:
            print(f"  ✓ Found {len(messages)} matching message(s)")
            for msg in messages:
                try:
                    channel_id = msg['channel_id']
                    message_id = msg['id']
                    message_link = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"

                    # Check if message mentions "Hieu Le"
                    content = msg.get('content', '')
                    if 'hieu le' in content.lower() and 'birthday' in content.lower():
                        self.react_to_message(channel_id, message_id, message_link, message=msg, user_id=user_id)
                except Exception as e:
                    print(f"  ✗ Error processing message: {e}")
        else:
            print(f"  ℹ No matching messages found")

    def process_dm_channels(self, user_id: str):
        """Process DM channels"""
        print(f"\n💬 Searching in DM channels...")
        dm_channels = self.get_dm_channels()

        for channel in dm_channels:
            channel_id = channel['id']
            channel_type = channel.get('type')

            # Get recipient name
            recipients = channel.get('recipients', [])
            recipient_names = ', '.join([r.get('username', 'Unknown') for r in recipients])

            print(f"\n  Searching DM with: {recipient_names}")
            messages = self.search_messages_in_channel(channel_id, "birthday Hieu Le")

            if messages:
                print(f"  ✓ Found {len(messages)} matching message(s)")
                for msg in messages:
                    message_id = msg['id']
                    message_link = f"https://discord.com/channels/@me/{channel_id}/{message_id}"
                    self.react_to_message(channel_id, message_id, message_link, message=msg, user_id=user_id)
            else:
                print(f"  ℹ No matching messages found")

    def parse_channel_link(self, link: str) -> Optional[tuple]:
        """Parse a Discord channel link to extract guild_id and channel_id"""
        try:
            # Format: https://discord.com/channels/{guild_id}/{channel_id}
            # or https://discord.com/channels/@me/{channel_id} for DMs
            parts = link.strip().split('/')
            if 'channels' in parts:
                idx = parts.index('channels')
                if len(parts) > idx + 2:
                    guild_id = parts[idx + 1]
                    channel_id = parts[idx + 2].split('?')[0]  # Remove query params if any
                    return (guild_id, channel_id)
        except Exception as e:
            print(f"✗ Failed to parse link: {e}")
        return None

    def process_specific_channel(self, guild_id: str, channel_id: str, user_id: str, date_filter: Optional[str] = None, keywords: List[str] = None):
        """Process a specific channel"""
        print(f"\n📁 Searching in channel: {channel_id}")

        messages = self.search_messages_in_channel(
            channel_id,
            "birthday Hieu Le",
            user_id=user_id,
            debug=True,
            date_filter=date_filter,
            keywords=keywords
        )

        if messages:
            print(f"\n  ✓ Found {len(messages)} matching message(s)")
            for msg in messages:
                message_id = msg['id']
                if guild_id == "@me":
                    message_link = f"https://discord.com/channels/@me/{channel_id}/{message_id}"
                else:
                    message_link = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"
                self.react_to_message(channel_id, message_id, message_link, message=msg, user_id=user_id)
        else:
            print(f"  ℹ No matching messages found")

    def run(self, channel_links: Optional[List[str]] = None, date_filter: Optional[str] = None, keywords: List[str] = None):
        """Main execution method

        Args:
            channel_links: Optional list of Discord channel links to search in.
                          If not provided, searches all accessible channels.
            date_filter: Optional date filter. Use "today" for today's messages,
                        or "YYYY-MM-DD" for a specific date (e.g., "2025-11-11").
                        If not provided, searches all messages.
            keywords: List of keywords to search for in messages (case-insensitive).
                     Defaults to ["birthday"] if not provided.
        """
        print("=" * 60)
        print("Discord Birthday Message Reactor")
        print("=" * 60)
        print("\n⚠  WARNING: This violates Discord's Terms of Service!")
        print("   Use at your own risk.\n")

        # Verify token and get user ID
        user_id = self.get_user_id()
        if not user_id:
            print("\n✗ Failed to authenticate. Check your token.")
            return

        print(f"ℹ  Your user ID: {user_id}\n")

        # If specific channel links provided, process only those
        if channel_links:
            print(f"✓ Processing {len(channel_links)} specific channel(s)")
            if date_filter:
                print(f"ℹ  Date filter: {date_filter}")
            if keywords:
                print(f"ℹ  Keywords: {', '.join(keywords)}")
            for link in channel_links:
                parsed = self.parse_channel_link(link)
                if parsed:
                    guild_id, channel_id = parsed
                    self.process_specific_channel(
                        guild_id,
                        channel_id,
                        user_id,
                        date_filter=date_filter,
                        keywords=keywords
                    )
                    time.sleep(1)
                else:
                    print(f"✗ Invalid channel link: {link}")
        else:
            # Original behavior: search all guilds and DMs
            guilds = self.get_guilds()
            print(f"\n✓ Found {len(guilds)} guild(s)")

            # Process each guild
            for guild in guilds:
                self.process_guild(guild, user_id)
                time.sleep(1)  # Delay between guilds

            # Process DM channels
            self.process_dm_channels(user_id)

        print("\n" + "=" * 60)
        print("✓ Completed!")
        print("=" * 60)


def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get Discord token (required)
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("❌ Error: DISCORD_TOKEN not found in .env file")
        print("Please create a .env file with your Discord token.")
        print("See .env.example for template.")
        sys.exit(1)

    # Get channel links (optional, comma-separated)
    channel_links_str = os.getenv("CHANNEL_LINKS", "")
    CHANNEL_LINKS = [link.strip() for link in channel_links_str.split(",") if link.strip()]

    # Get keywords (comma-separated)
    keywords_str = os.getenv("KEYWORDS", "birthday,HBD,sinh nhật")
    KEYWORDS = [keyword.strip() for keyword in keywords_str.split(",") if keyword.strip()]

    # Get date filter (optional)
    DATE_FILTER = os.getenv("DATE_FILTER", "").strip() or None

    # Get reaction emojis (comma-separated)
    emojis_str = os.getenv("REACTION_EMOJIS", "❤️,💖,🚀")
    REACTION_EMOJIS = [emoji.strip() for emoji in emojis_str.split(",") if emoji.strip()]

    # Get delay settings
    try:
        DELAY_MIN = float(os.getenv("REACTION_DELAY_MIN", "1.0"))
        DELAY_MAX = float(os.getenv("REACTION_DELAY_MAX", "2.0"))
    except ValueError:
        print("⚠ Warning: Invalid delay values in .env, using defaults (1.0-2.0s)")
        DELAY_MIN = 1.0
        DELAY_MAX = 2.0

    # Create reactor instance with configuration
    reactor = DiscordReactor(
        token=TOKEN,
        reaction_emojis=REACTION_EMOJIS,
        delay_min=DELAY_MIN,
        delay_max=DELAY_MAX
    )

    # Run the reactor
    if CHANNEL_LINKS:
        reactor.run(channel_links=CHANNEL_LINKS, date_filter=DATE_FILTER, keywords=KEYWORDS)
    else:
        print("\nℹ  No specific channels provided. Searching all accessible channels...")
        print("   To search specific channels only, add CHANNEL_LINKS to .env file.\n")
        reactor.run(date_filter=DATE_FILTER, keywords=KEYWORDS)


if __name__ == "__main__":
    main()
