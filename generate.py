import os
import requests
import csv
import argparse
from bs4 import BeautifulSoup

# Constantes
URL = 'https://selectra.es/energia/info/que-es/precio-kwh'
DATASET_PARSED_FILE = 'dataset_result/practica_1_tcvd.csv' # Relativo al proyecto

# Controlamos el entorno del FS
if not os.path.isdir('dataset_result'):
    os.mkdir('dataset_result')
if os.path.isfile(DATASET_PARSED_FILE):
    os.remove(DATASET_PARSED_FILE)

# Control de los argumentos
parser = argparse.ArgumentParser()
parser.add_argument("--debug", help="1 en caso de necesitar ver los dumps 0 en caso contrario")
args = parser.parse_args()

# Debug
debug = hasattr(args, 'debug') and args.debug is not None and int(args.debug) == 1

# Petición principal
paginaScraping = requests.get(URL)
if (paginaScraping.status_code != 200):
    raise Exception("No se ha podido descargar la página web")

bs = BeautifulSoup(paginaScraping.content, 'html.parser')

# El selector CSS nos selecciona la primera tabla, dado que
# cada tabla es un tag html "article"
tabla = bs.select("article.article:first-child table")

# O podemos usar el árbol del HTML, tener en cuenta que siempre coge
# el primer elemento dentro de la lista de nodos que hacen referencia al tag
tabla = bs.body.article.table

if (len(tabla) == 0):
    raise Exception("No se han encontrado elementos. Revisa el filtro CSS")

# Cogemos el caption para sacar una descripción de la tabla
# Nos devuelve un objeto ResultSet (type(captionTabla).__name__)
captionTabla = tabla.select("article.article:first-child table > caption")[0].string

# Cogemos el header para sacar los títulos de las columnas
headerTabla = tabla.select("article.article:first-child table > thead > tr > th")
headerTableCleaned = []
for headerTitle in headerTabla:
    headerTableCleaned.append(headerTitle.getText().replace('\t', '').replace('\n', ' '))

# Finalmente cogemos los datos
bodyTabla = tabla.select("article.article:first-child table > tbody > tr")
bodyTablaFilas = []
for filaTabla in bodyTabla:
    bodyTablaFilas.append([
        filaTabla.select('th')[0].getText(),
        filaTabla.select('td')[0].getText(),
        filaTabla.select('td')[1].getText()
    ])

# Juntamos
tablaACSV = []
tablaACSV.append(headerTableCleaned)
tablaACSV.extend(bodyTablaFilas)

# Guardamos en el CSV
ficheroCSV = csv.writer(open(DATASET_PARSED_FILE, "w+", encoding='UTF-8', newline=''))
ficheroCSV.writerows(tablaACSV)

# Debug
if debug:
    print("URL página: " + URL)
    print("Fichero CSV: " + DATASET_PARSED_FILE)
    print("Resultados:")
    print(tablaACSV)