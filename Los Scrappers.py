from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

# ----------------------------
# Proyecto Final
# Macias Gonzalez Marla
# 181184 Grrpo: 951
# ----------------------------

años = [2002, 2006, 2010, 2014, 2018, 2022]
urls = {año: f"https://www.espn.com.mx/futbol/estadisticas/_/liga/FIFA.WORLD/temporada/{año}/vista/anotaciones"
        for año in años}

def extraccion(url, año):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    divisor = soup.find('div', class_='Table__Title', string='Goleadores')
    tabla = divisor.find_next('table') if divisor else soup.find('table')
    if not tabla:
        print(f"{año} no hubo tabla")
        return pd.DataFrame()
    filas = tabla.find_all('tr')
    headers = [th.get_text(strip=True) for th in filas[0].find_all('th')]
    datos = []
    for tr in filas[1:]:
        c = [td.get_text(strip=True) for td in tr.find_all('td')]
        if len(c) == len(headers):
            datos.append(c)
    if not datos:
        print(f" {año}: no hay datos!!!!")
        return pd.DataFrame()

    df = pd.DataFrame(datos, columns=headers)
    df['Año'] = año
    return df

totaldf = pd.DataFrame()
for año, url in urls.items():
    df_temp = extraccion(url, año)
    if not df_temp.empty:
        totaldf = pd.concat([totaldf, df_temp], ignore_index=True)
if totaldf.empty:
    raise SystemExit("no hubo datos ")
candidatas = [c for c in totaldf.columns if c in ('G', 'Goles', 'Goals') or 'Gol' in c]
if not candidatas:
    raise SystemExit("no hubo columnas")
col_g = candidatas[0]
totaldf.rename(columns={col_g: 'G'}, inplace=True)

totaldf['G'] = pd.to_numeric(totaldf['G'], errors='coerce')
totaldf.to_csv('goleadores_mundiales.csv', index=False)
df_eq = totaldf.groupby(['Equipo', 'Año'])['G'].sum().reset_index()
df_eq.to_csv('goles_por_equipo.csv', index=False)
print("Los csv se crearon correctamente")
print("Registros de goleadores al año")
print(totaldf['Año'].value_counts().sort_index().to_string())
print(f"filas en goleadores_mundiales.csv: {len(totaldf)}\n")
print("Los registros de goles por equipo por año")
print(df_eq['Año'].value_counts().sort_index().to_string())
print(f"Total de filas en goles_por_equipo.csv: {len(df_eq)}")
