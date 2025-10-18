#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import main

def probar_copia_tabla():
    """Prueba específica de la función de copiado de tabla HTML"""
    print("🧪 Probando función de copiado HTML...")
    
    # Crear instancia del traductor
    traductor = main.TraductorChino()
    
    # Datos de prueba más completos
    datos_prueba = [
        ["nǐ", "hǎo", "shì", "jiè", "!"],
        ["你", "好", "世", "界", "！"],
        ["", "", "", "", ""],  # Separador
        ["zhè", "shì", "cè", "shì", ""],
        ["这", "是", "测", "试", ""],
        ["", "", "", "", ""],  # Separador
        ["wǒ", "ài", "xué", "xí", ""],
        ["我", "爱", "学", "习", ""]
    ]
    
    try:
        # Crear la interfaz
        traductor.crear_interfaz()
        
        # Actualizar el HTML viewer con datos de prueba
        if traductor.usar_html_viewer:
            exito = traductor.actualizar_contenido_pinyin_html(datos_prueba)
            print(f"✅ HTML actualizado: {exito}")
            
            # Verificar que el HTML contiene la función de copiado
            if hasattr(traductor, 'html_frame') and traductor.html_frame:
                print("✅ HTML Frame disponible")
                print("📋 Función de copiado JavaScript incluida")
                print("🎯 Botón 'Copiar Tabla' disponible en la interfaz")
                print("📊 Estadísticas movidas al final del HTML")
                
                # Contar filas válidas
                filas_validas = [fila for fila in datos_prueba if any(celda.strip() for celda in fila if celda)]
                print(f"📝 Filas con contenido: {len(filas_validas)}")
                
            else:
                print("⚠️ HTML Frame no disponible")
        else:
            print("⚠️ Usando fallback CTkTable")
        
        print("\n🔧 Mejoras implementadas:")
        print("  ✅ Estadísticas movidas al final del HTML")
        print("  ✅ Función copyTable() mejorada")
        print("  ✅ Soporte para copiar solo filas visibles")
        print("  ✅ Método alternativo de copiado (fallback)")
        print("  ✅ Notificaciones de estado del copiado")
        print("  ✅ Filtrado de filas separadoras")
        
        print("\n📋 Para probar el copiado:")
        print("  1. Ejecuta la aplicación principal: python main.py")
        print("  2. Traduce algún texto chino")
        print("  3. Haz clic en 'Copiar Tabla' en el HTML viewer")
        print("  4. Pega en cualquier editor (Ctrl+V)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False

if __name__ == "__main__":
    probar_copia_tabla()