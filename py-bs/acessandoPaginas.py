#!/usr/bin/python

import io
import json
import time
import requests
from bs4 import BeautifulSoup
import sys

sys.stdout = open("output_dumps", "w")

paginas = []
todas_despesas = []
dados_requisicao = False


def indice_paginador(pagina):
    indice = 0

    if pagina < 12:
        indice = pagina - 1

    else:
        indice = pagina % 10

        if indice < 2:
            indice += 10

    str_indice = str(indice)

    if len(str_indice) == 1:
        str_indice = '0' + str_indice

    return str_indice


def pagina(params):
    r = False
    despesas = []

    if params:
        pagina = params['pagina']
        indice = indice_paginador(pagina)

        dados = {
            '__VIEWSTATE': params['viewState'],
            '__VIEWSTATEGENERATOR': '48B4125A',
            '__EVENTVALIDATION': params['eventValidation'],
            '__EVENTTARGET':
                'ctl00$ContentPlaceHolder1$dpNoticia$ctl01$ctl' + indice,
            'ctl00$ContentPlaceHolder1$ToolkitScriptManager1': 'ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$dpNoticia$ctl01$ctl' + indice
        }

        r = requests.post('http://www.cms.ba.gov.br/despesa.aspx', data=dados)

    else:
        r = requests.get('http://www.cms.ba.gov.br/despesa.aspx')

    parsed_html = BeautifulSoup(r.text, 'html.parser')

    paginador = parsed_html.body.find(
        'span',
        attrs={'id': 'ContentPlaceHolder1_dpNoticia'}
    )
    pagina_atual = int(paginador.find('span').text)
    links_paginas = paginador.find_all('a')

    tem_proxima = False
    strListaPaginas = ''
    contador_interacao_paginador = 0

    for link in links_paginas:
        contador_interacao_paginador += 1
        strListaPaginas += link.text + ' '

        if not tem_proxima:
            if link.text.isnumeric() and \
                    pagina_atual and int(link.text) > pagina_atual:
                tem_proxima = True

            elif contador_interacao_paginador > 2 and link.text == '...':
                tem_proxima = True

    novo_view_state = parsed_html.body.find(
        'input',
        attrs={'id': '__VIEWSTATE'}
    )["value"]
    novo_event_validation = parsed_html.body.find(
        'input',
        attrs={'id': '__EVENTVALIDATION'}
    )["value"]

    area_despesas = parsed_html.body.find(
        'div',
        attrs={'id': 'ContentPlaceHolder1_UpdatePanel1'}
    )
    divs_internas = area_despesas.find_all('div')
    i = 0

    for a in divs_internas:
        i += 1

        if len(divs_internas) - 5 < i < len(divs_internas):
            despesas.append(a)

    return ({
        'despesas': despesas,
        'temMais': tem_proxima,
        'paginas': strListaPaginas,
        'viewState': novo_view_state,
        'paginaAtual': pagina_atual,
        'eventValidation': novo_event_validation
    })


def valor(dados):
    return dados.replace('R$', '').replace('.', '').replace(',', '.').strip()


def data(dados):
    array = dados.split('/')

    if len(array) != 3:
        return dados

    return array[2]+'-'+array[1]+'-'+array[0]


def conteudo_de(lista, dado):
    encontrou = False
    texto_encontrado = ''

    for texto in lista:
        if encontrou:
            texto_encontrado = texto
            break

        if str(texto).lower().find(dado.lower()) > -1:
            encontrou = True

    return texto_encontrado.strip()


def processar_despesas(lista, numero_pagina):
    retorno = []

    for despesa in lista:
        dados = {}
        array_dados = despesa.contents
        dados['Data'] = data(conteudo_de(array_dados, 'DATA'))
        dados['Tipo'] = conteudo_de(array_dados, 'tipo')
        dados['Responsavel'] = conteudo_de(array_dados, 'Responsável')
        dados['Usuario'] = conteudo_de(array_dados, 'Usuário')
        dados['Valor'] = valor(conteudo_de(array_dados, 'valor'))
        dados['Localidade'] = conteudo_de(array_dados, 'Localidade')
        dados['Justificativa'] = conteudo_de(array_dados, 'Justificativa')
        dados['Pagina'] = numero_pagina
        retorno.append(dados)

    return retorno


def gerar_json(lista, arquivo):
    print( ' ** Gerando '+arquivo )
    try:
        to_unicode = unicode
    except NameError:
        to_unicode = str

    data = {'lista': lista}

    with io.open(arquivo, 'w', encoding='utf8') as outfile:
        str_ = json.dumps(data,
                          indent=4, sort_keys=True,
                          separators=(',', ': '), ensure_ascii=False)
        outfile.write(to_unicode(str_))


def format_coluna_csv(valor):
    return str(valor).replace('\r', ' ').replace('\n', ' ').replace(';', '\\;')


def gerar_csv(lista, arquivo):
    print( ' ** Gerando '+arquivo )

    f = open(arquivo, 'w')
    f.write( 'Data;Valor;Tipo;Responsavel;Usuario;Localidade;Justificativa;Pagina\n' )

    for despesa in lista:
        linha = format_coluna_csv(despesa['Data'])
        linha = linha + ';' + format_coluna_csv(despesa['Valor'])
        linha = linha + ';' + format_coluna_csv(despesa['Tipo'])
        linha = linha + ';' + format_coluna_csv(despesa['Responsavel'])
        linha = linha + ';' + format_coluna_csv(despesa['Usuario'])
        linha = linha + ';' + format_coluna_csv(despesa['Localidade'])
        linha = linha + ';' + format_coluna_csv(despesa['Justificativa'])
        linha = linha + ';' + format_coluna_csv(despesa['Pagina'])
        f.write(linha+'\n')


while True:
    retorno = pagina(dados_requisicao)
    despesas_da_pagina = processar_despesas(retorno['despesas'], retorno['paginaAtual'])
    paginas.append({
        'numero': retorno['paginaAtual'],
        'listaDespesas': despesas_da_pagina
    })

    todas_despesas = todas_despesas + despesas_da_pagina

    print(' ** HTML ' + str(retorno['paginaAtual']))

    if not retorno['temMais']:
        break

    dados_requisicao = {
        'pagina': retorno['paginaAtual'] + 1,
        'viewState': retorno['viewState'],
        'eventValidation': retorno['eventValidation']
    }

    time.sleep(0.2)

gerar_json(todas_despesas, 'despesas.json')
gerar_csv(todas_despesas, 'despesas.csv')

print( ' --- FIM --- ' )
