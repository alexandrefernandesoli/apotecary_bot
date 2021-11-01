from bot_api import new_sentence, get_scores, intention_recognizer, entity_recognizer
from utils import get_catalog, quantity_convert

def look_for_order_item(order, item_id):
  '''
    Procura por item no pedido, usado para aumentar a quantidade ao invés de repetir o mesmo
  '''
  for order_item in order:
    if order_item['item_id'] == item_id:
      return order_item

  return None

def register_new_order(order, sentence):
  '''
    Registra novo pedido
  '''
  catalog = get_catalog()

  new_raw_order = entity_recognizer(sentence)

  # Itera nos items encontrados na frase cada item é composto por
  # 2 palavras que definem o item + 1 palavra que define a quantidade
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

    # Aqui ocorreu algum erro (algo errado na frase), a ordem não é registrada
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
  '''
    Calcula o valor do pedido
  '''
  price = 0
  for item in order:
    price += item['value'] * item['quantity']

  return price

def print_order(order):
  '''
    Imprime o pedido atual na tela
  '''
  for order_item in order:
    if order_item['quantity'] > 1:
      print('- {} {}'.format(order_item['quantity'], order_item['name_plural']))
    else:
      print('- {} {}'.format(order_item['quantity'], order_item['name_singular']))

def print_catalog():
  '''
    Formata catálogo, que se encontra em catalog.json, para uma só string
  '''
  catalog = get_catalog()
  catalog_string = ''

  for item in catalog:
    catalog_string = catalog_string + '- {} - ${}\n'.format(item['name_singular'], item['value'])

  return catalog_string

def bot_loop():
  '''
    Função principal que faz o loop do bot
  '''
  active = True
  has_order = False
  greeted = False

  last_bot = 'none'

  last_order = []
  actual_order = []
  

  while active:
    sentence = input('.: ')

    intention = intention_recognizer(sentence)

    # Intenção detectada foi a "inicial"
    if intention == 'greetings':
      print('- Bem vindo ao Apotecário do Xamã 🧙‍♂️, em que podemos lhe ajudar?')
      greeted = True
      last_bot = 'greetings'
    # Intenção detectada foi um pedido pelo catálogo
    elif intention == 'menu':
      if not greeted: 
        print('- Bem vindo ao Apotecário do Xamã 🧙‍♂️')
        greeted = True

      bot_response = '- Aqui vai nosso catálogo:'
      print(bot_response)
      print(print_catalog())
      last_bot = 'menu_sent'
    # Intenção detectada foi a de registrar um pedido
    elif intention == 'new_order':
      last_order = actual_order.copy()
      actual_order = register_new_order(actual_order, sentence)
      print('- Anotado, seu pedido até agora:')
      print_order(actual_order)
      has_order = True
      last_bot = 'order_registered'
    # Itenção detectada foi de pedir a conta
    elif intention == 'checkout':
      if not has_order:
        bot_response = '- Hmmm... você ainda não fez uma compra, de uma olhada em nosso catálogo:'
        print(bot_response)
        print(print_catalog())
        last_bot = 'menu_sent'
      else:
        # Calcula valor do pedido e manda
        price = calc_order_price(actual_order)
        bot_response = '- Seu pedido deu {} moedas, você pode realizar seu pagamento por este link <link aqui ;D>'.format(price)
        print(bot_response)
        has_order = False
        last_bot = 'checkout_sent'
    # Intenção detectada foi de sair
    elif intention == 'goodbye':
      if has_order:
        print('- Você ainda não finalizou a sua compra, deseja cancelar tudo? 😅')
        last_bot = 'order_open_error'
      else:
        print('- Obrigado pela sua visita ao Apotecário do Xamã 🧙‍♂️, volte sempre.')
        active = False
        order = []
        last_bot = 'none'
    # Intenção afirmativa
    elif intention == 'affirmative':
      # Cliente teve intenção de confirmar a finalização antecipada do pedido (sem pagamento)
      if last_bot == 'order_open_error':
        print('- Tudo bem, até a próxima então 😥')
        active = False
        order = []
        last_bot = 'none'
    # Intenção de negação
    elif intention == 'negative':
      # Cliente teve a intenção de negar a finalização antecipada do pedido
      if last_bot == 'order_open_error':
        print('- Hmmm, vamos continuar de onde paramos então, sua compra até agora é essa:')
        print_order(order)
        print('- Deseja mais alguma coisa?')
        last_bot = 'none'
      # Cliente nega o registro do ultimo pedido
      elif last_bot == 'order_registered':
        actual_order = last_order.copy()
        print('- Beleza, retornando seu pedido ao que era antes:')
        print_order(actual_order)
        last_bot = 'none'
    

def main():
  '''
    Função principal
  '''
  print("#" * 21)
  print("[0] Falar com o bot")
  print("[1] Adicionar nova sentença no corpus")
  print("[2] Obter pontuações")
  print("[ANYO] Sair")
  print("#" * 21)

  op = input()

  if op == '0':
    print('############# Falando com o bot #############')
    bot_loop()
  elif op == '1':
    new_sentence()
  elif op == '2':
    get_scores()
  

if __name__ == "__main__":
  main()


