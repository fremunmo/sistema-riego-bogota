import time
import random
from .config import Config

class SistemaRiego:
    """Sistema inteligente de riego para Bogotá"""
    
    def __init__(self):
        self.config = Config()
        self.riego_activo = False
        
    def leer_temperatura(self):
        """Simula la lectura de temperatura"""
        # En un sistema real, aquí leerías del sensor
        return random.uniform(15, 28)  # Temperatura típica de Bogotá
    
    def leer_humedad_suelo(self):
        """Simula la lectura de humedad del suelo"""
        return random.uniform(20, 80)  # Porcentaje
    
    def leer_probabilidad_lluvia(self):
        """Simula la probabilidad de lluvia"""
        return random.uniform(0, 100)  # Porcentaje
    
    def activar_riego(self):
        """Activa el sistema de riego"""
        print("💧 Activando sistema de riego...")
        self.riego_activo = True
        time.sleep(2)  # Simula el tiempo de riego
        print("✅ Riego completado")
        self.riego_activo = False
    
    def verificar_condiciones(self):
        """Verifica si es necesario regar"""
        temperatura = self.leer_temperatura()
        humedad = self.leer_humedad_suelo()
        lluvia = self.leer_probabilidad_lluvia()
        
        print(f"🌡️ Temperatura: {temperatura:.1f}°C")
        print(f"💦 Humedad suelo: {humedad:.1f}%")
        print(f"🌧️ Probabilidad lluvia: {lluvia:.1f}%")
        
        # Lógica de decisión para Bogotá
        if (humedad < self.config.HUMEDAD_MINIMA and 
            lluvia < self.config.PROBABILIDAD_LLUVIA_UMBRAL):
            return True
        return False
    
    def ejecutar_ciclo(self):
        """Ejecuta un ciclo completo de verificación"""
        print("\n" + "="*50)
        print("🔍 Verificando condiciones para riego...")
        
        if self.verificar_condiciones():
            print("🎯 Condiciones apropiadas - Activando riego")
            self.activar_riego()
        else:
            print("⏸️ Condiciones no apropiadas - Riego postergado")
        
        print(f"⏰ Próxima verificación en {self.config.INTERVALO_VERIFICACION_MINUTOS} minutos")
        print("="*50)
