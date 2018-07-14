#!/usr/bin/python

import time
import requests
from bs4 import BeautifulSoup

paginas = []
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
    registros = []

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
            registros.append(a.text)

    return ({
        'temMais': tem_proxima,
        'registros': registros,
        'paginas': strListaPaginas,
        'viewState': novo_view_state,
        'paginaAtual': pagina_atual,
        'eventValidation': novo_event_validation
    })


while True:
    retorno = pagina(dados_requisicao)
    paginas.append({
        'numero': retorno['paginaAtual'],
        'registros': retorno['registros']
    })

    print(' ** HTML ' + str(retorno['paginaAtual']))

    if not retorno['temMais']:
        break

    dados_requisicao = {
        'pagina': retorno['paginaAtual'] + 1,
        'viewState': retorno['viewState'],
        'eventValidation': retorno['eventValidation']
    }

    time.sleep(0.2)

print(paginas)
