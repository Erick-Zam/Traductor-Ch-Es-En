# 🈳 Traductor Chino Pro

Aplicación profesional de escritorio para traducir texto chino a español/inglés con pronunciación Pinyin, exportación a PDF y sistema de temas Dark/Light.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📦 Versiones Disponibles

### 🆕 [v2.0](v2.0/) - **Recomendada** ⭐
- ✨ Interfaz moderna con **PyQt6**
- 🌙 Sistema de temas **Dark/Light Mode**
- 📱 Diseño **100% Responsive**
- ⚡ Rendimiento optimizado con caché inteligente
- 🎨 Animaciones y transiciones suaves
- ⌨️ Atajos de teclado completos

[📖 Ver documentación v2.0](v2.0/README.md)

### 📦 [v1.0](v1.0/) - Clásica
- 🖼️ Interfaz básica con Tkinter
- ✅ Funcionalidad completa de traducción
- 📄 Exportación a PDF básica

[📖 Ver documentación v1.0](v1.0/README.md)

## 🚀 Inicio Rápido

### Opción 1: Ejecutable (Sin instalación)
1. Descarga `TraductorChinoPro.exe` desde [v2.0/](v2.0/)
2. Ejecuta directamente - ¡No requiere Python!

### Opción 2: Desde código fuente
```bash
# Clonar repositorio
git clone https://github.com/Erick-Zam/Pinguino.git
cd Pinguino

# Para v2.0 (Recomendado)
cd v2.0
pip install -r requirements.txt
python main.py

# Para v1.0
cd v1.0
pip install -r requirements.txt
python main.py
```

## ✨ Características Principales v2.0

### 🎨 Interfaz
- **Temas Dark/Light**: Cambia con `Ctrl+D` o botón 🌙/☀️
- **Responsive**: Se adapta perfectamente a cualquier tamaño de ventana
- **Diseño moderno**: Interfaz PyQt6 profesional

### 🌐 Traducción
- Chino → Español/Inglés
- Caché inteligente para velocidad
- Traducción automática en tiempo real

### 🗣️ Pinyin
- Generación automática de pronunciación
- Tabla interactiva con colores
- Separación por grupos de caracteres

### 📄 PDF
- Exportación profesional
- Diseño con colores y bordes
- Header personalizado

### ⌨️ Atajos de Teclado
| Atajo | Acción |
|-------|--------|
| `Ctrl+T` | Traducir |
| `Ctrl+D` | Cambiar tema |
| `Ctrl+L` | Limpiar |
| `Ctrl+Q` | Salir |

## 📊 Comparación de Versiones

| Característica | v1.0 | v2.0 |
|---------------|------|------|
| Framework | Tkinter | PyQt6 ✨ |
| Temas | ❌ | Dark/Light 🌙☀️ |
| Responsive | ❌ | ✅ |
| Rendimiento | Básico | Optimizado 🚀 |
| Caché | ❌ | Inteligente 💾 |
| Atajos | ❌ | ✅ ⌨️ |
| Monitor recursos | ❌ | ✅ 📊 |

## 🛠️ Tecnologías

### v2.0
- **PyQt6** - Framework UI moderno
- **deep-translator** - Motor de traducción
- **pypinyin** - Generador Pinyin
- **psutil** - Monitor de recursos

### v1.0
- **Tkinter** - Framework UI básico
- **googletrans** - Traducción
- **pypinyin** - Generador Pinyin
- **reportlab** - PDF básico

## 📁 Estructura del Proyecto

```
Pinguino/
├── v1.0/                    # Versión 1.0 (Tkinter)
│   ├── main.py
│   ├── requirements.txt
│   ├── build.bat
│   └── README.md
├── v2.0/                    # Versión 2.0 (PyQt6) ⭐
│   ├── main.py
│   ├── requirements.txt
│   ├── build.bat
│   ├── install.bat
│   ├── translate.png        # Ícono de la app
│   ├── TraductorChinoPro.exe
│   ├── README.md
│   ├── INSTALL.md
│   └── RESUMEN.md
├── .venv/                   # Entorno virtual (local)
├── README.md               # Este archivo
└── COMPARATIVA.md          # Comparativa detallada
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📜 Licencia

Este proyecto está bajo la Licencia MIT.

## 👨‍💻 Autor

**Erick-Zam**
- GitHub: [@Erick-Zam](https://github.com/Erick-Zam)

## 🙏 Agradecimientos

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - Framework UI moderno
- [deep-translator](https://github.com/nidhaloff/deep-translator) - Motor de traducción
- [pypinyin](https://github.com/mozillazg/python-pinyin) - Generador de Pinyin

---

**⭐ Si te gusta el proyecto, dale una estrella en GitHub!**

## ✨ Características Principales

### 🌐 Traducción Multiidioma
- **Traducción automática** chino → español/inglés
- **Detección automática** del idioma de origen
- **Caché inteligente** para traducciones frecuentes
- **Limpieza automática** de prefijos innecesarios

### 🀄 Pronunciación Pinyin
- **Generación automática** de pronunciación Pinyin
- **Tabla interactiva** con caracteres chinos y pronunciación
- **Visor HTML optimizado** o tabla CTkTable según hardware
- **Respeto de puntuaciones** chinas y occidentales

### 📊 Visualización Avanzada
- **Dos modos de visualización**:
  - HTML optimizado (hardware moderno)
  - CTkTable (compatibilidad universal)
- **Traducciones por grupo** de caracteres
- **Interfaz responsive** adaptable a diferentes tamaños
- **Modo oscuro/claro** automático

### 📄 Exportación a PDF
- **Conversión HTML → PDF** con múltiples métodos:
  - weasyprint (recomendado)
  - pdfkit (alternativa)
  - Navegador (fallback manual)
- **Diseño profesional** con:
  - Header con degradado azul y texto blanco
  - Tabla con bordes definidos
  - Traducciones por grupo resaltadas
  - Información de exportación automática

## 🚀 Instalación

### Requisitos Previos
- Python 3.8 o superior
- Windows / Linux / macOS

### Instalación Rápida

1. **Clonar el repositorio**:
```bash
git clone https://github.com/Erick-Zam/Pinguino.git
cd Pinguino
```

2. **Crear entorno virtual** (recomendado):
```bash
python -m venv .venv
```

3. **Activar entorno virtual**:
- Windows: `.venv\Scripts\activate`
- Linux/Mac: `source .venv/bin/activate`

4. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

### Dependencias Opcionales para PDF

**Para mejor conversión a PDF** (opcional pero recomendado):

**Opción 1: weasyprint** (Mejor soporte CSS)
```bash
pip install weasyprint
```

**Opción 2: pdfkit** (Alternativa)
```bash
pip install pdfkit
```
Además necesitas instalar [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)

## 📖 Uso

### Ejecutar la Aplicación

```bash
python main.py
```

### Interfaz de Usuario

1. **Ingresa texto chino** en el área de texto superior
2. **Selecciona el idioma** de traducción:
   - 🇪🇸 Español
   - 🇺🇸 English
   - 🌐 Detección automática
3. **Haz clic en "Traducir"**
4. **Visualiza resultados**:
   - Traducción en el área central
   - Tabla Pinyin en la parte inferior

### Exportar a PDF

1. Traduce un texto chino
2. Haz clic en **"📄 Exportar PDF"**
3. Selecciona ubicación y nombre del archivo
4. El PDF se genera automáticamente

## 🏗️ Generar Ejecutable

Para crear un ejecutable standalone:

```bash
# Windows
build.bat

# Linux/Mac
pyinstaller TraductorChino.spec
```

El ejecutable se generará en la carpeta `dist/`

## ⚙️ Optimizaciones y Rendimiento

### 🧠 Gestión Inteligente de Memoria
- **Caché con límites configurables** (500 entradas por defecto)
- **Limpieza automática** cuando >85% RAM ocupada
- **Estadísticas de rendimiento** guardadas automáticamente
- **Hit rate monitoring** para análisis de caché

### ⚡ Optimizaciones de Velocidad
- **Timeouts reducidos**: 6 segundos (vs 8s anteriores)
- **Límite de traducciones por lote**: 50 grupos
- **Caché global reutilizable** entre operaciones
- **Threading optimizado** según núcleos de CPU

### 📊 Métricas Automáticas
- Registro de cache hits/misses
- Cálculo de hit rate
- Guardado en `~/.traductor_chino/stats.json`
- Análisis de rendimiento en tiempo real

## 🎨 Características del PDF Exportado

### Diseño Visual
- **Header degradado azul** con texto blanco
- **Tabla con bordes definidos** (1.5px)
- **Colores diferenciados**:
  - Pinyin: Fondo azul claro (#e0e7ff)
  - Caracteres: Fondo gris claro (#f8fafc)
  - Traducción: Fondo azul muy claro (#f0f9ff)

### Información Incluida
- Título del documento
- Total de grupos y caracteres procesados
- Tabla completa de Pinyin y caracteres
- Traducciones por grupo en español/inglés
- Metadatos de exportación (fecha, versión, etc.)

## 🔧 Configuración

### Variables de Entorno Opcionales

```python
# En el código, puedes ajustar:
self.max_cache_size = 500  # Tamaño máximo del caché
socket.setdefaulttimeout(6)  # Timeout de red
max_traducciones_por_lote = 50  # Límite de traducciones
```

### Configuración por Hardware

**Hardware Alto**:
- max_cache_size = 1000
- timeout = 8s
- traducciones_lote = 100

**Hardware Medio** (por defecto):
- max_cache_size = 500
- timeout = 6s
- traducciones_lote = 50

**Hardware Bajo**:
- max_cache_size = 200
- timeout = 4s
- traducciones_lote = 25

## 📁 Estructura del Proyecto

```
Pinguino/
├── main.py              # Aplicación principal
├── requirements.txt     # Dependencias
├── README.md           # Documentación
├── build.bat           # Script de construcción (Windows)
├── TraductorChino.spec # Configuración PyInstaller
├── .venv/              # Entorno virtual (local)
├── build/              # Archivos de construcción (temporal)
├── dist/               # Ejecutables generados
└── __pycache__/        # Cache de Python (temporal)
```

## 🐛 Solución de Problemas

### Error: "No module named 'tkinterweb'"
```bash
pip install tkinterweb
```

### Error: "weasyprint not found"
Es opcional. Usa el método manual del navegador o instala:
```bash
pip install weasyprint
```

### La aplicación se cierra inmediatamente
Ejecuta desde terminal para ver errores:
```bash
python main.py
```

### PDF no se genera
1. Verifica que tengas librerías opcionales instaladas
2. Usa el método manual del navegador (Ctrl+P → Guardar como PDF)

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**Erick-Zam**
- GitHub: [@Erick-Zam](https://github.com/Erick-Zam)

## 🙏 Agradecimientos

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Framework de UI moderno
- [deep-translator](https://github.com/nidhaloff/deep-translator) - Motor de traducción
- [pypinyin](https://github.com/mozillazg/python-pinyin) - Generador de Pinyin
- [CTkTable](https://github.com/Akascape/CTkTable) - Componente de tablas
- [tkinterweb](https://github.com/Andereoo/TkinterWeb) - Visor HTML

## 📊 Estadísticas

- **Versión**: 2.1
- **Última actualización**: Octubre 2025
- **Idiomas soportados**: Chino → Español/Inglés
- **Plataformas**: Windows, Linux, macOS

---

**¿Te gusta el proyecto? Dale una ⭐ en GitHub!**
