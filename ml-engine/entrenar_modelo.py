import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report
import joblib
import json

print("Cargando y limpiando el dataset historico...")

# 1. Cargar el dataset
df = pd.read_excel('04-01-Financial Sample Data.xlsx')

# Limpiar espacios en los nombres de las columnas
df.columns = df.columns.str.strip()

print(f"Columnas detectadas: {df.columns.tolist()}")

# 2. Limpieza de datos numericos (quitar $, comas y espacios)
cols_numericas = ["Sales", "COGS", "Profit"]

for col in cols_numericas:
    if col not in df.columns:
        print(f"ERROR CRITICO: No existe la columna '{col}' en el Excel.")
        exit()

for col in cols_numericas:
    if df[col].dtype == object:
        df[col] = df[col].astype(str).str.replace(r"[\$,\(\)\s]", "", regex=True)
        df[col] = df[col].str.replace(r"^-$", "0", regex=True)
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Eliminar filas vacias o corruptas
df = df.dropna(subset=["Sales", "COGS", "Profit"])

print("Generando etiquetas de Riesgo...")

# 3. Logica de clasificacion de riesgo
def clasificar_riesgo(fila):
    ventas = fila['Sales']
    ganancia = fila['Profit']

    if ventas <= 0:
        return 2  # ALTO

    margen = (ganancia / ventas) * 100

    if ganancia < 0:
        return 2  # ALTO
    elif margen < 20:
        return 1  # MEDIO
    else:
        return 0  # BAJO

df['Etiqueta_Riesgo'] = df.apply(clasificar_riesgo, axis=1)

# 4. Entradas y salida
X = df[['Sales', 'COGS']]
y = df['Etiqueta_Riesgo']

# 5. Division train/test
print("Dividiendo dataset: 80% entrenamiento / 20% prueba...")
print(f"Entrenando el algoritmo Random Forest con {len(df)} registros reales...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print(f"  Registros de entrenamiento : {len(X_train)}")
print(f"  Registros de prueba        : {len(X_test)}")

# 6. Modelo de evaluacion
print("Entrenando modelo de evaluacion...")
modelo_eval = RandomForestClassifier(n_estimators=100, random_state=42)
modelo_eval.fit(X_train, y_train)

# 7. Metricas
y_pred   = modelo_eval.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
f1       = f1_score(y_test, y_pred, average='weighted')

print("")
print("=" * 55)
print("  METRICAS DE DESEMPENO DEL MODELO")
print("=" * 55)
print(f"  Accuracy  (Exactitud) : {accuracy * 100:.2f}%")
print(f"  F1-Score  (Ponderado) : {f1 * 100:.2f}%")
print("")
print("  Reporte por clase:")
labels_map     = {0: "Bajo", 1: "Medio", 2: "Alto"}
y_test_named   = [labels_map[v] for v in y_test]
y_pred_named   = [labels_map[v] for v in y_pred]
print(classification_report(y_test_named, y_pred_named, target_names=["Alto", "Bajo", "Medio"]))
print("=" * 55)

# 8. Guardar metricas en JSON
metricas = {
    "accuracy": round(accuracy * 100, 2),
    "f1_score": round(f1 * 100, 2),
    "train_samples": int(len(X_train)),
    "test_samples": int(len(X_test)),
    "total_samples": int(len(df)),
    "n_estimators": 100
}
with open('model_metrics.json', 'w', encoding='utf-8') as f:
    json.dump(metricas, f, indent=2)
print("Metricas guardadas en model_metrics.json")

# 9. Modelo definitivo (todos los datos)
print(f"Entrenando modelo definitivo con {len(df)} registros totales...")
modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X, y)

joblib.dump(modelo, 'modelo_riesgo_definitivo.pkl')
print("Modelo guardado como modelo_riesgo_definitivo.pkl")
print("Proceso completado exitosamente.")
