import os

class Config:
    """Configuración del sistema de riego para Bogotá"""
    
    # Configuración de sensores
    SENSOR_TEMPERATURA_PIN = 4
    SENSOR_HUMEDAD_PIN = 17
    SENSOR_LLUVIA_PIN = 27
    
    # Umbrales para Bogotá (puedes ajustarlos)
    HUMEDAD_MINIMA = 40  # Porcentaje
    TEMPERATURA_MAXIMA = 25  # Grados Celsius
    PROBABILIDAD_LLUVIA_UMBRAL = 30  # Porcentaje
    
    # Configuración del riego
    TIEMPO_RIEGO_SEGUNDOS = 300  # 5 minutos
    INTERVALO_VERIFICACION_MINUTOS = 30
    
    # API del clima (puedes usar OpenWeatherMap)
    API_KEY_CLIMA = os.getenv('API_KEY_CLIMA', 'tu-api-key-aqui')
    CIUDAD = "Bogota,CO"
