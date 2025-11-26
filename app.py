

from flask import Flask, jsonify, render_template_string
from waitress import serve
import datetime
import time
import random
import os
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import pytz  # Necesitarás instalar esta librería


app = Flask(__name__)

# Instala pytz si no lo tienes: pip install pytz

class SistemaRiegoBogota:
    def __init__(self):
        self.area_total = 8000  # m²
        self.humedad_actual = 65.0
        self.consumo_agua = 0
        self.historial_riego = []
        self.estado = "Ejecutándose en la nube"
        self.ultima_actualizacion = None

    def obtener_hora_bogota(self):
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
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            max-width: 900px; 
            margin: 0 auto; 
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #2c3e50, #3498db);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .card { 
            background: #f8f9fa; 
            padding: 25px; 
            margin: 15px; 
            border-radius: 10px;
            border-left: 5px solid #3498db;
        }
        .success { border-left-color: #27ae60; background: #d5f4e6; }
        .warning { border-left-color: #f39c12; background: #fef5e7; }
        .danger { border-left-color: #e74c3c; background: #fdeaea; }
        .info { border-left-color: #3498db; background: #ebf5fb; }
        .actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .btn {
            padding: 12px 20px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
        }
        .btn:hover {
            background: #2980b9;
            transform: translateY(-2px);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .hora-actual {
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
            background: #ecf0f1;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚰 Sistema de Riego Automatizado - Bogotá</h1>
            <p>Monitoreo en tiempo real de canchas de fútbol</p>
        </div>

        <div class="hora-actual">
            🕐 Hora actual en Bogotá: {{hora_actual}}
        </div>
        
        <div class="card info">
            <h2>📊 Estado del Sistema</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>💧 Humedad</h3>
                    <p style="font-size: 24px; margin: 5px 0; color: #3498db;">{{humedad_actual}}%</p>
                </div>
                <div class="stat-card">
                    <h3>💦 Consumo Agua</h3>
                    <p style="font-size: 24px; margin: 5px 0; color: #2980b9;">{{consumo_agua}}L</p>
                </div>
                <div class="stat-card">
                    <h3>🔄 Total Riegos</h3>
                    <p style="font-size: 24px; margin: 5px 0; color: #27ae60;">{{total_riegos}}</p>
                </div>
                <div class="stat-card">
                    <h3>📏 Área</h3>
                    <p style="font-size: 24px; margin: 5px 0; color: #8e44ad;">{{area_cancha}}m²</p>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>🔄 Acciones</h2>
            <div class="actions">
                <a href="/ejecutar-ciclo" class="btn">🔍 Ejecutar Ciclo</a>
                <a href="/reporte" class="btn">📊 Ver Reporte JSON</a>
                <a href="/reiniciar" class="btn">🔄 Reiniciar Sistema</a>
                <a href="/health" class="btn">❤️ Health Check</a>
            </div>
        </div>

        {% if ultimo_riego %}
        <div class="card {{ 'success' if ultimo_riego.activo else 'warning' }}">
            <h2>💧 Último Riego</h2>
            <p><strong>📅 Fecha:</strong> {{ultimo_riego.timestamp}}</p>
            <p><strong>🎯 Motivo:</strong> {{ultimo_riego.motivo}}</p>
            <p><strong>⏱️ Duración:</strong> {{ultimo_riego.duracion}} minutos</p>
            <p><strong>💦 Agua Utilizada:</strong> {{ultimo_riego.agua}} litros</p>
            <p><strong>📈 Humedad Inicial/Final:</strong> {{ultimo_riego.humedad_inicial|round(1)}}% → {{ultimo_riego.humedad_final|round(1)}}%</p>
        </div>
        {% endif %}

        <div class="card">
            <h2>ℹ️ Información del Sistema</h2>
            <p><strong>🖥️ Estado:</strong> {{estado_sistema}}</p>
            <p><strong>🕒 Última actualización:</strong> {{hora_actual}}</p>
            <p><strong>🔔 Próximo ciclo automático:</strong> Cada 30 minutos</p>
        </div>
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