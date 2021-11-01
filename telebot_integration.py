import logging
from telegram.ext.filters import Filters

from telegram.ext.messagehandler import MessageHandler
from bot_api import intention_recognizer
from main import calc_order_price, register_new_order
from settings import BOT_TOKEN
from telegram import Update
from telegram.ext import Updater, PicklePersistence, CommandHandler, CallbackContext
from utils import print_catalog, print_order

EXPECT_NAME, EXPECT_BUTTON_CLICK = range(2)

def start(update: Update, context: CallbackContext):
  ''' Responde e comando inicial, necessário para inicio de conversa com bot... '''
  update.message.reply_text('Bem vindo ao Apotecário do Xamã 🧙‍♂️, em que podemos lhe ajudar?')


def sentence_handler(update: Update, context: CallbackContext):
  ''' Responde as mensagens... '''

  # Gambiarra? Talvez, mas funciona: Evita que o contexto inicial seja setado toda vez que recebe uma mensagem, poderia ter sido feito na função start
  # talvez numa proxima
  context.user_data['is_data_ok'] = True

  if not context.user_data['is_data_ok']:
    context.user_data['greeted'] = False
    context.user_data['last_bot'] = 'none'
    context.user_data['last_order'] = []
    context.user_data['actual_order'] = []
    context.user_data['has_order'] = False

  sentence = update.message.text
  intention = intention_recognizer(sentence)

  # Intenção inicial
  if intention == 'greetings':
    context.user_data['greeted'] = True
    context.user_data['last_bot'] = 'greetings'
    update.message.reply_text('Bem vindo ao Apotecário do Xamã 🧙‍♂️, em que podemos lhe ajudar?')
  # Intenção de querer o catálogo
  elif intention == 'menu':
    if not context.user_data.get('greeted'): 
      update.message.reply_text('Bem vindo ao Apotecário do Xamã 🧙‍♂️')
      context.user_data['greeted'] = True

    update.message.reply_text('Aqui vai nosso catálogo:')
    update.message.reply_text(print_catalog())
    
    context.user_data['last_bot'] = 'menu_sent'
  # Intenção de registrar um novo pedido
  elif intention == 'new_order':
    context.user_data['last_order'] = context.user_data.get('actual_order').copy()
    context.user_data['actual_order'] = register_new_order(context.user_data.get('actual_order'), sentence)
    update.message.reply_text('Anotado, seu pedido até agora:')
    update.message.reply_text(print_order(context.user_data['actual_order']))
    context.user_data['has_order'] = True
    context.user_data['last_bot'] = 'order_registered'
  # Itenção detectada foi de pedir a conta
  elif intention == 'checkout':
    if not context.user_data.get('has_order'):
      update.message.reply_text('Hmmm... você ainda não fez uma compra, de uma olhada em nosso catálogo:')
      update.message.reply_text(print_catalog())
      context.user_data['last_bot'] = 'menu_sent'
    else:
      # Calcula valor do pedido e manda
      price = calc_order_price(context.user_data.get('actual_order'))
      update.message.reply_text('Seu pedido deu {} moedas, você pode realizar seu pagamento por este link <link aqui ;D>'.format(price))
      context.user_data['has_order'] = False
      context.user_data['last_bot'] = 'checkout_sent'
  # Intenção detectada foi de sair
  elif intention == 'goodbye':
    if context.user_data.get('has_order'):
      update.message.reply_text('Você ainda não finalizou a sua compra, deseja cancelar tudo? 😅')
      context.user_data['last_bot'] = 'order_open_error'
    else:
      update.message.reply_text('Obrigado pela sua visita ao Apotecário do Xamã 🧙‍♂️, volte sempre.')
      context.user_data['actual_order'] = []
      context.user_data['last_bot'] = 'none'
  # Intenção afirmativa
  elif intention == 'affirmative':
    # Cliente teve intenção de confirmar a finalização antecipada do pedido (sem pagamento)
    if context.user_data.get('last_bot') == 'order_open_error':
      update.message.reply_text('Tudo bem, até a próxima então 😥')
      context.user_data['actual_order'] = []
      context.user_data['last_bot'] = 'none'
  # Intenção de negação
  elif intention == 'negative':
    # Cliente teve a intenção de negar a finalização antecipada do pedido
    if context.user_data.get('last_bot') == 'order_open_error':
      update.message.reply_text('Hmmm, vamos continuar de onde paramos então, sua compra até agora é essa:')
      print_order(context.user_data.get('actual_order'))
      update.message.reply_text('Deseja mais alguma coisa?')
      context.user_data['last_bot'] = 'none'
    # Cliente nega o registro do ultimo pedido
    elif context.user_data.get('last_bot') == 'order_registered':
      context.user_data['actual_order'] = context.user_data.get('last_order').copy()
      update.message.reply_text('Beleza, retornando seu pedido ao que era antes:')
      print_order(context.user_data.get('actual_order'))
      context.user_data['last_bot'] = 'none'

if __name__ == "__main__":
  # Configuração do módulo de persistência de dados, utiliza arquivos aqui...
  pp = PicklePersistence(filename='bot_cache')
  updater = Updater(token=BOT_TOKEN, persistence=pp)
  dispatcher = updater.dispatcher

  logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

  dispatcher.add_handler(CommandHandler('start', start))
  dispatcher.add_handler(MessageHandler(Filters.text, sentence_handler))

  updater.start_polling()
  updater.idle()