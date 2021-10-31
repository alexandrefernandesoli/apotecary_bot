from bot_api import new_sentence, get_scores, intention_recognizer, entity_recognizer
from utils import get_catalog, print_catalog, quantity_convert


def look_for_order_item(order, item_id):
  for order_item in order:
    if order_item['item_id'] == item_id:
      return order_item

  return None

def register_new_order(order, sentence):
  catalog = get_catalog()

  new_raw_order = entity_recognizer(sentence)

  for order_item in new_raw_order:
    singular_order = {}

    # Descobre o que é o pedido
    for item_name in order_item['names']:
      for catalog_item in catalog:
        if item_name in catalog_item['keywords']:
          singular_order['item_id'] = catalog_item['id']
          singular_order['name_singular'] = catalog_item['name_singular']
          singular_order['name_plural'] = catalog_item['name_plural']
          singular_order['value'] = catalog_item['value']

    if 'item_id' in singular_order:
      singular_order['category'] = order_item['category']
      singular_order['quantity'] = quantity_convert(order_item['quantity'])

      same_order = look_for_order_item(order, singular_order['item_id'])
      if same_order:
        same_order['quantity'] += singular_order['quantity']
      else:
        order.append(singular_order)

  return order

def calc_order_price(order):
  price = 0
  for item in order:
    price += item['value'] * item['quantity']

  return price

def print_order(order):
  for order_item in order:
    if order_item['quantity'] > 1:
      print('{} {}'.format(order_item['quantity'], order_item['name_plural']))
    else:
      print('{} {}'.format(order_item['quantity'], order_item['name_singular']))


def bot_loop():
  active = True
  has_order = False
  greeted = False

  last_bot = 'none'

  order = []
  

  while active:
    sentence = input('.: ')

    intention = intention_recognizer(sentence)

    if intention == 'greetings':
      print(bot_responses['greetings'])
      greeted = True
      last_bot = 'greetings'
    elif intention == 'menu':
      if not greeted: 
        print('- Bem vindo ao Apotecário do Xamã 🧙‍♂️, em que podemos lhe ajudar?')
        greeted = True

      bot_response = '- Aqui vai nosso catálogo:'
      print(bot_response)
      print_catalog()
      last_bot = 'menu_sent'
    elif intention == 'new_order':
      order = register_new_order(order, sentence)

      print('- Anotado, seu pedido até agora:')
      print_order(order)
      has_order = True
      last_bot = 'order_registered'
    elif intention == 'checkout':
      if not has_order:
        bot_response = '- Hmmm... você ainda não fez uma compra, de uma olhada em nosso catálogo:'
        print(bot_response)
        print_catalog()
        last_bot = 'menu_sent'
      else:
        # Calcula valor do pedido e manda
        price = calc_order_price(order)
        bot_response = '- Seu pedido deu {} moedas'.format(price)
        print(bot_response)
        last_bot = 'checkout_sent'
    elif intention == 'goodbye':
      if has_order:
        print('- Você ainda não finalizou a sua compra, deseja cancelar tudo? 😅')
        last_bot = 'order_open_error'
      else:
        print('- Obrigado pela sua visita ao Apotecário do Xamã 🧙‍♂️, volte sempre. 😃')
        active = False
        order = []
        last_bot = 'none'
    elif intention == 'affirmative':
      if last_bot == 'order_open_error':
        print('- Tudo bem, até a próxima 😥')
        active = False
        order = []
        last_bot = 'none'
    elif intention == 'negative':
      if last_bot == 'order_open_error':
        print('- Hmmm, vamos continuar de onde paramos então, sua compra até agora é essa:')
        print_order(order)
        print('- Deseja mais alguma coisa?')
        last_bot = 'none'
    

def main():
  print("#" * 21)
  print("[1] Add new sentences")
  print("[2] Scores")
  print("[0] Talk With Bot")
  print("[ANYO] Exit")
  print("#" * 21)

  op = input()

  if op == '0':
    print('Falando com o bot: \n')
    bot_loop()
  elif op == '1':
    new_sentence()
  elif op == '2':
    get_scores()

  

if __name__ == "__main__":
  main()


