### Archivo: migracion.py
import csv
from pymongo import MongoClient

# Conexión a MongoDB con base de datos correcta
db_client = MongoClient('mongodb://localhost:27017/')
db = db_client['LasEstadisticasMundial']


# Migrar CSV a colección con mapeo flexible
def migrar_csv(archivo_csv, coleccion):
    coll = db[coleccion]
    with open(archivo_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        # Determinar columnas según la colección
        if coleccion == 'goleadores_mundiales':
            jugador_col = headers[0]
            equipo_col = headers[1]
            cols = [jugador_col, equipo_col, 'G', 'Año']
        else:
            cols = [h for h in headers if h in ('Equipo', 'Año', 'G')]

        for row in reader:
            # Construir documento según columnas detectadas
            doc = {}
            if coleccion == 'goleadores_mundiales':
                doc['Jugador'] = row.get(jugador_col)
                doc['Equipo'] = row.get(equipo_col)
            else:
                doc['Equipo'] = row.get('Equipo')
            doc['G'] = row.get('G')
            doc['Año'] = row.get('Año')

            # Insertar en MongoDB
            coll.insert_one(doc)


# Rutas de los archivos CSV
archivo_goleadores = 'goleadores_mundiales.csv'
archivo_equipos = 'goles_por_equipo.csv'

# Ejecutar migraciones
eprint_gol = migrar_csv(archivo_goleadores, 'goleadores_mundiales')
migrar_csv(archivo_equipos, 'goles_por_equipo')

print("Migración a MongoDB completada en 'LasEstadisticasMundial'.")
