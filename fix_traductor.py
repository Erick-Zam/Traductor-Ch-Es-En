#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de reparación para corregir problemas en el traductor chino
"""

import os
import re

def corregir_caracteres_corruptos():
    """Corrige caracteres corruptos en el archivo main.py"""
    
    archivo = "main.py"
    
    if not os.path.exists(archivo):
        print(f"❌ No se encontró el archivo {archivo}")
        return False
    
    try:
        # Leer el archivo con encoding UTF-8
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Backup del archivo original
        with open(f"{archivo}.backup", 'w', encoding='utf-8') as f:
            f.write(contenido)
        print(f"✅ Backup creado: {archivo}.backup")
        
        # Correcciones específicas
        correcciones = [
            # Corregir el carácter corrupto en el botón de inglés
            (r'text="[^"]*🇸 Inglés"', 'text="🇺🇸 Inglés"'),
            # Asegurar que las funciones de traducción guarden las variables
            (r'(self\.texto_traduccion\.insert\("1\.0", texto_ingles\))\s*\n\s*(self\.actualizar_progreso)', 
             r'\1\n                    # Guardar en variables para uso posterior\n                    self.traduccion_actual = texto_ingles\n                    self.texto_chino_actual = texto\n                    \2'),
        ]
        
        # Aplicar correcciones
        for patron, reemplazo in correcciones:
            if re.search(patron, contenido):
                contenido = re.sub(patron, reemplazo, contenido)
                print(f"✅ Aplicada corrección: {patron[:30]}...")
        
        # Guardar archivo corregido
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        print(f"✅ Archivo {archivo} corregido exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error corrigiendo el archivo: {e}")
        return False

def verificar_funciones_principales():
    """Verifica que las funciones principales estén presentes"""
    
    archivo = "main.py"
    
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        funciones_requeridas = [
            'def traducir_a_espanol',
            'def traducir_a_ingles',
            'def traducir_automatico',
            'def generar_pinyin_optimizado',
            'def crear_interfaz'
        ]
        
        print("\n🔍 Verificando funciones principales:")
        for funcion in funciones_requeridas:
            if funcion in contenido:
                print(f"✅ {funcion}")
            else:
                print(f"❌ {funcion} - ¡FALTA!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando funciones: {e}")
        return False

def verificar_dependencias():
    """Verifica que todas las dependencias estén disponibles"""
    
    dependencias = [
        'customtkinter',
        'tkinter',
        'deep_translator',
        'pyttsx3',
        'pypinyin',
        'CTkTable',
        'psutil'
    ]
    
    print("\n📦 Verificando dependencias:")
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - ¡FALTA! Instalar con: pip install {dep}")

def main():
    """Función principal del script de reparación"""
    
    print("🔧 Script de Reparación del Traductor Chino")
    print("=" * 50)
    
    # 1. Verificar dependencias
    verificar_dependencias()
    
    # 2. Verificar funciones principales
    verificar_funciones_principales()
    
    # 3. Corregir caracteres corruptos
    print("\n🛠️ Aplicando correcciones...")
    if corregir_caracteres_corruptos():
        print("✅ Todas las correcciones aplicadas exitosamente")
    else:
        print("❌ Hubo errores aplicando las correcciones")
    
    print("\n🎯 Reparación completada")
    print("💡 Sugerencias:")
    print("   - Reinicia el traductor para ver los cambios")
    print("   - Si persisten problemas, revisa los mensajes de error en la consola")
    print("   - Verifica que el texto chino se esté copiando correctamente")

if __name__ == "__main__":
    main()