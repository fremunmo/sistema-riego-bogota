from app import sistema
import time
import logging

# Configurar logging para ver qué está pasando
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Worker iniciado - Monitoreo cada 30 minutos")
    
    while True:
        try:
            logger.info("Ejecutando ciclo de monitoreo...")
            sistema.ejecutar_ciclo_monitoreo()
            logger.info("Ciclo de monitoreo completado")
            
            # Esperar 30 minutos (1800 segundos)
            logger.info("Esperando 30 minutos para próximo ciclo...")
            time.sleep(1800)
            
        except Exception as e:
            logger.error(f"Error en worker: {e}")
            logger.info("Reintentando en 5 minutos...")
            time.sleep(300)  # Esperar 5 minutos si hay error

if __name__ == "__main__":
    main()
