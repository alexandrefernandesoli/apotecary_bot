import json
import unicodedata

def remove_accents(input_str):
  nfkd_form = unicodedata.normalize('NFKD', input_str)
  only_ascii = nfkd_form.encode('ASCII', 'ignore')
  return only_ascii.decode('utf-8')

def quantity_convert(quantity: str) -> int:
  try:
    return int(quantity)
  except Exception:
    if quantity == 'um':
      return 1
    elif quantity == 'uma':
      return 1
    elif quantity == 'dois':
      return 2
    elif quantity == 'duas':
      return 2
    elif quantity == 'tres':
      return 3
    elif quantity == 'quatro':
      return 4
    elif quantity == 'cinco':
      return 5
    elif quantity == 'seis':
      return 6
    elif quantity == 'sete':
      return 7
    elif quantity == 'oito':
      return 8
    elif quantity == 'nove':
      return 9
    elif quantity == 'dez':
      return 10

def get_catalog():
  catalog = json.load(open('catalog.json', 'r', encoding='utf8'))

  return catalog

def print_catalog():
  catalog = get_catalog()

  catalog_string = ''

  for item in catalog:
    catalog_string = catalog_string + '{} - ${}\n'.format(item['name_singular'], item['value'])

  return catalog_string


def print_order(order):
  order_string = ''

  for order_item in order:
    if order_item['quantity'] > 1:
      order_string = order_string + '{} {}\n'.format(order_item['quantity'], order_item['name_plural'])
    else:
      order_string = order_string +  '{} {}\n'.format(order_item['quantity'], order_item['name_singular'])

  return order_string
