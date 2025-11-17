# inanna_v4_knowledge_base_manager.py
# Gestiona KB cargada desde archivo JSON.
import json
import logging
import os
import threading
import datetime 

logger = logging.getLogger(__name__)

class KnowledgeBaseManager:
    """Gestiona la KB cargándola desde un archivo JSON."""
    def __init__(self, filepath="knowledge_base.json"): # Espera ruta completa
        self._lock = threading.Lock()
        self.filepath = filepath # Guardar ruta para mensajes de error
        self._knowledge = {} 
        self._default_response = "Aunque mi conocimiento es vasto, ese tópico específico no está detallado en mi base actual."
        self._is_loaded = False 
        self._load_knowledge_from_file() 
        if self._is_loaded:
            with self._lock: self._knowledge.setdefault("conocimiento_actualizado", []) 
            self._max_datos_actualizados = 30
            logger.info(f"KnowledgeBaseManager OK: KB cargada desde '{os.path.basename(filepath)}'.")
        else: 
            self._knowledge = {"conocimiento_actualizado":[]}; self._max_datos_actualizados = 30
            logger.error(f"KnowledgeBaseManager FALLO CARGA: KB desde '{os.path.basename(filepath)}'.")

    def _load_knowledge_from_file(self):
        """Carga JSON a _knowledge."""
        logger.debug(f"Intentando cargar KB desde: {self.filepath}")
        if not os.path.exists(self.filepath):
            logger.error(f"ARCHIVO KB '{os.path.basename(self.filepath)}' NO ENCONTRADO en {os.path.dirname(self.filepath)}")
            self._knowledge = {"error": f"Archivo KB '{os.path.basename(self.filepath)}' no encontrado."} 
            self._is_loaded = False; return
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f: data = json.load(f)
            with self._lock: self._knowledge = {str(k).lower(): v for k, v in data.items()}
            with self._lock: self._knowledge.setdefault("conocimiento_actualizado", [])
            self._is_loaded = True
            topics_count = len([k for k in self._knowledge if k != "conocimiento_actualizado"])
            logger.info(f"KB cargada OK ({topics_count} tópicos base).")
        except json.JSONDecodeError as e: logger.error(f"Error JSON en '{os.path.basename(self.filepath)}': {e}"); self._is_loaded = False
        except IOError as e: logger.error(f"Error I/O leyendo KB '{os.path.basename(self.filepath)}': {e}"); self._is_loaded = False
        except Exception as e: logger.error(f"Error inesperado cargando KB: {e}"); self._is_loaded = False

    def is_loaded(self): return self._is_loaded
    def get_default_response(self): return self._default_response

    def query(self, topic):
        """Busca tópico en KB."""
        if not self._is_loaded: return self._knowledge.get("error", "KB no disponible.")
        if not topic or not isinstance(topic, str): return "Indica un tópico válido."
        topic_lower = topic.lower().strip("¿?¡!., ")
        if not topic_lower: return "Tópico vacío."
        logger.debug(f"KB Query: Buscando '{topic_lower}'")
        with self._lock: 
            if topic_lower in self._knowledge:
                 logger.debug(f"KB Hit (Exacto): '{topic_lower}'.")
                 return self._format_response(self._knowledge[topic_lower])
            if topic_lower in ["actualización", "novedades", "noticias", "dato nuevo", "hecho curioso", "última info"]:
                 lista = self._knowledge.get("conocimiento_actualizado", [])
                 if lista: last = lista[-1]; return f"Mi última info de {last.get('fuente','?')}: \"{last.get('dato','...')}\""
                 else: return "No tengo actualizaciones recientes."
            # Búsqueda parcial más restrictiva
            for key, value in self._knowledge.items():
                 if key == "conocimiento_actualizado": continue
                 # Buscar palabra completa o inicio/fin
                 if f" {topic_lower} " in f" {key} " or key.startswith(topic_lower) or key.endswith(topic_lower):
                      if len(topic_lower) > 2: 
                           logger.debug(f"KB Hit (Parcial): '{topic_lower}' en '{key}'.")
                           return self._format_response(value)
        logger.debug(f"KB Miss: '{topic_lower}'.")
        return self._default_response
            
    def _format_response(self, data):
         """Formatea datos complejos (dict/list) para chat."""
         if isinstance(data, dict): 
              # Formato mejorado para diccionarios
              lines = []
              for k, v in data.items():
                   # Si el valor es una lista, unirla; si es otro dict, indicar "[detalles]"; si no, mostrar valor
                   v_str = ""
                   if isinstance(v, list): v_str = ", ".join(map(str, v))
                   elif isinstance(v, dict): v_str = "[Más detalles disponibles]"
                   else: v_str = str(v)
                   lines.append(f"- {k.replace('_',' ').capitalize()}: {v_str}")
              return "\n".join(lines) if lines else "[Vacío]"
         elif isinstance(data, list): 
              if len(data) > 0 and isinstance(data[0], dict) and 'timestamp_utc' in data[0]: # Lista de actualizaciones
                  return f"Última Actualización: {self._format_response(data[-1])}" # Mostrar solo la última
              else: # Otra lista
                  return "\n * ".join(map(str, data)) if data else "[Lista Vacía]"
         else: return str(data) 

    def add_knowledge(self, source, data, timestamp_utc_iso=None):
        """Añade dato a la lista 'conocimiento_actualizado' EN MEMORIA."""
        if not self._is_loaded: logger.error("KB no cargada, no se puede añadir."); return False
        if not source or not data: logger.warning("Intento add_knowledge vacío."); return False
        if timestamp_utc_iso is None: timestamp_utc_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        nuevo = {"timestamp_utc": timestamp_utc_iso, "fuente": source, "dato": data}
        with self._lock:
            logger.info(f"KB Add (Memoria): Dato de '{source}'.")
            lista = self._knowledge.setdefault("conocimiento_actualizado", []) 
            lista.append(nuevo)
            if len(lista) > self._max_datos_actualizados:
                 self._knowledge["conocimiento_actualizado"] = lista[-self._max_datos_actualizados:]
            # Falta save_to_file() para persistencia real
        return True

    def get_all_base_topics(self):
        """Devuelve lista de tópicos base conocidos."""
        if not self._is_loaded: return []
        with self._lock:
             return sorted([k for k in self._knowledge.keys() if k not in ["conocimiento_actualizado", "error"]])

    # def save_knowledge_to_file(self): # Futuro: Guardar KB modificada al JSON
    #    pass 