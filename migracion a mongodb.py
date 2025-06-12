import csv
from pymongo import MongoClient
db_client = MongoClient('mongodb://localhost:27017/')
db = db_client['LasEstadisticasMundial']

def migrar_csv(archivo_csv, coleccion):
    coll = db[coleccion]
    with open(archivo_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        # Determinar columnas según la colección
        if coleccion == 'goleadores_mundiales':
            jugador = headers[0]
            equipo_col = headers[1]
            cols = [jugador, equipo_col, 'G', 'Año']
        else:
            cols = [h for h in headers if h in ('Equipo', 'Año', 'G')]
        for row in reader:
            doc = {}
            if coleccion == 'goleadores_mundiales':
                doc['Jugador'] = row.get(jugador)
                doc['Equipo'] = row.get(equipo_col)
            else:
                doc['Equipo'] = row.get('Equipo')
            doc['G'] = row.get('G')
            doc['Año'] = row.get('Año')
            coll.insert_one(doc)

losgoleadores = 'goleadores_mundiales.csv'
losequipos = 'goles_por_equipo.csv'

eprint_gol = migrar_csv(losgoleadores, 'goleadores_mundiales')
migrar_csv(losequipos, 'goles_por_equipo')

print("Migración a MongoDB completada en 'LasEstadisticasMundial'.")
