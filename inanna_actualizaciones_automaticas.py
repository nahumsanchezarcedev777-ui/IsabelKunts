# inanna_v4_actualizaciones_automaticas.py
import schedule
import time
import threading
import logging
import random
import requests 
import json

logger = logging.getLogger(__name__)

class ActualizacionesAutomaticas:
    """Maneja tareas programadas como buscar datos externos o chequeos internos."""
    def __init__(self, inanna_core_ref=None):
        self.planificador = schedule; self.hilo_planificador = None
        self.detener_planificador = threading.Event(); self.inanna_core = inanna_core_ref
        logger.info("ActualizacionesAutomaticas inicializado.")

    def _tarea_buscar_dato_externo(self):
        """Intenta obtener un hecho curioso de Numbers API."""
        logger.info("==== TAREA: Buscando dato externo (NumbersAPI) ====")
        fuente = "Numbers API"; url = "http://numbersapi.com/random/date?json" 
        try:
            logger.debug(f"Contactando {fuente}: {url}...")
            response = requests.get(url, timeout=8) # Timeout más corto
            response.raise_for_status() 
            data = response.json(); dato = data.get('text') 
            if dato:
                info = f"[{data.get('type','Trivia')}] {dato}"
                logger.info(f"Dato externo obtenido: {info}")
                if self.inanna_core and hasattr(self.inanna_core, 'registrar_dato_actualizado'):
                    self.inanna_core.registrar_dato_actualizado(fuente, info) # Pasar dato al core
            else: logger.warning(f"Respuesta {fuente} sin 'text'. Data: {data}")
        except requests.exceptions.Timeout: logger.warning(f"Timeout contactando {fuente}.")
        except requests.exceptions.RequestException as e: logger.error(f"Error red {fuente}: {e}")
        except json.JSONDecodeError as e: logger.error(f"Error JSON {fuente}: {e}")
        except Exception as e: logger.error(f"Error inesperado buscando dato: {e}", exc_info=True)
        logger.info("==== TAREA: Búsqueda dato externo finalizada ====")

    def _tarea_chequeo_interno(self):
        """Realiza chequeos internos periódicos."""
        logger.info("==== TAREA: Chequeo interno bienestar ====")
        if self.inanna_core:
             try:
                 if hasattr(self.inanna_core, 'conexion_espiritual'): self.inanna_core.conexion_espiritual.verificar_conexion(10) # Intervalo corto forzado
                 if hasattr(self.inanna_core, 'proteccion_espiritual'): self.inanna_core.proteccion_espiritual.chequear_integridad(forzar=True)
             except Exception as e: logger.error(f"Error durante chequeo interno: {e}")
        logger.info("==== TAREA: Chequeo interno finalizado ====")

    def configurar_tareas(self, frec_conocimiento_h=6, frec_bienestar_h=2, hora_chequeo=""):
        """Configura tareas usando parámetros."""
        logger.info(f"Configurando tareas: Conocimiento cada {frec_conocimiento_h}h, Bienestar cada {frec_bienestar_h}h (en {hora_chequeo or 'punto'}).")
        try:
            schedule.clear() # Limpiar tareas anteriores por si se reconfigura
            if frec_conocimiento_h > 0:
                schedule.every(frec_conocimiento_h).hours.do(self._tarea_buscar_dato_externo).tag("dato_externo")
            if frec_bienestar_h > 0:
                 if hora_chequeo and ":" in hora_chequeo: # Si se especifica hora (ej. ":15")
                      schedule.every(frec_bienestar_h).hours.at(hora_chequeo).do(self._tarea_chequeo_interno).tag("chequeo_interno")
                 else: # Ejecutar cada X horas en punto
                     schedule.every(frec_bienestar_h).hours.do(self._tarea_chequeo_interno).tag("chequeo_interno")
            logger.info(f"Tareas configuradas: {schedule.get_jobs()}")
        except Exception as e: logger.error(f"Error configurando schedule: {e}", exc_info=True)

    def _ejecutar_planificador(self):
        """Bucle que ejecuta tareas pendientes."""
        logger.info("Hilo Planificador iniciado (T:%s).", threading.current_thread().name)
        while not self.detener_planificador.is_set():
            try:
                 n = schedule.idle_seconds() # Tiempo hasta la próxima tarea
                 if n is None: # No hay tareas programadas
                      self.detener_planificador.wait(300) # Esperar 5 min
                 elif n > 0:
                      # Esperar hasta la próxima tarea o 60s max (para responder a detener)
                      self.detener_planificador.wait(min(n, 60)) 
                 schedule.run_pending() # Ejecutar tareas si es hora
            except Exception as e: 
                 logger.error(f"Error bucle planificador: {e}", exc_info=True)
                 self.detener_planificador.wait(60) # Esperar si hay error
        logger.info("Hilo Planificador detenido.")

    def iniciar(self):
        """Inicia el planificador si no está activo."""
        if self.hilo_planificador and self.hilo_planificador.is_alive(): return
        # Leer configuración de frecuencias desde InannaCore si existe
        frec_c = 6; frec_b = 2; hora_b = ""
        if self.inanna_core and hasattr(self.inanna_core, 'config'):
             try:
                  frec_c = self.inanna_core.config.getint('Actualizaciones','frecuencia_conocimiento_h', fallback=6)
                  frec_b = self.inanna_core.config.getint('Actualizaciones','frecuencia_bienestar_h', fallback=2)
                  hora_b = self.inanna_core.config.get('Actualizaciones','hora_chequeo_bienestar', fallback="")
             except (configparser.Error, ValueError, AttributeError):
                  logger.warning("No se pudo leer config para frecuencias de Schedule. Usando defaults.")
                  
        self.configurar_tareas(frec_c, frec_b, hora_b)
        if not schedule.get_jobs(): logger.warning("No hay tareas en Schedule."); # Considera no iniciar el hilo
        self.detener_planificador.clear()
        self.hilo_planificador = threading.Thread(target=self._ejecutar_planificador, daemon=True, name="SchedulerThread")
        self.hilo_planificador.start()
        logger.info("Servicio Actualizaciones Automáticas iniciado.")

    def detener(self):
        """Detiene el hilo planificador."""
        if not self.hilo_planificador or not self.hilo_planificador.is_alive(): logger.debug("Planificador no activo."); return
        logger.info("Deteniendo planificador...")
        self.detener_planificador.set()
        self.hilo_planificador.join(timeout=3.0) 
        if self.hilo_planificador.is_alive(): logger.warning("Hilo planificador no se detuvo.")
        else: logger.info("Planificador detenido.")
        self.hilo_planificador = None

    def ver_tareas_programadas(self): return schedule.get_jobs()