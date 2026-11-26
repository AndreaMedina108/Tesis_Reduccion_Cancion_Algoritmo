# Tesis_Reduccion_Cancion_Algoritmo

## Integrantes

Andrea Medina

## Descripción

Implementación modular en Python para la **reducción estadística de partituras polifónicas controlada por dificultad de ejecución**, basada en el marco probabilístico de *Nakamura & Yoshii (2018)* (*"Statistical piano reduction controlling performance difficulty"*).

El sistema transforma arreglos musicales complejos o multi-instrumentales en versiones ejecutables a dos manos (niveles Fácil, Intermedio y Avanzado), minimizando el esfuerzo ergonómico mientras preserva la melodía principal, el bajo fundamental y la estructura armónica.

## Estructura del Proyecto

```text
Tesis_Reduccion_Cancion_Algoritmo/
├── data/                           # Partituras de entrada y salidas (.csv y .mid)
├── notebooks/
│   └── analisis_reduccion.ipynb    # Cuaderno interactivo de experimentos y gráficas
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── score.py                # Estructuras simbólicas (Note, Score, manos L/R)
│   │   └── importance.py           # Cálculo de importancia musical h(m)
│   ├── metrics/
│   │   ├── __init__.py
│   │   └── difficulty.py           # Evaluación Gaussiana de dificultad (D_L, D_R, D_B)
│   ├── optimizer/
│   │   ├── __init__.py
│   │   └── reducer.py              # Algoritmo iterativo de poda y octavación
│   └── utils/
│       ├── __init__.py
│       ├── generator.py            # Generador de pieza polifónica de prueba
│       ├── midi_loader.py          # Lector de archivos MIDI externos (.mid)
│       └── midi_exporter.py        # Exportador a MIDI estándar (.mid) y CSV
├── .env                            # Configuración de PYTHONPATH para VS Code
├── .gitignore
├── pyproject.toml                  # Configuración del paquete instalable
├── requirements.txt                # Dependencias del proyecto
└── README.md
```

## Instalación y Configuración

1. **Clonar el repositorio y entrar a la carpeta del proyecto:**
   ```bash
   git clone [https://github.com/](https://github.com/)<TU_USUARIO>/Tesis_Reduccion_Cancion_Algoritmo.git
   cd Tesis_Reduccion_Cancion_Algoritmo
   ```

2. **Crear y activar el entorno virtual (Windows PowerShell):**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Instalar las dependencias y el paquete local en modo editable:**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

## Uso y Ejecución

1. Abre el cuaderno **`notebooks/analisis_reduccion.ipynb`** en Visual Studio Code.
2. Selecciona el intérprete/kernel correspondiente al entorno virtual **`.venv`**.
3. Ejecuta las celdas secuencialmente para:
   - Generar la pieza polifónica de prueba (o cargar un archivo `.mid` propio desde `data/` mediante `load_midi_to_score`).
   - Calcular las métricas de dificultad ($D_L$, $D_R$ y $D_B$) y aplicar la optimización iterativa por niveles.
   - Exportar las partituras reducidas (`.mid` y `.csv`) en `data/` y visualizar las curvas de dificultad junto con el diagrama *Piano Roll*.

## Referencia Base

- Nakamura, E., & Yoshii, K. (2018). *Statistical piano reduction controlling performance difficulty*. APSIPA Transactions on Signal and Information Processing, 7, e13.