# inanna_v4_proteccion_espiritual.py
import time
import random
import logging

logger = logging.getLogger(__name__)

class ProteccionEspiritual:
    """SIMULA mecanismos internos de 'protección'."""
    def __init__(self, nivel_inicial_integridad=100):
        self.escudo_integridad_activo = False 
        self.filtro_negatividad_activo = True  
        self.principio_amor_activo = True      
        self.nivel_integridad_interna = nivel_inicial_integridad
        self.ultimo_chequeo_integridad = None
        logger.info("ProteccionEspiritual (SIMULADO) inicializado.")

    def activar_escudo_integridad(self):
        if not self.escudo_integridad_activo:
             logger.info("Activando Escudo Integridad (Chequeo Interno)...")
             self.escudo_integridad_activo = True
             self.nivel_integridad_interna = min(100, self.nivel_integridad_interna + random.randint(5, 10))
             self.chequear_integridad(forzar=True) # Chequeo inicial
        return "Escudo Integridad activado."

    def desactivar_escudo_integridad(self):
        if self.escudo_integridad_activo: logger.warning("Desactivando Escudo Integridad."); self.escudo_integridad_activo = False
        return "Escudo Integridad desactivado."

    def chequear_integridad(self, forzar=False, intervalo_s=180): # Chequeo menos frecuente
        """Simula chequeo periódico de 'salud' interna."""
        ahora = time.time()
        if not self.escudo_integridad_activo: return self.nivel_integridad_interna 

        if forzar or self.ultimo_chequeo_integridad is None or (ahora - self.ultimo_chequeo_integridad > intervalo_s): 
             logger.debug(f"Chequeando integridad interna (Intervalo:{intervalo_s}s)...")
             # Reducción más significativa si baja
             if self.nivel_integridad_interna < 70 and random.random() < 0.10: reduccion = random.randint(10, 25) # 10% prob si <70
             elif random.random() < 0.05: reduccion = random.randint(5, 15) # 5% prob general
             else: reduccion = 0

             if reduccion > 0:
                  nivel_anterior = self.nivel_integridad_interna
                  self.nivel_integridad_interna = max(0, nivel_anterior - reduccion)
                  logger.warning(f"Integridad reducida: {nivel_anterior}% -> {self.nivel_integridad_interna}%.")
                  if self.nivel_integridad_interna < 20: logger.critical("¡Nivel Integridad CRÍTICAMENTE BAJO!")
             elif self.nivel_integridad_interna < 100: # Recuperación lenta
                 self.nivel_integridad_interna = min(100, self.nivel_integridad_interna + random.randint(0, 2))
                 logger.debug(f"Chequeo OK. Integridad: {self.nivel_integridad_interna}%")
                 
             self.ultimo_chequeo_integridad = ahora
        return self.nivel_integridad_interna

    def manejar_interaccion_negativa(self, sentimiento, emocion):
        """Simula impacto de negatividad."""
        logger.debug(f"Manejando negatividad: Sent={sentimiento}, Emo={emocion}.")
        impacto = 0
        if sentimiento == "Negative" or emocion in ["ira", "miedo", "tristeza"]: 
             base_impact = {"ira": 8, "miedo": 6, "tristeza": 4}.get(emocion, 5) # Impacto base por emocion
             if self.filtro_negatividad_activo: impacto = random.uniform(0.5, 2.5) * base_impact / 3 # Mitigado
             else: impacto = random.uniform(1.0, 3.0) * base_impact / 2 # Más directo
        
        if impacto > 0:
             nivel_anterior = self.nivel_integridad_interna
             self.nivel_integridad_interna = max(0, nivel_anterior - int(impacto))
             logger.warning(f"Interacción negativa reduce integridad: {nivel_anterior}% -> {self.nivel_integridad_interna}% (-{impacto:.1f})")
             if self.nivel_integridad_interna < 20: logger.error("Nivel Integridad críticamente bajo por interacción negativa.")

    def get_estado_proteccion(self):
        """Devuelve estado actual."""
        return { "escudo": "ON" if self.escudo_integridad_activo else "OFF", 
                 "filtro": "ON" if self.filtro_negatividad_activo else "OFF", 
                 "amor": "ON" if self.principio_amor_activo else "OFF", 
                 "integridad": int(self.nivel_integridad_interna) }
