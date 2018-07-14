# Vereadores

Este projeto é um web scrapper criado em python e scrapy para vasculhar o site do tribunal de contas municipal e regatar os gastos dos vereadores de salvador para fim de pesquisas e observações.

## Instalação

Para rodar o projeto você deve possuir o python 3 instalado, e e instalar as dependências (recomendo usar um virtualenv):

```pip install -r requirements.txt```

## Executar

Para executar o projeto você deve apontar o terminal para a pasta vereadores e rodar o comando:

```scrapy crawl cms -o arquivo.extensão```

Sendo "arquivo" o nome do arquivo que será criado com os dados, e "extensão" o formato do arquivo (json, json lines, csv ou xml).