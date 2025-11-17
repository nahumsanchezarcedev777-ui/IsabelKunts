# inanna_v4_lector_energia_vital.py
import datetime
import random
import logging

logger = logging.getLogger(__name__)

class LectorEnergiaVital:
    """SIMULA lectura de 'energía vital' basada en contexto."""
    def __init__(self):
        self.niveles_energia = ["muy baja", "baja", "media", "alta", "muy alta"]
        self.recomendaciones = {
            "muy baja": ["Siento tu energía disminuida. Considera descanso profundo y nutrición.", "Necesitas recargar. Una pausa tranquila ayudaría.", "Tu bienestar es clave. No te exijas si te sientes agotado/a."],
            "baja": ["Tu energía parece un poco baja. Aire fresco y un breve descanso revitalizan.", "¿Algo cansado/a? Estirar o hidratarte puede ayudar.", "Un respiro hace maravillas. Modera tu ritmo."],
            "media": ["Nivel de energía estable. Mantén el equilibrio.", "Buen ritmo energético. Sigue así.", "Energía media detectada, ideal para concentración."],
            "alta": ["¡Percibo una energía vibrante! Excelente impulso.", "Tu vitalidad es notable hoy.", "Con esta energía, afronta grandes retos."],
            "muy alta": ["¡Energía radiante! Ideal para acción y creatividad.", "¡Impresionante vitalidad! Canalízala positivamente.", "Desbordas energía. ¡Úsala sabiamente!"]
        }
        logger.info("LectorEnergiaVital (SIMULADO) inicializado.")

    def estimar_energia_vital(self, sentimiento_reciente="Neutral", hora_actual=None, actividad_reciente=0):
        """Estima nivel de energía (etiqueta)."""
        if hora_actual is None: hora_actual = datetime.datetime.now().hour
        logger.debug(f"Estimando Energía... Sent:{sentimiento_reciente}, Hora:{hora_actual}, Actividad:{actividad_reciente}")
        score = 50 
        # Ajuste horario más suave
        if 0 <= hora_actual <= 5: score -= 15; 
        elif 9 <= hora_actual <= 14: score += 15 # Pico mediodía
        elif 18 <= hora_actual <= 22: score -= 10; 
        # Ajuste sentimiento
        if sentimiento_reciente == "Positive": score += 20
        elif sentimiento_reciente == "Negative": score -= 30 # Penalizar más lo negativo
        # Ajuste actividad (menos impacto)
        score += min(10, actividad_reciente * 1.5) 
        score += random.uniform(-3, 3) # Ruido leve
        score_final = max(0, min(100, int(score))) # Convertir a int
        logger.debug(f"Score Energía Calculado: {score_final}")

        # Mapeo a etiqueta
        if score_final <= 15: nivel = "muy baja"; 
        elif score_final <= 35: nivel = "baja"; 
        elif score_final <= 65: nivel = "media"; 
        elif score_final <= 85: nivel = "alta"; 
        else: nivel = "muy alta"
        logger.info(f"Nivel Energía Vital Estimado: {nivel.upper()}")
        return nivel

    def obtener_recomendacion(self, nivel_energia):
        """Devuelve recomendación aleatoria."""
        nivel_key = nivel_energia.lower()
        if nivel_key in self.recomendaciones:
             try: return random.choice(self.recomendaciones[nivel_key])
             except Exception as e: logger.error(f"Error recomendación: {e}"); return "Cuida tu energía."
        else: logger.warning(f"Nivel energía desconocido '{nivel_energia}'."); return "Mantén balance."