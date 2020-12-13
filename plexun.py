from dep.NFA import NFA
from dep.rgx_engine import RGXGRMM
import json
import sys


out = []

programa = """

from dep.rgx_engine import  RGXGRMM
from dep.NFA import NFA
import json
import sys

automatas = []

def __main__():
	args = sys.argv

	fl = args[1]

	entrada = open(fl, 'r').readlines()
	js = open('out.json', 'r').read()

	crearAutomatas(json.loads(js))
	salida = evaluarLineas(entrada)
	if(salida != None):
		with open('tokens.tun', 'w') as o:
			o.write(salida)


def crearAutomatas(jA):
	for aut in jA:
		automatas.append(RGXGRMM(aut, aut['token']).automata)

def evaluarLineas(lineas):
	res = ''
	error = False
	for linea in lineas:
		for palabra in linea.split(' '):
			for automata in automatas:
				find = True
				if automata.reco(palabra):
					res += automata.token + ' '
					find=False
			if(find):
				error = True
	if error:
		print("Type error")
	else:
		return res

__main__()

"""

def leer(entrada):
	lineas = entrada.split('\n')
	for linea in lineas:
		expresion, token = linea.split()
		automata = RGXGRMM(expresion, token)
		out.append(automata.export())

def exportar():
	with open('out.json', 'w') as o:
		json.dump(out, o)
	with open('plex.un.py', 'w') as o:
		o.write(programa)

def __main__():
	args = sys.argv

	fl = args[1]

	entrada = open(fl, "r").read()
	leer(entrada)
	exportar()

__main__()