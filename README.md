# Discord Birthday Message Reactor

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/googlesky/discord-birthday-react.svg)](https://github.com/googlesky/discord-birthday-react/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/googlesky/discord-birthday-react.svg)](https://github.com/googlesky/discord-birthday-react/issues)

Automatically reacts to Discord messages containing "birthday" that mention "Hieu Le" with ❤️, 💖, and 🚀 emojis.

## ⚠️ WARNING

**Using personal Discord tokens for automation violates Discord's Terms of Service and may result in account suspension or ban. Use at your own risk.**

## Installation

1. Install Python 3.7 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

All configuration is now done via a `.env` file for better security and easier management.

### Setup Steps

1. **Copy the example configuration:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file with your settings:**
   ```bash
   nano .env  # or use any text editor
   ```

3. **Required Configuration:**
   - `DISCORD_TOKEN` - Your Discord personal token (required)

4. **Optional Configuration:**
   - `CHANNEL_LINKS` - Specific channels to search (comma-separated URLs)
   - `KEYWORDS` - Words to search for (default: "birthday,HBD,sinh nhật")
   - `DATE_FILTER` - Filter by date ("today", "YYYY-MM-DD", or empty for all)
   - `REACTION_EMOJIS` - Emojis to react with (default: "❤️,💖,🚀")
   - `REACTION_DELAY_MIN` - Minimum delay between reactions (default: 1.0)
   - `REACTION_DELAY_MAX` - Maximum delay between reactions (default: 2.0)

### Example .env Configuration

```env
# Your Discord token (REQUIRED)
DISCORD_TOKEN=your_token_here

# Specific channels to search (optional, comma-separated)
CHANNEL_LINKS=https://discord.com/channels/123/456,https://discord.com/channels/789/012

# Keywords to search for (comma-separated)
KEYWORDS=happy,HBD,sinh nhật,birthday

# Date filter (today, YYYY-MM-DD, or empty)
DATE_FILTER=today

# Reaction emojis (comma-separated)
REACTION_EMOJIS=❤️,💖,🚀

# Delay between reactions (in seconds)
REACTION_DELAY_MIN=1.0
REACTION_DELAY_MAX=2.0
```

## Usage

Once configured, simply run:
```bash
python discord_birthday_reactor.py
```

The script will:
- Read all settings from your `.env` file
- Search for messages matching your keywords
- React to messages that mention you
- Skip messages you've already reacted to

## How to Get Channel Links

1. Open Discord in your browser or desktop app
2. Navigate to the channel you want to search
3. Copy the URL from your browser's address bar
   - Format: `https://discord.com/channels/{server_id}/{channel_id}`
   - For DMs: `https://discord.com/channels/@me/{channel_id}`

## Features

- Searches for messages with configurable keywords ("birthday", "HBD", "sinh nhật", etc.)
- Filters messages that mention you (@Hieu Le)
- Optional date filtering (today, or specific date)
- **Smart reaction checking** - automatically skips messages you've already reacted to
- Adds three reactions: ❤️ (heart), 💖 (rainbow heart), 🚀 (rocket)
- Only adds missing reactions if some are already present
- 1-2 second delay between reactions to avoid rate limiting
- Supports both server channels and DMs
- Can process specific channels or search all accessible channels
- Detailed debug output showing matched messages

## What the Script Does

1. Authenticates using your personal Discord token
2. Searches for messages containing ANY of the specified keywords
3. Filters for messages that mention you (via @mention or plain text)
4. Optionally filters by date (today or specific date)
5. **Checks each message for existing reactions**
   - If all three reactions already exist, skips the message completely
   - If some reactions exist, only adds the missing ones
6. Adds three emoji reactions to each matching message: ❤️ 💖 🚀
7. Waits 1-2 seconds between each reaction to avoid rate limits
8. Shows detailed debug output of what was found

## Notes

- The script only searches the last 100 messages in each channel
- Rate limits are handled automatically with retry logic
- All actions are logged to the console
- Your token is stored in `.env` file (never commit this file!)
- The `.env` file is automatically ignored by git (see `.gitignore`)
- All configuration can be changed without editing the Python code

## Security Best Practices

🔒 **IMPORTANT**: Your Discord token grants full access to your account!

- ✅ **DO**: Keep your `.env` file secure and private
- ✅ **DO**: Never share your `.env` file or Discord token
- ✅ **DO**: Use `.gitignore` to prevent committing `.env`
- ✅ **DO**: Use `.env.example` as a template (without real tokens)
- ❌ **DON'T**: Commit `.env` to version control (git, GitHub, etc.)
- ❌ **DON'T**: Share screenshots showing your token
- ❌ **DON'T**: Hardcode tokens in the Python script

If your token is ever exposed, immediately:
1. Go to Discord → User Settings → Advanced → Developer Mode
2. Regenerate your token
3. Update your `.env` file with the new token

## Troubleshooting

### Authentication Failed
- Check that `DISCORD_TOKEN` is set correctly in `.env`
- Verify your token hasn't expired
- Ensure there are no extra spaces or quotes around the token

### No Messages Found
- Ensure the messages contain at least one of your keywords ("birthday", "HBD", "sinh nhật")
- Check that the messages mention you (via @mention or "Hieu Le" in text)
- The script shows debug output of messages found with keywords but no mention
- The search is case-insensitive
- Only the last 100 messages per channel are searched
- If using date filter, make sure messages are from the specified date

### Rate Limited
- The script will automatically wait when rate limited
- If you get rate limited frequently, increase the delays in the code

## License

Use at your own risk. This script is for educational purposes only.
