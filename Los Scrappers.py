from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

# ----------------------------
# 1. SCRAPER CON SELENIUM
# ----------------------------

años = [2002, 2006, 2010, 2014, 2018, 2022]
urls = {año: f"https://www.espn.com.mx/futbol/estadisticas/_/liga/FIFA.WORLD/temporada/{año}/vista/anotaciones"
        for año in años}

def extraer_goleadores_selenium(url, año):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)  # Espera a que cargue el JS
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Buscar la sección de Goleadores y su tabla
    title_div = soup.find('div', class_='Table__Title', string='Goleadores')
    tabla = title_div.find_next('table') if title_div else soup.find('table')
    if not tabla:
        print(f"[Advertencia] Año {año}: tabla no encontrada")
        return pd.DataFrame()

    filas = tabla.find_all('tr')
    headers = [th.get_text(strip=True) for th in filas[0].find_all('th')]
    datos = []
    for tr in filas[1:]:
        c = [td.get_text(strip=True) for td in tr.find_all('td')]
        if len(c) == len(headers):
            datos.append(c)
    if not datos:
        print(f"[Advertencia] Año {año}: filas vacías")
        return pd.DataFrame()

    df = pd.DataFrame(datos, columns=headers)
    df['Año'] = año
    return df

# Construir DataFrame total
df_tot = pd.DataFrame()
for año, url in urls.items():
    df_temp = extraer_goleadores_selenium(url, año)
    if not df_temp.empty:
        df_tot = pd.concat([df_tot, df_temp], ignore_index=True)

if df_tot.empty:
    raise SystemExit("No se obtuvieron datos. Verifica Selenium o URLs.")

# Renombrar columna de goles buscándola entre varias posibilidades
candidatas = [c for c in df_tot.columns if c in ('G', 'Goles', 'Goals') or 'Gol' in c]
if not candidatas:
    raise SystemExit("No se encontró columna de goles para renombrar")
col_g = candidatas[0]
df_tot.rename(columns={col_g: 'G'}, inplace=True)

# Convertir G a numérico y guardar CSV
df_tot['G'] = pd.to_numeric(df_tot['G'], errors='coerce')
df_tot.to_csv('goleadores_mundiales.csv', index=False)

# Agrupar y guardar goles por equipo
df_eq = df_tot.groupby(['Equipo', 'Año'])['G'].sum().reset_index()
df_eq.to_csv('goles_por_equipo.csv', index=False)

print("Scraping y CSV generados exitosamente.")
# Después de crear df_tot y df_eq en scraper.py

# Cantidad de registros de goleadores individuales
print("Registros de goleadores individuales por año:")
print(df_tot['Año'].value_counts().sort_index().to_string())
print(f"Total de filas en goleadores_mundiales.csv: {len(df_tot)}\n")

# Cantidad de registros de goles por equipo
print("Registros de goles por equipo por año:")
print(df_eq['Año'].value_counts().sort_index().to_string())
print(f"Total de filas en goles_por_equipo.csv: {len(df_eq)}")
