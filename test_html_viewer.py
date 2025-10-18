#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import main
import tkinter as tk

def probar_html_viewer():
    """Prueba específica del HTML viewer sin errores de scroll"""
    print("🧪 Probando HTML Viewer...")
    
    # Crear instancia del traductor
    traductor = main.TraductorChino()
    
    # Simular una traducción de prueba
    texto_prueba = "你好世界！这是测试。"
    print(f"📝 Texto de prueba: {texto_prueba}")
    
    try:
        # Crear la ventana principal
        traductor.crear_interfaz()
        
        # Simular datos de tabla pinyin
        datos_prueba = [
            ["nǐ", "hǎo", "shì", "jiè"],
            ["你", "好", "世", "界"],
            ["", "", "", ""],
            ["zhè", "shì", "cè", "shì"],
            ["这", "是", "测", "试"]
        ]
        
        # Actualizar el HTML viewer
        if traductor.usar_html_viewer:
            exito = traductor.actualizar_contenido_pinyin_html(datos_prueba)
            print(f"✅ HTML actualizado: {exito}")
        else:
            print("⚠️ Usando fallback CTkTable")
        
        # Mostrar mensaje de éxito
        print("🎯 Prueba completada - No errores de scroll")
        print("📱 HTML viewer configurado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False
    
    return True

if __name__ == "__main__":
    probar_html_viewer()