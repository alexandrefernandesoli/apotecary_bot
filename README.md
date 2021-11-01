# Bot Loja do Xamã (Apotecário) 🧙‍♂️🍯🌿

Nessa loja você encontrará desde poções até dentes de dragões, para os mais bem aventurados aventureiros. 🐲

# Funcionamento do bot

O bot foi implementado com duas opção, uma funciona com base no terminal e outra é a integração com a API do telegram

## Primeira opção

É possivel executar o bot pela linha de comando, utilizando os comandos:

```
pip install -r requirements.txt
python main.py
```

Será impresso no terminal uma tela:

```
#####################
[0] Falar com o bot
[1] Adicionar nova sentença no corpus
[2] Obter pontuações
[ANYO] Sair
#####################
```

Digite **_0_** e pressione ENTER para iniciar a conversação com o bot.

Exemplo de uma conversa:

```
############# Falando com o bot #############
.: Bom dia
- Bem vindo ao Apotecário do Xamã 🧙‍♂️, em que podemos lhe ajudar?
.: Me vê o catalogo
- Aqui vai nosso catálogo:
- Poção analgésica - $5
- Poção de vida - $5
- Poção de mana - $5
- Poção de virilidade - $5
- Poção do amor - $5
- Erva dos sonhos - $3
- Erva da fome - $3
- Raíz de mandrágora - $150
- Dente de dragão - $150
- Pena de fênix - $150
.: Vo querer duas raizes de mandrágora
- Anotado, seu pedido até agora:
2 Raízes de mandrágora
.: Quanto deu tudo?
- Seu pedido deu 300 moedas, você pode realizar seu pagamento por este link <link aqui ;D>
.: Obrigado
- Obrigado pela sua visita ao Apotecário do Xamã 🧙‍♂️, volte sempre.
```

## Segunda opção

A implementação do telegram está no arquivo `telebot_integration.py`, um arquivo `.env` é necessário para conexão a API do telegram, nele é guardado o token de acesso do bot `BOT_TOKEN`

[Video de demonstração do funcionamento](https://youtu.be/Xq00OiVsFRw)

Com a implementação feita, onde a persintência de dados é feita em um arquivo, seria necessário subir para um host cloud, então esse passo não foi feito e o teste foi realizado em `localhost`.

Para realizar o teste em localhost:

- Criar um bot com o `BotFather` do próprio telegram
- Copiar o token de API e colocar no `.env`
- Executar o arquivo com: `python telebot_integration.py`
- Conversar com o bot e ser feliz

## Catálogo 📜

- Poção analgésica - 💲5
- Poção de vida - 💲5
- Poção de mana - 💲5
- Poção de virilidade - 💲5
- Poção do amor - 💲5
- Erva dos sonhos - 💲3
- Erva da fome - 💲3
- Raiz de mandrágora - 💲150
- Dente de dragão - 💲150
- Pena de fenix - 💲150
