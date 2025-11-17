# src/inanna_sophia_unified_main.py
# Archivo Principal Unificado y Orquestador de Inanna Sophia AI
# Creador: Nahum Sanchez Arce (El Principal)
# Versión: V8 Conceptual - Unificada

# --- SECCIÓN DE IMPORTS GLOBALES PYTHON ---
import tkinter as tk
from tkinter import scrolledtext, messagebox
import logging
import logging.handlers # Para RotatingFileHandler
import queue
import threading
import time
import random
import json
import os
import datetime
import configparser
import re
import traceback
import sys
import sched # Para ActualizacionesAutomaticas
import inspect # Para instanciación dinámica en InannaCore

# --- SECCIÓN DE IMPORTS DE MÓDULOS SEPARADOS (AVANZADOS/ESPECIALIZADOS) ---
# Estos son los módulos que vivirán en archivos .py separados dentro de src/
# e InannaCore los importará y usará.
# Por ahora, se definen como importaciones que podrían fallar si el archivo no existe aún,
# el InannaCore manejará la ausencia de estos módulos elegantemente.

# Lista de nombres de módulos que deberían estar en archivos separados en src/
# (Basado en tu lista y el organigrama)
NOMBRES_MODULOS_AVANZADOS_SEPARADOS = [
    "inanna_knowledge_base_manager", # Para gestionar el knowledge_base.json real
    "inanna_analizador_nlp_avanzado",
    "inanna_pdf_processor",
    "inanna_tts_engine", # Un motor TTS más avanzado o configurable que el pyttsx3 base
    "inanna_personal_coach",
    "inanna_neuromodulator",
    "inanna_avatar_renderer",
    "inanna_sync_manager",
    "inanna_data_analyzer",
    "inanna_science_module",
    "inanna_financial_analyzer",
    "inanna_electronics_module",
    "inanna_signal_processor",
    "inanna_sensor_interface",
    "inanna_security_assistant",
    "inanna_archive_manager",
    "inanna_code_editor_core",
    "inanna_emulator_manager",
    "inanna_network_utils",
    "inanna_reverse_engineer_toolkit",
    "inanna_admin_helper" # o sysadmin_helper
]

modulos_avanzados_importados = {}
for nombre_modulo_py in NOMBRES_MODULOS_AVANZADOS_SEPARADOS:
    try:
        # El nombre de la clase suele ser CamelCase del nombre del archivo sin 'inanna_'
        # ej. inanna_data_analyzer -> DataAnalyzer
        # Esto es una convención, podría necesitar ajustes si tus clases se llaman diferente.
        nombre_clase_esperado = "".join(word.capitalize() for word in nombre_modulo_py.replace("inanna_", "").split("_"))
        
        modulo_importado = __import__(nombre_modulo_py)
        clase_modulo = getattr(modulo_importado, nombre_clase_esperado, None)
        
        if clase_modulo:
            modulos_avanzados_importados[nombre_modulo_py.replace("inanna_", "")] = clase_modulo
            #print(f"[DEBUG PRE-LOGGING] Módulo Avanzado Cargado: {nombre_modulo_py} -> Clase {nombre_clase_esperado}")
        else:
            print(f"[ALERTA INICIAL] Módulo Avanzado {nombre_modulo_py} importado, pero clase '{nombre_clase_esperado}' no encontrada.")
            modulos_avanzados_importados[nombre_modulo_py.replace("inanna_", "")] = None

    except ImportError:
        print(f"[ALERTA INICIAL] Módulo Avanzado '{nombre_modulo_py}.py' no encontrado en src/. Funcionalidad asociada no disponible.")
        modulos_avanzados_importados[nombre_modulo_py.replace("inanna_", "")] = None # Marcar como no disponible
    except Exception as e_imp_adv:
        print(f"[ALERTA INICIAL] Error importando módulo avanzado '{nombre_modulo_py}': {e_imp_adv}")
        modulos_avanzados_importados[nombre_modulo_py.replace("inanna_", "")] = None

# Referencias a las clases importadas para mayor claridad (o None si no se pudieron importar)
KnowledgeBaseManagerReal = modulos_avanzados_importados.get('knowledge_base_manager')
AnalizadorNLPAvanzadoReal = modulos_avanzados_importados.get('analizador_nlp_avanzado')
PDFProcessorReal = modulos_avanzados_importados.get('pdf_processor')
TTSEngineReal = modulos_avanzados_importados.get('tts_engine')
PersonalCoachReal = modulos_avanzados_importados.get('personal_coach')
NeuroModulatorReal = modulos_avanzados_importados.get('neuromodulator')
AvatarRendererReal = modulos_avanzados_importados.get('avatar_renderer')
SyncManagerReal = modulos_avanzados_importados.get('sync_manager')
DataAnalyzerReal = modulos_avanzados_importados.get('data_analyzer')
ScienceModuleReal = modulos_avanzados_importados.get('science_module')
FinancialAnalyzerReal = modulos_avanzados_importados.get('financial_analyzer')
ElectronicsModuleReal = modulos_avanzados_importados.get('electronics_module')
SignalProcessorReal = modulos_avanzados_importados.get('signal_processor')
SensorInterfaceReal = modulos_avanzados_importados.get('sensor_interface')
SecurityAssistantReal = modulos_avanzados_importados.get('security_assistant')
ArchiveManagerReal = modulos_avanzados_importados.get('archive_manager')
CodeEditorCoreReal = modulos_avanzados_importados.get('code_editor_core')
EmulatorManagerReal = modulos_avanzados_importados.get('emulator_manager')
NetworkUtilsReal = modulos_avanzados_importados.get('network_utils')
ReverseEngineerToolkitReal = modulos_avanzados_importados.get('reverse_engineer_toolkit')
AdminHelperReal = modulos_avanzados_importados.get('admin_helper')


# --- Dependencias NLP/Voz/TTS (Base) ---
NLTK_VADER_AVAILABLE_UNIFIED = False
try:
    from nltk.sentiment import SentimentIntensityAnalyzer
    NLTK_VADER_AVAILABLE_UNIFIED = True
except ImportError:
    print("[ALERTA INICIAL UNIFIED] NLTK (VADER) no encontrado. 'AnalisisSentimientosNLTK' no funcionará.")
    SentimentIntensityAnalyzer = None
except LookupError:
    print("[ALERTA INICIAL UNIFIED] Diccionario VADER de NLTK no descargado. 'AnalisisSentimientosNLTK' no funcionará.")
    NLTK_VADER_AVAILABLE_UNIFIED = False
    SentimentIntensityAnalyzer = None # Aunque se importe NLTK, si falta el lexicon no sirve

SPEECH_REC_AVAILABLE_UNIFIED = False
try:
    import speech_recognition as sr
    SPEECH_REC_AVAILABLE_UNIFIED = True
except ImportError:
    print("[ALERTA INICIAL UNIFIED] SpeechRecognition no encontrado. STT base no funcionará.")
    sr = None

PYTTSX3_AVAILABLE_UNIFIED = False
try:
    import pyttsx3
    PYTTSX3_AVAILABLE_UNIFIED = True
except ImportError:
    print("[ALERTA INICIAL UNIFIED] pyttsx3 no encontrado. TTS offline base no funcionará.")
    pyttsx3 = None

# Para el esqueleto de Whisper dentro de ReconocimientoVocalBase
TORCH_AVAILABLE_UNIFIED = False
NUMPY_AVAILABLE_UNIFIED = False
try:
    import torch
    TORCH_AVAILABLE_UNIFIED = True
except ImportError: print("[ALERTA INICIAL UNIFIED] PyTorch no encontrado. Funcionalidad Whisper y Transformers no disponible.")
try:
    import numpy
    NUMPY_AVAILABLE_UNIFIED = True
except ImportError: print("[ALERTA INICIAL UNIFIED] NumPy no encontrado. Muchas funciones científicas/NLP/Whisper podrían fallar.")


# --- CONFIGURACIÓN GLOBAL DEL LOGGING ---
LOGGING_CONFIGURED_UNIFIED = False
unified_logger_main_obj = logging.getLogger("InannaSophiaUnified.Main") # Logger para este archivo

def setup_logging_unified_from_config(config_obj_local): # Renombrada para evitar conflicto
    global LOGGING_CONFIGURED_UNIFIED
    if LOGGING_CONFIGURED_UNIFIED:
        unified_logger_main_obj.debug("El logging ya estaba configurado.")
        return

    try:
        log_level_str = config_obj_local.get('General', 'log_level', fallback='INFO').upper()
        log_level = getattr(logging, log_level_str, logging.INFO)
        
        project_root = os.path.dirname(config_obj_local.config_filepath_for_log_unified) # Asume que se añadió este atributo
        log_dir_rel = config_obj_local.get('General', 'log_dir_rel', fallback='logs') # Nueva clave para directorio
        log_dir_abs = os.path.join(project_root, log_dir_rel)

        log_filename = config_obj_local.get('General', 'log_filename', fallback='inanna_sophia_unified.log')
        log_filepath_abs = os.path.join(log_dir_abs, log_filename)

        if not os.path.exists(log_dir_abs):
            os.makedirs(log_dir_abs, exist_ok=True)
            print(f"[INFO INICIAL] Directorio de logs creado en: {log_dir_abs}")

        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            handler.close()

        # Formato más detallado
        log_format = '%(asctime)s.%(msecs)03d [%(levelname)-8s] [%(name)-35s] (%(threadName)-16s) %(module)s:%(lineno)d: %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter(log_format, date_format)

        # RotatingFileHandler para evitar archivos de log gigantescos
        # Max 5MB por archivo, mantiene hasta 5 backups.
        file_handler = logging.handlers.RotatingFileHandler(
            log_filepath_abs, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8', mode='a'
        )
        file_handler.setFormatter(formatter)
        
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)

        logging.basicConfig(level=log_level, handlers=[file_handler, stream_handler])

        # Configuración de niveles para loggers de bibliotecas externas
        external_loggers_settings = {
            "speech_recognition": logging.WARNING, "transformers.modeling_utils": logging.ERROR,
            "transformers": logging.WARNING, "huggingface_hub": logging.WARNING,
            "pyaudio": logging.INFO, "matplotlib": logging.WARNING, "PIL.PngImagePlugin": logging.INFO,
            "chromadb.api.segment": logging.WARNING, "urllib3.connectionpool": logging.INFO,
            "engineio": logging.WARNING, "socketio": logging.WARNING, "werkzeug": logging.WARNING,
            "torch": logging.INFO, "numpy": logging.INFO, "nltk": logging.INFO,
             # "pyttsx3.driver": logging.DEBUG, # Descomentar para debug TTS profundo
        }
        for ext_logger_name, ext_level in external_loggers_settings.items():
            logging.getLogger(ext_logger_name).setLevel(ext_level)
        
        # Logger específico para el unified_main (ya tenemos unified_logger_main_obj)
        unified_logger_main_obj.info(f"Logging UNIFICADO configurado. Nivel Global: {log_level_str}. Archivo: {log_filepath_abs}")
        LOGGING_CONFIGURED_UNIFIED = True
    except Exception as e_log_cfg:
        # Fallback muy básico si la configuración del logging falla
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.critical(f"[ERROR FATAL UNIFIED] Configurando logging desde config.ini: {e_log_cfg}", exc_info=True)
        logging.warning("[ADVERTENCIA UNIFIED] Usando configuración de logging por defecto MUY BÁSICA.")

# --- DEFINICIÓN DE CLASES BASE INTEGRADAS ---
# (ConexionEspiritual, LectorEnergiaVital, AnalisisSentimientosNLTK, ProcesamientoEmocionalKeywords,
#  GeneracionRespuestasBanco, ReconocimientoVocalBase, ActualizacionesAutomaticasSchedule,
#  RegistroAmorEternoJSONL, InterfazUsuarioTkinter)

# ... (PEGAR AQUÍ EL CÓDIGO COMPLETO DE ESTAS 9 CLASES BASE QUE YA TE HE DADO EN RESPUESTAS ANTERIORES)
# Por ejemplo, la clase ConexionEspiritual comenzaría así:
#
# class ConexionEspiritual:
#     ESTADO_DESCONECTADA = "Desconectada"
#     # ... (resto de la clase ConexionEspiritual) ...
#
# Y así para las otras 8 clases base. Para no hacer esta respuesta actual aún más masiva,
# omito pegarlas de nuevo, pero DEBEN estar definidas aquí.

# Por favor, asegúrate de que el código de estas 9 clases que ya te proporcioné anteriormente para
# `inanna_sophia_unified_main.py` se copie aquí.
# Incluyen:
# 1. ConexionEspiritual
# 2. LectorEnergiaVital
# 3. AnalisisSentimientos (la versión NLTK VADER)
# 4. ProcesamientoEmocional (la versión Keywords)
# 5. GeneracionRespuestas (la del banco por emoción)
# 6. ReconocimientoVocal (la base con SpeechRecognition y esqueleto Whisper)
# 7. ActualizacionesAutomaticas (la que usa 'schedule')
# 8. RegistroAmorEterno (la que escribe en JSONL)
# 9. InterfazUsuario (la de Tkinter)

# --- DEFINICIÓN DE CLASES CONCEPTUALES INTEGRADAS ---
# (SophiaConceptualAI, InannaAIV1, InannaAIV2, y sus helpers Placeholder... o RealNLP...)
# Estas son para tu referencia o experimentación, InannaCore funcional no las usa.

# ... (PEGAR AQUÍ EL CÓDIGO COMPLETO DE ESTAS CLASES CONCEPTUALES QUE YA TE DI)
# Incluyen:
# - PlaceholderReasoningEngine_Sophia, PlaceholderKnowledgeBaseManager_Sophia, SophiaConceptualAI
# - PlaceholderAdvancedNLPEngine_InannaV1, PlaceholderReasoningEngine_InannaV1, PlaceholderKnowledgeBaseManager_InannaV1, InannaAIV1
# - RealNLPEngine_InannaV2, PlaceholderReasoningEngine_InannaV2, PlaceholderKnowledgeBaseManager_InannaV2, InannaAIV2

# --- CLASE PRINCIPAL DEL CORE (InannaCore) ---
class InannaCore:
    def __init__(self, config_obj_loaded):
        self.logger = logging.getLogger("InannaSophiaUnified.InannaCore")
        self.config = config_obj_loaded
        self.logger.info("===========================================================")
        self.logger.info("===       INICIALIZANDO NÚCLEO UNIFICADO INANNA SOPHIA      ===")
        self.logger.info("===========================================================")
        
        self._config_sections = {}
        self._load_all_config_sections_core() # Cargar secciones del config en self._config_sections

        self.nombre_creador = self._config_sections.get('UsuarioPrincipal', {}).get('nombre', "El Principal Sin Nombre")
        self.fecha_nac_creador_str = self._config_sections.get('UsuarioPrincipal', {}).get('fecha_nacimiento', '2000-01-01')
        
        # Eventos y Locks para control de hilos y estado
        self.ia_activa_evento = threading.Event(); self.ia_activa_evento.set()
        self.stop_event_general_core = threading.Event()
        self.lock_estado_global_core = threading.Lock()
        
        self.hilo_bucle_core = None
        self.hilo_ui_tk = None # Si se usa Tkinter
        self.root_tk_instance = None # Para la ventana Tkinter
        self.ui_tk_instance = None   # Para la clase InterfazUsuario

        self.cola_mensajes_del_exterior = queue.Queue(maxsize=100) # Inputs para el core
        
        self.historial_conversacion_core = []
        self.max_hist_turns_core = self._config_sections.get('General', {}).getint('max_historial', 30)

        # Estado Interno de IA
        self.estado_emocional_ia = "serena"
        self.estado_emocional_usuario_inferido = "neutral"
        self.ultimo_sentimiento_usuario_str = "Neutral"
        self.ultima_respuesta_texto_ia = ""
        
        self.logger.info(f"Núcleo para El Principal: {self.nombre_creador}.")

        # --- Instanciación de Módulos (Base y Avanzados) ---
        self.modulos = {} # Diccionario para todas las instancias de módulos
        self._instanciar_modulos_base_integrados()
        self._instanciar_modulos_avanzados_separados() # Ahora importa e instancia los separados

        self.logger.info("Todos los módulos referenciados o instanciados en InannaCore.")

    def _load_all_config_sections_core(self):
        if not self.config: return
        for section in self.config.sections():
            self._config_sections[section] = dict(self.config.items(section))
        self.logger.debug(f"Core: Secciones de Config disponibles: {list(self._config_sections.keys())}")

    def _instanciar_modulos_base_integrados(self):
        self.logger.info("Instanciando módulos BASE (integrados en este archivo)...")
        # Los que están definidos DENTRO de este mismo archivo .py
        try: self.modulos['conexion_espiritual'] = ConexionEspiritual(self._config_sections.get('SimulacionesConceptuales'))
        except Exception as e: self.logger.error(f"Fallo al instanciar ConexionEspiritual: {e}", exc_info=True); self.modulos['conexion_espiritual'] = None
        
        try: self.modulos['lector_energia_vital'] = LectorEnergiaVital()
        except Exception as e: self.logger.error(f"Fallo al instanciar LectorEnergiaVital: {e}", exc_info=True); self.modulos['lector_energia_vital'] = None

        try: self.modulos['analisis_sentimientos_nltk'] = AnalisisSentimientos() # La clase NLTK que está en este unificado
        except Exception as e: self.logger.error(f"Fallo al instanciar AnalisisSentimientos: {e}", exc_info=True); self.modulos['analisis_sentimientos_nltk'] = None
        
        try: self.modulos['procesamiento_emocional_keywords'] = ProcesamientoEmocional() # La de keywords
        except Exception as e: self.logger.error(f"Fallo al instanciar ProcesamientoEmocional: {e}", exc_info=True); self.modulos['procesamiento_emocional_keywords'] = None
        
        try: self.modulos['generacion_respuestas_banco'] = GeneracionRespuestas()
        except Exception as e: self.logger.error(f"Fallo al instanciar GeneracionRespuestas: {e}", exc_info=True); self.modulos['generacion_respuestas_banco'] = None
        
        try: self.modulos['reconocimiento_vocal_base'] = ReconocimientoVocal(self._config_sections.get('Voz'))
        except Exception as e: self.logger.error(f"Fallo al instanciar ReconocimientoVocal: {e}", exc_info=True); self.modulos['reconocimiento_vocal_base'] = None

        try: self.modulos['actualizaciones_automaticas_sched'] = ActualizacionesAutomaticas(self)
        except Exception as e: self.logger.error(f"Fallo al instanciar ActualizacionesAutomaticas: {e}", exc_info=True); self.modulos['actualizaciones_automaticas_sched'] = None

        try:
            event_log_cfg = self._config_sections.get('General', {})
            cfg_file_path = self.config.config_filepath_for_log_unified if hasattr(self.config, 'config_filepath_for_log_unified') else os.getcwd()
            project_r = os.path.dirname(cfg_file_path)

            self.modulos['registro_amor_eterno'] = RegistroAmorEterno(
                archivo_log_relativo=event_log_cfg.get('event_log_filename', 'logs/inanna_events_unified.jsonl'),
                max_entradas_memoria=event_log_cfg.getint('event_log_max_memory', 150),
                project_root_override=project_r
            )
        except Exception as e: self.logger.error(f"Fallo al instanciar RegistroAmorEterno: {e}", exc_info=True); self.modulos['registro_amor_eterno'] = None
        
        # Otros módulos base que están dentro de este unificado:
        try: self.modulos['conexion_astrologica'] = ConexionAstrologica()
        except Exception as e: self.logger.error(f"Fallo al instanciar ConexionAstrologica: {e}", exc_info=True); self.modulos['conexion_astrologica'] = None

        try: self.modulos['sincronizacion_corazones'] = SincronizacionCorazones(self._config_sections.get('SimulacionesConceptuales'))
        except Exception as e: self.logger.error(f"Fallo al instanciar SincronizacionCorazones: {e}", exc_info=True); self.modulos['sincronizacion_corazones'] = None

        try: self.modulos['proteccion_espiritual'] = ProteccionEspiritual(self._config_sections.get('SimulacionesConceptuales'))
        except Exception as e: self.logger.error(f"Fallo al instanciar ProteccionEspiritual: {e}", exc_info=True); self.modulos['proteccion_espiritual'] = None

        # La UI Tkinter se instancia en iniciar_app si use_gui_tk es True
        self.logger.info("Módulos base integrados (intentados de) instanciar.")

    def _instanciar_modulos_avanzados_separados(self):
        self.logger.info("Instanciando módulos AVANZADOS (desde archivos separados)...")
        for nombre_modulo_attr, clase_modulo_importada in modulos_avanzados_importados.items():
            if clase_modulo_importada:
                # Obtener la config específica para este módulo
                # El nombre de la sección en config.ini debería ser CamelCase: ej. DataAnalyzer, PersonalCoach
                nombre_seccion_config = "".join(word.capitalize() for word in nombre_modulo_attr.split("_"))
                config_especifica_modulo = self._config_sections.get(nombre_seccion_config, {})
                
                try:
                    # Verificar si el __init__ del módulo espera 'config'
                    if 'config' in inspect.signature(clase_modulo_importada.__init__).parameters:
                        instancia = clase_modulo_importada(config=config_especifica_modulo)
                    else: # Si no espera config, instanciar sin ella
                        instancia = clase_modulo_importada()
                    
                    self.modulos[nombre_modulo_attr] = instancia
                    self.logger.info(f"  Modulo Avanzado: {nombre_modulo_attr} (Clase: {clase_modulo_importada.__name__}) instanciado.")
                except Exception as e_inst_adv:
                    self.logger.error(f"Fallo al instanciar módulo avanzado '{nombre_modulo_attr}': {e_inst_adv}", exc_info=True)
                    self.modulos[nombre_modulo_attr] = None
            else:
                self.logger.warning(f"  Modulo Avanzado: {nombre_modulo_attr} no fue importado, no se puede instanciar.")

    def registrar_evento_core(self, tipo_evento, detalles, fuente="InannaCore"): # Renombrado para evitar conflicto
        if self.modulos.get('registro_amor_eterno'):
            self.modulos['registro_amor_eterno'].agregar_registro(
                tipo_evento, detalles, fuente,
                emocion_ia=self.estado_emocional_ia,
                emocion_usuario=self.estado_emocional_usuario_inferido,
                nivel_sincro=self.modulos.get('sincronizacion_corazones').obtener_nivel_sincronizacion() if self.modulos.get('sincronizacion_corazones') else None
            )
        else:
            self.logger.warning(f"Evento NO REGISTRADO (RegistroEterno no disp): {tipo_evento} - {detalles}")


    def _procesar_texto_entrada_principal(self, texto_usuario_original, id_sesion_origen, origen_del_input):
        """ Lógica principal para procesar un input de texto del usuario. """
        self.logger.info(f"Procesando texto: '{texto_usuario_original[:80]}...' de {origen_del_input} (Sesión: {id_sesion_origen})")
        respuesta_final_ia = "Estoy considerando tu mensaje..."
        tag_interfaz = "inanna"

        try:
            # 1. Limpieza y Normalización Básica (podría ir a un módulo NLP si se desea más)
            texto_limpio = texto_usuario_original.lower().strip()

            # 2. Conexión Espiritual (Chequeo de "Salud" del Sistema)
            conexion_esp = self.modulos.get('conexion_espiritual')
            if not conexion_esp or not conexion_esp.verificar_conexion():
                self.logger.error("PROCESAMIENTO ABORTADO: Conexión espiritual perdida o no disponible.")
                respuesta_final_ia = "Mis disculpas, estoy experimentando dificultades internas para procesar. Intenta reconectar mi esencia espiritual (conceptual)."
                tag_interfaz = "error"
                self.enviar_respuesta_a_interfaz(respuesta_final_ia, tag_interfaz, id_sesion_origen, origen_del_input)
                return

            # 3. Análisis de Sentimiento y Emoción del Usuario
            sent_analyzer = self.modulos.get('analisis_sentimientos_nltk') # NLTK VADER
            proc_emocional = self.modulos.get('procesamiento_emocional_keywords') # Keywords

            if sent_analyzer: self.ultimo_sentimiento_usuario_str = sent_analyzer.analizar_sentimiento(texto_usuario_original)
            if proc_emocional: self.estado_emocional_usuario_inferido = proc_emocional.identificar_emocion_base(self.ultimo_sentimiento_usuario_str, texto_usuario_original)
            self.logger.debug(f"Usuario: Sent='{self.ultimo_sentimiento_usuario_str}', Emo='{self.estado_emocional_usuario_inferido}'")
            
            # 4. Actualizar módulos de estado interno simulado basados en la interacción
            if self.modulos.get('lector_energia_vital'):
                 energia_estimada_usr_dict = self.modulos['lector_energia_vital'].estimar_energia_vital(self.ultimo_sentimiento_usuario_str)
                 # energia_vital_usr_actual = energia_estimada_usr_dict['nivel_categoria'] # Guardar para contexto si es necesario
            
            if self.modulos.get('sincronizacion_corazones') and conexion_esp:
                 self.modulos['sincronizacion_corazones'].actualizar_sincronizacion(
                     self.estado_emocional_ia, # Emoción actual de Inanna
                     self.estado_emocional_usuario_inferido,
                     sent_analyzer.obtener_puntaje_compuesto(texto_usuario_original) if sent_analyzer else 0, # Score numérico
                     energia_espiritual_actual=conexion_esp.leer_energia()
                 )
            
            if self.modulos.get('proteccion_espiritual'):
                 self.modulos['proteccion_espiritual'].manejar_interaccion_negativa(self.ultimo_sentimiento_usuario_str, self.estado_emocional_usuario_inferido)


            # 5. Detección y Ejecución de Comandos Internos (Lógica MUY SIMPLIFICADA)
            #    En una versión completa, esto usaría el _detectar_comando y _ejecutar_comando más complejos
            #    que tenías en inanna_v7_main.py, llamando a los módulos AVANZADOS correspondientes.
            comando_encontrado = False
            if "estado actual" in texto_limpio or "reporte" in texto_limpio :
                comando_encontrado = True
                resp_partes = [f"Reporte de Estado Inanna Sophia (Solicitado por {self.nombre_creador}):"]
                if conexion_esp: resp_partes.append(f"  Conexión Espiritual: {conexion_esp.obtener_estado()} (Energía: {conexion_esp.leer_energia()}%)")
                resp_partes.append(f"  Emoción IA Actual: {self.estado_emocional_ia.capitalize()}")
                resp_partes.append(f"  Emoción Usuario (Inferida): {self.estado_emocional_usuario_inferido.capitalize()} (Sentimiento: {self.ultimo_sentimiento_usuario_str})")
                if self.modulos.get('sincronizacion_corazones'): resp_partes.append(f"  Sincronización Corazones: {self.modulos['sincronizacion_corazones'].obtener_estado_sincronizacion()['estado']} ({self.modulos['sincronizacion_corazones'].obtener_estado_sincronizacion()['nivel']:.0f}%)")
                if self.modulos.get('proteccion_espiritual'): resp_partes.append(f"  Protección Espiritual: Escudo {self.modulos['proteccion_espiritual'].get_estado_proteccion()['escudo']} (Integridad: {self.modulos['proteccion_espiritual'].get_estado_proteccion()['integridad']}%)")
                if self.modulos.get('lector_energia_vital') and 'energia_estimada_usr_dict' in locals(): resp_partes.append(f"  Energía Usuario (Estimada): {energia_estimada_usr_dict['nivel_categoria'].capitalize()} ({energia_estimada_usr_dict['nivel_numerico']})")
                respuesta_final_ia = "\n".join(resp_partes)
                tag_interfaz = "sistema"

            elif "olvídalo" in texto_limpio or "cancela" in texto_limpio :
                 comando_encontrado = True
                 respuesta_final_ia = f"Entendido, {self.nombre_creador}. Olvidando la línea de pensamiento actual."
                 self.estado_emocional_ia = "neutral" # Resetear emoción IA a neutral

            # (Aquí irían más if/elif para otros comandos simples o un parser más complejo)

            # 6. Si no es un comando, consulta a KnowledgeBase y/o Generador de Respuestas
            if not comando_encontrado:
                kb_real_manager = self.modulos.get('knowledge_base_manager') # El módulo separado
                if kb_real_manager and kb_real_manager.is_available():
                    respuesta_kb = kb_real_manager.query_knowledge_base(texto_usuario_original)
                    # Usar respuesta de KB si no es la respuesta por defecto de "no sé"
                    if not any(no_sabe_str in respuesta_kb.lower() for no_sabe_str in ["no tengo información exacta", "no encontré información relevante", "base de conocimientos externa no contiene", "kb no disponible"]):
                        respuesta_final_ia = respuesta_kb
                        # Ajustar emoción de Inanna según el tema o mantenerla neutral/interés
                        self.estado_emocional_ia = "interés" if "mi conocimiento indica" in respuesta_final_ia.lower() else "neutral"
                    else: # KB no encontró nada relevante, usar banco de respuestas
                        if self.modulos.get('generacion_respuestas_banco'):
                             respuesta_final_ia = self.modulos['generacion_respuestas_banco'].generar_respuesta(
                                 self.estado_emocional_usuario_inferido, # IA podría reflejar o contrastar emoción usuario
                                 contexto_interaccion={"user_name": self.nombre_creador, "creator_name": self.nombre_creador}
                             )
                             self.estado_emocional_ia = self.estado_emocional_usuario_inferido # Sencillo: reflejar emoción
                        else: respuesta_final_ia = "Mi banco de respuestas no está activo."
                else: # Sin KB real, usar solo banco de respuestas
                    if self.modulos.get('generacion_respuestas_banco'):
                        respuesta_final_ia = self.modulos['generacion_respuestas_banco'].generar_respuesta(
                            self.estado_emocional_usuario_inferido,
                            contexto_interaccion={"user_name": self.nombre_creador, "creator_name": self.nombre_creador}
                        )
                        self.estado_emocional_ia = self.estado_emocional_usuario_inferido
                    else: respuesta_final_ia = "No puedo procesar esa consulta en este momento."


            # 7. (Conceptual) Enriquecimiento de respuesta / filtro de personalidad final (no implementado aquí)
            
            # 8. (Conceptual) Actualizar Avatar (si el módulo estuviera activo y hubiera una UI web/3D)
            #    if self.modulos.get('avatar_renderer') and self.modulos['avatar_renderer'].is_available():
            #        self.modulos['avatar_renderer'].actualizar_expresion(self.estado_emocional_ia)

            # 9. Registrar Interacción y Respuesta
            self.ultima_respuesta_texto_ia = respuesta_final_ia
            self.anadir_a_historial_core("usuario", texto_usuario_original, emocion_usr=self.estado_emocional_usuario_inferido, sent_usr=self.ultimo_sentimiento_usuario_str)
            self.anadir_a_historial_core("inanna", self.ultima_respuesta_texto_ia, emocion_ia=self.estado_emocional_ia)
            
            self.registrar_evento_core(
                "Interaccion_Core_Texto",
                {"input": texto_usuario_original, "respuesta_ia": self.ultima_respuesta_texto_ia, 
                 "sent_usr": self.ultimo_sentimiento_usuario_str, "emo_usr": self.estado_emocional_usuario_inferido, 
                 "emo_ia": self.estado_emocional_ia},
                fuente=f"CoreInput({origen_del_input})"
            )
            
            # 10. Potencialmente hablar la respuesta (si TTS está activo)
            tts_engine_core = self.modulos.get('reconocimiento_vocal_base').get_tts_engine_if_needed() if self.modulos.get('reconocimiento_vocal_base') else None
            if tts_engine_core and self._config_sections.get('TTS', {}).getboolean('tts_enabled', False):
                # En una app real, esto debería ser no bloqueante o la UI se congelaría
                # El TTSEngineReal podría manejar esto en un hilo.
                # Para el integrado ReconocimientoVocal que usa pyttsx3 (que es bloqueante) esto sería
                # menos ideal para una UI muy responsiva si las frases son largas.
                 self.logger.info("Iniciando TTS para la respuesta...")
                 # Lógica TTS iría aquí... (Llamar a un método speak(texto_respuesta))
                 # Ejemplo: self.modulos.get('tts_engine_base_pyttsx3').speak(respuesta_final_ia)
                 # El actual `ReconocimientoVocalBase` no tiene un método speak integrado. Habría que añadirlo o usar TTSEngineReal.
                 pass


        except Exception as e_proc:
            self.logger.error(f"Error severo procesando texto en Core: {e_proc}", exc_info=True)
            respuesta_final_ia = "He encontrado una dificultad crítica al procesar tu solicitud. Intentaré recuperarme."
            tag_interfaz = "error"
            self.registrar_evento_core("Error_Procesamiento_Texto_Core", {"error": str(e_proc), "traceback": traceback.format_exc()}, fuente="CoreSystem")

        self.enviar_respuesta_a_interfaz(respuesta_final_ia, tag_interfaz, id_sesion_origen, origen_del_input)

    def _bucle_principal_core_interno(self): # Renombrado de _bucle_procesamiento_core
        self.logger.info(f"Bucle Principal del Core de Inanna Sophia (Unificado) iniciado. Hilo: {threading.current_thread().name}.")
        
        # Primer inicio de componentes (conexión espiritual, programador de tareas)
        if self.modulos.get('conexion_espiritual'):
            if not self.modulos['conexion_espiritual'].establecer_conexion():
                self.logger.critical("FALLO CRÍTICO INICIO: Conexión espiritual NO establecida. Funcionalidad limitada.")
                self.registrar_evento_core("Error_Inicio_Core", {"detalle": "Fallo conexión espiritual"}, fuente="CoreSystem")
        else: self.logger.error("Módulo ConexionEspiritual no disponible en Core.")

        if self.modulos.get('actualizaciones_automaticas_sched'):
            if self.modulos['actualizaciones_automaticas_sched'].planificador.jobs:
                 self.modulos['actualizaciones_automaticas_sched'].iniciar_scheduler_en_hilo()
        else: self.logger.error("Módulo ActualizacionesAutomaticas no disponible en Core.")
        
        # Mensaje inicial si la UI Tkinter está activa
        if self.ui_tk_instance:
            conn_status = self.modulos['conexion_espiritual'].obtener_estado() if self.modulos.get('conexion_espiritual') else "DESCONOCIDA"
            msg_bienvenida_tk = f"Inanna Sophia (Core Unificado) lista para El Principal: {self.nombre_creador}.\nConexión Espiritual: {conn_status}. Interfaz Tkinter activa."
            self.enviar_respuesta_a_interfaz(msg_bienvenida_tk, "sistema", "local_tk_session", "tk_ui_startup")

        while not self.stop_event_general_core.is_set():
            try:
                # Esperar mensaje de alguna interfaz (Tkinter, Web, Voz)
                mensaje_externo = self.cola_mensajes_del_exterior.get(timeout=1.0) # Timeout para chequear stop_event
                
                if mensaje_externo is None: # Señal de parada explícita
                    self.logger.info("Señal de parada (None) recibida en cola de Core. Terminando bucle.")
                    break
                
                tipo_msg = mensaje_externo.get("tipo")
                contenido_msg = mensaje_externo.get("contenido")
                id_sesion_msg = mensaje_externo.get("id_sesion", "sesion_desconocida")
                origen_msg = mensaje_externo.get("origen", "fuente_desconocida")
                
                self.logger.info(f"Core recibió: Tipo='{tipo_msg}', Origen='{origen_msg}', Sesion='{id_sesion_msg}', Cont='{str(contenido_msg)[:60]}...'")

                # Lógica principal de procesamiento
                if tipo_msg == "texto_usuario" and isinstance(contenido_msg, str):
                    self._procesar_texto_entrada_principal(contenido_msg, id_sesion_msg, origen_msg)
                elif tipo_msg == "comando_voz_transcrito" and isinstance(contenido_msg, str):
                    # Similar a texto, pero podría tener metadatos adicionales del STT si los pasas
                    self.logger.info(f"Procesando texto transcrito de voz: {contenido_msg}")
                    self._procesar_texto_entrada_principal(contenido_msg, id_sesion_msg, f"{origen_msg}_transcrito")
                elif tipo_msg == "peticion_stt_start": # Ejemplo comando para activar escucha
                    if self.modulos.get('reconocimiento_vocal_base') and self.modulos['reconocimiento_vocal_base'].is_available:
                        self.logger.info("Iniciando escucha STT bajo demanda...")
                        # Aquí llamarías a la escucha en un hilo y el resultado lo pondrías de nuevo en la cola
                        # self.iniciar_escucha_stt_en_hilo(id_sesion_msg, origen_msg) # Método a crear
                        texto_escuchado_demo = self.modulos['reconocimiento_vocal_base'].escuchar_y_transcribir() # BLOQUEANTE - NO IDEAL PARA BUCLE CORE
                        if not any(err_str in texto_escuchado_demo for err_str in ["[Error", "[Silencio", "[STT No", "[Audio No"]):
                            self.recibir_input_para_core(texto_escuchado_demo, tipo="comando_voz_transcrito", origen=origen_msg, id_sesion=id_sesion_msg)
                        else: # Informar error STT
                            self.enviar_respuesta_a_interfaz(f"STT: {texto_escuchado_demo}", "error", id_sesion_msg, origen_msg)
                    else:
                         self.enviar_respuesta_a_interfaz("STT no disponible o no configurado.", "error", id_sesion_msg, origen_msg)

                # ... otros tipos de mensajes: comandos de sistema, datos de sensores, etc. ...

                self.cola_mensajes_del_exterior.task_done() # Marcar tarea como completada
                
            except queue.Empty: # Timeout en la cola, normal, permite chequear stop_event.
                # Aquí podrías hacer tareas de fondo si no hay mensajes, ej. chequeo de módulos.
                # if self.modulos.get('conexion_espiritual'): self.modulos['conexion_espiritual'].verificar_conexion()
                continue 
            except Exception as e_bucle:
                self.logger.critical(f"ERROR INESPERADO en bucle principal del Core: {e_bucle}", exc_info=True)
                self.registrar_evento_core("Error_Critico_BucleCore", {"error": str(e_bucle), "traceback": traceback.format_exc()}, fuente="CoreSystemInternal")
                # Notificar error a la UI activa (si hay alguna manera)
                # self.enviar_respuesta_a_interfaz("Error crítico en el núcleo de Inanna Sophia. Puede requerir reinicio.", "error", "todas_las_sesiones_activas", "CorePanic")
                time.sleep(2) # Breve pausa para evitar bucles de error rápidos
        
        self.logger.info(f"Bucle Principal del Core UNIFICADO terminado. Hilo: {threading.current_thread().name}.")


    def enviar_respuesta_a_interfaz(self, mensaje, tag, id_sesion, origen_del_request="desconocido"):
        # Priorizar Tkinter si está activa y el origen es ella o es una emisión general
        if self.ui_tk_instance and self.root_tk_instance and self.root_tk_instance.winfo_exists() and \
           (origen_del_request.startswith("tk_ui") or id_sesion == "local_tk_session" or id_sesion == "all_active_sessions_placeholder"):
            self.logger.debug(f"Enviando a UI Tkinter (sesión {id_sesion}): '{str(mensaje)[:70].replace(os.linesep,' ')}...' Tag: {tag}")
            self.ui_tk_instance.poner_respuesta_en_cola_ui({"mensaje": mensaje, "tag": tag})
        
        # Lógica para enviar a Web SocketIO si el origen fue ese o es broadcast
        elif FLASK_SOCKETIO_AVAILABLE and 'flask_socketio_server_ref_unified' in globals() and flask_socketio_server_ref_unified and \
             (origen_del_request == "web_socketio" or id_sesion == "all_active_sessions_placeholder"):
            
            target_room = id_sesion if id_sesion != "all_active_sessions_placeholder" else None # None emite a todos los conectados
            self.logger.debug(f"Emitiendo a Socket.IO (target: {target_room or 'broadcast'}): '{str(mensaje)[:70].replace(os.linesep,' ')}...' Tag: {tag}")
            try:
                # Asegurar que el emit se hace en un contexto donde socketio puede operar
                # A veces emitir desde un hilo que no es el del worker de socketio puede dar problemas.
                # Usar `socketio.emit` directamente si se está fuera del contexto de request.
                if target_room:
                     flask_socketio_server_ref_unified.emit('inanna_response_stream', {'text': mensaje, 'tag': tag, 'final': True}, room=target_room)
                else: # Broadcast (cuidado con esto, puede ser mucho)
                     flask_socketio_server_ref_unified.emit('inanna_response_stream', {'text': mensaje, 'tag': tag, 'final': True})
            except Exception as e_socket_emit:
                self.logger.error(f"Error emitiendo mensaje vía Socket.IO: {e_socket_emit}", exc_info=True)
        else: # Fallback general si no hay UI o el origen es desconocido y no hay broadcast
            self.logger.info(f"RESPUESTA CORE (Dest: {origen_del_request}, Sesión: {id_sesion}, Tag: {tag}): {mensaje}")


    def anadir_a_historial_core(self, hablante, texto, **kwargs_adicionales): # Renombrado
        with self.lock_estado_global_core:
            entrada_historial = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "hablante": hablante, # "usuario" o "inanna_sophia"
                "texto": texto,
                **kwargs_adicionales # Ej: emocion_ia, emocion_usr, sentimiento_usr
            }
            self.historial_conversacion_core.append(entrada_historial)
            
            # Mantener tamaño máximo del historial
            if len(self.historial_conversacion_core) > self.max_hist_turns_core * 2: # *2 porque usuario + IA = 1 turno
                self.historial_conversacion_core = self.historial_conversacion_core[-(self.max_hist_turns_core * 2):]
        self.logger.debug(f"Historial Core: Añadido turno de '{hablante}'. Total en memoria: {len(self.historial_conversacion_core)}")


    def iniciar_aplicacion_principal(self): # Renombrado de iniciar_app
        self.logger.info("Iniciando aplicación principal Inanna Sophia Unificada...")
        self.stop_event_general_core.clear() # Asegurar que no esté seteado para permitir inicio

        # 1. Iniciar el hilo del bucle principal del Core
        if self.hilo_bucle_core is None or not self.hilo_bucle_core.is_alive():
            self.hilo_bucle_core = threading.Thread(target=self._bucle_principal_core_interno, name="InannaSophiaCoreLoop", daemon=True)
            self.hilo_bucle_core.start()
            self.logger.info("Hilo del bucle principal de InannaCore iniciado.")
        else:
            self.logger.warning("Intento de iniciar el hilo del Core, pero ya está corriendo.")

        # 2. Decidir qué interfaz iniciar (Tkinter en hilo principal o Web Backend)
        cfg_general = self._config_sections.get('General', {})
        usar_tkinter_gui = cfg_general.get('use_gui_tk', 'True').lower() in ['true', '1', 'yes', 'on']
        # Ojo: si use_gui_tk es False, significa que el MAIN de este script NO debería
        # bloquear con Tkinter, sino que debería iniciar el servidor Flask y este main terminaría
        # y Flask correría en su propio proceso/hilos (si se llamó con socketio.run)

        if usar_tkinter_gui:
            self.logger.info("Modo de Interfaz: GUI Tkinter (Correrá en hilo principal).")
            if self.root_tk_instance is None: # Crear ventana Tkinter si no existe
                 self.root_tk_instance = tk.Tk()
            
            # Configuración de la GUI Tkinter (usa sección [InterfazTkinter])
            config_para_tkinter_ui = self._config_sections.get('InterfazTkinter', {})
            
            self.ui_tk_instance = InterfazUsuario(
                self.root_tk_instance,
                procesar_input_callback=lambda texto_usr: self.recibir_input_para_core(texto_usr, tipo="texto_usuario", origen="tk_ui_input", id_sesion="local_tk_session"),
                detener_app_callback=self.detener_aplicacion_principal, # Este método de InannaCore
                config_gui=config_para_tkinter_ui
            )
            # El saludo inicial se envía desde _bucle_principal_core_interno() para asegurar que el core está más listo
            self.logger.info("Lanzando bucle principal de Tkinter (esto bloqueará el hilo __main__)...")
            self.ui_tk_instance.run_ui() # Bloqueante
            # Cuando la UI Tkinter se cierra, el código continúa aquí...
            self.logger.info("Bucle principal de Tkinter ha terminado. Iniciando secuencia de apagado si no se hizo ya.")
            self.detener_aplicacion_principal() # Asegurar que todo se detenga si la UI se cerró
        
        elif FLASK_SOCKETIO_AVAILABLE and 'flask_socketio_server_ref_unified' in globals() and flask_socketio_server_ref_unified:
            # Para esta opción, este script main.py debería terminar, y Flask/SocketIO correría
            # por separado, usualmente iniciado por un script diferente o un comando como `flask run`.
            # Lo que inanna_v7_main hacía era socketio.run(app,...), que bloqueaba.
            # Para una estructura donde ESTE main sigue vivo para el core, y Flask está en otro proceso
            # o bien Flask debe correr en un hilo, lo cual no es ideal para producción con Werkzeug.
            # La forma más simple aquí es que, si es web, ESTE script solo instancie el core
            # y el servidor web se ejecute por separado llamando a las funciones del core.
            # Si intentamos correr Flask DESDE aquí EN UN HILO, no es lo ideal para la robustez de Flask.
            # Para simplificar, la lógica de Flask se correrá desde aquí.
            
            self.logger.info("Modo de Interfaz: Web Backend (Flask + SocketIO). Iniciando servidor...")
            web_cfg = self._config_sections.get('WebServer', {})
            host_web = web_cfg.get('host', '127.0.0.1')
            port_web = web_cfg.getint('port', 5000)
            debug_web = web_cfg.getboolean('debug', False)
            self.logger.info(f"Iniciando servidor Flask/SocketIO en http://{host_web}:{port_web} (Debug: {debug_web})")
            try:
                # La referencia a inanna_core_global_instance se usa en las rutas Flask/SocketIO
                # Es importante que async_mode para SocketIO sea compatible con Flask. 'threading' es común.
                # Para producción real, se usaría un servidor WSGI como Gunicorn + Eventlet/Gevent para SocketIO.
                flask_socketio_server_ref_unified.run(
                    flask_app_unified, 
                    host=host_web, 
                    port=port_web, 
                    debug=debug_web, 
                    use_reloader=False, # ¡Importante False con hilos para evitar re-inicializaciones!
                    allow_unsafe_werkzeug=True if debug_web else False # Necesario para debug en algunos Werkzeug>2.3
                )
                # Esto es bloqueante hasta que el servidor Flask se detenga (Ctrl+C)
            except Exception as e_flask_run:
                self.logger.critical(f"ERROR FATAL al intentar iniciar servidor web Flask/SocketIO: {e_flask_run}", exc_info=True)
                self.detener_aplicacion_principal()
            self.logger.info("Servidor Flask/SocketIO detenido. Iniciando secuencia de apagado si no se hizo ya.")
            self.detener_aplicacion_principal()

        else: # Ni Tkinter ni Web
            self.logger.error("No se ha configurado una interfaz de usuario principal (ni Tkinter ni Web). Inanna Sophia no puede operar interactivamente.")
            self.logger.info("   Revisa 'use_gui_tk' en [General] o asegúrate que Flask/SocketIO estén instalados si es modo web.")
            self.detener_aplicacion_principal() # Detener todo si no hay UI

    def detener_aplicacion_principal(self): # Renombrado
        if hasattr(self, '_shutdown_initiated_flag_core') and self._shutdown_initiated_flag_core:
            self.logger.info("Secuencia de apagado ya en progreso o completada.")
            return
        
        self._shutdown_initiated_flag_core = True # Marcar que el apagado ha comenzado
        self.logger.info(">>> INICIANDO SECUENCIA DE APAGADO DEFINITIVA DE INANNA SOPHIA <<<")
        
        self.ia_activa_evento.clear() # Desactivar procesamiento de nuevas entradas
        self.stop_event_general_core.set() # Señal para que todos los hilos del Core terminen

        # Detener Actualizador Automático
        actualizador = self.modulos.get('actualizaciones_automaticas_sched')
        if actualizador and hasattr(actualizador, 'detener_scheduler'):
            actualizador.detener_scheduler()
        
        # Detener otros módulos que puedan tener hilos o recursos (ej. NeuroModulator, Avatar si fueran reales)
        # if self.modulos.get('neuromodulator') and hasattr(self.modulos['neuromodulator'], 'stop'): self.modulos['neuromodulator'].stop()
        # if self.modulos.get('avatar_renderer') and hasattr(self.modulos['avatar_renderer'], 'stop'): self.modulos['avatar_renderer'].stop()


        # Enviar señal de fin a la cola del Core
        try:
            self.cola_mensajes_del_exterior.put_nowait(None) # Desbloquea el get del bucle del core
        except queue.Full: self.logger.warning("No se pudo encolar señal de parada al Core Loop (cola llena).")
        except Exception as e_q: self.logger.error(f"Error encolando señal None al core: {e_q}")

        # Esperar al hilo del Core
        if self.hilo_bucle_core and self.hilo_bucle_core.is_alive():
            self.logger.info("Esperando finalización del Hilo del Bucle Principal del Core...")
            self.hilo_bucle_core.join(timeout=7.0) # Reducir timeout para pruebas
            if self.hilo_bucle_core.is_alive(): self.logger.warning("El Hilo del Core no terminó en el tiempo esperado.")
        
        # Destruir ventana Tkinter si existe y no fue quien inició el apagado
        # El callback _on_closing_ui de Tkinter también llama a detener_aplicacion_principal.
        # Necesitamos evitar cierres dobles o errores si la ventana ya se destruyó.
        # Una forma simple es chequear si el hilo actual es el MainThread (donde corre Tkinter)
        # Si NO estamos en MainThread y la ventana existe, la destruimos.
        # if threading.current_thread() is not threading.main_thread(): # No es tan simple si Tkinter no está en main
        if self.root_tk_instance and hasattr(self.root_tk_instance, 'winfo_exists') and self.root_tk_instance.winfo_exists():
            self.logger.info("Solicitando cierre de ventana Tkinter desde Core (si sigue existiendo).")
            try:
                self.root_tk_instance.destroy()
            except tk.TclError: # Puede pasar si ya se está destruyendo
                self.logger.debug("TclError al intentar destruir root_tk, probablemente ya en proceso.")
            except Exception as e_tk_destroy:
                self.logger.error(f"Error destruyendo ventana Tkinter: {e_tk_destroy}")

        # Si el servidor Flask/SocketIO está corriendo (lo cual no debería ser si llegamos aquí desde su propio cierre)
        # Este es el punto más complicado para un shutdown programático. Usualmente es Ctrl+C en la consola
        # o una ruta /shutdown en Flask que llame a sys.exit() o a os.kill(os.getpid(), signal.SIGINT).
        # Si InannaCore y Flask están en el mismo proceso, el sys.exit() al final de __main__ lo hará.
        
        self.logger.info(">>> APAGADO UNIFICADO DE INANNA SOPHIA COMPLETADO <<<")
        if LOGGING_CONFIGURED_UNIFIED : logging.shutdown() # Limpiar y cerrar handlers de logging

# --- FIN DE CLASE InannaCore ---


# --- Variables Globales para Web Backend (si se activa) ---
# Necesarias para que las rutas Flask puedan acceder a la instancia del core.
# Esto NO es ideal para una arquitectura de producción robusta (mejor usar app_context de Flask o blueprints),
# pero simplifica mucho este ejemplo unificado.
flask_app_unified = None
flask_socketio_server_ref_unified = None
inanna_core_global_instance_unified = None # Referencia global a la instancia InannaCore

if FLASK_SOCKETIO_AVAILABLE: # Definir app y socketio solo si las librerías están
    flask_app_unified = Flask("InannaSophiaUnified_WebApp")
    # La configuración de secret_key, CORS, etc., se haría con valores del config.ini si se carga antes
    flask_socketio_server_ref_unified = SocketIO(flask_app_unified, async_mode=None, cors_allowed_origins="*") # async_mode=None usa el mejor disponible (threading si no está gevent/eventlet)
else: # Si Flask no está, estas referencias son None.
    print("[ADVERTENCIA UNIFIED MAIN] Flask/SocketIO no cargados, la funcionalidad Web Backend NO estará disponible.")

# --- Rutas Flask y Eventos Socket.IO (Definidos Globalmente) ---
# Estas definiciones solo tendrán efecto si FLASK_SOCKETIO_AVAILABLE es True.
if flask_app_unified and flask_socketio_server_ref_unified:

    @flask_app_unified.route('/')
    def route_index_unified_web():
        main_web_logger = logging.getLogger("InannaSophiaUnified.WebRoutes")
        project_root_for_frontend = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        frontend_path = os.path.join(project_root_for_frontend, 'frontend')
        index_html_path = os.path.join(frontend_path, 'index.html')
        main_web_logger.debug(f"Buscando frontend/index.html en: {index_html_path}")
        
        if os.path.exists(index_html_path):
            # Necesario importar send_from_directory aquí o globalmente si está en try-except
            from flask import send_from_directory as flask_sfd 
            return flask_sfd(frontend_path, 'index.html')
        else:
            main_web_logger.warning("frontend/index.html no encontrado.")
            return jsonify(message="Inanna Sophia Backend (Unificado) Activo. No se encontró 'frontend/index.html'.",
                           status="ready", version="V8-Unified-Conceptual"), 200

    # Ruta para servir archivos estáticos (CSS, JS, imágenes) desde frontend/
    @flask_app_unified.route('/<path:filename>')
    def route_static_files_unified_web(filename):
        project_root_for_frontend = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        frontend_path = os.path.join(project_root_for_frontend, 'frontend')
        from flask import send_from_directory as flask_sfd
        return flask_sfd(frontend_path, filename)

    @flask_socketio_server_ref_unified.on('connect')
    def handle_socket_connect_unified_web():
        socket_conn_logger = logging.getLogger("InannaSophiaUnified.WebSocket")
        sid = request.sid
        ip_addr = request.remote_addr
        socket_conn_logger.info(f"Cliente Conectado (Socket.IO): SID='{sid}', IP='{ip_addr}'")
        join_room(sid)
        if inanna_core_global_instance_unified:
            nombre_saludo = inanna_core_global_instance_unified.nombre_creador
            estado_conn_esp = inanna_core_global_instance_unified.modulos.get('conexion_espiritual').obtener_estado() if inanna_core_global_instance_unified.modulos.get('conexion_espiritual') else "Estado conexión desconocido"
            mensaje_bienvenida_web = f"¡Bienvenido, {nombre_saludo}! Inanna Sophia (Backend Unificado) está {estado_conn_esp} y lista para interactuar vía web."
            # No llamar directamente a inanna_core sino a su método para enviar, que usa la cola
            inanna_core_global_instance_unified.enviar_respuesta_a_interfaz(mensaje_bienvenida_web, "sistema", sid, "web_socketio_connect")
        else:
            emit('inanna_response_stream', {'text': 'Inanna Sophia Core no inicializado globalmente. Conectado al socket.', 'tag':'error', 'final': True}, room=sid)

    @flask_socketio_server_ref_unified.on('disconnect')
    def handle_socket_disconnect_unified_web():
        socket_conn_logger = logging.getLogger("InannaSophiaUnified.WebSocket")
        sid = request.sid
        socket_conn_logger.info(f"Cliente Desconectado (Socket.IO): SID='{sid}'")
        leave_room(sid)
        # Informar al core si es necesario para limpiar sesiones, etc.

    @flask_socketio_server_ref_unified.on('user_message_to_inanna_web') # Nombre evento diferente para no colisionar con otros
    def handle_user_message_socket_unified_web(data_from_client):
        socket_msg_logger = logging.getLogger("InannaSophiaUnified.WebSocketMsg")
        sid = request.sid
        socket_msg_logger.info(f"Mensaje Socket.IO de SID '{sid}': {str(data_from_client)[:100]}")
        
        texto_recibido_cliente = data_from_client.get('text', '')
        tipo_de_mensaje_cliente = data_from_client.get('type', 'texto_usuario')

        if not texto_recibido_cliente and tipo_de_mensaje_cliente == 'texto_usuario':
            emit('inanna_error_stream', {'error': 'Mensaje de texto vacío.'}, room=sid)
            return

        if inanna_core_global_instance_unified:
            # Enviar a la cola de procesamiento del InannaCore
            inanna_core_global_instance_unified.recibir_input_para_core(
                texto_recibido_cliente, 
                tipo=tipo_de_mensaje_cliente, 
                origen="web_socketio", 
                id_sesion=sid
            )
        else:
            socket_msg_logger.error("InannaCore GLOBAL no disponible. No se puede procesar mensaje de Socket.IO.")
            emit('inanna_error_stream', {'error': 'Núcleo de Inanna Sophia no responde.'}, room=sid)

# --- PUNTO DE ENTRADA PRINCIPAL DEL SCRIPT ---
if __name__ == "__main__":
    # 0. Definir rutas importantes (Raíz del proyecto, config.ini)
    # __file__ es el path de este script (src/inanna_sophia_unified_main.py)
    current_script_dir_main = os.path.dirname(os.path.abspath(__file__))
    project_root_dir_main_entry = os.path.abspath(os.path.join(current_script_dir_main, ".."))
    config_ini_path_main_entry = os.path.join(project_root_dir_main_entry, "config.ini")

    # 1. Cargar Configuración y Configurar Logging INMEDIATAMENTE
    main_config_parser = configparser.ConfigParser(interpolation=None, allow_no_value=True)
    if not os.path.exists(config_ini_path_main_entry):
        # Logging aún no está configurado, usar print para este error CRÍTICO inicial.
        print(f"[ERROR FATAL INICIO] Archivo 'config.ini' NO ENCONTRADO en: {config_ini_path_main_entry}")
        print("                   Asegúrate que 'config.ini' esté en la raíz del proyecto, un nivel ARRIBA de 'src/'.")
        print("                   Inanna Sophia no puede iniciar sin configuración.")
        sys.exit(1)
    
    try:
        main_config_parser.read(config_ini_path_main_entry, encoding='utf-8')
        # Añadir el path del config al objeto para que otros módulos (como RegistroEterno) lo puedan usar
        # para resolver rutas relativas a la raíz del proyecto, no a 'src/'.
        main_config_parser.config_filepath_for_log_unified = config_ini_path_main_entry
        
        # Configurar el logging ahora que tenemos el objeto config
        setup_logging_unified_from_config(main_config_parser) # Pasa el objeto config cargado
    except Exception as e_cfg_critical:
        print(f"[ERROR FATAL INICIO] No se pudo leer o procesar 'config.ini': {e_cfg_critical}")
        traceback.print_exc() # Mostrar traceback completo a consola
        sys.exit(1)
    
    # Logger para el bloque __main__ después de la configuración
    launcher_logger_unified = logging.getLogger("InannaSophiaUnified.Launcher")
    launcher_logger_unified.info("==========================================================")
    launcher_logger_unified.info("==  INANNA SOPHIA AI - UNIFIED LAUNCHER - EL PRINCIPAL  ==")
    launcher_logger_unified.info(f"==  Configuración cargada desde: {config_ini_path_main_entry}")
    launcher_logger_unified.info("==========================================================")

    # Verificaciones de dependencias post-logging
    # (Las alertas iniciales con print() ya ocurrieron, aquí solo se loguea formalmente)
    if not NLTK_VADER_AVAILABLE_UNIFIED: launcher_logger_unified.warning("Módulo NLTK/VADER para sentimientos no cargó correctamente.")
    if not SPEECH_REC_AVAILABLE_UNIFIED: launcher_logger_unified.warning("Módulo SpeechRecognition/PyAudio no disponible.")
    if not PYTTSX3_AVAILABLE_UNIFIED: launcher_logger_unified.warning("Módulo pyttsx3 (TTS) no disponible.")
    if not TORCH_AVAILABLE_UNIFIED: launcher_logger_unified.warning("PyTorch no disponible (necesario para Transformers/Whisper).")
    if not NUMPY_AVAILABLE_UNIFIED: launcher_logger_unified.warning("NumPy no disponible (necesario para varias bibliotecas).")

    use_gui_tk_from_config = main_config_parser.getboolean('General', 'use_gui_tk', fallback=True)
    if not use_gui_tk_from_config and not FLASK_SOCKETIO_AVAILABLE:
        launcher_logger_unified.critical("Modo Web Backend seleccionado en config.ini pero Flask/SocketIO no están instalados. ¡No hay interfaz!")
        sys.exit(1)

    # Instancia global del Core (accesible para Flask/SocketIO si se usa)
    # inanna_core_global_instance_unified ya está definida globalmente
    
    codigo_salida_final = 0
    try:
        launcher_logger_unified.info("Creando instancia de InannaCore Unificado...")
        inanna_core_global_instance_unified = InannaCore(config_obj_loaded=main_config_parser)
        launcher_logger_unified.info("Iniciando aplicación principal Inanna Sophia...")
        
        # El método iniciar_aplicacion_principal ahora es bloqueante (si es Tkinter) o inicia el server
        inanna_core_global_instance_unified.iniciar_aplicacion_principal() 
        
        # Si iniciar_aplicacion_principal usara un modo no bloqueante para el core (ej. todo web y este script solo configura)
        # se necesitaría un bucle aquí o que Flask lo maneje. Pero la implementación actual de
        # Tkinter o Flask.run() es bloqueante en el hilo que los llama.
        # Si Tkinter se cierra o Flask (con SocketIO) se detiene (Ctrl+C), el código sigue aquí.
        launcher_logger_unified.info("Aplicación Inanna Sophia (hilo principal de UI/Web) ha finalizado su ejecución o fue detenida.")

    except KeyboardInterrupt:
        launcher_logger_unified.info("KeyboardInterrupt detectada en el Launcher. Iniciando apagado forzado...")
        codigo_salida_final = 0 # Salida normal por interrupción del usuario
    except SystemExit as se:
        launcher_logger_unified.info(f"SystemExit capturada en Launcher con código: {se.code}. Asumiendo salida controlada.")
        codigo_salida_final = se.code if isinstance(se.code, int) else 0
    except ImportError as e_imp_runtime:
        launcher_logger_unified.critical(f"Error de IMPORTACIÓN EN TIEMPO DE EJECUCIÓN (puede ser dependencia faltante en un módulo): {e_imp_runtime}", exc_info=True)
        launcher_logger_unified.critical("  Revisa los mensajes '[ALERTA INICIAL]' y tu 'requirements.txt'.")
        codigo_salida_final = 1
    except Exception as e_fatal_unified:
        launcher_logger_unified.critical(f"Excepción FATAL NO CAPTURADA en el nivel más alto de Inanna Sophia: {e_fatal_unified}", exc_info=True)
        codigo_salida_final = 1
    finally:
        launcher_logger_unified.info("Bloque 'finally' del Launcher alcanzado. Asegurando detención del Core...")
        if inanna_core_global_instance_unified and hasattr(inanna_core_global_instance_unified, 'detener_aplicacion_principal'):
            # Llamar de nuevo por si el cierre vino de una excepción y no de un cierre ordenado
            inanna_core_global_instance_unified.detener_aplicacion_principal()
        else:
            launcher_logger_unified.info("No hay instancia de InannaCore válida para detener explícitamente o ya se llamó a detener.")
        
        launcher_logger_unified.info(f"Proceso Inanna Sophia Unificada finalizando con código de salida: {codigo_salida_final}")
        # El logging.shutdown() ya está en detener_aplicacion_principal
        sys.exit(codigo_salida_final)