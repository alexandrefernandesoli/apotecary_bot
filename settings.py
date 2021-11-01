import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

if __name__ == '__main__':
  print(BOT_TOKEN)