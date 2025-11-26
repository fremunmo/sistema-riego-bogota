import time
from .sistema_riego import SistemaRiego
from .config import Config

def main():
    """Función principal del sistema de riego"""
    print("🚀 Iniciando Sistema de Riego Inteligente para Bogotá")
    print("📍 Ciudad: Bogotá, Colombia")
    print("⏰ Intervalo de verificación: 30 minutos")
    
    sistema = SistemaRiego()
    config = Config()
    
    try:
        while True:
            sistema.ejecutar_ciclo()
            # Esperar antes de la próxima verificación
            time.sleep(config.INTERVALO_VERIFICACION_MINUTOS * 60)
            
    except KeyboardInterrupt:
        print("\n🛑 Sistema detenido por el usuario")
    except Exception as e:
        print(f"❌ Error en el sistema: {e}")

if __name__ == "__main__":
    main()
