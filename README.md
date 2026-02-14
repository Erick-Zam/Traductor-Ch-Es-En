# 🈳 Traductor Chino Pro - Proyecto Experimental

Bienvenido al repositorio del **Traductor Chino Pro**. Este proyecto es una colección de **pruebas de concepto y prototipos** diseñados para explorar y demostrar diferentes tecnologías de desarrollo de aplicaciones de escritorio en Python, enfocadas en la traducción y procesamiento del idioma chino.

> ⚠️ **Nota Importante**: Este repositorio contiene versiones experimentales creadas con fines educativos y de demostración para probar capacidades de frameworks como Tkinter y PyQt6, así como integración con APIs de traducción.

## 🎯 Objetivo del Proyecto

El objetivo principal es iterar sobre diferentes arquitecturas y librerías para lograr una herramienta de traducción eficiente. Se busca:

- Comparar rendimiento entre frameworks de UI (**Tkinter** vs **PyQt6**).
- Implementar sistemas de **traducción automática** y generación de **Pinyin**.
- Probar sistemas de exportación de documentos (**PDF**).
- Experimentar con patrones de diseño modernos (Temas Dark/Light, Responsive).

## 📂 Versiones y Evolución

El proyecto se divide en dos etapas de desarrollo claramente diferenciadas:

### 🆕 [v2.0 - Versión Moderna (PyQt6)](./v2.0/)

Esta es la iteración más avanzada para escritorio, donde se aplican conceptos de diseño moderno y optimización.

- **Estado**: Prototipo Avanzado / Recomendado.
- **Tecnología**: Python + **PyQt6**.
- **Enfoque**: Experiencia de usuario (UX), rendimiento y estética.
- **Características Clave**:
  - ✨ Interfaz moderna y **Responsive**.
  - 🌙 Sistema de temas **Dark/Light Mode**.
  - ⚡ **Caché inteligente** y gestión de memoria.
  - 📄 Exportación a PDF con diseño profesional.
  - ⌨️ Atajos de teclado y animaciones.

### 📱 [Mobile - App Móvil Premium (Expo)](./movil/)

Nueva versión móvil diseñada para llevar la traducción a cualquier lugar con una experiencia táctil fluida.

- **Estado**: Versión inicial funcional.
- **Tecnología**: **React Native + Expo**.
- **Enfoque**: Portabilidad, diseño premium y servicios de IA.
- **Características Clave**:
  - 🎨 Diseño Moderno con gradientes y micro-interacciones.
  - 🗣️ Generación de Pinyin interactiva por tokens.
  - 🌐 Traducción instantánea multilingüe (ES/EN).
  - 🏗️ Arquitectura escalable lista para integración con Gemini/OpenAI.

### 🕰️ [v1.0 - Versión Clásica (Tkinter)](./v1.0/)

La primera prueba de concepto funcional.

- **Estado**: Legacy / Referencia.
- **Tecnología**: Python + **Tkinter**.
- **Enfoque**: Funcionalidad básica y simplicidad.
- **Características Clave**:
  - Traducción funcional básica.
  - Generación de Pinyin.
  - Interfaz estándar de sistema.

## 🛠️ Tecnologías Exploradas

| Tecnología       | v1.0 (Legacy) | v2.0 (Modern)         | Propósito            |
| ---------------- | ------------- | --------------------- | -------------------- |
| **UI Framework** | Tkinter       | **PyQt6**             | Interfaz Gráfica     |
| **Traducción**   | googletrans   | **deep-translator**   | Motor de traducción  |
| **Fonética**     | pypinyin      | **pypinyin**          | Generación de Pinyin |
| **Recursos**     | N/A           | **psutil**            | Monitoreo de RAM/CPU |
| **Reportes**     | reportlab     | **weasyprint/pdfkit** | Generación de PDF    |

## 🚀 Cómo probar el proyecto

Dado que son versiones de prueba, puedes ejecutar cualquiera de las dos para comparar su funcionamiento.

1. **Clonar el repositorio**:

   ```bash
   git clone https://github.com/Erick-Zam/Pinguino.git
   cd Pinguino
   ```

2. **Seleccionar versión**:
   - Para la experiencia moderna: `cd v2.0`
   - Para la versión clásica: `cd v1.0`

3. **Instalar dependencias y ejecutar**:
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

## 🤝 Contribuciones y Feedback

Al ser un proyecto de pruebas, cualquier sugerencia para mejorar la arquitectura, el rendimiento o la interfaz es bienvenida. Si encuentras errores o tienes ideas para la v3.0, no dudes en abrir un _Issue_ o un _Pull Request_.

---

**Desarrollado por [Erick-Zam](https://github.com/Erick-Zam)**
_Explorando los límites de Python en el escritorio._
