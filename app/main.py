from sistema_riego import SistemaRiego
from config import Config

def main():
    """Función principal del sistema de riego"""
    sistema = SistemaRiego()
    sistema.iniciar()
    
    # Ejemplo de uso
    sistema.regar_zona("norte", 30)  # Regar zona norte por 30 segundos

if __name__ == "__main__":
    main()
