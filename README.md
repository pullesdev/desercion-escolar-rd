# Deserción Escolar en República Dominicana 🇩🇴

## Descripción

Proyecto de Data Science enfocado en analizar y predecir la deserción escolar en República Dominicana, utilizando datos oficiales del Ministerio de Educación (MINERD).

## Objetivo

Identificar centros educativos con mayor riesgo de deserción estudiantil, permitiendo la toma de decisiones preventivas basadas en datos.

## Datos

- **Centros Educativos**: Catálogo oficial de centros educativos de RD (2023-2024)
- **Anuarios Estadísticos**: Datos de matrícula, repitencia, abandono y aprobación (2020-2024)
- **Indicadores Educativos**: Tasas de deserción, reprobación y sobreedad por regional y distrito (2020-2024)

> Fuente: [Ministerio de Educación de República Dominicana (MINERD)](https://www.ministeriodeeducacion.gob.do/)

## Estructura del Proyecto

```
desercion-escolar-rd/
├── data/
│   ├── raw/              # Datos originales (CSVs y PDFs del MINERD)
│   └── processed/        # Datos limpios y transformados
├── notebooks/            # Jupyter notebooks del análisis
├── .gitignore
└── README.md
```

## Metodología

| Fase | Descripción | Estado |
|------|-------------|--------|
| 1. Exploración de datos | Carga y exploración inicial de los datasets | ✅ Completado |
| 2. Limpieza | Tratamiento de valores nulos, duplicados y formatos | ✅ Completado |
| 3. Extracción de indicadores | Extracción de datos desde PDFs del MINERD | 🔜 Próximamente |
| 4. Feature Engineering | Creación de variables y merge de datasets | 🔜 Próximamente |
| 5. Modelo Predictivo | Entrenamiento y evaluación de modelos ML | 🔜 Próximamente |

## Tech Stack

- Python 3.12
- Pandas, NumPy
- Scikit-Learn
- Matplotlib, Seaborn
- Jupyter Notebook

## Autor

**Eddy Luis Pullés Martín**  
Data Scientist · Santo Domingo, República Dominicana

- GitHub: [@pullesdev](https://github.com/pullesdev)
- Email: eddy.pulles83@gmail.com
