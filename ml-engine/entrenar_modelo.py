# entrenar_modelo.py
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

print("⚙️ Iniciando entrenamiento del modelo...")

# 1. Datos de ejemplo: [Ingresos, Costos Totales]
X_entrenamiento = [
    [15000, 5000],  # Gana mucho, gasta poco (Bajo Riesgo)
    [20000, 8000],  # Bajo Riesgo
    [8000, 7500],   # Margen muy apretado (Medio Riesgo)
    [5000, 4000],   # Medio Riesgo
    [3000, 5000],   # Gasta más de lo que gana (Alto Riesgo)
    [1000, 3000]    # Alto Riesgo
]

# 2. Etiquetas: 0 = BAJO, 1 = MEDIO, 2 = ALTO
y_etiquetas = [0, 0, 1, 1, 2, 2]

# 3. Entrenar el algoritmo Random Forest (Requisito del documento)
modelo = RandomForestClassifier(n_estimators=50, random_state=42)
modelo.fit(X_entrenamiento, y_etiquetas)

# 4. Exportar el modelo como un archivo real
joblib.dump(modelo, 'modelo_riesgo.pkl')
print("✅ ¡Modelo Random Forest guardado exitosamente como 'modelo_riesgo.pkl'!")