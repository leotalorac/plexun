
from dep.rgx_engine import  RGXGRMM
from dep.NFA import NFA
import json

automatas = []

def __main__():

	entrada = open('asd', 'r').readlines()
	js = open('out.json', 'r').read()

	crearAutomatas(json.loads(js))
	salida = evaluarLineas(entrada)

	with open('tokens.tun', 'w') as o:
		o.write(salida)


def crearAutomatas(jA):
	for aut in jA:
		automatas.append(RGXGRMM(aut, aut['token']).automata)

def evaluarLineas(lineas):
	res = ''
	for linea in lineas:
		for palabra in linea.split(' '):
			for automata in automatas:
				if automata.reco(palabra):
					res += automata.token + ' '

	return res


__main__()