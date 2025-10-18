#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prueba de respeto de puntuaciones importantes
"""

def dividir_linea_en_segmentos_occidentales(linea, limite):
    """Divide una línea en idiomas occidentales en segmentos respetando puntuaciones importantes"""
    if len(linea) <= limite:
        return [linea]
    
    segmentos = []
    segmento_actual = ""
    
    # Puntuaciones que indican fin de oración o pausa en idiomas occidentales (mejoradas)
    puntuaciones_corte = ['.', '!', '?', ';', '。', '！', '？', '；']  # Incluyendo chinas
    puntuaciones_pausa = [',', ':', ')', ']', '}', '，', '：', '）', '】', '》']  # Incluyendo chinas
    puntuaciones_enfasis = ['!', '?', '！', '？']  # Puntuaciones que requieren énfasis especial
    
    i = 0
    while i < len(linea):
        char = linea[i]
        segmento_actual += char
        
        # Si alcanzamos el límite, buscar un punto de corte apropiado
        if len(segmento_actual) >= limite:
            # Buscar punto de corte hacia atrás
            punto_corte = -1
            
            # Primero buscar puntuaciones de corte (especialmente exclamación y pregunta)
            for j in range(len(segmento_actual) - 1, max(0, len(segmento_actual) - 200), -1):
                if segmento_actual[j] in puntuaciones_corte:
                    punto_corte = j + 1
                    # Si es una puntuación de énfasis, asegurarse de que se incluya completa
                    if segmento_actual[j] in puntuaciones_enfasis:
                        # Verificar si hay espacios adicionales después para incluirlos
                        k = j + 1
                        while k < len(segmento_actual) and segmento_actual[k] in ' \n\t':
                            k += 1
                        punto_corte = k
                    break
            
            # Si no encontramos puntuación de corte, buscar puntuación de pausa
            if punto_corte == -1:
                for j in range(len(segmento_actual) - 1, max(0, len(segmento_actual) - 100), -1):
                    if segmento_actual[j] in puntuaciones_pausa:
                        punto_corte = j + 1
                        break
            
            # Si no encontramos nada, cortar en espacio
            if punto_corte == -1:
                for j in range(len(segmento_actual) - 1, max(0, len(segmento_actual) - 50), -1):
                    if segmento_actual[j] == ' ':
                        punto_corte = j + 1
                        break
            
            # Si aún no encontramos, cortar forzosamente
            if punto_corte == -1:
                punto_corte = limite
            
            # Agregar segmento y continuar
            segmentos.append(segmento_actual[:punto_corte])
            segmento_actual = segmento_actual[punto_corte:]
            # No incrementar i porque ya avanzamos en segmento_actual
            continue
        
        i += 1
    
    # Agregar el último segmento si queda algo
    if segmento_actual.strip():
        segmentos.append(segmento_actual)
    
    return segmentos

def validar_respeto_puntuaciones(texto_original, texto_procesado):
    """Valida que las puntuaciones importantes se respeten en el procesamiento"""
    # Contar puntuaciones importantes en el texto original
    puntuaciones_importantes = ['!', '?', '！', '？', '.', '。', ';', '；', ':', '：']
    
    contador_original = {}
    contador_procesado = {}
    
    for punct in puntuaciones_importantes:
        contador_original[punct] = texto_original.count(punct)
        contador_procesado[punct] = texto_procesado.count(punct)
    
    # Verificar que no se hayan perdido puntuaciones
    perdidas = []
    for punct, count_orig in contador_original.items():
        count_proc = contador_procesado.get(punct, 0)
        if count_proc < count_orig:
            perdidas.append(f"{punct}: {count_orig} → {count_proc}")
    
    if perdidas:
        print(f"⚠️ Puntuaciones perdidas: {', '.join(perdidas)}")
        return False
    else:
        print("✅ Todas las puntuaciones importantes fueron respetadas")
        return True

def main():
    """Función principal de prueba"""
    textos_prueba = [
        "¡Hola! ¿Cómo estás? Espero que bien; todo está perfecto.",
        "你好！你好吗？我很好；谢谢你的关心。",
        "What?! Are you serious? This is amazing!",
        "¡¿En serio?! ¡Esto es increíble! ¿Verdad?",
        "Testing: normal, punctuation; works? Yes!",
    ]
    
    print("🔍 Probando respeto de puntuaciones importantes...")
    print("="*60)
    
    for i, texto in enumerate(textos_prueba, 1):
        print(f"\n--- Prueba {i} ---")
        print(f"Texto original: {texto}")
        
        # Probar división en segmentos
        segmentos = dividir_linea_en_segmentos_occidentales(texto, 20)
        texto_reunido = ''.join(segmentos)
        
        print(f"Segmentos: {segmentos}")
        print(f"Texto procesado: {texto_reunido}")
        
        # Validar
        respetado = validar_respeto_puntuaciones(texto, texto_reunido)
        print(f"Resultado: {'✅ CORRECTO' if respetado else '❌ ERROR'}")
        
        # Mostrar estadísticas
        puntuaciones_enfasis = ['!', '?', '！', '？']
        orig_enfasis = sum(texto.count(p) for p in puntuaciones_enfasis)
        proc_enfasis = sum(texto_reunido.count(p) for p in puntuaciones_enfasis)
        print(f"Puntuaciones de énfasis: {orig_enfasis} → {proc_enfasis}")
    
    print(f"\n{'='*60}")
    print("🎯 Prueba de respeto de puntuaciones completada.")

if __name__ == "__main__":
    main()