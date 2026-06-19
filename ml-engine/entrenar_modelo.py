import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

print("⏳ Cargando y limpiando el dataset histórico...")

# 1. Cargar el dataset
df = pd.read_excel('04-01-Financial Sample Data.xlsx')

# ¡EL PARCHE MÁGICO! Limpiar espacios ocultos en los nombres de las columnas
df.columns = df.columns.str.strip()

print(f"📊 Columnas detectadas en el Excel: {df.columns.tolist()}")

# 2. Limpieza de datos numéricos (quitar $, comas y espacios)
cols_numericas = ["Sales", "COGS", "Profit"]

# Verificar que las columnas existan antes de limpiar
for col in cols_numericas:
    if col not in df.columns:
        print(f" ERROR CRÍTICO: No existe la columna '{col}' en tu Excel.")
        exit()

for col in cols_numericas:
    if df[col].dtype == object:
        df[col] = df[col].astype(str).str.replace(r"[\$,\(\)\s]", "", regex=True)
        df[col] = df[col].str.replace(r"^-$", "0", regex=True)
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Eliminar filas vacías o corruptas
df = df.dropna(subset=["Sales", "COGS", "Profit"])

print("⚙️ Analizando datos y generando etiquetas de 'Riesgo'...")

# 3. Crear la lógica para que la IA aprenda qué es riesgo Alto, Medio y Bajo
def clasificar_riesgo(fila):
    ventas = fila['Sales']
    ganancia = fila['Profit']
    
    if ventas <= 0: 
        return 2 # ALTO
        
    margen = (ganancia / ventas) * 100
    
    if ganancia < 0:
        return 2 # ALTO
    elif margen < 20:
        return 1 # MEDIO
    else:
        return 0 # BAJO

# Aplicar la función a todo el dataset histórico
df['Etiqueta_Riesgo'] = df.apply(clasificar_riesgo, axis=1)

# 4. Seleccionar Entradas (Ingresos y Costos) y Salida (El riesgo calculado)
X = df[['Sales', 'COGS']]
y = df['Etiqueta_Riesgo']

print(f" Entrenando el algoritmo Random Forest con {len(df)} registros reales...")

# 5. Entrenar el modelo
modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X, y)

# 6. Guardar el "cerebro" ya entrenado
joblib.dump(modelo, 'modelo_riesgo_definitivo.pkl')
print(" ¡Modelo entrenado con éxito! Guardado como 'modelo_riesgo_definitivo.pkl'")