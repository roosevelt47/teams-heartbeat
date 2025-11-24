# Teams Heartbeat

Look, we've all been there - you step away for a bit and suddenly you're "away" on Teams. This bot keeps you looking active by editing a single message with the current time every few minutes ;)

## What it does

Sends one message to your self-chat that says "Active - 12:34:56 PM" and keeps updating it. That's it. Clean and simple.

## Requirements

- Python 3.7+
- Microsoft Edge
- Windows

## Setup

Install stuff:

```powershell
pip install -r requirements.txt
playwright install chromium
```

## Usage

Just double-click `daily_bot.bat` and follow the prompts :)

That's it. The batch file opens Edge, lets you login, saves your session, and starts the bot.

## Configuration

Open `teams_heartbeat.py` and change these at the top:

```python
YOUR_EMAIL = "your.email@company.com"  # Your work email
LOOP_SLEEP_MS = 180000  # How often to update (3 mins default)
RUN_HOURS = 8           # How long to run
```

## Files you care about

- `daily_bot.bat` - Run this every morning, does everything
- `teams_heartbeat.py` - The actual bot (headless)
- `teams_heartbeat_headed.py` - Same thing but you can watch it work
- `save_session.py` - Saves your login so you don't have to re-login every time

## Common issues

**Session expired?** Run `save_session.py` again while logged into Teams.

**Can't find the message box?** Make sure you're in your self-chat. The headed version helps debug this.

**Bot keeps failing?** You probably navigated away from the chat or got a popup. It'll keep retrying every 10 seconds.

## Notes

- Runs for 8 hours by default (full work day)
- Updates every 3 minutes (not too frequent, not too slow)
- Press Ctrl+C to stop anytime
- Your session gets saved to `teams_session_backup.json`

---

## License

MIT License - do whatever you want with this code!

**Disclaimer:** Use this responsibly. Check your company's policies first - I'm not responsible if they have issues with it!
