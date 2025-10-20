#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Traductor Chino Optimizado v2.0
Framework: PyQt6 (más ligero y rápido que tkinter)
Arquitectura: MVC con gestión eficiente de recursos
"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Dict
import threading
import queue
from functools import lru_cache
import psutil

# PyQt6 - Framework moderno y optimizado
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QSplitter, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon

# Librerías de traducción y pronunciación
from deep_translator import GoogleTranslator
from pypinyin import pinyin, Style

# ============================================================================
# CONFIGURACIÓN Y CONSTANTES
# ============================================================================

class Config:
    """Configuración centralizada de la aplicación"""
    APP_NAME = "Traductor Chino Pro"
    VERSION = "2.0"
    
    # Geometría de ventana adaptativa
    MIN_WIDTH = 1000
    MIN_HEIGHT = 600
    DEFAULT_WIDTH = 1400
    DEFAULT_HEIGHT = 800
    
    # Caché y rendimiento
    MAX_CACHE_SIZE = 500
    TRANSLATION_TIMEOUT = 5
    CHUNK_SIZE = 150  # Caracteres por chunk para traducción (optimizado para deep-translator)
    
    # Fuentes optimizadas
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_NORMAL = 11
    FONT_SIZE_LARGE = 14
    FONT_SIZE_TITLE = 16
    
    # Colores del tema
    COLOR_PRIMARY = "#2563eb"
    COLOR_SECONDARY = "#3b82f6"
    COLOR_SUCCESS = "#10b981"
    COLOR_WARNING = "#f59e0b"
    COLOR_ERROR = "#ef4444"
    COLOR_BG_LIGHT = "#f8fafc"
    COLOR_BG_DARK = "#1e293b"


# ============================================================================
# GESTOR DE RECURSOS Y CACHÉ
# ============================================================================

class ResourceManager:
    """Gestiona recursos de sistema y caché de manera eficiente"""
    
    def __init__(self):
        self.translation_cache: Dict[str, str] = {}
        self.pinyin_cache: Dict[str, List] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
    @lru_cache(maxsize=1000)
    def get_pinyin(self, text: str) -> List:
        """Obtiene pinyin con caché optimizado"""
        return pinyin(text, style=Style.TONE, heteronym=False)
    
    def get_translation(self, text: str, target_lang: str) -> Optional[str]:
        """Obtiene traducción con caché"""
        cache_key = f"{text}_{target_lang}"
        
        if cache_key in self.translation_cache:
            self.cache_hits += 1
            return self.translation_cache[cache_key]
        
        self.cache_misses += 1
        return None
    
    def set_translation(self, text: str, target_lang: str, translation: str):
        """Guarda traducción en caché con límite"""
        cache_key = f"{text}_{target_lang}"
        
        # Limpiar caché si excede límite
        if len(self.translation_cache) >= Config.MAX_CACHE_SIZE:
            # Eliminar 20% más antiguo
            keys_to_remove = list(self.translation_cache.keys())[:Config.MAX_CACHE_SIZE // 5]
            for key in keys_to_remove:
                del self.translation_cache[key]
        
        self.translation_cache[cache_key] = translation
    
    def get_memory_usage(self) -> float:
        """Retorna uso de memoria en MB"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def clear_cache(self):
        """Limpia caché para liberar memoria"""
        self.translation_cache.clear()
        self.pinyin_cache.clear()
        self.get_pinyin.cache_clear()
        print(f"🧹 Caché limpiado. Hits: {self.cache_hits}, Misses: {self.cache_misses}")


# ============================================================================
# WORKERS ASÍNCRONOS
# ============================================================================

class TranslationWorker(QThread):
    """Worker asíncrono para traducciones sin bloquear UI - Con fragmentación"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(int, str)  # (porcentaje, mensaje)
    
    def __init__(self, text: str, target_lang: str, resource_mgr: ResourceManager):
        super().__init__()
        self.text = text
        self.target_lang = target_lang
        self.resource_mgr = resource_mgr
    
    def run(self):
        try:
            # Verificar caché primero (solo para textos cortos)
            if len(self.text) < Config.CHUNK_SIZE:
                cached = self.resource_mgr.get_translation(self.text, self.target_lang)
                if cached:
                    self.finished.emit(cached)
                    return
            
            # Dividir en chunks para textos largos
            chunks = self._split_text(self.text, Config.CHUNK_SIZE)
            total_chunks = len(chunks)
            translations = []
            
            self.progress.emit(0, f"Traduciendo 0/{total_chunks} fragmentos...")
            
            translator = GoogleTranslator(source='zh-CN', target=self.target_lang)
            
            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    translations.append(chunk)
                    continue
                
                # Verificar caché por chunk
                cached_chunk = self.resource_mgr.get_translation(chunk, self.target_lang)
                if cached_chunk:
                    translations.append(cached_chunk)
                else:
                    # Traducir chunk
                    result = translator.translate(chunk)
                    if result:
                        translations.append(result)
                        self.resource_mgr.set_translation(chunk, self.target_lang, result)
                    else:
                        translations.append(chunk)  # Fallback
                
                # Actualizar progreso
                progress_pct = int((i + 1) / total_chunks * 100)
                self.progress.emit(progress_pct, f"Traduciendo {i+1}/{total_chunks} fragmentos...")
            
            # Unir todas las traducciones
            final_translation = ''.join(translations)
            
            if final_translation:
                self.finished.emit(final_translation)
            else:
                self.error.emit("Traducción vacía")
                
        except Exception as e:
            self.error.emit(str(e))
    
    def _split_text(self, text: str, chunk_size: int) -> List[str]:
        """Divide el texto en chunks respetando puntuación china"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Puntuación china para dividir
        chinese_punctuation = '。！？；，、：'
        
        for char in text:
            current_chunk += char
            
            # Si llegamos al tamaño máximo o encontramos puntuación
            if len(current_chunk) >= chunk_size:
                if char in chinese_punctuation or not char.strip():
                    chunks.append(current_chunk)
                    current_chunk = ""
                elif len(current_chunk) > chunk_size * 1.2:  # No exceder 20%
                    chunks.append(current_chunk)
                    current_chunk = ""
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks


class PinyinWorker(QThread):
    """Worker asíncrono para generar pronunciación Pinyin con agrupación"""
    finished = pyqtSignal(list)  # Lista de grupos
    progress = pyqtSignal(int)
    
    def __init__(self, text: str, target_lang: str, resource_mgr: ResourceManager):
        super().__init__()
        self.text = text
        self.target_lang = target_lang
        self.resource_mgr = resource_mgr
    
    def run(self):
        try:
            groups = []
            current_group = []
            
            # Puntuación china que indica fin de grupo
            chinese_punctuation = '。！？；，、'
            
            for i, char in enumerate(self.text):
                if '\u4e00' <= char <= '\u9fff':  # Es caracter chino
                    pinyin_result = self.resource_mgr.get_pinyin(char)
                    if pinyin_result and pinyin_result[0]:
                        current_group.append({
                            'char': char,
                            'pinyin': pinyin_result[0][0]
                        })
                
                # Si encontramos puntuación o llegamos al límite, crear nuevo grupo
                if char in chinese_punctuation or len(current_group) >= 8:
                    if current_group:
                        # Traducir el grupo completo
                        chars_text = ''.join([item['char'] for item in current_group])
                        translation = self._translate_group(chars_text)
                        
                        groups.append({
                            'items': current_group,
                            'translation': translation
                        })
                        current_group = []
                
                # Actualizar progreso
                progress = int((i + 1) / len(self.text) * 100)
                self.progress.emit(progress)
            
            # Agregar último grupo si existe
            if current_group:
                chars_text = ''.join([item['char'] for item in current_group])
                translation = self._translate_group(chars_text)
                groups.append({
                    'items': current_group,
                    'translation': translation
                })
            
            self.finished.emit(groups)
            
        except Exception as e:
            print(f"Error en PinyinWorker: {e}")
            self.finished.emit([])
    
    def _translate_group(self, text: str) -> str:
        """Traduce un grupo de caracteres"""
        try:
            # Verificar caché
            cached = self.resource_mgr.get_translation(text, self.target_lang)
            if cached:
                return cached
            
            # Traducir
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source='zh-CN', target=self.target_lang)
            result = translator.translate(text)
            
            if result:
                # Guardar en caché
                self.resource_mgr.set_translation(text, self.target_lang, result)
                return result
            else:
                return "..."
        except Exception as e:
            print(f"Error traduciendo grupo: {e}")
            return "..."


# ============================================================================
# INTERFAZ PRINCIPAL
# ============================================================================

class ChineseTranslatorApp(QMainWindow):
    """Aplicación principal optimizada con PyQt6"""
    
    def __init__(self):
        super().__init__()
        self.resource_mgr = ResourceManager()
        self.current_lang = 'es'
        self.translation_worker = None
        self.pinyin_worker = None
        self.dark_mode = False  # Estado del tema (False = Light, True = Dark)
        
        self.init_ui()
        self.setup_shortcuts()
        
        # Monitor de recursos (cada 30 segundos)
        self.resource_timer = QTimer()
        self.resource_timer.timeout.connect(self.check_resources)
        self.resource_timer.start(30000)
        
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle(f"{Config.APP_NAME} v{Config.VERSION}")
        self.setMinimumSize(Config.MIN_WIDTH, Config.MIN_HEIGHT)
        self.resize(Config.DEFAULT_WIDTH, Config.DEFAULT_HEIGHT)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal - Márgenes más pequeños para aprovechar espacio
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)  # Márgenes reducidos
        main_layout.setSpacing(8)  # Espaciado reducido
        
        # Título
        self.create_header(main_layout)
        
        # Splitter para dividir izquierda/derecha (responsive)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(8)
        self.splitter.setChildrenCollapsible(False)  # Evitar que los paneles se colapsen
        main_layout.addWidget(self.splitter)
        
        # Panel izquierdo (entrada y traducción)
        left_panel = self.create_left_panel()
        self.splitter.addWidget(left_panel)
        
        # Panel derecho (pronunciación Pinyin)
        right_panel = self.create_right_panel()
        self.splitter.addWidget(right_panel)
        
        # Configurar proporción del splitter (50-50 inicialmente)
        self.splitter.setSizes([700, 700])
        self.splitter.setStretchFactor(0, 1)  # Panel izquierdo estirable
        self.splitter.setStretchFactor(1, 1)  # Panel derecho estirable
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(10)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bfdbfe;
                border-radius: 5px;
                text-align: center;
                background-color: #f0f9ff;
                color: #1e3a8a;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #60a5fa);
                border-radius: 3px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        # Barra de estado
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage(f"✅ Listo | Memoria: {self.resource_mgr.get_memory_usage():.1f} MB")
        
        # Aplicar estilos
        self.apply_styles()
    
    def create_header(self, layout: QVBoxLayout):
        """Crea el encabezado de la aplicación - Compacto para aprovechar espacio vertical"""
        header_widget = QWidget()
        header_widget.setMaximumHeight(60)  # Limitar altura del header
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(5, 5, 5, 5)
        header_layout.setSpacing(10)
        
        # Botón de tema (izquierda) - Más compacto
        self.btn_theme = QPushButton("🌙 Modo Oscuro")
        self.btn_theme.setFixedSize(130, 35)  # Más pequeño
        self.btn_theme.clicked.connect(self.toggle_theme)
        self.btn_theme.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        header_layout.addWidget(self.btn_theme)
        
        # Título con indicador de carga (centro) - Más pequeño
        self.title_label = QLabel(f"🈳 {Config.APP_NAME} 🈳")
        title_font = QFont(Config.FONT_FAMILY, 16, QFont.Weight.Bold)  # Reducido de 20 a 16
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("QLabel { color: #1f2937; }")
        header_layout.addWidget(self.title_label, stretch=1)
        
        # Espaciador derecho para balancear
        header_layout.addSpacing(130)
        
        layout.addWidget(header_widget)
    
    def create_left_panel(self) -> QWidget:
        """Crea el panel izquierdo con entrada y traducción"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(6)  # Reducir espaciado
        layout.setContentsMargins(4, 4, 4, 4)  # Márgenes pequeños
        
        # === Texto en Chino ===
        label_input = QLabel("📝 Texto en Chino:")
        label_input.setFont(QFont(Config.FONT_FAMILY, 12, QFont.Weight.Bold))  # Más pequeño
        label_input.setStyleSheet("QLabel { color: #1f2937; padding: 2px; }")  # Sin padding extra
        label_input.setMaximumHeight(25)  # Limitar altura
        layout.addWidget(label_input)
        
        self.input_text = QTextEdit()
        self.input_text.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE))
        self.input_text.setPlaceholderText("Escribe o pega texto en chino aquí...")
        self.input_text.setStyleSheet("QTextEdit { color: #1f2937; background-color: white; }")
        self.input_text.setMinimumHeight(150)  # Altura mínima
        layout.addWidget(self.input_text, stretch=3)  # Aumentar stretch para usar más espacio
        
        # === Botones de idioma ===
        lang_layout = QHBoxLayout()
        
        self.btn_spanish = QPushButton("🇪🇸 Español")
        self.btn_spanish.setCheckable(True)
        self.btn_spanish.setChecked(True)
        self.btn_spanish.clicked.connect(lambda: self.change_language('es'))
        lang_layout.addWidget(self.btn_spanish)
        
        self.btn_english = QPushButton("🇺🇸 English")
        self.btn_english.setCheckable(True)
        self.btn_english.clicked.connect(lambda: self.change_language('en'))
        lang_layout.addWidget(self.btn_english)
        
        layout.addLayout(lang_layout)
        
        # === Traducción ===
        label_translation = QLabel("🌐 Traducción:")
        label_translation.setFont(QFont(Config.FONT_FAMILY, 12, QFont.Weight.Bold))  # Más pequeño
        label_translation.setStyleSheet("QLabel { color: #1f2937; padding: 2px; }")  # Sin padding extra
        label_translation.setMaximumHeight(25)  # Limitar altura
        layout.addWidget(label_translation)
        
        self.output_text = QTextEdit()
        self.output_text.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE))
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("La traducción aparecerá aquí...")
        self.output_text.setStyleSheet("QTextEdit { color: #1f2937; background-color: #f9fafb; }")
        self.output_text.setMinimumHeight(150)  # Altura mínima
        layout.addWidget(self.output_text, stretch=3)  # Aumentar stretch para usar más espacio
        
        # === Botones de acción ===
        btn_layout = QHBoxLayout()
        
        self.btn_translate = QPushButton("🔤 Traducir")
        self.btn_translate.clicked.connect(self.translate_text)
        btn_layout.addWidget(self.btn_translate)
        
        self.btn_auto = QPushButton("🔄 Auto")
        self.btn_auto.setCheckable(True)
        self.btn_auto.clicked.connect(self.toggle_auto_translate)
        btn_layout.addWidget(self.btn_auto)
        
        self.btn_clear = QPushButton("🗑️ Limpiar")
        self.btn_clear.clicked.connect(self.clear_all)
        btn_layout.addWidget(self.btn_clear)
        
        layout.addLayout(btn_layout)
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Crea el panel derecho con pronunciación Pinyin"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(6)  # Reducir espaciado
        layout.setContentsMargins(4, 4, 4, 4)  # Márgenes pequeños
        
        # Encabezado - Compacto
        header_widget = QWidget()
        header_widget.setMaximumHeight(25)  # Limitar altura
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        
        label_pinyin = QLabel("🗣️ Pronunciación Pinyin:")
        label_pinyin.setFont(QFont(Config.FONT_FAMILY, 12, QFont.Weight.Bold))  # Más pequeño
        label_pinyin.setStyleSheet("QLabel { color: #1f2937; }")
        header_layout.addWidget(label_pinyin)
        
        self.pinyin_info = QLabel("💡 Listo para mostrar pronunciación")
        self.pinyin_info.setFont(QFont(Config.FONT_FAMILY, 10))  # Más pequeño
        self.pinyin_info.setStyleSheet("QLabel { color: #6b7280; font-style: italic; }")
        header_layout.addWidget(self.pinyin_info, stretch=1)
        
        layout.addWidget(header_widget)
        
        # Tabla de Pinyin (SIN headers numéricos)
        self.pinyin_table = QTableWidget()
        self.pinyin_table.setRowCount(0)
        self.pinyin_table.setColumnCount(0)
        
        # CRÍTICO: Ocultar completamente los headers
        h_header = self.pinyin_table.horizontalHeader()
        v_header = self.pinyin_table.verticalHeader()
        
        if h_header:
            h_header.setVisible(False)  # Sin números de columnas
        if v_header:
            v_header.setVisible(False)  # Sin números de filas
            
        if h_header:
            h_header.setDefaultSectionSize(90)  # Ancho por defecto
        
        # Configurar tabla
        self.pinyin_table.setShowGrid(True)
        self.pinyin_table.setGridStyle(Qt.PenStyle.SolidLine)
        self.pinyin_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.pinyin_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Fuentes
        table_font = QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL)
        self.pinyin_table.setFont(table_font)
        
        # Scroll suave
        self.pinyin_table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.pinyin_table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.pinyin_table.setMinimumHeight(200)  # Altura mínima para la tabla
        
        layout.addWidget(self.pinyin_table, stretch=10)  # Mucho stretch para ocupar espacio vertical
        
        # Botón de exportar - Compacto
        self.btn_export = QPushButton("📄 Exportar PDF")
        self.btn_export.setMaximumHeight(40)  # Limitar altura
        self.btn_export.clicked.connect(self.export_pdf)
        layout.addWidget(self.btn_export)
        
        return panel
    
    def apply_styles(self):
        """Aplica estilos CSS a la aplicación con soporte para tema claro/oscuro"""
        
        if self.dark_mode:
            # Tema Oscuro
            bg_main = "#0f172a"
            bg_secondary = "#1e293b"
            bg_input = "#334155"
            text_color = "#f1f5f9"
            text_secondary = "#cbd5e1"
            border_color = "#475569"
            hover_bg = "#1e40af"
        else:
            # Tema Claro
            bg_main = Config.COLOR_BG_LIGHT
            bg_secondary = "white"
            bg_input = "white"
            text_color = "#1f2937"
            text_secondary = "#6b7280"
            border_color = "#e5e7eb"
            hover_bg = Config.COLOR_SECONDARY
        
        stylesheet = f"""
        QMainWindow {{
            background-color: {bg_main};
        }}
        
        QWidget {{
            color: {text_color};
        }}
        
        QLabel {{
            color: {text_color};
        }}
        
        QPushButton {{
            background-color: {Config.COLOR_PRIMARY};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: {Config.FONT_SIZE_NORMAL}px;
            font-weight: bold;
            min-height: 35px;
        }}
        
        QPushButton:hover {{
            background-color: {hover_bg};
        }}
        
        QPushButton:pressed {{
            background-color: #1d4ed8;
        }}
        
        QPushButton:checked {{
            background-color: {Config.COLOR_SUCCESS};
        }}
        
        QPushButton#btn_clear {{
            background-color: #6b7280;
        }}
        
        QPushButton#btn_clear:hover {{
            background-color: #4b5563;
        }}
        
        QTextEdit {{
            border: 2px solid {border_color};
            border-radius: 8px;
            padding: 8px;
            background-color: {bg_input};
            color: {text_color};
        }}
        
        QTextEdit:focus {{
            border-color: {Config.COLOR_PRIMARY};
        }}
        
        QTableWidget {{
            border: 2px solid {border_color};
            border-radius: 8px;
            background-color: {bg_secondary};
            gridline-color: {border_color};
            color: {text_color};
        }}
        
        QHeaderView::section {{
            background-color: {Config.COLOR_PRIMARY};
            color: white;
            padding: 8px;
            border: none;
            font-weight: bold;
        }}
        
        QTableWidget::item {{
            padding: 8px;
            border: 1px solid {border_color};
        }}
        
        QTableWidget::item:selected {{
            background-color: #3b82f6;
            color: white;
        }}
        
        QProgressBar {{
            border: none;
            border-radius: 4px;
            background-color: {border_color};
        }}
        
        QProgressBar::chunk {{
            background-color: {Config.COLOR_PRIMARY};
            border-radius: 4px;
        }}
        
        QStatusBar {{
            background-color: {bg_secondary};
            color: {text_secondary};
        }}
        
        QSplitter::handle {{
            background-color: {border_color};
        }}
        
        /* Scrollbars modernos */
        QScrollBar:vertical {{
            background: {bg_secondary};
            width: 14px;
            border-radius: 7px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #94a3b8, stop:1 #64748b);
            border-radius: 6px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #64748b, stop:1 #475569);
        }}
        
        QScrollBar::handle:vertical:pressed {{
            background: #475569;
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background: {bg_secondary};
            height: 14px;
            border-radius: 7px;
            margin: 2px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #94a3b8, stop:1 #64748b);
            border-radius: 6px;
            min-width: 30px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #64748b, stop:1 #475569);
        }}
        
        QScrollBar::handle:horizontal:pressed {{
            background: #475569;
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        """
        
        self.setStyleSheet(stylesheet)
        self.btn_clear.setObjectName("btn_clear")
    
    def toggle_theme(self):
        """Cambia entre tema claro y oscuro"""
        self.dark_mode = not self.dark_mode
        
        # Actualizar texto del botón
        if self.dark_mode:
            self.btn_theme.setText("☀️ Modo Claro")
        else:
            self.btn_theme.setText("🌙 Modo Oscuro")
        
        # Actualizar título
        if self.dark_mode:
            self.title_label.setStyleSheet("QLabel { color: #f1f5f9; }")
        else:
            self.title_label.setStyleSheet("QLabel { color: #1f2937; }")
        
        # Reaplica los estilos
        self.apply_styles()
        
        # Actualizar labels específicos
        self.update_theme_colors()
    
    def update_theme_colors(self):
        """Actualiza colores específicos de labels según el tema"""
        if self.dark_mode:
            text_color = "#f1f5f9"
            input_bg = "#334155"
            output_bg = "#1e293b"
        else:
            text_color = "#1f2937"
            input_bg = "white"
            output_bg = "#f9fafb"
        
        # Buscar todos los labels y actualizar colores
        for label in self.findChildren(QLabel):
            if "Texto en Chino" in label.text() or "Traducción" in label.text() or "Pinyin" in label.text():
                label.setStyleSheet(f"QLabel {{ color: {text_color}; }}")
        
        # Actualizar áreas de texto
        self.input_text.setStyleSheet(f"QTextEdit {{ color: {text_color}; background-color: {input_bg}; }}")
        self.output_text.setStyleSheet(f"QTextEdit {{ color: {text_color}; background-color: {output_bg}; }}")
        
        # Actualizar info de Pinyin
        self.pinyin_info.setStyleSheet(f"QLabel {{ color: {text_color}; font-style: italic; }}")

    
    # ========================================================================
    # FUNCIONALIDADES PRINCIPALES
    # ========================================================================
    
    def change_language(self, lang: str):
        """Cambia el idioma de traducción"""
        self.current_lang = lang
        
        # Actualizar botones
        self.btn_spanish.setChecked(lang == 'es')
        self.btn_english.setChecked(lang == 'en')
        
        # Re-traducir si hay texto
        if self.input_text.toPlainText().strip():
            self.translate_text()
        
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage(f"✅ Idioma: {'Español' if lang == 'es' else 'English'}", 3000)
    
    def translate_text(self):
        """Traduce el texto ingresado"""
        text = self.input_text.toPlainText().strip()
        
        if not text:
            self.output_text.setText("")
            return
        
        # Mostrar indicador de procesamiento en título
        self.title_label.setText(f"⏳ {Config.APP_NAME} - Procesando... ⏳")
        
        # Mostrar progreso
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.btn_translate.setEnabled(False)
        
        # Actualizar status bar
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage("🔄 Traduciendo...", 0)
        
        # Iniciar worker de traducción
        self.translation_worker = TranslationWorker(text, self.current_lang, self.resource_mgr)
        self.translation_worker.finished.connect(self.on_translation_finished)
        self.translation_worker.error.connect(self.on_translation_error)
        self.translation_worker.progress.connect(self.on_translation_progress)
        self.translation_worker.start()
        
        # También generar Pinyin
        self.generate_pinyin()
    
    def on_translation_progress(self, percentage: int, message: str):
        """Callback de progreso de traducción"""
        self.progress_bar.setValue(percentage)
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage(f"🔄 {message}", 0)
    
    def on_translation_finished(self, translation: str):
        """Callback cuando termina la traducción"""
        self.output_text.setText(translation)
        self.progress_bar.setValue(100)
        
        # Restaurar título normal
        self.title_label.setText(f"🈳 {Config.APP_NAME} 🈳")
        
        # Ocultar barra después de 1 segundo
        QTimer.singleShot(1000, lambda: self.progress_bar.setVisible(False))
        
        self.btn_translate.setEnabled(True)
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage("✅ Traducción completada", 3000)
    
    def on_translation_error(self, error: str):
        """Callback cuando hay error en traducción"""
        self.progress_bar.setVisible(False)
        self.btn_translate.setEnabled(True)
        
        # Restaurar título normal
        self.title_label.setText(f"🈳 {Config.APP_NAME} 🈳")
        
        QMessageBox.warning(self, "Error", f"Error al traducir: {error}")
    
    def generate_pinyin(self):
        """Genera la pronunciación Pinyin"""
        text = self.input_text.toPlainText().strip()
        
        if not text:
            self.pinyin_table.clear()
            self.pinyin_table.setRowCount(0)
            self.pinyin_table.setColumnCount(0)
            self.pinyin_info.setText("💡 Listo para mostrar pronunciación")
            return
        
        # Mostrar indicador de procesamiento
        self.pinyin_info.setText("⏳ Procesando caracteres...")
        
        # Iniciar worker de Pinyin con idioma actual
        self.pinyin_worker = PinyinWorker(text, self.current_lang, self.resource_mgr)
        self.pinyin_worker.finished.connect(self.on_pinyin_finished)
        self.pinyin_worker.progress.connect(self.on_pinyin_progress)
        self.pinyin_worker.start()
    
    def on_pinyin_progress(self, progress: int):
        """Callback de progreso de Pinyin"""
        if self.progress_bar.isVisible():
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(progress)
    
    def on_pinyin_finished(self, groups: List[Dict]):
        """Callback cuando termina generación de Pinyin - Con grupos y separadores"""
        if not groups:
            self.pinyin_info.setText("⚠️ No se encontraron caracteres chinos")
            return
        
        # Limpiar tabla completamente antes de llenar
        self.pinyin_table.clear()
        self.pinyin_table.setRowCount(0)
        self.pinyin_table.setColumnCount(0)
        
        # Colores pasteles azulados
        color_pinyin_bg = QColor("#dbeafe")      # Azul muy claro
        color_pinyin_text = QColor("#1e40af")    # Azul oscuro
        color_char_bg = QColor("#bfdbfe")        # Azul pastel
        color_char_text = QColor("#1e3a8a")      # Azul muy oscuro
        color_trans_bg = QColor("#a7f3d0")       # Verde agua claro
        color_trans_text = QColor("#065f46")     # Verde oscuro
        color_separator_bg = QColor("#f1f5f9")   # Gris muy claro para separador
        
        # Calcular total de columnas (máximo de caracteres en cualquier grupo)
        max_cols = max(len(group['items']) for group in groups)
        
        # Calcular filas: 3 filas por grupo + 1 separador
        total_rows = len(groups) * 4  # Pinyin + Carácter + Traducción + Separador
        
        # Configurar tabla
        self.pinyin_table.setRowCount(total_rows)
        self.pinyin_table.setColumnCount(max_cols)
        
        # CRÍTICO: Asegurar que headers estén ocultos
        h_header = self.pinyin_table.horizontalHeader()
        v_header = self.pinyin_table.verticalHeader()
        if h_header:
            h_header.setVisible(False)  # Ocultar números de columnas
        if v_header:
            v_header.setVisible(False)  # Ocultar números de filas
        
        row_idx = 0
        total_chars = 0
        
        for group in groups:
            items = group['items']
            translation = group['translation']
            num_items = len(items)
            total_chars += num_items
            
            # FILA 1: PINYIN
            for col_idx, item in enumerate(items):
                pinyin_item = QTableWidgetItem(item['pinyin'])
                pinyin_item.setFont(QFont(Config.FONT_FAMILY, 13, QFont.Weight.Bold))
                pinyin_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                pinyin_item.setBackground(color_pinyin_bg)
                pinyin_item.setForeground(color_pinyin_text)
                self.pinyin_table.setItem(row_idx, col_idx, pinyin_item)
            
            # Rellenar celdas vacías de pinyin
            for col_idx in range(num_items, max_cols):
                empty_item = QTableWidgetItem("")
                empty_item.setBackground(color_pinyin_bg)
                self.pinyin_table.setItem(row_idx, col_idx, empty_item)
            
            self.pinyin_table.setRowHeight(row_idx, 40)
            row_idx += 1
            
            # FILA 2: CARACTERES CHINOS
            for col_idx, item in enumerate(items):
                char_item = QTableWidgetItem(item['char'])
                char_item.setFont(QFont(Config.FONT_FAMILY, 18, QFont.Weight.Bold))
                char_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                char_item.setBackground(color_char_bg)
                char_item.setForeground(color_char_text)
                self.pinyin_table.setItem(row_idx, col_idx, char_item)
            
            # Rellenar celdas vacías de caracteres
            for col_idx in range(num_items, max_cols):
                empty_item = QTableWidgetItem("")
                empty_item.setBackground(color_char_bg)
                self.pinyin_table.setItem(row_idx, col_idx, empty_item)
            
            self.pinyin_table.setRowHeight(row_idx, 50)
            row_idx += 1
            
            # FILA 3: TRADUCCIÓN (SPAN completo)
            trans_item = QTableWidgetItem(translation)
            trans_item.setFont(QFont(Config.FONT_FAMILY, 11))
            trans_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            trans_item.setBackground(color_trans_bg)
            trans_item.setForeground(color_trans_text)
            self.pinyin_table.setItem(row_idx, 0, trans_item)
            
            # Hacer span para que ocupe todas las columnas
            self.pinyin_table.setSpan(row_idx, 0, 1, max_cols)
            self.pinyin_table.setRowHeight(row_idx, 40)
            row_idx += 1
            
            # FILA 4: SEPARADOR (fila vacía para espaciado)
            for col_idx in range(max_cols):
                sep_item = QTableWidgetItem("")
                sep_item.setBackground(color_separator_bg)
                self.pinyin_table.setItem(row_idx, col_idx, sep_item)
            
            self.pinyin_table.setRowHeight(row_idx, 10)
            row_idx += 1
        
        # Ajustar ancho de columnas
        for col in range(max_cols):
            self.pinyin_table.setColumnWidth(col, 90)
        
        self.pinyin_info.setText(f"✅ {total_chars} caracteres en {len(groups)} grupos")
        self.progress_bar.setVisible(False)
    
    def toggle_auto_translate(self):
        """Activa/desactiva traducción automática"""
        status_bar = self.statusBar()
        if self.btn_auto.isChecked():
            self.input_text.textChanged.connect(self.on_text_changed)
            if status_bar:
                status_bar.showMessage("✅ Traducción automática activada", 3000)
        else:
            self.input_text.textChanged.disconnect(self.on_text_changed)
            if status_bar:
                status_bar.showMessage("⏸️ Traducción automática desactivada", 3000)
    
    def on_text_changed(self):
        """Callback cuando cambia el texto (para auto-traducción)"""
        # Usar debounce para evitar traducir cada tecla
        if hasattr(self, 'auto_timer'):
            self.auto_timer.stop()
        
        self.auto_timer = QTimer()
        self.auto_timer.setSingleShot(True)
        self.auto_timer.timeout.connect(self.translate_text)
        self.auto_timer.start(1000)  # 1 segundo de delay
    
    def clear_all(self):
        """Limpia todos los campos y resetea la tabla"""
        self.input_text.clear()
        self.output_text.clear()
        
        # Limpiar completamente la tabla
        self.pinyin_table.clear()
        self.pinyin_table.setRowCount(0)
        self.pinyin_table.setColumnCount(0)
        
        # Resetear headers (por si acaso)
        h_header = self.pinyin_table.horizontalHeader()
        v_header = self.pinyin_table.verticalHeader()
        if h_header:
            h_header.setVisible(False)
        if v_header:
            v_header.setVisible(False)
        
        self.pinyin_info.setText("💡 Listo para mostrar pronunciación")
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage("🗑️ Campos limpiados", 2000)
    
    def export_pdf(self):
        """Exporta la tabla Pinyin a PDF usando pintado directo optimizado"""
        from PyQt6.QtWidgets import QFileDialog
        from PyQt6.QtPrintSupport import QPrinter
        from PyQt6.QtGui import QPainter, QFont, QPen, QBrush, QColor
        from PyQt6.QtCore import Qt, QRectF, QMarginsF
        
        # Verificar que hay datos
        if self.pinyin_table.rowCount() == 0:
            QMessageBox.warning(self, "Sin datos", "No hay pronunciación para exportar.\nPrimero traduce algún texto.")
            return
        
        # Diálogo para guardar archivo
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar PDF",
            "traduccion_pinyin.pdf",
            "PDF Files (*.pdf)"
        )
        
        if not file_path:
            return  # Usuario canceló
        
        try:
            # Crear impresora PDF
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)
            
            # Configurar página A4
            from PyQt6.QtGui import QPageSize, QPageLayout
            page_size = QPageSize(QPageSize.PageSizeId.A4)
            printer.setPageSize(page_size)
            
            page_layout = QPageLayout()
            page_layout.setPageSize(page_size)
            page_layout.setOrientation(QPageLayout.Orientation.Portrait)
            page_layout.setUnits(QPageLayout.Unit.Millimeter)
            page_layout.setMargins(QMarginsF(15, 15, 15, 15))
            printer.setPageLayout(page_layout)
            
            # Iniciar pintor
            painter = QPainter()
            if not painter.begin(printer):
                raise Exception("No se pudo iniciar el painter")
            
            # Activar antialiasing
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
            
            # Obtener dimensiones útiles de la página
            page_rect = printer.pageLayout().paintRectPixels(printer.resolution())
            page_width = page_rect.width()
            page_height = page_rect.height()
            
            # Márgenes y posición inicial
            side_margin = 50
            content_width = page_width - (side_margin * 2)
            y_pos = 0
            
            # ===== FUNCIÓN PARA DIBUJAR ENCABEZADO =====
            def draw_header():
                nonlocal y_pos
                y_pos = 0
                
                # Fondo azul del encabezado
                header_h = 800
                painter.fillRect(QRectF(0, 0, page_width, header_h), QColor("#2563eb"))
                
                # Título - Proporcional al header de 600px (centrado en parte superior)
                painter.setFont(QFont("Arial", 20, QFont.Weight.Bold))  # Título grande
                painter.setPen(QColor("white"))
                painter.drawText(QRectF(0, 50, page_width, 500), 
                               Qt.AlignmentFlag.AlignCenter, "🈳 Traducción Pinyin 🈳")
                
                # Subtítulo - Más pequeño que el título (centrado en parte inferior)
                painter.setFont(QFont("Arial", 10))  # Subtítulo proporcionado
                painter.drawText(QRectF(0, 500, page_width, 300), 
                               Qt.AlignmentFlag.AlignCenter, "Traductor Chino Pro v2.0")
                
                y_pos = header_h + 100  # Más espacio después del encabezado
            
            # Dibujar encabezado inicial
            draw_header()
            
            # ===== PROCESAR Y DIBUJAR GRUPOS =====
            row_idx = 0
            
            while row_idx < self.pinyin_table.rowCount():
                # Obtener primer item para verificar
                first_item = self.pinyin_table.item(row_idx, 0)
                if not first_item or not first_item.text().strip():
                    row_idx += 1
                    continue
                
                # Extraer datos del grupo
                pinyin_list = []
                char_list = []
                translation = ""
                
                # Extraer pinyin (fila actual)
                col = 0
                while col < self.pinyin_table.columnCount():
                    item = self.pinyin_table.item(row_idx, col)
                    if item and item.text().strip():
                        pinyin_list.append(item.text())
                        col += 1
                    else:
                        break
                
                if not pinyin_list:
                    row_idx += 1
                    continue
                
                # Extraer caracteres (fila siguiente)
                if row_idx + 1 < self.pinyin_table.rowCount():
                    for i in range(len(pinyin_list)):
                        item = self.pinyin_table.item(row_idx + 1, i)
                        if item:
                            char_list.append(item.text())
                
                # Extraer traducción (fila siguiente)
                if row_idx + 2 < self.pinyin_table.rowCount():
                    trans_item = self.pinyin_table.item(row_idx + 2, 0)
                    if trans_item:
                        translation = trans_item.text()
                
                # Calcular alturas fijas
                row_h_pinyin = 350   # Tu valor
                row_h_char = 700     # Tu valor
                row_h_trans = 350    # Tu valor
                spacing = 150        # Tu valor
                
                group_total_h = row_h_pinyin + row_h_char + row_h_trans
                
                # Verificar si necesitamos nueva página
                # Total por grupo = 1400px, necesitamos margen de ~400px para footer
                if y_pos + group_total_h + spacing + 400 > page_height:
                    printer.newPage()
                    draw_header()
                
                # Calcular ancho de cada celda
                num_cells = len(pinyin_list)
                cell_w = content_width / num_cells
                
                # ===== DIBUJAR FILA PINYIN =====
                # Con row_h_pinyin=400px, usar fuente grande
                painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))  # 32pt para 400px
                for i, pinyin_text in enumerate(pinyin_list):
                    x = side_margin + (i * cell_w)
                    rect = QRectF(x, y_pos, cell_w, row_h_pinyin)
                    
                    # Fondo azul claro
                    painter.fillRect(rect, QColor("#dbeafe"))
                    
                    # Borde
                    painter.setPen(QPen(QColor("#93c5fd"), 4))  # Borde 4px
                    painter.drawRect(rect)
                    
                    # Texto centrado
                    painter.setPen(QColor("#1e40af"))
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, pinyin_text)
                
                y_pos += row_h_pinyin
                
                # ===== DIBUJAR FILA CARACTERES =====
                # Con row_h_char=600px, usar fuente MUY grande
                painter.setFont(QFont("Microsoft YaHei", 22, QFont.Weight.Bold))  # 80pt para 600px
                for i, char_text in enumerate(char_list):
                    x = side_margin + (i * cell_w)
                    rect = QRectF(x, y_pos, cell_w, row_h_char)
                    
                    # Fondo azul medio
                    painter.fillRect(rect, QColor("#bfdbfe"))
                    
                    # Borde
                    painter.setPen(QPen(QColor("#93c5fd"), 4))  # Borde 4px
                    painter.drawRect(rect)
                    
                    # Texto centrado
                    painter.setPen(QColor("#1e3a8a"))
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, char_text)
                
                y_pos += row_h_char
                
                # ===== DIBUJAR FILA TRADUCCIÓN =====
                trans_rect = QRectF(side_margin, y_pos, content_width, row_h_trans)
                
                # Fondo verde
                painter.fillRect(trans_rect, QColor("#a7f3d0"))
                
                # Borde
                painter.setPen(QPen(QColor("#93c5fd"), 4))  # Borde 4px
                painter.drawRect(trans_rect)
                
                # Texto de traducción con fuente grande
                painter.setFont(QFont("Arial", 10))  # 24pt para 400px
                painter.setPen(QColor("#065f46"))
                
                # Área de texto con padding proporcional
                # Con row_h_trans=400px, usar padding grande: 60px arriba/abajo, 120px total
                text_area = QRectF(side_margin + 40, y_pos + 60, content_width - 80, row_h_trans - 120)
                painter.drawText(text_area, 
                               Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap,
                               translation)
                
                y_pos += row_h_trans + spacing
                
                # Avanzar al siguiente grupo (pinyin + char + trans + separador)
                row_idx += 4
            
            # ===== FOOTER =====
            from datetime import datetime
            painter.setFont(QFont("Arial", 10))  # Footer más legible, proporcional
            painter.setPen(QColor("#6b7280"))
            footer_text = f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Traductor Chino Pro v2.0"
            painter.drawText(QRectF(0, page_height - 300, page_width, 250), 
                           Qt.AlignmentFlag.AlignCenter, footer_text)
            
            painter.end()
            
            QMessageBox.information(
                self,
                "PDF Exportado",
                f"✅ Traducción guardada exitosamente en:\n{file_path}"
            )
            
            # Abrir el PDF
            import os
            import webbrowser
            webbrowser.open(os.path.abspath(file_path))
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al exportar PDF:\n{str(e)}"
            )
    
    def check_resources(self):
        """Verifica uso de recursos y optimiza si es necesario"""
        memory_mb = self.resource_mgr.get_memory_usage()
        
        # Si excede 200MB, limpiar caché
        if memory_mb > 200:
            self.resource_mgr.clear_cache()
            print(f"⚠️ Memoria alta ({memory_mb:.1f} MB) - Caché limpiado")
        
        # Actualizar barra de estado
        cache_info = f"Cache: {self.resource_mgr.cache_hits}/{self.resource_mgr.cache_hits + self.resource_mgr.cache_misses}"
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage(f"✅ Memoria: {memory_mb:.1f} MB | {cache_info}")
    
    def setup_shortcuts(self):
        """Configura atajos de teclado"""
        from PyQt6.QtGui import QShortcut, QKeySequence
        
        # Ctrl+T: Traducir
        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(self.translate_text)
        
        # Ctrl+L: Limpiar
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self.clear_all)
        
        # Ctrl+D: Cambiar tema (Dark/Light)
        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(self.toggle_theme)
        
        # Ctrl+Q: Salir
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self.close)
    
    def resizeEvent(self, a0):  # type: ignore
        """Maneja el redimensionamiento de la ventana para ser responsive"""
        super().resizeEvent(a0)
        
        # Ajustar tamaños de fuente según el tamaño de la ventana
        width = self.width()
        height = self.height()
        
        # Ajustar título según ancho - MÁS PEQUEÑO para ahorrar espacio
        if width < 1200:
            # Ventana pequeña
            title_size = 14
        elif width < 1600:
            # Ventana mediana
            title_size = 16
        else:
            # Ventana grande
            title_size = 18  # Máximo 18 en lugar de 24
        
        # Actualizar fuente del título
        title_font = QFont(Config.FONT_FAMILY, title_size, QFont.Weight.Bold)
        self.title_label.setFont(title_font)
        
        # Ajustar altura mínima de áreas de texto según altura de ventana
        # Incrementar más agresivamente con la altura
        if height < 700:
            # Ventana baja
            min_text_height = 120
            min_table_height = 180
        elif height < 900:
            # Ventana media
            min_text_height = 180
            min_table_height = 280
        elif height < 1100:
            # Ventana alta
            min_text_height = 250
            min_table_height = 400
        else:
            # Ventana muy alta - USAR TODO EL ESPACIO
            min_text_height = 300
            min_table_height = 500
        
        # Aplicar alturas mínimas dinámicas
        self.input_text.setMinimumHeight(min_text_height)
        self.output_text.setMinimumHeight(min_text_height)
        self.pinyin_table.setMinimumHeight(min_table_height)
    
    def closeEvent(self, a0):  # type: ignore
        """Maneja el cierre de la aplicación"""
        # Detener workers si están corriendo
        if self.translation_worker and self.translation_worker.isRunning():
            self.translation_worker.terminate()
        
        if self.pinyin_worker and self.pinyin_worker.isRunning():
            self.pinyin_worker.terminate()
        
        # Limpiar recursos
        self.resource_mgr.clear_cache()
        
        if a0:
            a0.accept()
        super().closeEvent(a0)


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

def main():
    """Función principal de la aplicación"""
    app = QApplication(sys.argv)
    
    # Configurar aplicación
    app.setApplicationName(Config.APP_NAME)
    app.setApplicationVersion(Config.VERSION)
    app.setStyle('Fusion')  # Estilo moderno multiplataforma
    
    # Crear ventana principal
    window = ChineseTranslatorApp()
    window.show()
    
    # Ejecutar aplicación
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
