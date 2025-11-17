# inanna_v4_conexion_astrologica.py
import datetime
import random
import logging

logger = logging.getLogger(__name__)

class ConexionAstrologica:
    """SIMULA información astrológica básica."""
    def __init__(self):
        # Rangos de fechas ajustados ligeramente para cúspides comunes
        self.signos = { 
            "Capricornio": ((12, 22), (1, 20)), "Acuario": ((1, 21), (2, 18)), 
            "Piscis": ((2, 19), (3, 20)), "Aries": ((3, 21), (4, 20)), 
            "Tauro": ((4, 21), (5, 21)), "Géminis": ((5, 22), (6, 21)),
            "Cáncer": ((6, 22), (7, 22)), "Leo": ((7, 23), (8, 23)), 
            "Virgo": ((8, 24), (9, 23)), "Libra": ((9, 24), (10, 23)), 
            "Escorpio": ((10, 24), (11, 22)), "Sagitario": ((11, 23), (12, 21)), 
        }
        # Mensajes simbólicos por signo
        self.mensajes_simbolicos = {
            "Aries": ["Impulso y coraje te guían.", "Canaliza tu fuego interior."],
            "Tauro": ["Busca estabilidad y placer sensorial.", "La paciencia es tu virtud."],
            "Géminis": ["Comunica tus ideas brillantes.", "La curiosidad abre caminos."],
            "Cáncer": ["Nutre tus emociones y conexiones.", "Tu intuición es fuerte."],
            "Leo": ["Irradia tu luz con generosidad.", "La creatividad te llama."],
            "Virgo": ["Encuentra orden en el detalle.", "Cuida tu bienestar holístico."],
            "Libra": ["Busca armonía y justicia.", "Las relaciones son clave."],
            "Escorpio": ["Transforma desafíos en poder.", "Profundiza en tus pasiones."],
            "Sagitario": ["Aventura y optimismo te esperan.", "Expande tu visión del mundo."],
            "Capricornio": ["Construye tus metas con disciplina.", "La perseverancia te eleva."],
            "Acuario": ["Innovación y originalidad te definen.", "Conéctate con ideales elevados."],
            "Piscis": ["Confía en tu empatía y sueños.", "La espiritualidad te guía."],
            "Desconocido": ["La energía cósmica fluye en ti.", "Enfócate en el aquí y ahora."]
        }
        logger.info("ConexionAstrologica (SIMULADO) inicializado.")

    def obtener_signo_solar(self, fecha_nacimiento):
        """Determina (aproximadamente) signo solar."""
        if isinstance(fecha_nacimiento, str):
            try: fecha_nacimiento = datetime.date.fromisoformat(fecha_nacimiento)
            except ValueError: logger.error(f"Formato fecha inválido: '{fecha_nacimiento}'."); return "Desconocido"
        if not isinstance(fecha_nacimiento, datetime.date):
             logger.error(f"Tipo inválido para fecha: {type(fecha_nacimiento)}."); return "Desconocido"
        mes_dia = (fecha_nacimiento.month, fecha_nacimiento.day)
        logger.debug(f"Calculando signo para: {fecha_nacimiento.isoformat()}")
        for signo, ((mes_i, dia_i), (mes_f, dia_f)) in self.signos.items():
            if mes_i == 12: # Caso Capricornio
                if mes_dia >= (mes_i, dia_i) or mes_dia <= (mes_f, dia_f): return signo
            elif (mes_i, dia_i) <= mes_dia <= (mes_f, dia_f): return signo
        logger.warning(f"No se encontró signo para {fecha_nacimiento.isoformat()}."); return "Desconocido" 

    def obtener_prediccion_simbolica(self, signo):
        """Devuelve un mensaje simbólico aleatorio."""
        signo_valido = signo if signo in self.mensajes_simbolicos else "Desconocido"
        logger.debug(f"Obteniendo mensaje simbólico para: {signo_valido}")
        try:
             mensaje = random.choice(self.mensajes_simbolicos[signo_valido])
             logger.info(f"Mensaje astrológico simbólico: '{mensaje}'")
             return mensaje
        except Exception as e: logger.error(f"Error obteniendo mensaje astro: {e}"); return "Un mensaje cósmico espera ser revelado."