import time
from config import Config

class SistemaRiego:
    def __init__(self):
        self.config = Config()
        self.estado = "inactivo"
    
    def iniciar(self):
        """Inicializa el sistema de riego"""
        self.estado = "activo"
        print("Sistema de riego iniciado")
    
    def regar_zona(self, zona, duracion):
        """Activa el riego en una zona específica"""
        print(f"Regando zona {zona} por {duracion} segundos")
        time.sleep(duracion)
        print(f"Riego en zona {zona} completado")
    
    def detener(self):
        """Detiene el sistema de riego"""
        self.estado = "inactivo"
        print("Sistema de riego detenido")
