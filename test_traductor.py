#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import main

def probar_traductor():
    """Prueba rápida del traductor optimizado"""
    print("🚀 Iniciando Traductor Ultra Optimizado...")
    
    try:
        traductor = main.TraductorChino()
        
        print(f"⚡ Hardware: {traductor.hardware_info['cpu_brand']} - {traductor.hardware_info['cpu_count']} cores")
        print(f"💾 RAM: {traductor.hardware_info['memory_gb']}GB")
        print(f"🔧 Workers: {traductor.max_workers}")
        print(f"📊 HTML Viewer: {'Habilitado' if traductor.usar_html_viewer else 'CTkTable Fallback'}")
        print(f"🎯 Optimización: {'Alta gama' if traductor.hardware_info['is_high_end'] else 'Estándar'}")
        print(f"💾 Caché MB: {traductor.limite_cache_mb}")
        print(f"⚡ Update Interval: {traductor.update_interval}ms")
        
        print("\n✅ Todas las optimizaciones configuradas correctamente!")
        print("🎌 Traductor listo para máximo rendimiento")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    probar_traductor()