from flask import Flask, jsonify, render_template_string, request
import datetime
import time
import random
import os
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import pytz
import json

class SistemaRiegoBogota:
    def __init__(self):
        self.area_total = 8000
        self.humedad_actual = 65.0
        self.consumo_agua = 0
        self.historial_riego = []
        self.estado = "Ejecutándose en PythonAnywhere"
        self.ultima_actualizacion = None
        self.riegos_hoy = 0
        self.modo_automatico = True
        self.temperatura_actual = 22.0
        self.velocidad_viento = 5.0
        self.lluvia_detectada = False
        self.bogota_tz = pytz.timezone('America/Bogota')

    def obtener_hora_bogota(self):
        """Obtiene la hora real de Bogotá"""
        try:
            hora_utc = datetime.datetime.now(pytz.UTC)
            hora_bogota = hora_utc.astimezone(self.bogota_tz)
            self.ultima_actualizacion = hora_bogota
            return hora_bogota
        except:
            # Fallback para PythonAnywhere
            hora_utc = datetime.datetime.utcnow()
            hora_bogota = hora_utc - datetime.timedelta(hours=5)
            self.ultima_actualizacion = hora_bogota
            return hora_bogota

    def simular_clima(self):
        """Simula condiciones climáticas"""
        hora_bogota = self.obtener_hora_bogota()
        hora_actual = hora_bogota.hour
        
        # Temperatura basada en la hora
        if 5 <= hora_actual < 12:
            base_temp = 14 + (hora_actual - 5) * 1.2
        elif 12 <= hora_actual < 17:
            base_temp = 19 - (hora_actual - 12) * 0.5
        else:
            base_temp = 16 - (hora_actual - 17) * 0.7
        
        self.temperatura_actual = max(8, min(25, base_temp + random.uniform(-2, 2)))
        
        # Viento
        if 13 <= hora_actual < 18:
            base_viento = 8 + random.uniform(-2, 4)
        else:
            base_viento = 4 + random.uniform(-2, 2)
        self.velocidad_viento = max(0, min(30, base_viento))
        
        # Lluvia
        prob_lluvia = 0.15
        if 14 <= hora_actual < 20:
            prob_lluvia = 0.25
            
        if random.random() < prob_lluvia:
            self.lluvia_detectada = True
            self.humedad_actual = min(95, self.humedad_actual + random.uniform(15, 30))
        else:
            self.lluvia_detectada = False

    def simular_sensores(self):
        """Simula lectura de sensores"""
        self.simular_clima()
        
        variacion_base = random.uniform(-1.5, 1.5)
        
        if self.temperatura_actual > 20:
            variacion_base -= (self.temperatura_actual - 20) * 0.08
            
        variacion_base -= self.velocidad_viento * 0.03
        
        if self.lluvia_detectada:
            variacion_base += random.uniform(10, 25)
        
        self.humedad_actual = max(20, min(95, self.humedad_actual + variacion_base))
        return self.humedad_actual

    def decidir_riego(self):
        """Decide si es necesario regar"""
        hora_actual = self.obtener_hora_bogota().hour
        
        if 22 <= hora_actual or hora_actual < 6:
            if self.humedad_actual > 30:
                return False, "Horario nocturno"
        
        if self.lluvia_detectada:
            return False, "Lluvia detectada"
        
        if self.humedad_actual < 30:
            return True, "Humedad crítica"
        elif self.humedad_actual < 50:
            return True, "Humedad baja"
        else:
            return False, "Humedad adecuada"

    def ejecutar_riego(self, motivo):
        """Ejecuta el sistema de riego"""
        hora_actual = self.obtener_hora_bogota()
        
        if self.lluvia_detectada and "crítica" not in motivo:
            return {
                "timestamp": hora_actual.strftime('%Y-%m-%d %H:%M:%S'),
                "motivo": "Cancelado - lluvia",
                "duracion": 0,
                "agua": 0,
                "humedad_inicial": self.humedad_actual,
                "humedad_final": self.humedad_actual,
                "activo": False
            }
        
        deficit_humedad = max(0, 65 - self.humedad_actual)
        duracion = int(deficit_humedad * 1.2)
        agua_utilizada = duracion * 8
        
        humedad_inicial = self.humedad_actual
        incremento_humedad = min(30, deficit_humedad * 0.8)
        self.humedad_actual = min(80, self.humedad_actual + incremento_humedad)
        
        self.consumo_agua += agua_utilizada
        self.riegos_hoy += 1
        
        registro_riego = {
            "timestamp": hora_actual.strftime('%Y-%m-%d %H:%M:%S'),
            "motivo": motivo,
            "duracion": duracion,
            "agua": agua_utilizada,
            "humedad_inicial": round(humedad_inicial, 1),
            "humedad_final": round(self.humedad_actual, 1),
            "activo": True
        }
        self.historial_riego.append(registro_riego)
        
        if len(self.historial_riego) > 50:
            self.historial_riego = self.historial_riego[-50:]
            
        return registro_riego

    def ejecutar_ciclo_monitoreo(self):
        """Ejecuta un ciclo completo de monitoreo"""
        hora_bogota = self.obtener_hora_bogota()
        print(f"Ciclo monitoreo - {hora_bogota.strftime('%H:%M:%S')}")
        
        humedad = self.simular_sensores()
        
        necesita_riego, motivo = self.decidir_riego()
        
        if necesita_riego and self.modo_automatico:
            print(f"Iniciando riego: {motivo}")
            return self.ejecutar_riego(motivo)
        else:
            print(f"No se requiere riego: {motivo}")
            return {"activo": False, "motivo": motivo, "timestamp": hora_bogota.strftime('%Y-%m-%d %H:%M:%S')}

    def generar_reporte(self):
        """Genera un reporte del sistema"""
        hora_bogota = self.obtener_hora_bogota()
        return {
            "fecha_generacion": hora_bogota.strftime('%Y-%m-%d %H:%M:%S'),
            "humedad_actual": round(self.humedad_actual, 1),
            "temperatura": round(self.temperatura_actual, 1),
            "velocidad_viento": round(self.velocidad_viento, 1),
            "lluvia_detectada": self.lluvia_detectada,
            "consumo_agua_total": self.consumo_agua,
            "total_riegos": len(self.historial_riego),
            "riegos_hoy": self.riegos_hoy,
            "area_cancha": self.area_total,
            "estado_sistema": self.estado,
            "modo_automatico": self.modo_automatico
        }

# Instancia global del sistema
sistema = SistemaRiegoBogota()

# Plantilla HTML simplificada
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sistema de Riego - Bogotá</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f2f5; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center; }
        .header h1 { color: #2c3e50; margin-bottom: 10px; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .card h2 { color: #2c3e50; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        .stat { display: flex; justify-content: space-between; margin: 10px 0; padding: 8px; background: #f8f9fa; border-radius: 5px; }
        .controls { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 20px 0; }
        .btn { padding: 12px; border: none; border-radius: 5px; color: white; text-decoration: none; text-align: center; }
        .btn-primary { background: #3498db; }
        .btn-success { background: #27ae60; }
        .btn-warning { background: #f39c12; }
        .hora-actual { background: #2c3e50; color: white; padding: 10px; border-radius: 5px; text-align: center; margin: 10px 0; }
        .historial { max-height: 300px; overflow-y: auto; }
        .evento { padding: 10px; margin: 5px 0; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #3498db; }
        .evento.riego { border-left-color: #27ae60; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚰 Sistema de Riego Inteligente</h1>
            <p>Bogotá, Colombia - PythonAnywhere</p>
            <div class="hora-actual">
                <span id="hora-bogota">Cargando...</span>
                <br>
                <small id="fecha-bogota"></small>
            </div>
        </div>
        
        <div class="controls">
            <a href="/ejecutar-ciclo" class="btn btn-primary">🔍 Monitoreo</a>
            <a href="/reporte" class="btn btn-success" target="_blank">📊 Reporte</a>
            <a href="/reiniciar" class="btn btn-warning">🔄 Reiniciar</a>
        </div>

        <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0;">
            <label>Modo Automático: </label>
            <input type="checkbox" id="modoAuto" {{ 'checked' if modo_automatico else '' }} onchange="toggleModo()">
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h2>📊 Sistema</h2>
                <div class="stat"><span>Estado:</span><span>{{ estado_sistema }}</span></div>
                <div class="stat"><span>Modo:</span><span>{{ 'Automático' if modo_automatico else 'Manual' }}</span></div>
                <div class="stat"><span>Área:</span><span>{{ area_cancha }} m²</span></div>
            </div>
            
            <div class="card">
                <h2>🌡️ Condiciones</h2>
                <div class="stat"><span>💧 Humedad:</span><span style="color: #3498db">{{ humedad_actual }}%</span></div>
                <div class="stat"><span>🌡️ Temp:</span><span style="color: #e74c3c">{{ temperatura }}°C</span></div>
                <div class="stat"><span>💨 Viento:</span><span>{{ viento }} km/h</span></div>
                <div class="stat"><span>🌧️ Lluvia:</span><span>{{ 'Sí' if lluvia else 'No' }}</span></div>
            </div>
            
            <div class="card">
                <h2>💧 Agua</h2>
                <div class="stat"><span>Consumo:</span><span style="color: #27ae60">{{ consumo_agua }}L</span></div>
                <div class="stat"><span>Total Riegos:</span><span>{{ total_riegos }}</span></div>
                <div class="stat"><span>Riegos Hoy:</span><span>{{ riegos_hoy }}</span></div>
            </div>
        </div>
        
        {% if ultimo_riego %}
        <div class="card">
            <h2>🚰 Último Riego</h2>
            <div class="stat"><span>Hora:</span><span>{{ ultimo_riego.timestamp }}</span></div>
            <div class="stat"><span>Motivo:</span><span>{{ ultimo_riego.motivo }}</span></div>
            <div class="stat"><span>Duración:</span><span>{{ ultimo_riego.duracion }}min</span></div>
            <div class="stat"><span>Agua:</span><span>{{ ultimo_riego.agua }}L</span></div>
        </div>
        {% endif %}
        
        <div class="card">
            <h2>📜 Historial</h2>
            <div class="historial">
                {% for evento in historial_reciente %}
                <div class="evento {{ 'riego' if evento.activo else '' }}">
                    <strong>{{ evento.timestamp.split(' ')[1] }}</strong> - 
                    {{ evento.motivo }} 
                    {% if evento.agua > 0 %}({{ evento.agua }}L){% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    <script>
        function actualizarHora() {
            const ahora = new Date();
            const offsetBogota = -5 * 60;
            const offsetLocal = ahora.getTimezoneOffset();
            const diferencia = offsetBogota - offsetLocal;
            const horaBogota = new Date(ahora.getTime() + diferencia * 60000);
            
            document.getElementById('hora-bogota').textContent = horaBogota.toLocaleTimeString('es-CO');
            document.getElementById('fecha-bogota').textContent = horaBogota.toLocaleDateString('es-CO', { 
                weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' 
            });
        }

        function toggleModo() {
            const modoAuto = document.getElementById('modoAuto').checked;
            fetch('/toggle-automatico', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({modo_automatico: modoAuto})
            });
        }

        actualizarHora();
        setInterval(actualizarHora, 1000);
        setInterval(() => window.location.reload(), 30000);
    </script>
</body>
</html>
"""

app = Flask(__name__)

@app.route('/')
def dashboard():
    hora_bogota = sistema.obtener_hora_bogota()
    contexto = {
        'humedad_actual': round(sistema.humedad_actual, 1),
        'temperatura': round(sistema.temperatura_actual, 1),
        'viento': round(sistema.velocidad_viento, 1),
        'lluvia': sistema.lluvia_detectada,
        'consumo_agua': sistema.consumo_agua,
        'total_riegos': len(sistema.historial_riego),
        'riegos_hoy': sistema.riegos_hoy,
        'area_cancha': sistema.area_total,
        'estado_sistema': sistema.estado,
        'modo_automatico': sistema.modo_automatico,
        'ultimo_riego': sistema.historial_riego[-1] if sistema.historial_riego else None,
        'historial_reciente': list(reversed(sistema.historial_riego[-8:])),
    }
    return render_template_string(HTML_TEMPLATE, **contexto)

@app.route('/ejecutar-ciclo')
def ejecutar_ciclo():
    resultado = sistema.ejecutar_ciclo_monitoreo()
    return jsonify({
        "status": "success",
        "hora_bogota": sistema.obtener_hora_bogota().strftime('%H:%M:%S'),
        "resultado": resultado
    })

@app.route('/reporte')
def reporte():
    return jsonify(sistema.generar_reporte())

@app.route('/reiniciar')
def reiniciar():
    global sistema
    sistema = SistemaRiegoBogota()
    return jsonify({"status": "sistema reiniciado"})

@app.route('/toggle-automatico', methods=['POST'])
def toggle_automatico():
    data = request.get_json()
    sistema.modo_automatico = data.get('modo_automatico', True)
    return jsonify({"modo_automatico": sistema.modo_automatico})

@app.route('/health')
def health_check():
    return jsonify({
        "status": "online", 
        "hora_bogota": sistema.obtener_hora_bogota().strftime('%Y-%m-%d %H:%M:%S'),
        "servicio": "Sistema Riego Bogotá"
    })

# Configuración para PythonAnywhere
if __name__ == '__main__':
    print("✅ Sistema de Riego iniciado en PythonAnywhere")
    # En PythonAnywhere usamos app directamente, no waitress
    app.run(debug=False)
