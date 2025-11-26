from flask import Flask, jsonify, render_template_string
from waitress import serve
import datetime
import time
import random
import os
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import pytz  # Necesitarás instalar esta librería
class SistemaRiegoBogota:
    def __init__(self):
        # ... (mantener tu código original igual)
        self.area_total = 8000  # m²
        self.humedad_actual = 65.0
        self.consumo_agua = 0
        self.historial_riego = []
        self.estado = "Ejecutándose en la nube"
        self.ultima_actualizacion = None
    def obtener_hora_bogota(self):
        sistema = SistemaRiegoBogota()
        """Obtiene la hora real de Bogotá (UTC-5)"""
        # Zona horaria de Bogotá
        bogota_tz = pytz.timezone('America/Bogota')
        hora_bogota = datetime.datetime.now(bogota_tz)
        self.ultima_actualizacion = hora_bogota
        return hora_bogota
    def simular_sensores(self):
        """Simula la lectura de sensores de humedad"""
        # Variación más realista basada en la hora del día
        hora_actual = self.obtener_hora_bogota().hour
        if 6 <= hora_actual < 12:  # Mañana
            variacion = random.uniform(-3, 1)
        elif 12 <= hora_actual < 18:  # Tarde (más evaporación)
            variacion = random.uniform(-5, -1)
        else:  # Noche (menos evaporación)
            variacion = random.uniform(-1, 2)
        self.humedad_actual = max(20, min(95, self.humedad_actual + variacion))
        return self.humedad_actual
    def decidir_riego(self):
        """Decide si es necesario regar basado en la humedad actual"""
        if self.humedad_actual < 40:
            return True, "Humedad crítica"
        elif self.humedad_actual < 60:
            return True, "Humedad baja"
        else:
            return False, "Humedad adecuada"
    def ejecutar_riego(self, motivo):
        """Ejecuta el sistema de riego"""
        # Cálculo más realista basado en el déficit de humedad
        deficit_humedad = max(0, 70 - self.humedad_actual)
        duracion = int(deficit_humedad * 2)  # minutos
        agua_utilizada = (duracion * 10)  # litros/minuto
        # Simular el riego
        time.sleep(2)  # Simular tiempo de riego
        # Actualizar humedad después del riego
        self.humedad_actual = min(85, self.humedad_actual + deficit_humedad * 0.8)
        self.consumo_agua += agua_utilizada
        registro_riego = {
            "timestamp": self.obtener_hora_bogota().strftime('%Y-%m-%d %H:%M:%S'),
            "motivo": motivo,
            "duracion": duracion,
            "agua": agua_utilizada,
            "humedad_inicial": self.humedad_actual - deficit_humedad * 0.8,
            "humedad_final": self.humedad_actual,
            "activo": True
        }
        self.historial_riego.append(registro_riego)
        return registro_riego
    def ejecutar_ciclo_monitoreo(self):
        """Ejecuta un ciclo completo de monitoreo"""
        print(f"🔍 Iniciando ciclo de monitoreo - {self.obtener_hora_bogota().strftime('%Y-%m-%d %H:%M:%S')}")
        # Leer sensores
        humedad = self.simular_sensores()
        print(f"💧 Humedad actual: {humedad:.1f}%")
        # Decidir si regar
        necesita_riego, motivo = self.decidir_riego()
        if necesita_riego:
            print(f"🚰 Iniciando riego: {motivo}")
            riego = self.ejecutar_riego(motivo)
            print(f"✅ Riego completado: {riego['agua']}L en {riego['duracion']}min")
        else:
            print(f"⏸️  No se requiere riego: {motivo}")
        return necesita_riego
    def generar_reporte(self):
        """Genera un reporte del sistema"""
        reporte = {
            "fecha_generacion": self.obtener_hora_bogota().strftime('%Y-%m-%d %H:%M:%S'),
            "humedad_actual": round(self.humedad_actual, 1),
            "consumo_agua_total": self.consumo_agua,
            "total_riegos": len(self.historial_riego),
            "area_cancha": self.area_total,
            "estado_sistema": self.estado
        }
        return reporte
# Instancia global del sistema
sistema = SistemaRiegoBogota()

# Plantilla HTML mejorada
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sistema de Riego - Bogotá</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .card { background: #f5f5f5; padding: 20px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; }
        .warning { background: #fff3cd; }
        .danger { background: #f8d7da; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚰 Sistema de Riego Automatizado - Bogotá</h1>
        
        <div class="card">
            <h2>📊 Estado Actual</h2>
            <p><strong>Hora Bogotá:</strong> <span id="hora-bogota"></span>
    <small id="fecha-bogota"></small>
<script>
function actualizarHoraBogota() {
    const ahora = new Date();
    
    // Opciones para la hora
    const opcionesHora = {
        timeZone: 'America/Bogota',
        hour12: true,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    };
    // Opciones para la fecha
    const opcionesFecha = {
        timeZone: 'America/Bogota',
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    
    const hora = ahora.toLocaleTimeString('es-CO', opcionesHora);
    const fecha = ahora.toLocaleDateString('es-CO', opcionesFecha);
    
    document.getElementById('hora-bogota').textContent = hora;
    document.getElementById('fecha-bogota').textContent = ` (${fecha})`;
}

// Iniciar y actualizar cada segundo
actualizarHoraBogota();
setInterval(actualizarHoraBogota, 1000);
</script>

<style>
.hora-actual {
    font-family: Arial, sans-serif;
    padding: 10px;
    background: #f0f0f0;
    border-radius: 5px;
    display: inline-block;
}
.hora-actual small {
    color: #666;
    font-size: 0.8em;
}
</style>
            </p>
            <p><strong>Humedad Promedio:</strong> {{humedad_actual}}%</p>
            <p><strong>Consumo Agua Total:</strong> {{consumo_agua}} litros</p>
            <p><strong>Total Riegos:</strong> {{total_riegos}}</p>
        </div>

        <div class="card">
            <h2>🔄 Acciones</h2>
            <a href="/ejecutar-ciclo">🔍 Ejecutar Ciclo de Monitoreo</a> |
            <a href="/reporte">📊 Ver Reporte Completo</a> |
            <a href="/reiniciar">🔄 Reiniciar Sistema</a>
        </div>

        {% if ultimo_riego %}
        <div class="card {{ 'success' if ultimo_riego.activo else 'warning' }}">
            <h2>💧 Último Riego</h2>
            <p><strong>Motivo:</strong> {{ultimo_riego.motivo}}</p>
            <p><strong>Duración:</strong> {{ultimo_riego.duracion}} minutos</p>
            <p><strong>Agua Utilizada:</strong> {{ultimo_riego.agua}} litros</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""
@app.route('/')
def dashboard():
    """Dashboard principal del sistema"""
    hora_actual = sistema.obtener_hora_bogota().strftime('%Y-%m-%d %H:%M:%S')
    
    contexto = {
        'hora_actual': hora_actual,
        'humedad_actual': round(sistema.humedad_actual, 1),
        'consumo_agua': sistema.consumo_agua,
        'total_riegos': len(sistema.historial_riego),
        'area_cancha': sistema.area_total,
        'estado_sistema': sistema.estado,
        'ultimo_riego': sistema.historial_riego[-1] if sistema.historial_riego else None
    }
    
    return render_template_string(HTML_TEMPLATE, **contexto)

@app.route('/ejecutar-ciclo')
def ejecutar_ciclo():
    """Ejecuta un ciclo de monitoreo manual"""
    sistema.ejecutar_ciclo_monitoreo()
    return jsonify({
        "status": "success",
        "message": "Ciclo de monitoreo ejecutado",
        "hora_bogota": sistema.obtener_hora_bogota().strftime('%Y-%m-%d %H:%M:%S'),
        "humedad_actual": round(sistema.humedad_actual, 1)
    })

@app.route('/reporte')
def reporte():
    """Genera reporte en JSON"""
    reporte_data = sistema.generar_reporte()
    return jsonify(reporte_data)

@app.route('/reiniciar')
def reiniciar():
    """Reinicia las estadísticas del sistema"""
    global sistema
    sistema = SistemaRiegoBogota()
    return jsonify({
        "status": "success", 
        "message": "Sistema reiniciado",
        "hora_bogota": sistema.obtener_hora_bogota().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/health')
def health_check():
    """Endpoint para verificar que la app está funcionando"""
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.datetime.now().isoformat(),
        "hora_bogota": sistema.obtener_hora_bogota().strftime('%Y-%m-%d %H:%M:%S'),
        "servicio": "Sistema de Riego Bogotá"
    })

def tarea_programada():
    """Tarea que se ejecuta automáticamente cada 30 minutos"""
    with app.app_context():
        try:
            hora_actual = sistema.obtener_hora_bogota()
            print(f"🔄 Ejecutando tarea programada - {hora_actual.strftime('%Y-%m-%d %H:%M:%S')}")
            sistema.ejecutar_ciclo_monitoreo()
        except Exception as e:
            print(f"❌ Error en tarea programada: {e}")

# Configurar tareas programadas
scheduler = BackgroundScheduler()
scheduler.add_job(func=tarea_programada, trigger="interval", minutes=30)
scheduler.start()

# Apagar el scheduler al cerrar la aplicación
atexit.register(lambda: scheduler.shutdown())

# ... todo tu código actual de Flask ...

if __name__ == '__main__':
    if os.environ.get('ENV') == 'production':
        # En producción usar Waitress
        print("🚀 Servidor en producción con Waitress")
        serve(app, host='0.0.0.0', port=5000)
    else:
        # En desarrollo usar servidor de Flask
        print("🔧 Servidor en desarrollo")
        app.run(debug=True, host='0.0.0.0', port=5000)
