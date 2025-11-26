import os
class Config:
    """Configuración del sistema de riego"""
    def __init__(self):
        self.intervalo_riego = int(os.getenv("INTERVALO_RIEGO", "3600"))  # 1 hora por defecto
        self.duracion_riego = int(os.getenv("DURACION_RIEGO", "300"))     # 5 minutos por defecto
        self.humedad_umbral = float(os.getenv("HUMEDAD_UMBRAL", "30.0"))  # 30% por defecto
        self.zonas = ["norte", "sur", "este", "oeste"]
