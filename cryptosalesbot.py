import urllib3
import asyncio
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import json
import time
import re
from datetime import datetime

token = ""
chat_id = ""

volume_in_usd = 0
total_supply =  #total_supply
 API_URL = "" #api link with contract address

bot = Bot(token=token)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
MAX_TRADES_STORED = 70  

####################################################################################

def get_latest_trades():
    http = urllib3.PoolManager()
    try:
        response = http.request('GET', API_URL)
        if response.status == 200:
            data = response.data.decode('utf-8')
            data = json.loads(data)
            if "data" in data and len(data["data"]) > 0:
                return [trade["attributes"] for trade in data["data"]]
        return []
    except urllib3.exceptions.RequestError as e:
        print(f"Error fetching data from API: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error in get_latest_trades: {e}")
        return []

async def send_trade_message(trade):
    try:
        kind = trade["kind"].capitalize()
        tx_hash = trade["tx_hash"]
        from_token_amount = float(trade["from_token_amount"])
        to_token_amount = float(trade["to_token_amount"])
        volume_in_usd = float(trade["volume_in_usd"])
        tx_from_address = trade["tx_from_address"]
        price_to_in_usd = float(trade["price_to_in_usd"])
        
        if kind == "Sell": 
            print(f"Transaction {tx_hash} is of type 'Sell'. Skipping.")
            return
        
        if volume_in_usd is not None and volume_in_usd < 300:
            print(f"Transaction {tx_hash} has USD sum {volume_in_usd:.2f}, below threshold. Skipping.")
            return
        
        hamsters_line = generate_hamsters(volume_in_usd)
        gif_path = select_gif_path(volume_in_usd)
        market_cap_usd = (
            price_to_in_usd * (total_supply / 10**18)
            if price_to_in_usd
            else None
        )
        
        message = (
            f"*Token {kind}* \n"
            f"\n"
            f"{hamsters_line}\n"                
            f"\n"
            f"*Spent:* ${volume_in_usd:.2f} ({from_token_amount:.3f} ETH) \n"
            f"*Got:* {to_token_amount:,.0f} TOKEN\n"
            f"\n"
            f"\U0001F464 [Buyer](https://basescan.org/address/{tx_from_address})\n"
            f"\U0001F4B8 *Market Cap:* ${market_cap_usd:,.0f}\n"
            f"\n"
            f"[TX](https://basescan.org/tx/{tx_hash}) | [Swap](link) | [Chart](link) | [Community](link)"
        )
        await bot.send_animation(chat_id=chat_id, animation=gif_path, caption=message, parse_mode='Markdown')
    except KeyError as e:
        print(f"KeyError while processing trade data: {e}")
    except Exception as e:
        error_message = str(e)
        print(f"Error while sending message for trade {trade['tx_hash']}: {error_message}")
        if "Flood control exceeded" in error_message:
            match = re.search(r'Retry in (\d+) seconds', error_message)
            if match:
                retry_after = int(match.group(1))
                print(f"Flood control error. Pausing for {retry_after} seconds before retrying...")
                await asyncio.sleep(retry_after)  
                await send_trade_message(trade)  
                print(f"Send {tx_hash} after Flood control")

trade_task = None
last_trade_timestamp = None  

async def main():
    global last_trade_timestamp
    all_trades = [] 
    print("Bot is running and waiting for the /startsales command...")

    while True:
        try:
            print(f"Checking for new trades... {len(all_trades)}")
            latest_trades = get_latest_trades()
            if latest_trades:
                if last_trade_timestamp is None:
                    last_trade = latest_trades[0]
                    last_trade_timestamp = datetime.fromisoformat(last_trade["block_timestamp"][:-1])
                    print(f"Sending the most recent trade at start: {last_trade['tx_hash']}")
                    try:
                        await send_trade_message(last_trade)
                    except Exception as e:
                        print(f"Error while sending the most recent trade: {e}")
                    all_trades.append(last_trade)
                else:
                    new_trades = []
                    for trade in latest_trades:
                        trade_timestamp = datetime.fromisoformat(trade["block_timestamp"][:-1])
                        if trade_timestamp <= last_trade_timestamp:
                            break
                        new_trades.append(trade)
                    for trade in reversed(new_trades):
                        await asyncio.sleep(3)
                        print(f"New trade found: {trade['tx_hash']}")
                        try:
                            await send_trade_message(trade)
                            last_trade_timestamp = datetime.fromisoformat(trade["block_timestamp"][:-1])
                        except Exception as e:
                            print(f"Error while sending new trade {trade['tx_hash']}: {e}")
                        all_trades.append(trade)
            if len(all_trades) > MAX_TRADES_STORED:
                excess = len(all_trades) - MAX_TRADES_STORED
                all_trades = all_trades[excess:]
                print(f"[INFO] Trimmed the trades list to the last {MAX_TRADES_STORED} entries. Removed {excess} old trades.")
            await asyncio.sleep(8)
        except Exception as e:
            print(f"Unexpected error in main loop: {e}")
            print("Restarting main loop in 5 seconds...")
            await asyncio.sleep(5)

def generate_hamsters(volume_in_usd):
    try:
        hamsters_count = int(volume_in_usd // 50)
        max_hamsters = 100
        return "\U0001F439" * min(hamsters_count, max_hamsters)
    except Exception as e:
        print(f"Error in generate_hamsters: {e}")
        return "\U0001F439"

def select_gif_path(volume_in_usd):
    try:
        if volume_in_usd <= 300:
            return "gif/1.gif"
        elif 300 < volume_in_usd <= 700:
            return "gif/2.gif"
        elif 700 < volume_in_usd <= 900:
            return "gif/3.gif"
        elif 900 < volume_in_usd <= 1500:
            return "gif/4.gif"
        else:
            return "gif/5.gif"
    except Exception as e:
        print(f"Error in select_gif_path: {e}")
        return "gif/default.gif"

####################################################################################

async def start(update: Update, context):
    global trade_task
    try:
        await update.message.delete()
    except Exception as e:
        print(f"Error deleting user's /startsales command message: {e}")
    if trade_task is not None and not trade_task.done():
        try:
            already_running_message = await update.message.reply_text("Bot is already running.")
            await asyncio.sleep(2)
            await already_running_message.delete()
        except Exception as e:
            print(f"Error sending or deleting 'already running' message: {e}")
        return
    try:
        start_message = await update.message.reply_text("Bot has started tracking trades.")
        await asyncio.sleep(2)
        await start_message.delete()
    except Exception as e:
        print(f"Error sending or deleting start message: {e}")
    if trade_task is None or trade_task.done():
        trade_task = asyncio.create_task(main())

async def restart(update: Update, context):
    global trade_task
    try:
        await update.message.delete()
    except Exception as e:
        print(f"Error deleting user's /restartsales command message: {e}")
    if trade_task is not None and not trade_task.done():
        trade_task.cancel()
        print("Stopping the current task...")
    try:
        restart_message = await update.message.reply_text("Bot has been restarted.")
        await asyncio.sleep(2)
        await restart_message.delete()
    except Exception as e:
        print(f"Error sending or deleting restart message: {e}")
    trade_task = asyncio.create_task(main())
    print("Bot has been restarted.")

async def ca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"BASE $TOKEN `0x23a96680ccde03bd4bdd9a3e9a0cb56a5d27f7c9`",
        parse_mode='Markdown',
        reply_to_message_id=update.message.message_id,
    )

if __name__ == "__main__":
    while True:
        try:
            print("Starting bot...")
            application = ApplicationBuilder().token(token).build()
            start_handler = CommandHandler('startsales', start)
            restart_handler = CommandHandler('restartsales', restart)
            ca_handler = MessageHandler(filters.Regex(r"(?i)\bca\b"), ca)
            application.add_handler(start_handler)
            application.add_handler(restart_handler)
            application.add_handler(ca_handler)
            application.run_polling()
        except Exception as e:
            print(f"Error during bot initialization: {e}")
            print("Restarting bot in 5 seconds...")
            time.sleep(5)
