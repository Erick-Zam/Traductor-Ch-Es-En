# 🈳 Traductor Chino Pro v2.0

## 📋 Descripción
Versión 2.0 del Traductor Chino Pro - Aplicación moderna de escritorio con interfaz PyQt6, sistema de temas Dark/Light y diseño responsive.

## ✨ Características v2.0

### 🎨 Interfaz Moderna
- ✅ Framework PyQt6 (más rápido y eficiente)
- ✅ Sistema de temas **Dark/Light Mode** (🌙/☀️)
- ✅ Diseño **100% Responsive** (se adapta a cualquier tamaño de ventana)
- ✅ Animaciones y transiciones suaves

### 🚀 Funcionalidades
- ✅ Traducción chino → español/inglés con deep-translator
- ✅ Generación automática de pronunciación Pinyin
- ✅ Exportación a PDF con formato profesional
- ✅ Gestión inteligente de caché y memoria
- ✅ Traducción automática en tiempo real
- ✅ Interfaz optimizada para alto rendimiento

### ⌨️ Atajos de Teclado
- `Ctrl+T` - Traducir texto
- `Ctrl+D` - Cambiar tema (Dark/Light)
- `Ctrl+L` - Limpiar todo
- `Ctrl+Q` - Salir

## 📦 Instalación

### Opción 1: Ejecutable (Recomendado)
Simplemente ejecuta `TraductorChinoPro.exe` - No requiere instalación de Python.

### Opción 2: Desde Código Fuente

#### Requisitos
- Python 3.11 o superior
- pip

#### Pasos
1. Instalar dependencias:
```bash
install.bat
```
O manualmente:
```bash
pip install -r requirements.txt
```

2. Ejecutar la aplicación:
```bash
python main.py
```

## 🔨 Crear Ejecutable
```bash
build.bat
```

El ejecutable se generará con el ícono personalizado y todas las características incluidas.

## 📚 Dependencias Principales
- **PyQt6** - Framework de interfaz gráfica moderna
- **deep-translator** - Traducción avanzada
- **pypinyin** - Generación de pronunciación Pinyin
- **psutil** - Gestión de recursos del sistema

## 🎯 Mejoras respecto a v1.0

| Característica | v1.0 | v2.0 |
|---------------|------|------|
| Framework | Tkinter | PyQt6 ✨ |
| Temas | Solo claro | Dark/Light 🌙☀️ |
| Responsive | No | Sí ✅ |
| Rendimiento | Básico | Optimizado 🚀 |
| Caché | No | Inteligente 💾 |
| PDF | Básico | Profesional 📄 |
| Atajos | No | Sí ⌨️ |

## 📸 Capturas

### Modo Claro ☀️
- Interfaz limpia y clara
- Ideal para uso durante el día

### Modo Oscuro 🌙
- Reduce fatiga visual
- Perfecto para uso nocturno

## 🛠️ Características Técnicas
- Arquitectura MVC optimizada
- Gestión eficiente de memoria con caché LRU
- Multithreading para operaciones asíncronas
- Sistema de workers para traducción y Pinyin
- Monitor de recursos en tiempo real

## 📖 Documentación Adicional
- `INSTALL.md` - Guía detallada de instalación
- `RESUMEN.md` - Resumen técnico de cambios

---
**Desarrollado con ❤️ usando PyQt6**
