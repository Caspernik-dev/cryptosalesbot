# CryptoSalesBot

### Overview
CryptoSalesBot is a Telegram bot designed to track cryptocurrency trades and provide detailed notifications for trades meeting certain criteria. The bot integrates with an API to fetch trade data and sends real-time updates via Telegram, offering transaction details and custom graphics based on trade volume.

### Features
- Tracks trades from an API in real time.
- Sends trade details with custom animations based on trade volume.
- Includes flood control handling to avoid Telegram rate limits.
- Supports commands to start, restart, and interact with the bot.

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the bot:
   - Set your `token` and `chat_id` in the script.
   - Update the `API_URL` with the endpoint for fetching trade data.

4. Run the bot:
   ```bash
   python cryptosalesbot.py
   ```

### Commands
- `/startsales` - Start tracking cryptocurrency trades.
- `/restartsales` - Restart the bot and clear previous tasks.
- Send "ca" - Get the contract address of the token.

### Requirements
- Python 3.8+
- Libraries (specified in `requirements.txt`):
  - `urllib3`
  - `python-telegram-bot`
  - `asyncio`
