# inanna_v4_analizador_nlp_avanzado.py
import logging
try:
    from transformers import pipeline
    # Modelo por defecto (puedes cambiarlo en config.ini si modificas InannaMain)
    MODELO_SENTIMIENTO_DEFAULT = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
except ImportError:
    logging.getLogger(__name__).critical("Transformers/Torch/TF/SentencePiece NO INSTALADO. NLP Avanzado DESHABILITADO.")
    pipeline = None

logger = logging.getLogger(__name__)
MODELO_SENTIMIENTO_DEFAULT = "cardiffnlp/MODELO_SENTIMIENTO_DEFAULT"
class AnalizadorNLPAvanzado:
    """Análisis NLP con Hugging Face Transformers."""
    def __init__(self, model_name=MODELO_SENTIMIENTO_DEFAULT, device_id=-1): # Aceptar parámetros
        self.clasificador_sentimiento = None
        self.is_available = False
        self.model_name = model_name
        self.device_id = device_id

        if pipeline:
            try:
                logger.info(f"Cargando pipeline sentimiento: '{self.model_name}' en device:{self.device_id}...")
                # Añadir manejo específico si el modelo no existe online o localmente
                self.clasificador_sentimiento = pipeline("sentiment-analysis", model=self.model_name, device=self.device_id) 
                logger.info("Pipeline sentimiento cargado.")
                self.is_available = True
            except Exception as e: # Captura errores de carga (modelo no encontrado, memoria, etc.)
                logger.error(f"Error CRÍTICO cargando modelo '{self.model_name}': {e}", exc_info=True)
                logger.error("NLP Avanzado estará DESHABILITADO.")
        else:
            logger.error("NLP Avanzado no inicializado (falta lib Transformers).")

    def analizar_sentimiento_avanzado(self, texto):
        """Analiza sentimiento con modelo Transformer."""
        default = {"label": "Neutral", "score": 0.0}
        if not self.is_available or not isinstance(texto, str) or not texto.strip():
            if not self.is_available: logger.warning("Análisis sentimiento Transformer no disponible.")
            return default
        try:
            # Limitar longitud para evitar errores en modelos con límite de secuencia
            max_len = 512 
            texto_corto = texto[:max_len]
            if len(texto) > max_len: logger.warning(f"Texto truncado a {max_len} caracteres para análisis NLP.")
                
            logger.debug(f"Analizando (Transformer): '{texto_corto[:60]}...'")
            resultado = self.clasificador_sentimiento(texto_corto) 
            
            if resultado and isinstance(resultado, list):
                 res = resultado[0] 
                 label_raw = res.get("label", "Unknown")
                 score = res.get("score", 0.0)
                 # Mapeo robusto para diferentes posibles salidas de modelos
                 label_map = {"Label_0": "Negative", "Label_1": "Neutral", "Label_2": "Positive", 
                              "0":"Negative", "1":"Neutral", "2":"Positive", "3": "Positive", "4":"Positive", # Para modelos 0-4 estrellas
                              "negative": "Negative", "neutral": "Neutral", "positive": "Positive",
                              "NEG":"Negative", "NEU":"Neutral", "POS":"Positive"}
                 mapped_label = label_map.get(str(label_raw).lower(), "Neutral") # Mapeo a str y lower para flexibilidad
                 
                 logger.info(f"Sentimiento (Transformer): Label={mapped_label} (Raw={label_raw}), Score={score:.4f}")
                 return {"label": mapped_label, "score": score}
            else: logger.warning(f"Resultado inesperado pipeline: {resultado}"); return default
        except Exception as e: logger.error(f"Error análisis sentimiento Transformer: {e}", exc_info=True); return default

    def obtener_sentimiento_simple(self, texto):
        """Devuelve etiqueta simple ('Positive', 'Negative', 'Neutral')."""
        return self.analizar_sentimiento_avanzado(texto).get("label", "Neutral")