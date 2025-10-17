import customtkinter
import tkinter as tk
from deep_translator import GoogleTranslator
import pyttsx3
import threading
from pypinyin import pinyin, lazy_pinyin, Style
from CTkTable import CTkTable
import sys
import os
import time
from concurrent.futures import ThreadPoolExecutor
import queue

# --- Configuración para ejecutable ---
def resource_path(relative_path):
    """Obtener path absoluto del recurso, funciona para dev y para PyInstaller"""
    try:
        # PyInstaller crea una carpeta temporal y almacena el path en _MEIPASS
        # type: ignore - _MEIPASS es creado dinámicamente por PyInstaller
        base_path = sys._MEIPASS  # type: ignore
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Configuración inicial de la apariencia ---
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")


class TraductorChino:
    """Aplicación de traductor chino con pronunciación Pinyin"""
    
    def __init__(self):
        """Inicializa la aplicación del traductor"""
        # Caché para traducciones (optimización)
        self.cache_traducciones = {}
        self.cache_pinyin = {}
        
        # Variables para guardar traducciones actuales
        self.traduccion_actual = ""
        self.pinyin_actual = ""
        self.texto_chino_actual = ""
        
        # Pool de hilos para traducción asíncrona
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.translation_queue = queue.Queue()
        
        # Variables de control de progreso
        self.progreso_actual = 0
        self.progreso_total = 100
        self.traduccion_en_progreso = False
        
        # Control de optimización de UI
        self.resize_timer = None
        self.ui_bloqueada = False
        
        # Inicializar traductor y motor de voz
        self.translator = GoogleTranslator(source='auto', target='zh-CN')
        self.engine = None
        self.inicializar_motor_voz()
        
        # Crear ventana principal con mejor geometría inicial
        self.app = customtkinter.CTk()
        self.app.geometry("1400x800")  # Más ancho, menos alto
        self.app.title("Traductor Chino → Español e Inglés con Pinyin")
        self.app.resizable(True, True)
        
        # Configurar icono si existe (para .exe)
        try:
            icon_path = resource_path("icon.ico")
            if os.path.exists(icon_path):
                self.app.iconbitmap(icon_path)
        except:
            pass  # Continuar sin icono si no existe
        
        # Configurar tamaño mínimo más realista
        self.app.minsize(900, 500)
        
        # Variables para responsividad mejorada
        self.ventana_ancho = 1400
        self.ventana_alto = 800
        self.es_modo_compacto = False
        
        # Configurar grid principal para mejor control del layout
        self.app.grid_columnconfigure(0, weight=1)
        self.app.grid_rowconfigure(0, weight=1)
        
        # Crear la interfaz
        self.crear_interfaz()
        
        # Configurar optimización periódica
        self.app.after(30000, self.optimizacion_periodica)  # Cada 30 segundos
        
        # Configurar eventos de redimensionamiento para responsividad OPTIMIZADA
        self.app.bind("<Configure>", self.on_window_resize_optimizado)
    
    def inicializar_motor_voz(self):
        """Inicializa el motor de síntesis de voz con manejo de errores"""
        try:
            self.engine = pyttsx3.init()
            self.configurar_voz()
        except Exception as e:
            print(f"Advertencia: No se pudo inicializar el motor de voz: {e}")
            self.engine = None
    
    def configurar_voz(self):
        """Configura el motor de voz con configuración básica"""
        if not self.engine:
            return
        
        try:
            # Configurar solo la velocidad de habla para evitar problemas de tipo
            self.engine.setProperty('rate', 150)
            print("Motor de voz configurado con velocidad estándar")
        except Exception as e:
            print(f"Error configurando motor de voz: {e}")
    
    def crear_interfaz(self):
        """Crea todos los elementos de la interfaz con diseño reorganizado"""
        
        # --- Container principal con grid ---
        self.main_container = customtkinter.CTkFrame(self.app)
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configurar grid del container principal para nueva distribución
        self.main_container.grid_columnconfigure(0, weight=1)  # Lado izquierdo (texto y traducción)
        self.main_container.grid_columnconfigure(1, weight=1)  # Lado derecho (tabla Pinyin)
        self.main_container.grid_rowconfigure(0, weight=0)  # Título fijo
        self.main_container.grid_rowconfigure(1, weight=1)  # Contenido principal
        self.main_container.grid_rowconfigure(2, weight=0)  # Barra de progreso
        self.main_container.grid_rowconfigure(3, weight=0)  # Botones fijos
        
        # --- Título compacto ---
        titulo = customtkinter.CTkLabel(
            self.main_container,
            text="🈳 Traductor de Chino 🈳",
            font=("Arial", 26, "bold")  # Letra más grande
        )
        titulo.grid(row=0, column=0, columnspan=2, pady=(10, 15), sticky="ew")
        
        # === LADO IZQUIERDO: Texto y Traducción ===
        frame_izquierdo = customtkinter.CTkFrame(self.main_container)
        frame_izquierdo.grid(row=1, column=0, sticky="nsew", padx=(5, 2.5), pady=5)
        frame_izquierdo.grid_columnconfigure(0, weight=1)
        frame_izquierdo.grid_rowconfigure(1, weight=1)  # Texto chino
        frame_izquierdo.grid_rowconfigure(3, weight=1)  # Traducción
        
        # --- Texto en Chino (arriba) ---
        label_entrada = customtkinter.CTkLabel(
            frame_izquierdo,
            text="Texto en Chino:",
            font=("Arial", 18, "bold")  # Letra más grande
        )
        label_entrada.grid(row=0, column=0, pady=(10, 5), sticky="w", padx=10)
        
        self.texto_entrada = customtkinter.CTkTextbox(
            frame_izquierdo,
            height=200,  # Más alto
            font=("Arial", 20),  # Letra más grande
            wrap="word"
        )
        self.texto_entrada.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # --- Botones para seleccionar idioma ---
        frame_idiomas = customtkinter.CTkFrame(frame_izquierdo)
        frame_idiomas.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        frame_idiomas.grid_columnconfigure(0, weight=1)
        frame_idiomas.grid_columnconfigure(1, weight=1)
        
        self.btn_espanol = customtkinter.CTkButton(
            frame_idiomas,
            text="🇪🇸 Español",
            command=self.traducir_a_espanol,
            font=("Arial", 14, "bold"),
            height=35,  # Más alto
            corner_radius=8
        )
        self.btn_espanol.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")
        
        self.btn_ingles = customtkinter.CTkButton(
            frame_idiomas,
            text="�🇸 Inglés",
            command=self.traducir_a_ingles,
            font=("Arial", 14, "bold"),
            height=35,  # Más alto
            corner_radius=8
        )
        self.btn_ingles.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="ew")
        
        # --- Traducción (abajo) ---
        label_traduccion = customtkinter.CTkLabel(
            frame_izquierdo,
            text="Traducción:",
            font=("Arial", 18, "bold")  # Letra más grande
        )
        label_traduccion.grid(row=3, column=0, pady=(0, 5), sticky="w", padx=10)
        
        self.texto_traduccion = customtkinter.CTkTextbox(
            frame_izquierdo,
            height=200,  # Más alto
            font=("Arial", 20),  # Letra más grande
            wrap="word"
        )
        self.texto_traduccion.grid(row=4, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # === LADO DERECHO: Tabla Pinyin Completa ===
        self.crear_seccion_pinyin_derecha()
        
        # === BARRA DE PROGRESO (entre contenido y botones) ===
        self.crear_barra_progreso()
        
        # --- Botones centrados (AL FINAL) ---
        self.crear_botones_responsive()
    
    def crear_botones_responsive(self):
        """Crea los botones con layout responsive y fuentes más grandes"""
        self.frame_botones = customtkinter.CTkFrame(self.main_container)
        self.frame_botones.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=10)
        
        # Configurar grid para centrar botones (4 botones ahora)
        for i in range(4):
            self.frame_botones.grid_columnconfigure(i, weight=1)
        
        # Botones con tamaños optimizados y fuentes más grandes
        self.btn_traducir = customtkinter.CTkButton(
            self.frame_botones,
            text="🈳 Traducir",
            command=self.traducir_chino_a_espanol,
            font=("Arial", 16, "bold"),  # Fuente más grande
            height=45,  # Más alto
            corner_radius=10
        )
        self.btn_traducir.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        
        self.btn_auto = customtkinter.CTkButton(
            self.frame_botones,
            text="🔄 Auto",
            command=self.traducir_automatico,
            font=("Arial", 16, "bold"),  # Fuente más grande
            height=45,  # Más alto
            corner_radius=10
        )
        self.btn_auto.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        self.btn_copiar = customtkinter.CTkButton(
            self.frame_botones,
            text="📋 Copiar Todo",
            command=self.copiar_tabla_pinyin,
            font=("Arial", 16, "bold"),  # Fuente más grande
            height=45,  # Más alto
            corner_radius=10,
            fg_color="#059669",
            hover_color="#047857"
        )
        self.btn_copiar.grid(row=0, column=2, padx=5, pady=10, sticky="ew")
        
        self.btn_limpiar = customtkinter.CTkButton(
            self.frame_botones,
            text="🗑️ Limpiar",
            command=self.limpiar_campos,
            font=("Arial", 16, "bold"),  # Fuente más grande
            height=45,  # Más alto
            corner_radius=10,
            fg_color="#666666",
            hover_color="#777777"
        )
        self.btn_limpiar.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
    
    def crear_seccion_pinyin_derecha(self):
        """Crea la sección de pinyin en el lado derecho con diseño optimizado"""
        # Frame principal del pinyin (lado derecho completo)
        self.frame_pinyin_principal = customtkinter.CTkFrame(self.main_container)
        self.frame_pinyin_principal.grid(row=1, column=1, sticky="nsew", padx=(2.5, 5), pady=5)
        self.frame_pinyin_principal.grid_columnconfigure(0, weight=1)
        self.frame_pinyin_principal.grid_rowconfigure(1, weight=1)
        
        # Header del pinyin con info
        header_pinyin = customtkinter.CTkFrame(self.frame_pinyin_principal)
        header_pinyin.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 10))
        header_pinyin.grid_columnconfigure(1, weight=1)
        
        label_pinyin = customtkinter.CTkLabel(
            header_pinyin,
            text="Pronunciación Pinyin:",
            font=("Arial", 18, "bold")  # Letra más grande
        )
        label_pinyin.grid(row=0, column=0, pady=10, padx=10, sticky="w")
        
        # Info responsive
        self.info_pinyin = customtkinter.CTkLabel(
            header_pinyin,
            text="💡 Ingresa caracteres chinos para ver la pronunciación",
            font=("Arial", 12),  # Letra más grande
            text_color="gray"
        )
        self.info_pinyin.grid(row=0, column=1, pady=10, padx=10, sticky="e")
        
        # Frame contenedor para la tabla con scroll (más grande)
        self.frame_tabla_container = customtkinter.CTkFrame(self.frame_pinyin_principal)
        self.frame_tabla_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))
        self.frame_tabla_container.grid_columnconfigure(0, weight=1)
        self.frame_tabla_container.grid_rowconfigure(0, weight=1)
        
        # Frame scrollable para la tabla
        self.scrollable_frame = customtkinter.CTkScrollableFrame(
            self.frame_tabla_container,
            corner_radius=8,
            scrollbar_button_color=("#2563eb", "#1d4ed8"),
            scrollbar_button_hover_color=("#1d4ed8", "#1e40af")
        )
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=3, pady=3)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Inicializar tabla vacía (se creará dinámicamente)
        self.tabla_pinyin = None
        
        # Textbox para mostrar información cuando no hay tabla
        self.texto_info = customtkinter.CTkTextbox(
            self.scrollable_frame,
            font=("Arial", 14),  # Letra más grande
            fg_color=("#f8f9fa", "#1a1a1a"),
            wrap="word",
            corner_radius=8,
            border_width=1,
            border_color=("#d1d5db", "#374151")
        )
        self.texto_info.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        
        # Mensaje inicial
        self.mostrar_mensaje_inicial()
    
    def crear_barra_progreso(self):
        """Crea la barra de progreso para traducción"""
        # Frame para la barra de progreso
        self.frame_progreso = customtkinter.CTkFrame(self.main_container)
        self.frame_progreso.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=(5, 0))
        self.frame_progreso.grid_columnconfigure(0, weight=1)
        
        # Etiqueta de progreso
        self.label_progreso = customtkinter.CTkLabel(
            self.frame_progreso,
            text="Listo para traducir",
            font=("Arial", 12),
            text_color="gray"
        )
        self.label_progreso.grid(row=0, column=0, pady=2, sticky="w", padx=10)
        
        # Barra de progreso
        self.progress_bar = customtkinter.CTkProgressBar(
            self.frame_progreso,
            height=8,
            corner_radius=4
        )
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))
        self.progress_bar.set(0)  # Inicializar en 0
        
        # Ocultar inicialmente
        self.frame_progreso.grid_remove()
    
    def mostrar_barra_progreso(self, texto="Procesando..."):
        """Muestra la barra de progreso con texto"""
        self.frame_progreso.grid()
        self.label_progreso.configure(text=texto)
        self.progress_bar.set(0)
        self.app.update()
    
    def actualizar_progreso(self, valor, texto=""):
        """Actualiza el progreso de la barra"""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.set(valor / 100.0)  # CTkProgressBar usa valores 0.0-1.0
            if texto:
                self.label_progreso.configure(text=texto)
            self.app.update()
    
    def ocultar_barra_progreso(self):
        """Oculta la barra de progreso"""
        if hasattr(self, 'frame_progreso'):
            self.frame_progreso.grid_remove()
            self.app.update()
    
    def crear_seccion_pinyin(self):
        """Crea la sección de pinyin optimizada con CTkTable"""
        # Frame principal del pinyin
        self.frame_pinyin_principal = customtkinter.CTkFrame(self.main_container)
        self.frame_pinyin_principal.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.frame_pinyin_principal.grid_columnconfigure(0, weight=1)
        self.frame_pinyin_principal.grid_rowconfigure(1, weight=1)
        
        # Header del pinyin con info
        header_pinyin = customtkinter.CTkFrame(self.frame_pinyin_principal)
        header_pinyin.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        header_pinyin.grid_columnconfigure(1, weight=1)
        
        label_pinyin = customtkinter.CTkLabel(
            header_pinyin,
            text="Pronunciación Pinyin:",
            font=("Arial", 16, "bold")
        )
        label_pinyin.grid(row=0, column=0, pady=8, padx=10, sticky="w")
        
        # Info responsive
        self.info_pinyin = customtkinter.CTkLabel(
            header_pinyin,
            text="💡 Ingresa caracteres chinos para ver la pronunciación",
            font=("Arial", 11),
            text_color="gray"
        )
        self.info_pinyin.grid(row=0, column=1, pady=8, padx=10, sticky="e")
        
        # Frame contenedor para la tabla con scroll
        self.frame_tabla_container = customtkinter.CTkFrame(self.frame_pinyin_principal)
        self.frame_tabla_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))
        self.frame_tabla_container.grid_columnconfigure(0, weight=1)
        self.frame_tabla_container.grid_rowconfigure(0, weight=1)
        
        # Frame scrollable para la tabla
        self.scrollable_frame = customtkinter.CTkScrollableFrame(
            self.frame_tabla_container,
            corner_radius=8,
            scrollbar_button_color=("#2563eb", "#1d4ed8"),
            scrollbar_button_hover_color=("#1d4ed8", "#1e40af")
        )
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Inicializar tabla vacía (se creará dinámicamente)
        self.tabla_pinyin = None
        
        # Textbox para mostrar información cuando no hay tabla
        self.texto_info = customtkinter.CTkTextbox(
            self.scrollable_frame,
            font=("Arial", 12),
            fg_color=("#f8f9fa", "#1a1a1a"),
            wrap="word",
            corner_radius=8,
            border_width=1,
            border_color=("#d1d5db", "#374151")
        )
        self.texto_info.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Mensaje inicial
        self.mostrar_mensaje_inicial()
    
    def mostrar_mensaje_inicial(self):
        """Muestra el mensaje inicial en el área de información"""
        mensaje_inicial = (
            "🎌 Traductor de Chino Optimizado - Ultra Rápido ⚡\n\n"
            "💡 Instrucciones:\n"
            "• Ingresa texto en chino en el campo izquierdo superior\n"
            "• Haz clic en '🇪🇸 Español' o '🇺🇸 Inglés' para traducir\n"
            "• La traducción aparecerá en el campo inferior izquierdo\n"
            "• La pronunciación Pinyin aparecerá aquí con scroll\n"
            "• Usa los botones de acción para traducir y copiar\n\n"
            "⚡ Nuevas optimizaciones de velocidad:\n"
            "🔸 Traducción asíncrona en hilos separados\n"
            "🔸 Barra de progreso visual en tiempo real\n"
            "🔸 Caché inteligente para traducciones repetidas\n"
            "🔸 Procesamiento por lotes de caracteres Pinyin\n"
            "🔸 Bloqueo de botones durante procesamiento\n"
            "🔸 Límites optimizados para mejor rendimiento\n"
            "� Respeto mejorado de puntuaciones importantes (¡!?, ？！。)\n"
            "�🖱️ Interfaz fluida • Progreso visible • ¡Más rápido!\n\n"
            "🧪 Para probar el respeto de puntuaciones, escribe en la consola:\n"
            "traductor.probar_respeto_puntuaciones()"
        )
        self.texto_info.delete("1.0", "end")
        self.texto_info.insert("1.0", mensaje_inicial)
    
    def copiar_tabla_pinyin(self):
        """Copia el contenido de la tabla de pinyin y la traducción al portapapeles"""
        try:
            # Verificar si hay contenido para copiar
            traduccion_texto = self.texto_traduccion.get("1.0", "end-1c").strip()
            
            if not traduccion_texto and (not hasattr(self, 'tabla_pinyin') or not self.tabla_pinyin):
                self.mostrar_error("No hay traducción ni tabla de Pinyin para copiar")
                return
            
            contenido_final = []
            
            # 1. Agregar la traducción si existe
            if traduccion_texto:
                contenido_final.append("=== TRADUCCIÓN ===")
                contenido_final.append(traduccion_texto)
                contenido_final.append("")  # Línea en blanco
            
            # 2. Agregar la tabla de pinyin si existe
            if hasattr(self, 'tabla_pinyin') and self.tabla_pinyin:
                contenido_final.append("=== PRONUNCIACIÓN PINYIN ===")
                
                # Obtener los datos de la tabla
                for i in range(self.tabla_pinyin.rows):
                    fila = []
                    for j in range(self.tabla_pinyin.columns):
                        try:
                            celda = self.tabla_pinyin.get(i, j)
                            if isinstance(celda, list) and len(celda) > 0:
                                fila.append(str(celda[0]))
                            else:
                                fila.append(str(celda) if celda else "")
                        except:
                            fila.append("")
                    contenido_final.append("\t".join(fila))
            
            # Si no hay nada que copiar
            if not contenido_final:
                self.mostrar_error("No hay contenido para copiar")
                return
            
            # Unir todo el contenido
            texto_final = "\n".join(contenido_final)
            
            # Copiar al portapapeles
            self.app.clipboard_clear()
            self.app.clipboard_append(texto_final)
            self.app.update()  # Asegurar que se copie
            
            # Mostrar confirmación temporal
            texto_original = self.btn_copiar.cget("text")
            self.btn_copiar.configure(text="✅ Copiado")
            self.app.after(1500, lambda: self.btn_copiar.configure(text=texto_original))
            
        except Exception as e:
            self.mostrar_error(f"Error copiando contenido: {str(e)}")
    
    def configurar_scroll_mejorado(self):
        """Configuración de scroll ya no necesaria con CTkTable"""
        pass

    def on_window_resize_optimizado(self, event):
        """Manejo optimizado de redimensionamiento de ventana con debounce"""
        # Solo procesar eventos de la ventana principal, no de widgets hijos
        if event.widget != self.app:
            return
        
        # Cancelar timer anterior si existe (debounce)
        if self.resize_timer:
            self.app.after_cancel(self.resize_timer)
        
        # Programar ajuste con retraso para evitar múltiples llamadas
        self.resize_timer = self.app.after(150, self.ejecutar_ajuste_responsive)
    
    def ejecutar_ajuste_responsive(self):
        """Ejecuta el ajuste responsive de manera eficiente"""
        if self.ui_bloqueada:
            return
        
        try:
            self.ui_bloqueada = True
            self.ajustar_responsive_optimizado()
        except Exception as e:
            print(f"Error en ajuste responsive: {e}")
        finally:
            self.ui_bloqueada = False
            self.resize_timer = None
    
    def ajustar_responsive_optimizado(self):
        """Ajusta parámetros responsive de manera más eficiente"""
        try:
            # Obtener dimensiones actuales
            ancho_actual = self.app.winfo_width()
            alto_actual = self.app.winfo_height()
            
            # Solo actualizar si hay cambio significativo (> 50px)
            if (hasattr(self, 'ultimo_ancho') and 
                abs(ancho_actual - self.ultimo_ancho) < 50 and
                abs(alto_actual - self.ultimo_alto) < 50):
                return
            
            self.ultimo_ancho = ancho_actual
            self.ultimo_alto = alto_actual
            
            # Cálculo optimizado de caracteres por línea
            if ancho_actual < 700:
                caracteres_linea = 4
                font_size = 16
            elif ancho_actual < 1100:
                caracteres_linea = 6
                font_size = 18
            else:
                caracteres_linea = 8
                font_size = 20
            
            # Actualizar solo si cambió significativamente
            if not hasattr(self, 'caracteres_por_linea') or self.caracteres_por_linea != caracteres_linea:
                self.caracteres_por_linea = caracteres_linea
                
                # Regenerar tabla solo si hay datos y cambió el layout
                if (hasattr(self, 'pinyin_actual') and self.pinyin_actual and 
                    hasattr(self, 'tabla_pinyin') and self.tabla_pinyin):
                    self.app.after_idle(self.regenerar_tabla_pinyin)
            
            # Actualizar fuentes de manera eficiente
            if not hasattr(self, 'ultimo_font_size') or self.ultimo_font_size != font_size:
                self.ultimo_font_size = font_size
                self.actualizar_fuentes_optimizado(font_size)
            
            # Actualizar info label responsive
            self.actualizar_info_responsive(ancho_actual)
                
        except Exception as e:
            print(f"Error en ajuste responsive optimizado: {e}")
    
    def actualizar_fuentes_optimizado(self, font_size):
        """Actualiza las fuentes de manera eficiente"""
        try:
            nueva_fuente = ("Arial", font_size)
            
            # Actualizar solo los campos principales
            if hasattr(self, 'texto_entrada'):
                self.texto_entrada.configure(font=nueva_fuente)
            if hasattr(self, 'texto_traduccion'):
                self.texto_traduccion.configure(font=nueva_fuente)
                
        except Exception as e:
            print(f"Error actualizando fuentes: {e}")
    
    def actualizar_info_responsive(self, ancho):
        """Actualiza el texto de información de manera responsive"""
        try:
            if hasattr(self, 'info_pinyin'):
                if ancho < 700:
                    texto = "💡 Pinyin"
                elif ancho < 1000:
                    texto = "💡 Pronunciación"
                else:
                    texto = "💡 Ingresa caracteres chinos para ver la pronunciación"
                
                if self.info_pinyin.cget("text") != texto:
                    self.info_pinyin.configure(text=texto)
        except:
            pass
    
    def regenerar_tabla_pinyin(self):
        """Regenera la tabla de pinyin con el layout actual"""
        if hasattr(self, 'pinyin_actual') and self.pinyin_actual:
            try:
                self.regenerar_tabla_pinyin()
            except Exception as e:
                print(f"Error regenerando tabla: {e}")
    
    def optimizacion_periodica(self):
        """Ejecuta optimizaciones periódicas para mantener el rendimiento"""
        try:
            # Optimizar caché si es necesario
            self.optimizar_rendimiento_ui()
            
            # Programar la siguiente optimización
            self.app.after(30000, self.optimizacion_periodica)
            
        except Exception as e:
            print(f"Error en optimización periódica: {e}")
            # Reprogramar de todos modos
            self.app.after(30000, self.optimizacion_periodica)
    
    def optimizar_rendimiento_ui(self):
        """Optimiza el rendimiento general de la UI"""
        try:
            # Limpiar caché si es muy grande (más de 50 elementos)
            if len(self.cache_traducciones) > 50:
                # Mantener solo los 30 más recientes
                items = list(self.cache_traducciones.items())[-30:]
                self.cache_traducciones = dict(items)
                print("Caché de traducciones optimizado")
            
            if len(self.cache_pinyin) > 50:
                # Mantener solo los 30 más recientes
                items = list(self.cache_pinyin.items())[-30:]
                self.cache_pinyin = dict(items)
                print("Caché de pinyin optimizado")
            
            # Forzar recolección de basura si es necesario
            import gc
            if len(self.cache_traducciones) + len(self.cache_pinyin) > 80:
                gc.collect()
                print("Recolección de basura ejecutada")
            
        except Exception as e:
            print(f"Error optimizando rendimiento: {e}")
    
    def recargar_contenido_inteligente(self):
        """Recarga el contenido de manera inteligente usando variables de caché"""
        try:
            # Verificar si hay contenido en variables para recargar
            if (hasattr(self, 'traduccion_actual') and self.traduccion_actual and
                hasattr(self, 'texto_chino_actual') and self.texto_chino_actual):
                
                # Recargar desde variables sin re-procesar
                exito = self.cargar_traduccion_desde_variable()
                if exito:
                    print("Contenido recargado desde variables de caché")
                    return True
            
            # Si no hay variables, verificar caché de traducciones
            texto_actual = self.texto_entrada.get("1.0", "end-1c")
            if texto_actual.strip():
                cache_key = f"es_{texto_actual}"
                if cache_key in self.cache_traducciones:
                    traduccion = self.cache_traducciones[cache_key]
                    self.texto_traduccion.delete("1.0", "end")
                    self.texto_traduccion.insert("1.0", traduccion)
                    
                    # Recargar pinyin desde caché
                    pinyin_key = f"pinyin_{texto_actual}"
                    if pinyin_key in self.cache_pinyin:
                        datos_tabla = self.cache_pinyin[pinyin_key]
                        self.crear_tabla_pinyin_optimizada_desde_cache(datos_tabla)
                    
                    print("Contenido recargado desde caché de traducciones")
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error recargando contenido inteligente: {e}")
            return False

    def traducir_chino_a_espanol(self):
        """Traduce texto del chino al español específicamente - función principal"""
        self.traducir_a_espanol()
    
    def traducir_automatico(self):
        """Detecta automáticamente el idioma y traduce con optimización"""
        texto = self.texto_entrada.get("1.0", "end-1c")
        if not texto.strip():
            self.mostrar_error("Por favor, ingresa un texto para traducir")
            return
        
        # Prevenir múltiples traducciones simultáneas
        if self.traduccion_en_progreso:
            self.mostrar_error("Ya hay una traducción en progreso. Espera a que termine.")
            return
        
        try:
            # Detectar idioma rápidamente
            if self.es_texto_chino(texto):
                # Si es chino, traducir al español (por defecto)
                self.traducir_a_espanol()
            else:
                # Si no es chino, usar traducción optimizada a chino
                self.deshabilitar_botones()
                
                def traducir_hilo():
                    try:
                        self.traduccion_en_progreso = True
                        self.app.after(0, lambda: self.mostrar_barra_progreso("Detectando idioma y traduciendo..."))
                        
                        self.app.after(0, lambda: self.actualizar_progreso(30, "Traduciendo a chino..."))
                        texto_traducido = self.traducir_texto_optimizado_a_chino(texto)
                        
                        # Mostrar traducción
                        def mostrar_resultado():
                            self.texto_traduccion.delete("1.0", "end")
                            self.texto_traduccion.insert("1.0", texto_traducido)
                            self.actualizar_progreso(80, "Generando Pinyin...")
                        
                        self.app.after(0, mostrar_resultado)
                        
                        # Generar pinyin
                        self.app.after(0, lambda: self.generar_pinyin_optimizado(texto_traducido))
                        
                        # Completar
                        self.app.after(0, lambda: self.actualizar_progreso(100, "¡Traducción automática completada!"))
                        time.sleep(0.5)
                        self.app.after(0, self.ocultar_barra_progreso)
                        
                    except Exception as e:
                        self.app.after(0, lambda: self.mostrar_error(f"Error en la traducción automática: {str(e)}"))
                        self.app.after(0, self.ocultar_barra_progreso)
                    finally:
                        self.traduccion_en_progreso = False
                        self.app.after(0, self.habilitar_botones)
                
                self.executor.submit(traducir_hilo)
            
        except Exception as e:
            self.mostrar_error(f"Error en la traducción automática: {str(e)}")
    
    def traducir_texto_optimizado_a_chino(self, texto):
        """Versión optimizada de traducción al chino"""
        try:
            limite_segmento = 2000
            
            if len(texto) <= limite_segmento:
                traductor_chino = GoogleTranslator(source='auto', target='zh-CN')
                return traductor_chino.translate(texto)
            
            # Dividir por líneas para mejor control
            lineas = texto.split('\n')
            lineas_traducidas = []
            total_lineas = len(lineas)
            
            for idx, linea in enumerate(lineas):
                progreso = 30 + (idx / total_lineas) * 40  # Entre 30% y 70%
                self.app.after(0, lambda p=progreso: self.actualizar_progreso(p, f"Traduciendo línea {idx+1}/{total_lineas}"))
                
                if not linea.strip():
                    lineas_traducidas.append('')
                    continue
                
                try:
                    traductor_chino = GoogleTranslator(source='auto', target='zh-CN')
                    linea_traducida = traductor_chino.translate(linea.strip())
                    lineas_traducidas.append(linea_traducida)
                except Exception as e:
                    print(f"Error traduciendo línea {idx} a chino: {e}")
                    lineas_traducidas.append(linea)
                
                time.sleep(0.1)  # Pausa breve
            
            return '\n'.join(lineas_traducidas)
            
        except Exception as e:
            raise Exception(f"Error en traducción optimizada a chino: {str(e)}")
    
    def traducir_a_chino(self):
        """Traduce texto del español al chino con soporte para textos largos"""
        texto = self.texto_entrada.get("1.0", "end-1c")
        if not texto.strip():
            self.mostrar_error("Por favor, ingresa un texto para traducir")
            return
        
        try:
            # Traducir usando el sistema de chunks
            texto_chino = self.traducir_texto_largo_a_chino(texto)
            
            # Mostrar traducción preservando formato
            self.texto_traduccion.delete("1.0", "end")
            self.texto_traduccion.insert("1.0", texto_chino)
            
            # Generar pinyin
            self.generar_pinyin(texto_chino)
            
        except Exception as e:
            self.mostrar_error(f"Error en la traducción: {str(e)}")
    
    def traducir_texto_largo_a_chino(self, texto):
        """Traduce textos largos del español/inglés al chino preservando formato exacto"""
        try:
            # Límite más pequeño para mejor precisión
            limite_segmento = 1500
            
            # Si el texto es corto, traducir directamente
            if len(texto) <= limite_segmento:
                traductor_chino = GoogleTranslator(source='auto', target='zh-CN')
                return traductor_chino.translate(texto)
            
            # Dividir por líneas para preservar formato exacto
            lineas = texto.split('\n')
            lineas_traducidas = []
            
            for linea in lineas:
                if not linea.strip():  # Línea vacía
                    lineas_traducidas.append('')  # Preservar líneas vacías
                    continue
                
                # Si la línea es muy larga, dividirla por oraciones
                if len(linea) > limite_segmento:
                    # Dividir por puntuaciones para respetar el contexto
                    segmentos = self.dividir_linea_en_segmentos_occidentales(linea, limite_segmento)
                    segmentos_traducidos = []
                    
                    for segmento in segmentos:
                        if segmento.strip():
                            try:
                                traductor_chino = GoogleTranslator(source='auto', target='zh-CN')
                                segmento_traducido = traductor_chino.translate(segmento.strip())
                                segmentos_traducidos.append(segmento_traducido)
                            except Exception as e:
                                print(f"Error traduciendo segmento a chino: {e}")
                                segmentos_traducidos.append(segmento)  # Mantener original si falla
                    
                    # Unir segmentos de la línea
                    linea_completa = ''.join(segmentos_traducidos)  # Sin espacios para chino
                    lineas_traducidas.append(linea_completa)
                else:
                    # Línea corta, traducir directamente
                    try:
                        traductor_chino = GoogleTranslator(source='auto', target='zh-CN')
                        linea_traducida = traductor_chino.translate(linea)
                        lineas_traducidas.append(linea_traducida)
                    except Exception as e:
                        print(f"Error traduciendo línea a chino: {e}")
                        lineas_traducidas.append(linea)  # Mantener original si falla
            
            # Unir todas las líneas preservando saltos de línea exactos
            return '\n'.join(lineas_traducidas)
            
        except Exception as e:
            raise Exception(f"Error en traducción a chino por segmentos: {str(e)}")
    
    def dividir_linea_en_segmentos_occidentales(self, linea, limite):
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
    
    def traducir_a_espanol(self):
        """Traduce texto del chino al español con barra de progreso y optimización"""
        texto = self.texto_entrada.get("1.0", "end-1c")
        if not texto.strip():
            self.mostrar_error("Por favor, ingresa texto en chino para traducir")
            return
        
        # Prevenir múltiples traducciones simultáneas
        if self.traduccion_en_progreso:
            self.mostrar_error("Ya hay una traducción en progreso. Espera a que termine.")
            return
        
        # Deshabilitar botones durante traducción
        self.deshabilitar_botones()
        
        # Ejecutar traducción en hilo separado
        def traducir_hilo():
            try:
                self.traduccion_en_progreso = True
                self.app.after(0, lambda: self.mostrar_barra_progreso("Iniciando traducción..."))
                
                # Verificar caché primero
                cache_key = f"es_{texto}"
                if cache_key in self.cache_traducciones:
                    self.app.after(0, lambda: self.actualizar_progreso(50, "Recuperando del caché..."))
                    texto_espanol = self.cache_traducciones[cache_key]
                    self.app.after(0, lambda: self.actualizar_progreso(80, "Caché recuperado"))
                else:
                    # Traducir texto optimizado
                    self.app.after(0, lambda: self.actualizar_progreso(20, "Analizando texto..."))
                    texto_espanol = self.traducir_texto_optimizado(texto, 'es')
                    # Guardar en caché
                    self.cache_traducciones[cache_key] = texto_espanol
                    self.app.after(0, lambda: self.actualizar_progreso(80, "Traducción completada"))
                
                # Mostrar traducción
                def mostrar_resultado():
                    self.texto_traduccion.delete("1.0", "end")
                    self.texto_traduccion.insert("1.0", texto_espanol)
                    # Guardar en variables para uso posterior
                    self.traduccion_actual = texto_espanol
                    self.texto_chino_actual = texto
                    self.actualizar_progreso(90, "Mostrando traducción...")
                
                self.app.after(0, mostrar_resultado)
                
                # Generar pinyin si es necesario
                if self.es_texto_chino(texto):
                    self.app.after(0, lambda: self.actualizar_progreso(95, "Generando tabla Pinyin..."))
                    self.app.after(0, lambda: self.generar_pinyin_optimizado(texto))
                
                # Completar
                self.app.after(0, lambda: self.actualizar_progreso(100, "¡Traducción completada!"))
                time.sleep(0.5)  # Mostrar brevemente el 100%
                self.app.after(0, self.ocultar_barra_progreso)
                
            except Exception as e:
                self.app.after(0, lambda: self.mostrar_error(f"Error en la traducción: {str(e)}"))
                self.app.after(0, self.ocultar_barra_progreso)
            finally:
                self.traduccion_en_progreso = False
                self.app.after(0, self.habilitar_botones)
        
        # Ejecutar en hilo separado
        self.executor.submit(traducir_hilo)
    
    def traducir_texto_optimizado(self, texto, idioma_destino):
        """Versión optimizada de traducción con mejor gestión de memoria"""
        try:
            # Límite optimizado basado en performance
            limite_segmento = 2000  # Aumentado para menos requests
            
            # Para textos cortos, traducir directamente
            if len(texto) <= limite_segmento:
                if idioma_destino == 'es':
                    traductor = GoogleTranslator(source='zh-CN', target='es')
                else:
                    traductor = GoogleTranslator(source='zh-CN', target='en')
                return traductor.translate(texto)
            
            # Dividir texto de manera más eficiente
            lineas = texto.split('\n')
            lineas_traducidas = []
            total_lineas = len(lineas)
            
            for idx, linea in enumerate(lineas):
                # Actualizar progreso basado en líneas procesadas
                progreso = 20 + (idx / total_lineas) * 50  # Entre 20% y 70%
                self.app.after(0, lambda p=progreso: self.actualizar_progreso(p, f"Procesando línea {idx+1}/{total_lineas}"))
                
                if not linea.strip():
                    lineas_traducidas.append('')
                    continue
                
                # Traducir línea por línea para mejor control de progreso
                try:
                    if idioma_destino == 'es':
                        traductor = GoogleTranslator(source='zh-CN', target='es')
                    else:
                        traductor = GoogleTranslator(source='zh-CN', target='en')
                    
                    linea_traducida = traductor.translate(linea.strip())
                    lineas_traducidas.append(linea_traducida)
                except Exception as e:
                    print(f"Error traduciendo línea {idx}: {e}")
                    lineas_traducidas.append(linea)  # Mantener original si falla
                
                # Pequeña pausa para no sobrecargar la API
                time.sleep(0.1)
            
            return '\n'.join(lineas_traducidas)
            
        except Exception as e:
            raise Exception(f"Error en traducción optimizada: {str(e)}")
    
    def generar_pinyin_optimizado(self, texto_chino):
        """Versión optimizada de generación de pinyin con progreso y caché mejorado"""
        try:
            if not texto_chino.strip():
                return
            
            # Guardar en variable para uso posterior
            self.pinyin_actual = texto_chino
            
            # Verificar caché primero para evitar procesamiento
            cache_key = f"pinyin_{texto_chino}"
            if cache_key in self.cache_pinyin:
                datos_tabla = self.cache_pinyin[cache_key]
                self.crear_tabla_pinyin_optimizada_desde_cache(datos_tabla)
                return
            
            # Procesar de manera optimizada
            if not self.contiene_caracteres_chinos(texto_chino):
                self.mostrar_error_pinyin("No se encontraron caracteres chinos válidos para generar Pinyin")
                return
            
            # Generar datos de manera más eficiente
            datos_tabla = self.crear_datos_pinyin_rapido(texto_chino)
            
            # Guardar en caché y mostrar
            self.cache_pinyin[cache_key] = datos_tabla
            self.crear_tabla_pinyin_optimizada_desde_cache(datos_tabla)
            
        except Exception as e:
            print(f"Error en generar_pinyin_optimizado: {e}")
            self.mostrar_error_pinyin(f"Error generando Pinyin: {str(e)}")
    
    def crear_tabla_pinyin_optimizada_desde_cache(self, datos_tabla):
        """Crea tabla de pinyin optimizada usando datos de caché"""
        try:
            if not datos_tabla:
                return
            
            # Verificar si ya existe la tabla y evitar recrearla innecesariamente
            if (hasattr(self, 'tabla_pinyin') and self.tabla_pinyin and 
                hasattr(self, 'ultima_tabla_datos') and 
                self.ultima_tabla_datos == datos_tabla):
                return  # La tabla ya está actualizada
            
            # Guardar referencia para evitar recreaciones
            self.ultima_tabla_datos = datos_tabla
            
            # Crear la tabla de manera eficiente
            self.crear_tabla_pinyin(datos_tabla)
            
        except Exception as e:
            print(f"Error creando tabla desde caché: {e}")
    
    def cargar_traduccion_desde_variable(self):
        """Carga la traducción desde las variables en caché para evitar re-procesamiento"""
        try:
            if hasattr(self, 'traduccion_actual') and self.traduccion_actual:
                # Cargar traducción en UI
                self.texto_traduccion.delete("1.0", "end")
                self.texto_traduccion.insert("1.0", self.traduccion_actual)
                
                # Cargar pinyin si existe
                if hasattr(self, 'texto_chino_actual') and self.texto_chino_actual:
                    self.generar_pinyin_optimizado(self.texto_chino_actual)
                
                return True
            return False
        except Exception as e:
            print(f"Error cargando desde variables: {e}")
            return False
    
    def crear_datos_pinyin_rapido(self, texto_completo):
        """Versión más rápida de creación de datos pinyin"""
        if not hasattr(self, 'caracteres_por_linea'):
            self.caracteres_por_linea = 8  # Aumentado para mejor rendimiento
        
        # Ajuste rápido de caracteres por línea
        total_chars_chinos = sum(1 for c in texto_completo if '\u4e00' <= c <= '\u9fff')
        if total_chars_chinos > 200:
            self.caracteres_por_linea = 12
        elif total_chars_chinos > 100:
            self.caracteres_por_linea = 10
        else:
            self.caracteres_por_linea = 8
        
        datos = []
        lineas = texto_completo.split('\n')
        
        # Procesamiento optimizado por lotes
        for idx_linea, linea in enumerate(lineas):
            if not linea.strip():
                datos.append(['┈' * min(3, self.caracteres_por_linea)])
                continue
            
            # Procesar caracteres en grupos más grandes
            caracteres_linea = list(linea)
            
            for i in range(0, len(caracteres_linea), self.caracteres_por_linea):
                grupo = caracteres_linea[i:i + self.caracteres_por_linea]
                
                fila_pinyin = []
                fila_caracteres = []
                
                # Procesamiento por lotes de pinyin para mejor rendimiento
                caracteres_chinos = [c for c in grupo if '\u4e00' <= c <= '\u9fff']
                if caracteres_chinos:
                    try:
                        # Procesar múltiples caracteres a la vez
                        pinyin_resultados = pinyin(caracteres_chinos, style=Style.TONE, heteronym=False)
                        pinyin_dict = {char: resultado[0] if resultado else "?" 
                                     for char, resultado in zip(caracteres_chinos, pinyin_resultados)}
                    except:
                        pinyin_dict = {char: "?" for char in caracteres_chinos}
                else:
                    pinyin_dict = {}
                
                # Construir filas con mejor manejo de puntuaciones importantes
                for char in grupo:
                    if '\u4e00' <= char <= '\u9fff':
                        fila_pinyin.append(pinyin_dict.get(char, "?"))
                        fila_caracteres.append(f' {char} ')
                    # Puntuaciones chinas importantes (respetadas con mayor énfasis)
                    elif char in '！？。，；：':
                        if char == '！':
                            fila_pinyin.append('❗️EXCL')
                            fila_caracteres.append(f'【{char}】')
                        elif char == '？':
                            fila_pinyin.append('❓PREG')
                            fila_caracteres.append(f'【{char}】')
                        elif char == '。':
                            fila_pinyin.append('⭕PUNTO')
                            fila_caracteres.append(f'《{char}》')
                        else:
                            fila_pinyin.append(f'●{char}●')
                            fila_caracteres.append(char)
                    # Puntuaciones occidentales importantes
                    elif char in '!?.,;:':
                        if char == '!':
                            fila_pinyin.append('❗️EXCL')
                            fila_caracteres.append(f'【{char}】')
                        elif char == '?':
                            fila_pinyin.append('❓PREG')
                            fila_caracteres.append(f'【{char}】')
                        elif char in '.,':
                            fila_pinyin.append(f'⚫{char}')
                            fila_caracteres.append(char)
                        else:
                            fila_pinyin.append(f'◦{char}◦')
                            fila_caracteres.append(char)
                    # Comillas y paréntesis (importantes para contexto)
                    elif char in '""''（）()[]{}【】《》':
                        fila_pinyin.append(f'📝{char}')
                        fila_caracteres.append(char)
                    # Otros símbolos
                    elif char in '"\'"/<>-=+*&%$#@~`^|\\':
                        fila_pinyin.append(f'◦{char}◦')
                        fila_caracteres.append(char)
                    elif char == ' ':
                        fila_pinyin.append('▫️')
                        fila_caracteres.append(char)
                    elif char.isdigit():
                        fila_pinyin.append(f'🔢{char}')
                        fila_caracteres.append(char)
                    elif char.isalpha():
                        fila_pinyin.append(f'🔤{char}')
                        fila_caracteres.append(char)
                    else:
                        fila_pinyin.append(f'◊{char}◊')
                        fila_caracteres.append(char)
                
                if fila_pinyin:
                    datos.append(fila_pinyin)
                    datos.append(fila_caracteres)
            
            # Separador entre líneas (optimizado)
            if idx_linea < len(lineas) - 1 and linea.strip():
                separador = ['━━━'] * min(2, self.caracteres_por_linea)
                if len(separador) < self.caracteres_por_linea:
                    separador.extend([''] * (self.caracteres_por_linea - len(separador)))
                datos.append(separador)
        
        return datos
    
    def deshabilitar_botones(self):
        """Deshabilita los botones durante la traducción"""
        botones = [self.btn_traducir, self.btn_auto, self.btn_espanol, self.btn_ingles]
        for btn in botones:
            if hasattr(btn, 'configure'):
                btn.configure(state="disabled")
    
    def habilitar_botones(self):
        """Habilita los botones después de la traducción"""
        botones = [self.btn_traducir, self.btn_auto, self.btn_espanol, self.btn_ingles]
        for btn in botones:
            if hasattr(btn, 'configure'):
                btn.configure(state="normal")
    
    def mostrar_progreso_traduccion(self, mensaje):
        """Muestra mensajes de progreso durante la traducción"""
        if hasattr(self, 'info_pinyin'):
            self.info_pinyin.configure(text=f"⏳ {mensaje}")
            self.app.update()  # Forzar actualización de la UI
    
    def traducir_a_ingles(self):
        """Traduce texto del chino al inglés con barra de progreso y optimización"""
        texto = self.texto_entrada.get("1.0", "end-1c")
        if not texto.strip():
            self.mostrar_error("Por favor, ingresa texto en chino para traducir")
            return
        
        # Prevenir múltiples traducciones simultáneas
        if self.traduccion_en_progreso:
            self.mostrar_error("Ya hay una traducción en progreso. Espera a que termine.")
            return
        
        # Deshabilitar botones durante traducción
        self.deshabilitar_botones()
        
        # Ejecutar traducción en hilo separado
        def traducir_hilo():
            try:
                self.traduccion_en_progreso = True
                self.app.after(0, lambda: self.mostrar_barra_progreso("Iniciando traducción a inglés..."))
                
                # Verificar caché primero
                cache_key = f"en_{texto}"
                if cache_key in self.cache_traducciones:
                    self.app.after(0, lambda: self.actualizar_progreso(50, "Recuperando del caché..."))
                    texto_ingles = self.cache_traducciones[cache_key]
                    self.app.after(0, lambda: self.actualizar_progreso(80, "Caché recuperado"))
                else:
                    # Traducir texto optimizado
                    self.app.after(0, lambda: self.actualizar_progreso(20, "Analizando texto..."))
                    texto_ingles = self.traducir_texto_optimizado(texto, 'en')
                    # Guardar en caché
                    self.cache_traducciones[cache_key] = texto_ingles
                    self.app.after(0, lambda: self.actualizar_progreso(80, "Traducción completada"))
                
                # Mostrar traducción
                def mostrar_resultado():
                    self.texto_traduccion.delete("1.0", "end")
                    self.texto_traduccion.insert("1.0", texto_ingles)
                    self.actualizar_progreso(90, "Mostrando traducción...")
                
                self.app.after(0, mostrar_resultado)
                
                # Generar pinyin si es necesario
                if self.es_texto_chino(texto):
                    self.app.after(0, lambda: self.actualizar_progreso(95, "Generando tabla Pinyin..."))
                    self.app.after(0, lambda: self.generar_pinyin_optimizado(texto))
                
                # Completar
                self.app.after(0, lambda: self.actualizar_progreso(100, "¡Traducción completada!"))
                time.sleep(0.5)  # Mostrar brevemente el 100%
                self.app.after(0, self.ocultar_barra_progreso)
                
            except Exception as e:
                self.app.after(0, lambda: self.mostrar_error(f"Error en la traducción: {str(e)}"))
                self.app.after(0, self.ocultar_barra_progreso)
            finally:
                self.traduccion_en_progreso = False
                self.app.after(0, self.habilitar_botones)
        
        # Ejecutar en hilo separado
        self.executor.submit(traducir_hilo)
    
    def traducir_texto_largo(self, texto, idioma_destino):
        """Traduce textos largos dividiéndolos en segmentos pequeños preservando formato exacto"""
        try:
            # Límite más pequeño para mejor precisión y respeto del formato
            limite_segmento = 1500  # Segmentos más pequeños para mejor control
            
            # Si el texto es muy corto, traducir directamente
            if len(texto) <= limite_segmento:
                if idioma_destino == 'es':
                    traductor = GoogleTranslator(source='zh-CN', target='es')
                else:  # 'en'
                    traductor = GoogleTranslator(source='zh-CN', target='en')
                return traductor.translate(texto)
            
            # Dividir por líneas para preservar formato exacto
            lineas = texto.split('\n')
            lineas_traducidas = []
            
            for linea in lineas:
                if not linea.strip():  # Línea vacía
                    lineas_traducidas.append('')  # Preservar líneas vacías
                    continue
                
                # Si la línea es muy larga, dividirla por oraciones
                if len(linea) > limite_segmento:
                    # Dividir por puntuaciones para respetar el contexto
                    segmentos = self.dividir_linea_en_segmentos(linea, limite_segmento)
                    segmentos_traducidos = []
                    
                    for segmento in segmentos:
                        if segmento.strip():
                            try:
                                if idioma_destino == 'es':
                                    traductor = GoogleTranslator(source='zh-CN', target='es')
                                else:  # 'en'
                                    traductor = GoogleTranslator(source='zh-CN', target='en')
                                
                                segmento_traducido = traductor.translate(segmento.strip())
                                segmentos_traducidos.append(segmento_traducido)
                            except Exception as e:
                                print(f"Error traduciendo segmento: {e}")
                                segmentos_traducidos.append(segmento)  # Mantener original si falla
                    
                    # Unir segmentos de la línea
                    linea_completa = ' '.join(segmentos_traducidos)
                    lineas_traducidas.append(linea_completa)
                else:
                    # Línea corta, traducir directamente
                    try:
                        if idioma_destino == 'es':
                            traductor = GoogleTranslator(source='zh-CN', target='es')
                        else:  # 'en'
                            traductor = GoogleTranslator(source='zh-CN', target='en')
                        
                        linea_traducida = traductor.translate(linea)
                        lineas_traducidas.append(linea_traducida)
                    except Exception as e:
                        print(f"Error traduciendo línea: {e}")
                        lineas_traducidas.append(linea)  # Mantener original si falla
            
            # Unir todas las líneas preservando saltos de línea exactos
            return '\n'.join(lineas_traducidas)
            
        except Exception as e:
            raise Exception(f"Error en traducción por segmentos: {str(e)}")
    
    def dividir_linea_en_segmentos(self, linea, limite):
        """Divide una línea larga en segmentos respetando puntuaciones importantes (versión mejorada)"""
        if len(linea) <= limite:
            return [linea]
        
        segmentos = []
        segmento_actual = ""
        
        # Puntuaciones que indican fin de oración o pausa (mejoradas)
        puntuaciones_corte = ['。', '！', '？', '；', '.', '!', '?', ';', '…', '——']
        puntuaciones_pausa = ['，', '、', ',', ':', '：', '（', '）', '(', ')', '"', '"', ''', ''']
        puntuaciones_enfasis = ['！', '？', '!', '?']  # Requieren tratamiento especial
        
        i = 0
        while i < len(linea):
            char = linea[i]
            segmento_actual += char
            
            # Si alcanzamos el límite, buscar un punto de corte apropiado
            if len(segmento_actual) >= limite:
                # Buscar punto de corte hacia atrás
                punto_corte = -1
                
                # Primero buscar puntuaciones de corte (prioridad a exclamación y pregunta)
                for j in range(len(segmento_actual) - 1, max(0, len(segmento_actual) - 200), -1):
                    if segmento_actual[j] in puntuaciones_corte:
                        punto_corte = j + 1
                        # Si es puntuación de énfasis, incluir posibles espacios después
                        if segmento_actual[j] in puntuaciones_enfasis:
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
    
    def generar_pinyin(self, texto_chino):
        """Genera pinyin usando CTkTable con formato responsive optimizado, caché y sin límites"""
        try:
            if not texto_chino.strip():
                return
            
            # Verificar caché de pinyin
            if texto_chino in self.cache_pinyin:
                datos_tabla = self.cache_pinyin[texto_chino]
                self.crear_tabla_pinyin(datos_tabla)
                return
            
            # Asegurar que tenemos la configuración responsive
            if not hasattr(self, 'caracteres_por_linea'):
                self.ejecutar_ajuste_responsive()
            
            # Procesar texto completo incluyendo puntuaciones y espacios
            # Ya no limitamos a solo caracteres chinos - procesamos todo
            if not self.contiene_caracteres_chinos(texto_chino):
                self.mostrar_error_pinyin("No se encontraron caracteres chinos válidos para generar Pinyin")
                return
            
            # Crear datos para la tabla sin límites de caracteres
            datos_tabla = self.crear_datos_tabla_pinyin_completo(texto_chino)
            
            # Guardar en caché
            self.cache_pinyin[texto_chino] = datos_tabla
            
            # Crear o actualizar la tabla
            self.crear_tabla_pinyin(datos_tabla)
            
            # Mostrar información sobre caracteres procesados
            total_chars = len([c for c in texto_chino if '\u4e00' <= c <= '\u9fff'])
            if hasattr(self, 'info_pinyin') and total_chars > 50:
                mensaje_info = f"💡 {total_chars} caracteres chinos procesados • Texto completo con puntuaciones"
                self.info_pinyin.configure(text=mensaje_info)
            
        except Exception as e:
            print(f"Error completo en generar_pinyin: {e}")
            self.mostrar_error_pinyin(f"Error generando Pinyin: {str(e)}")
    
    def contiene_caracteres_chinos(self, texto):
        """Verifica si el texto contiene al menos un carácter chino"""
        for char in texto:
            if '\u4e00' <= char <= '\u9fff':
                return True
        return False
    
    def crear_datos_tabla_pinyin_completo(self, texto_completo):
        """Crea los datos para la tabla de pinyin preservando puntuaciones, espacios y saltos de línea con mejor visualización"""
        if not hasattr(self, 'caracteres_por_linea'):
            self.caracteres_por_linea = 6
        
        # Ajustar caracteres por línea basado en cantidad de caracteres chinos
        total_chars_chinos = len([c for c in texto_completo if '\u4e00' <= c <= '\u9fff'])
        if total_chars_chinos > 150:
            self.caracteres_por_linea = 10  # Más caracteres para textos muy largos
        elif total_chars_chinos > 100:
            self.caracteres_por_linea = 8
        elif total_chars_chinos > 50:
            self.caracteres_por_linea = 7
        else:
            self.caracteres_por_linea = 6
            
        datos = []
        
        # Dividir por líneas para preservar saltos de línea
        lineas = texto_completo.split('\n')
        
        for idx_linea, linea in enumerate(lineas):
            if not linea.strip():  # Línea vacía
                # Agregar fila vacía más visible para preservar espaciado
                datos.append(['┈' * self.caracteres_por_linea])  # Línea punteada para espacios
                continue
            
            # Procesar línea carácter por carácter respetando todo
            caracteres_linea = list(linea)
            
            # Procesar en grupos
            for i in range(0, len(caracteres_linea), self.caracteres_por_linea):
                grupo = caracteres_linea[i:i + self.caracteres_por_linea]
                
                # Fila de pinyin (pronunciación)
                fila_pinyin = []
                # Fila de caracteres originales
                fila_caracteres = []
                
                for char in grupo:
                    if '\u4e00' <= char <= '\u9fff':  # Es un carácter chino
                        try:
                            # Generar pinyin con tonos
                            pinyin_result = pinyin(char, style=Style.TONE, heteronym=False)
                            if pinyin_result and pinyin_result[0]:
                                pinyin_char = pinyin_result[0][0]
                            else:
                                # Fallback: sin tonos
                                pinyin_result = lazy_pinyin(char)
                                pinyin_char = pinyin_result[0] if pinyin_result else "?"
                            
                            pinyin_char = pinyin_char.strip()
                            fila_pinyin.append(pinyin_char)
                            
                        except Exception as e:
                            print(f"Error procesando carácter '{char}': {e}")
                            fila_pinyin.append("?")
                    
                    elif char in '，。！？；：""''（）【】《》、':  # Puntuaciones chinas
                        fila_pinyin.append(f'•{char}•')  # Destacar puntuaciones chinas
                    elif char in ',.!?;:"\'"()[]{}/<>-=+*&%$#@~`^|\\':  # Puntuaciones occidentales
                        fila_pinyin.append(f'◦{char}◦')  # Destacar puntuaciones occidentales
                    elif char == ' ':  # Espacio
                        fila_pinyin.append('▫')  # Cuadro pequeño para espacios
                    elif char.isdigit():  # Números
                        fila_pinyin.append(f'#{char}')  # Destacar números
                    elif char.isalpha():  # Letras occidentales
                        fila_pinyin.append(f'[{char}]')  # Corchetes para letras
                    else:  # Otros caracteres especiales
                        fila_pinyin.append(f'◊{char}◊')  # Rombo para caracteres especiales
                    
                    # Agregar carácter original con formato
                    if '\u4e00' <= char <= '\u9fff':
                        fila_caracteres.append(f' {char} ')  # Espacios para caracteres chinos
                    else:
                        fila_caracteres.append(char)  # Sin espacios adicionales para otros
                
                # Agregar las filas si tienen contenido
                if fila_pinyin:
                    datos.append(fila_pinyin)
                    datos.append(fila_caracteres)
            
            # Agregar separador visual entre líneas (excepto la última)
            if idx_linea < len(lineas) - 1 and linea.strip():
                # Línea separadora más visible
                separador = ['━━━'] * min(3, self.caracteres_por_linea)  # Línea gruesa como separador
                if len(separador) < self.caracteres_por_linea:
                    separador.extend([''] * (self.caracteres_por_linea - len(separador)))
                datos.append(separador)
        
        return datos
    
    def mostrar_advertencia_limite(self, total_caracteres, limite):
        """Muestra advertencia cuando el texto excede el límite recomendado"""
        mensaje = (f"⚠️ Texto muy largo ({total_caracteres} caracteres)\n"
                  f"Se procesarán los primeros {limite} caracteres para mejor rendimiento.\n"
                  f"Para textos muy largos, considera dividirlos en secciones.")
        
        # Mostrar en el área de información temporalmente
        if hasattr(self, 'info_pinyin'):
            texto_original = self.info_pinyin.cget("text")
            self.info_pinyin.configure(text=mensaje)
            # Restaurar el texto después de 3 segundos
            self.app.after(3000, lambda: self.info_pinyin.configure(text=texto_original))
    
    def crear_datos_tabla_pinyin(self, texto_limpio):
        """Crea los datos para la tabla de pinyin de forma continua"""
        if not hasattr(self, 'caracteres_por_linea'):
            self.caracteres_por_linea = 6
        
        # Ajustar caracteres por línea basado en cantidad total para mejor visualización
        total_chars = len(texto_limpio)
        if total_chars > 100:
            self.caracteres_por_linea = 10  # Más caracteres por línea para textos largos
        elif total_chars > 50:
            self.caracteres_por_linea = 8
        else:
            self.caracteres_por_linea = 6
            
        datos = []
        
        # Procesar caracteres en grupos sin separadores
        for i in range(0, len(texto_limpio), self.caracteres_por_linea):
            grupo = texto_limpio[i:i + self.caracteres_por_linea]
            
            # Fila de pinyin (pronunciación)
            fila_pinyin = []
            # Fila de caracteres (destacada)
            fila_caracteres = []
            
            for char in grupo:
                try:
                    # Usar pypinyin correctamente - primero con tonos diacríticos
                    pinyin_result = pinyin(char, style=Style.TONE, heteronym=False)
                    if pinyin_result and pinyin_result[0]:
                        pinyin_char = pinyin_result[0][0]
                    else:
                        # Fallback: sin tonos
                        pinyin_result = lazy_pinyin(char)
                        pinyin_char = pinyin_result[0] if pinyin_result else "?"
                    
                    # Limpiar el resultado
                    pinyin_char = pinyin_char.strip()
                    fila_pinyin.append(pinyin_char)
                    # Caracteres con espacios para destacar
                    fila_caracteres.append(f" {char} ")
                    
                except Exception as e:
                    print(f"Error procesando carácter '{char}': {e}")
                    # Fallback: intentar método más simple
                    try:
                        pinyin_simple = lazy_pinyin(char)
                        if pinyin_simple:
                            fila_pinyin.append(pinyin_simple[0])
                        else:
                            fila_pinyin.append("?")
                    except:
                        fila_pinyin.append("?")
                    fila_caracteres.append(f" {char} ")
            
            # Agregar las filas directamente sin separadores
            datos.append(fila_pinyin)
            datos.append(fila_caracteres)
        
        return datos
    
    def crear_tabla_pinyin(self, datos):
        """Crea la tabla CTk optimizada con scroll elegante y letras más grandes"""
        try:
            # Solo proceder si hay datos válidos
            if not datos:
                return
            
            # Destruir tabla anterior eficientemente
            if hasattr(self, 'tabla_pinyin') and self.tabla_pinyin:
                self.tabla_pinyin.destroy()
                self.tabla_pinyin = None
            
            # Ocultar texto de información
            self.texto_info.grid_remove()
            
            # Calcular dimensiones una sola vez
            filas = len(datos)
            columnas = len(datos[0]) if datos else 1
            
            # Tamaños optimizados con letras más grandes
            if filas > 20:  # Para textos muy largos
                ancho_celda, alto_celda, font_size = 100, 45, 14  # Más grande
            elif self.ventana_ancho < 900:
                ancho_celda, alto_celda, font_size = 110, 50, 16  # Más grande
            elif self.ventana_ancho < 1300:
                ancho_celda, alto_celda, font_size = 130, 55, 18  # Más grande
            else:
                ancho_celda, alto_celda, font_size = 150, 60, 20  # Más grande
            
            # Crear tabla dentro del frame scrollable con letras más grandes
            self.tabla_pinyin = CTkTable(
                master=self.scrollable_frame,
                row=filas,
                column=columnas,
                values=datos,
                corner_radius=6,  # Esquinas más redondeadas
                header_color=("#2563eb", "#1d4ed8"),
                colors=[("#f8fafc", "#1e293b"), ("#ffffff", "#111827")],
                font=("Arial", font_size, "bold"),  # Fuente más grande
                text_color=("#0f172a", "#f8fafc"),
                width=ancho_celda,
                height=alto_celda
            )
            
            # Posicionar la tabla en el frame scrollable
            self.tabla_pinyin.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            
            # Configurar el scrollable frame para que se expanda con la tabla
            self.scrollable_frame.grid_columnconfigure(0, weight=1)
            
            # Agregar información sobre la cantidad de caracteres procesados
            total_caracteres = sum(len([c for c in fila if c.strip()]) for i, fila in enumerate(datos) if i % 2 == 1)
            if hasattr(self, 'info_pinyin') and total_caracteres > 50:
                # Mensaje informativo mejorado
                mensaje_info = f"💡 {total_caracteres} caracteres procesados • Usa scroll para navegar"
                self.info_pinyin.configure(text=mensaje_info)
            
        except Exception as e:
            print(f"Error creando tabla: {e}")
            self.mostrar_error_pinyin(f"Error: {str(e)}")
    
    def mostrar_error_pinyin(self, mensaje):
        """Muestra errores en el área de pinyin de forma eficiente"""
        # Limpiar tabla si existe
        if hasattr(self, 'tabla_pinyin') and self.tabla_pinyin:
            self.tabla_pinyin.destroy()
            self.tabla_pinyin = None
        
        # Mostrar error en texto de información en el frame scrollable
        self.texto_info.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.texto_info.delete("1.0", "end")
        self.texto_info.insert("1.0", f"❌ {mensaje}")
    
    def limpiar_pinyin(self):
        """Limpia el área de pinyin"""
        if hasattr(self, 'tabla_pinyin') and self.tabla_pinyin:
            self.tabla_pinyin.destroy()
            self.tabla_pinyin = None
        
        # Mostrar mensaje inicial en el frame scrollable
        self.texto_info.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.mostrar_mensaje_inicial()
    
    def limpiar_campos(self):
        """Limpia todos los campos y caché de manera optimizada"""
        try:
            # Limpiar UI
            self.texto_entrada.delete("1.0", "end")
            self.texto_traduccion.delete("1.0", "end")
            self.limpiar_pinyin()
            
            # Limpiar variables de caché
            self.traduccion_actual = ""
            self.pinyin_actual = ""
            self.texto_chino_actual = ""
            
            # Resetear referencia de última tabla
            if hasattr(self, 'ultima_tabla_datos'):
                self.ultima_tabla_datos = None
            
            # Ocultar barra de progreso si está visible
            if hasattr(self, 'frame_progreso'):
                self.ocultar_barra_progreso()
            
            # Enfocar el campo de entrada
            self.texto_entrada.focus_set()
            
            print("Campos limpiados correctamente con optimización")
            
        except Exception as e:
            print(f"Error limpiando campos: {e}")
            # Fallback básico
            self.texto_entrada.delete("1.0", "end")
            self.texto_traduccion.delete("1.0", "end")
            self.limpiar_pinyin()
            self.texto_entrada.focus_set()
    
    def es_texto_chino(self, texto):
        """Verifica si el texto contiene caracteres chinos"""
        for char in texto:
            if '\u4e00' <= char <= '\u9fff':
                return True
        return False
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error en una ventana emergente responsive"""
        try:
            ventana_error = customtkinter.CTkToplevel(self.app)
            
            # Tamaño responsive para la ventana de error
            if self.ventana_ancho < 600:
                ventana_error.geometry("300x120")
            else:
                ventana_error.geometry("400x150")
                
            ventana_error.title("Error")
            ventana_error.resizable(False, False)
            
            # Centrar la ventana
            ventana_error.transient(self.app)
            ventana_error.grab_set()
            
            # Configurar grid
            ventana_error.grid_columnconfigure(0, weight=1)
            
            label_error = customtkinter.CTkLabel(
                ventana_error,
                text=mensaje,
                font=("Arial", 12),
                wraplength=350 if self.ventana_ancho >= 600 else 250
            )
            label_error.grid(row=0, column=0, pady=20, padx=20)
            
            btn_ok = customtkinter.CTkButton(
                ventana_error,
                text="OK",
                command=ventana_error.destroy,
                width=80,
                height=30
            )
            btn_ok.grid(row=1, column=0, pady=(0, 20))
            
            # Centrar la ventana en la pantalla
            ventana_error.update_idletasks()
            x = (ventana_error.winfo_screenwidth() // 2) - (ventana_error.winfo_width() // 2)
            y = (ventana_error.winfo_screenheight() // 2) - (ventana_error.winfo_height() // 2)
            ventana_error.geometry(f"+{x}+{y}")
            
        except Exception as e:
            print(f"Error mostrando mensaje: {e}")
    
    def on_window_resize(self, event):
        """Maneja redimensionamiento eficientemente"""
        # Solo procesar eventos de ventana principal
        if event.widget == self.app:
            # Cancelar timer anterior
            if hasattr(self, '_resize_timer'):
                self.app.after_cancel(self._resize_timer)
            
            # Delay más largo para menos llamadas
            self._resize_timer = self.app.after(200, self.ejecutar_ajuste_responsive)
    
    def ejecutar(self):
        """Inicia la aplicación con configuración inicial optimizada"""
        try:
            # Configuración inicial
            self.ejecutar_ajuste_responsive()
            
            # Configurar cierre limpio
            self.app.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
            
            # El mensaje de bienvenida ya se muestra en mostrar_mensaje_inicial()
            
            # Iniciar la aplicación
            self.app.mainloop()
        except KeyboardInterrupt:
            print("Aplicación cerrada por el usuario")
        except Exception as e:
            print(f"Error ejecutando la aplicación: {e}")
            # Mostrar error en consola para debugging
            import traceback
            traceback.print_exc()
    
    def validar_respeto_puntuaciones(self, texto_original, texto_procesado):
        """Valida que las puntuaciones importantes se respeten en el procesamiento"""
        try:
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
                
        except Exception as e:
            print(f"Error validando puntuaciones: {e}")
            return False
    
    def probar_respeto_puntuaciones(self):
        """Método de prueba para verificar el respeto de puntuaciones"""
        textos_prueba = [
            "¡Hola! ¿Cómo estás? Espero que bien; todo está perfecto.",
            "你好！你好吗？我很好；谢谢你的关心。",
            "What?! Are you serious? This is amazing!",
            "これは素晴らしい！本当ですか？信じられません…"
        ]
        
        print("🔍 Probando respeto de puntuaciones importantes...")
        
        for i, texto in enumerate(textos_prueba, 1):
            print(f"\n--- Prueba {i} ---")
            print(f"Texto original: {texto}")
            
            # Probar división en segmentos
            if self.contiene_caracteres_chinos(texto):
                segmentos = self.dividir_linea_en_segmentos(texto, 20)
            else:
                segmentos = self.dividir_linea_en_segmentos_occidentales(texto, 20)
            
            texto_reunido = ''.join(segmentos)
            print(f"Texto procesado: {texto_reunido}")
            
            # Validar
            respetado = self.validar_respeto_puntuaciones(texto, texto_reunido)
            print(f"Resultado: {'✅ CORRECTO' if respetado else '❌ ERROR'}")
        
        print("\n🎯 Prueba de respeto de puntuaciones completada.")
    
    def cerrar_aplicacion(self):
        """Cierra la aplicación de manera limpia"""
        try:
            # Cancelar traducciones en progreso
            if self.traduccion_en_progreso:
                self.traduccion_en_progreso = False
            
            # Cerrar el pool de hilos
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=False)
            
            # Cerrar la aplicación
            self.app.destroy()
        except Exception as e:
            print(f"Error cerrando aplicación: {e}")
            self.app.destroy()


# --- Punto de entrada principal ---
if __name__ == "__main__":
    try:
        traductor = TraductorChino()
        traductor.ejecutar()
    except Exception as e:
        print(f"Error iniciando la aplicación: {e}")
        input("Presiona Enter para salir...")