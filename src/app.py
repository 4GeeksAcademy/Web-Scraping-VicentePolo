import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


url = 'https://companiesmarketcap.com/tesla/revenue/'

# Hacer la petición a la página
response = requests.get(url)

# Comprobar si la petición fue exitosa
if response.status_code == 200:
    # Leer el contenido HTML con BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Buscar la tabla (ajusta el selector si es necesario)
    table = soup.find("table")
    
    if table:
        # Extraer encabezados
        headers = [header.text.strip() for header in table.find_all("th")]
        
        # Extraer filas
        rows = []
        for row in table.find_all("tr")[1:]:  # Omitir la fila de encabezados
            cells = [cell.text.strip() for cell in row.find_all("td")]
            rows.append(cells)
        
        # Crear un DataFrame con los datos extraídos
        df = pd.DataFrame(rows, columns=headers)
        
        # Guardar en un archivo CSV (opcional)
        df.to_csv("tabla_datos.csv", index=False, encoding="utf-8")
        
        # Mostrar un resumen del DataFrame
        print("Datos guardados en el DataFrame:")
        
    else:
        print("No se encontró ninguna tabla en la página.")
else:
    print(f"Error en la petición: {response.status_code}")

#Eliminar las B de billones y espacios

def convert_to_float(value):
    value = value.replace('$', '').strip()  # Elimina $ y espacios
    if 'B' in value:  # Si es en miles de millones (Billion)
        return float(value.replace('B', '')) * 1e9

#Aplicar la función
df['Revenue'] = df['Revenue'].apply(convert_to_float)


#Usar Sqlite3

# 1. Conectar o crear la base de datos SQLite
conn = sqlite3.connect("company_revenue.db")  # Crea un archivo .db en el directorio actual

# 2. Crear un cursor para ejecutar comandos SQL
cursor = conn.cursor()

# 3. Crear la tabla en la base de datos (si no existe)
cursor.execute("""
CREATE TABLE IF NOT EXISTS Tesla_revenue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Year TEXT NOT NULL,
    Revenue REAL NOT NULL,
    Change REAL
)
""")

# 4. Insertar los datos del DataFrame en la tabla
for index, row in df.iterrows():
    cursor.execute("""
    INSERT INTO Tesla_revenue (Year, Revenue, Change)
    VALUES (?, ?, ?)
    """, (row['Year'], row['Revenue'],row['Change']))

# 5. Guardar los cambios (commit) y cerrar la conexión
conn.commit()
conn.close()


#6 Elegir tres tipos de visualizacion

#Gráfico de líneas

df = df.sort_values(by="Year")# Invierto el orden para mostrar los datos de año mas antiguo a mas reciente

plt.figure(figsize=(10, 6))
plt.plot(df['Year'], df['Revenue'], linestyle='-', color='r', label="Ingresos")
plt.title("Evolución de los Ingresos de Tesla", fontsize=16)
plt.xlabel("Año", fontsize=12)
plt.ylabel("Ingresos (en billones de $)", fontsize=12)

# Mostrar el gráfico
plt.show()

#Gráfico de Barras

plt.figure(figsize=(10, 6))
plt.bar(df["Year"], df["Revenue"], color='red', edgecolor='black')
plt.title("Ingresos anuales de Tesla", fontsize=16)
plt.xlabel("Año", fontsize=12)
plt.ylabel("Ingresos (en billones de dolares)", fontsize=12)
plt.xticks(rotation=45)
plt.show()


#Gráfico combinado

fig, ax1 = plt.subplots(figsize=(10, 6))

# Gráfico de barras para los ingresos
ax1.bar(df["Year"], df["Revenue"], color='red', alpha=0.7, label="Ingresos")
ax1.set_ylabel("Ingresos (en billones de $)", fontsize=12, color='green')
ax1.tick_params(axis='y', labelcolor='green')

# Segundo eje para el cambio porcentual
ax2 = ax1.twinx()
ax2.plot(df["Year"], df["Change"], color='black', label="Cambio (%)")
ax2.set_ylabel("Cambio porcentual", fontsize=12, color='red')
ax2.tick_params(axis='y', labelcolor='red')

# Títulos y leyendas
plt.title("Ingresos y cambio porcentual de Tesla", fontsize=16)
fig.tight_layout()
plt.show()

