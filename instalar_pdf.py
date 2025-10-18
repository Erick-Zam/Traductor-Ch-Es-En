#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para instalar librerías opcionales de PDF para el traductor chino
"""

import subprocess
import sys

def instalar_libreria(nombre, descripcion):
    """Instala una librería usando pip"""
    try:
        print(f"📦 Instalando {nombre} ({descripcion})...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", nombre])
        print(f"✅ {nombre} instalado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando {nombre}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado instalando {nombre}: {e}")
        return False

def verificar_libreria(nombre):
    """Verifica si una librería está instalada"""
    try:
        __import__(nombre)
        print(f"✅ {nombre} ya está instalado")
        return True
    except ImportError:
        print(f"❌ {nombre} no está instalado")
        return False

def main():
    """Función principal"""
    print("🔧 Instalador de Librerías PDF para Traductor Chino")
    print("=" * 60)
    
    # Librerías para exportar PDF
    librerias_pdf = [
        ("weasyprint", "Conversión HTML a PDF (recomendado)"),
        ("pdfkit", "Conversión HTML a PDF (alternativo)")
    ]
    
    print("\n📋 Verificando librerías PDF existentes...")
    
    # Verificar cuáles ya están instaladas
    instaladas = []
    for nombre, desc in librerias_pdf:
        if verificar_libreria(nombre):
            instaladas.append(nombre)
    
    if len(instaladas) == len(librerias_pdf):
        print("\n🎉 ¡Todas las librerías PDF ya están instaladas!")
        print("💡 Tu traductor puede exportar PDF directamente")
        return
    
    print(f"\n🔨 Instalando {len(librerias_pdf) - len(instaladas)} librerías faltantes...")
    
    # Instalar las que faltan
    exitos = 0
    for nombre, desc in librerias_pdf:
        if nombre not in instaladas:
            if instalar_libreria(nombre, desc):
                exitos += 1
    
    print(f"\n📊 Resumen de instalación:")
    print(f"   ✅ Instaladas exitosamente: {exitos}")
    print(f"   ❌ Fallos de instalación: {len(librerias_pdf) - len(instaladas) - exitos}")
    
    if exitos > 0:
        print("\n🎯 ¡Instalación completada!")
        print("💡 Ahora puedes usar el botón '📄 PDF' en el traductor")
        print("   para exportar la tabla Pinyin como PDF")
    else:
        print("\n⚠️ No se pudo instalar ninguna librería PDF")
        print("💡 El traductor seguirá funcionando, pero el botón PDF")
        print("   guardará archivos HTML que puedes convertir manualmente")
    
    print("\n📝 Notas importantes:")
    print("   • weasyprint: Funciona mejor en la mayoría de sistemas")
    print("   • pdfkit: Requiere wkhtmltopdf instalado por separado")
    print("   • Si fallan ambas, el traductor usa método alternativo (HTML)")

if __name__ == "__main__":
    main()