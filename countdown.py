import telebot
import time
import datetime
import time
import pytz
import threading
from flask import Flask

# Replace with your Telegram bot token
BOT_TOKEN = "6753975076:AAFf1NSPNj9pFfLjnL1Wo2c54n4WOfNcBao"
# Replace with your Telegram user ID
USER_ID = 6897739611

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Target date for the countdown
TARGET_DATE = datetime.date(2025, 8, 27)

# Indian Standard Time timezone
IST = pytz.timezone("Asia/Kolkata")

# Global flag to indicate bot status
bot_status = {"active": True}

# Flask app for keep-alive
app = Flask('')

@app.route('/')
def home():
    return "I am alive"

def run_http_server():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run_http_server)
    t.start()

def calculate_days_remaining():
    """Calculates the days remaining to the target date."""
    today = datetime.date.today()
    days_remaining = (TARGET_DATE - today).days
    return days_remaining

def wait_until_midnight():
    """Waits until the next midnight IST."""
    now = datetime.datetime.now(IST)
    next_midnight = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    wait_seconds = max(0, (next_midnight - now).total_seconds())
    time.sleep(wait_seconds)

def send_daily_message():
    """Sends the countdown message daily at 12 AM IST."""
    while True:
        try:
            # Wait until 12 AM IST
            wait_until_midnight()
            
            # Calculate remaining days
            days_remaining = calculate_days_remaining()
            
            # Compose message
            if days_remaining > 0:
                message = f"Countdown to 27 August 2025: {days_remaining} days remaining."
            elif days_remaining == 0:
                message = "Today is the day: 27 August 2025!"
            else:
                message = "The countdown has ended!"

            # Send the message
            bot.send_message(USER_ID, message)

        except Exception as e:
            # Log errors and notify the user
            error_message = f"An error occurred: {e}"
            bot.send_message(USER_ID, error_message)
            time.sleep(60)  # Retry after 60 seconds

@bot.message_handler(commands=["count"])
def handle_count(message):
    """Handles the /count command to calculate days until a specified date."""
    if message.chat.id == USER_ID:
        try:
            # Extract date from the message text
            user_input = message.text.split(" ", 1)
            if len(user_input) < 2:
                bot.send_message(USER_ID, "Please provide a date in the format DD-MM-YYYY, DD-MMM-YYYY, or DD-MMMM-YYYY.")
                return
            
            date_str = user_input[1].strip()

            # Parse the date
            try:
                # Try different formats
                for fmt in ("%d-%m-%Y", "%d-%b-%Y", "%d-%B-%Y"):
                    try:
                        target_date = datetime.datetime.strptime(date_str, fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    raise ValueError("Invalid date format.")
                
                # Calculate days remaining
                today = datetime.date.today()
                days_remaining = (target_date - today).days
                
                # Compose response
                if days_remaining > 0:
                    response = f"The date {target_date.strftime('%d-%B-%Y')} is in {days_remaining} days."
                elif days_remaining == 0:
                    response = f"Today is the day: {target_date.strftime('%d-%B-%Y')}!"
                else:
                    response = f"The date {target_date.strftime('%d-%B-%Y')} was {-days_remaining} days ago."

                # Send response
                bot.send_message(USER_ID, response)

            except ValueError:
                bot.send_message(USER_ID, "Invalid date format. Please use DD-MM-YYYY, DD-MMM-YYYY, or DD-MMMM-YYYY.")

        except Exception as e:
            bot.send_message(USER_ID, f"An error occurred: {e}")
            
import time

@bot.message_handler(commands=["status"])
def handle_status(message):
    """Responds to /status command, deletes the user's command, and both bot's messages after 3 seconds."""
    if message.chat.id == USER_ID:
        # Send the status message
        status_message = "Bot is active and running."
        sent_status_message = bot.send_message(USER_ID, status_message)
        
        time.sleep(3)

         # Delete the user's /status command message
      
        bot.delete_message(USER_ID, message.message_id)

        # Wait for 3 seconds before deleting both messages
        time.sleep(1)

        # Delete both the bot's messages
        bot.delete_message(USER_ID, sent_status_message.message_id)
        bot.delete_message(USER_ID, status_command_message.message_id)



if __name__ == "__main__":
    # Start the daily message thread
    threading.Thread(target=send_daily_message, daemon=True).start()
    
    # Keep the HTTP server alive
    keep_alive()
    
    # Run the bot polling loop with error handling
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Error occurred in polling: {str(e)}")
            time.sleep(5)  # Retry after a brief pause
