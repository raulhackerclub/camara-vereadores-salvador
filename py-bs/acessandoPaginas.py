#!/usr/bin/python

import time
import requests
from bs4 import BeautifulSoup

paginas = []
dadosRequisicao = False

def indicePaginador( pagina ):
	indice = 0

	if pagina < 12:
		indice = pagina - 1

	else:
		indice = pagina % 10

		if indice < 2:
			indice += 10
	
	strIndice = str( indice )

	if len( strIndice ) == 1:
		strIndice = '0'+strIndice

	return strIndice

def pagina( params ):
	r = False
	registros = []

	if params:
		pagina = params['pagina']
		indice = indicePaginador( pagina )
		
		dados = {
			'__VIEWSTATE': params['viewState'],
			'__VIEWSTATEGENERATOR': '48B4125A',
			'__EVENTVALIDATION': params['eventValidation'],
			'__EVENTTARGET': 'ctl00$ContentPlaceHolder1$dpNoticia$ctl01$ctl'+indice,
			'ctl00$ContentPlaceHolder1$ToolkitScriptManager1': 'ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$dpNoticia$ctl01$ctl'+indice
		}

		r = requests.post( 'http://www.cms.ba.gov.br/despesa.aspx', data=dados )

	else:
		r = requests.get( 'http://www.cms.ba.gov.br/despesa.aspx' )

	parsed_html = BeautifulSoup( r.text, 'html.parser' )

	paginador = parsed_html.body.find('span', attrs={'id':'ContentPlaceHolder1_dpNoticia'})
	paginaAtual = int( paginador.find('span').text )
	linksPaginas = paginador.find_all('a')

	temProxima = False
	strListaPaginas = ''
	contadorInteracaoPaginador = 0

	for link in linksPaginas:
		contadorInteracaoPaginador += 1
		strListaPaginas += link.text + ' '

		if not temProxima:
			if link.text.isnumeric() and paginaAtual and int( link.text ) > paginaAtual:
				temProxima = True

			elif contadorInteracaoPaginador > 2 and link.text == '...':
				temProxima = True

	novoViewState = parsed_html.body.find('input', attrs={'id':'__VIEWSTATE'})["value"]
	novoEventValidation = parsed_html.body.find('input', attrs={'id':'__EVENTVALIDATION'})["value"]

	areaDespesas = parsed_html.body.find('div', attrs={'id':'ContentPlaceHolder1_UpdatePanel1'})
	divsInternas = areaDespesas.find_all( 'div' )
	i = 0

	for a in divsInternas:
		i += 1

		if i > len( divsInternas ) - 5 and i < len( divsInternas ):
			registros.append( a.text )

	return ({
		'temMais': temProxima,
		'registros': registros,
		'paginas': strListaPaginas,
		'viewState': novoViewState,
		'paginaAtual': paginaAtual,
		'eventValidation': novoEventValidation
	})

while True:
	retorno = pagina( dadosRequisicao )
	paginas.append({
		'numero': retorno['paginaAtual'],
		'registros': retorno['registros']
	})

	print( ' ** HTML ' + str( retorno['paginaAtual'] ) )

	if not retorno['temMais']:
		break

	dadosRequisicao = {
		'pagina': retorno['paginaAtual']+1,
		'viewState': retorno['viewState'],
		'eventValidation': retorno['eventValidation']
	}

	time.sleep( 0.2 )

print( paginas )
