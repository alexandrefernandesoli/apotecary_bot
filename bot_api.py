import json
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import accuracy_score, precision_score, recall_score

from utils import remove_accents

CORPUS_JSON_FILE = 'intentions.json'

def read_json():
  '''
    Lê o arquivo JSON de intenções (CORPUS), retorna uma lista com as sentences, uma com as tags (intentions), e um objeto no formato do JSON.
  '''

  json_file = open(CORPUS_JSON_FILE, 'r', encoding='utf8')
  json_data = json.load(json_file)

  intentions = json_data['intentions']
  sentences = []
  tags = []

  for intention in intentions:
    sentences.extend(intention['sentences'])
    tags.extend([intention['tag']] * len(intention['sentences']))

  return sentences, tags, json_data

def write_to_json(data):
  '''
    Função para escrever no arquivo JSON, usada na função para adicionar novas sentences
  '''
  json.dump(data, open(CORPUS_JSON_FILE, 'w', encoding='utf8'), ensure_ascii=False, indent=2)

def add_new_sentence(data, tag, sentence):
  '''
    Adiciona nova sentence no objeto que vêm do JSON.
  '''

  # Procura a tag especificada e garante que nenhuma frase repetida é adicionada
  for intention in data['intentions']:
    if intention['tag'] == tag and sentence not in intention['sentences']: intention['sentences'].append(sentence)

  return data

def init_model():
  '''
  Inicia model e vectorizer com KNN
  '''
  sentences, tags, json_data = read_json()

  vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5, strip_accents='unicode')
  x = vectorizer.fit_transform(sentences)
  y = np.array(tags)

  model = KNeighborsClassifier(n_neighbors=1)
  model.fit(x, y)

  return model, vectorizer, x, y, json_data

def get_scores():
  '''
    Função que pega scores, com KNN e Decision Tree
  '''
  _, _, x, y, _ = init_model()

  loo = LeaveOneOut()

  ## Á partir aqui testando com arvore de decisão
  y_true_tree = np.array([])
  y_pred_tree = np.array([])

  for train_index, test_index in loo.split(x):
    x_train, x_test = x[train_index], x[test_index]
    y_train, y_test = y[train_index], y[test_index]

    tree_model = DecisionTreeClassifier()
    tree_model.fit(x_train,y_train)

    y_true_tree = np.append(y_true_tree, y_test)
    y_pred_tree = np.append(y_pred_tree, tree_model.predict(x_test))

  acc_score = accuracy_score(y_true_tree, y_pred_tree)
  prec_score = precision_score(y_true_tree, y_pred_tree, average='weighted')
  rec_score = recall_score(y_true_tree, y_pred_tree, average='weighted')

  data_frame = pd.DataFrame({
    'Accuracy score': [acc_score],
    'Precision score': [prec_score],
    'Recall score': [rec_score]
  }, index=pd.Index(['Decision tree']))

  # Testando KNN com N_NEIGHBORS DE 1 A 9
  for i in range(1, 10):
    y_true_k = np.array([])
    y_pred_k = np.array([])

    for train_index, test_index in loo.split(x):
      x_train, x_test = x[train_index], x[test_index]
      y_train, y_test = y[train_index], y[test_index]

      k_model = KNeighborsClassifier(n_neighbors=i)
      k_model.fit(x_train,y_train)

      y_true_k = np.append(y_true_k, y_test)
      y_pred_k = np.append(y_pred_k, k_model.predict(x_test))

    acc_score = accuracy_score(y_true_k, y_pred_k)
    prec_score = precision_score(y_true_k, y_pred_k, average='weighted')
    rec_score = recall_score(y_true_k, y_pred_k, average='weighted')

    data_frame = data_frame.append(pd.DataFrame({
      'Accuracy score': [acc_score],
      'Precision score': [prec_score],
      'Recall score': [rec_score]
    }, index=pd.Index(['KNN(N_NEIGHBORS={})'.format(i)])))

  # Imprime dataFrame com todos scores (Tabela)
  print(data_frame)

  best_acc = 'Best Accuracy: {} - ({})'.format(data_frame['Accuracy score'].idxmax(), data_frame['Accuracy score'].max())
  best_prec = 'Best Precision: {} - ({})'.format(data_frame['Precision score'].idxmax(), data_frame['Precision score'].max())
  best_rec = 'Best Recall Score: {} - ({})'.format(data_frame['Recall score'].idxmax(), data_frame['Recall score'].max())

  print(best_acc)
  print(best_prec)
  print(best_rec)

def intention_recognizer(sentence: str) -> str:
  '''
    Reconhece a intenção da frase
  '''
  model, vectorizer, _,_,_ = init_model()

  if sentence == '': return

  inst = vectorizer.transform([sentence])
  pred = model.predict(inst)

  return pred[0]

def new_sentence():
  '''
    Função usada para adicionar novas sentenças ao corpus
  '''
  while True:
    model, vectorizer, _,_, json_data = init_model()
    sentence = input('Sentence: ')

    if sentence == '': continue

    inst = vectorizer.transform([sentence])
    pred = model.predict(inst)
    print(pred)

    is_true = input('OK? [Y/(right intention)]: ')

    if is_true != '' and (is_true == 'Y' or is_true == 'y'):
      json_data = add_new_sentence(json_data, pred, sentence)
      write_to_json(json_data)
    else:
      rightIntention = is_true

      if(rightIntention != ''):
        json_data = add_new_sentence(json_data, rightIntention, sentence)
        write_to_json(json_data)
    

def entity_recognizer(sentence: str):
  '''
    Processa a sentença do usuário quando detectada a intenção de fazer um pedido, categoriza os items e quantidade encontrada na frase
  '''

  dictionary = {
    'potions': ['pocao', 'pocoes', 'analgesica', 'analgesicas', 'vida', 'mana', 'virilidade', 'amor'],
    'herbs':  ['erva', 'ervas', 'sonhos', 'sonho', 'fome', 'fomes'],
    'misc': ['raiz', 'raizes', 'mandragora', 'dente', 'dentes', 'dragao', 'dragoes','pena', 'penas', 'fenix'],
    'number': ['1','2','3','4','5','6','7','8','9','10','um', 'uma','dois','duas','tres','quatro','cinco','seis','sete','oito','nove','dez']
  }

  splitted_word = sentence.split()

  items = []

  for word in splitted_word:
    for section in dictionary:
      if remove_accents(word) in dictionary[section]:
        items.append([section, remove_accents(word)])

  items_splitted = [items[x:x+3] for x in range(0, len(items), 3)]

  raw_order = []

  for order in items_splitted:
    real_order = {
      'names': [],
    }

    for order_item in order:
      if order_item[0] == 'number':
        real_order['quantity'] = order_item[1]
      else:
        real_order['category'] = order_item[0]
        real_order['names'].append(order_item[1])

    if 'quantity' not in real_order:
      real_order['quantity'] = '1'

    raw_order.append(real_order)
  
  return raw_order
