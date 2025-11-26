from flask import Flask, jsonify, render_template_string
import datetime
import time
import random
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__)

# Tu código original aquí (con algunas adaptaciones)
class SistemaRiegoBogota:
    def __init__(self):
        # ... (mantener tu código original igual)
        self.estado = "Ejecutándose en la nube"
        
    # ... (mantener todos tus métodos originales)

# Instancia global del sistema
sistema = SistemaRiegoBogota()

# Plantilla HTML simple
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
            <p><strong>Hora Bogotá:</strong> {{hora_actual}}</p>
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
        "hora": sistema.obtener_hora_bogota().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/reporte')
def reporte():
    """Genera reporte en JSON"""
    sistema.generar_reporte()
    
    reporte_data = {
        "fecha_reporte": sistema.obtener_hora_bogota().isoformat(),
        "area_cancha": sistema.area_total,
        "consumo_agua_total": sistema.consumo_agua,
        "total_riegos": len(sistema.historial_riego),
        "humedad_actual": sistema.humedad_actual,
        "historial_riegos": sistema.historial_riego[-10:]  # Últimos 10
    }
    
    return jsonify(reporte_data)

@app.route('/reiniciar')
def reiniciar():
    """Reinicia las estadísticas del sistema"""
    global sistema
    sistema = SistemaRiegoBogota()
    return jsonify({"status": "success", "message": "Sistema reiniciado"})

@app.route('/health')
def health_check():
    """Endpoint para verificar que la app está funcionando"""
    return jsonify({"status": "healthy", "timestamp": datetime.datetime.now().isoformat()})

def tarea_programada():
    """Tarea que se ejecuta automáticamente"""
    with app.app_context():
        print("🔄 Ejecutando tarea programada...")
        sistema.ejecutar_ciclo_monitoreo()

# Configurar tareas programadas
scheduler = BackgroundScheduler()
scheduler.add_job(func=tarea_programada, trigger="interval", minutes=30)
scheduler.start()

# Apagar el scheduler al cerrar la aplicación
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
