from flask import Flask, jsonify, render_template_string
import datetime
import random

app = Flask(__name__)

# Simulamos el sistema de riego
class SistemaRiegoBogota:
    def __init__(self):
        self.area_total = 8000
        self.humedad_actual = 65.0
        self.consumo_agua = 0
        self.historial_riego = []
        self.estado = "🌱 Funcionando en la nube"
        
    def obtener_hora_bogota(self):
        return datetime.datetime.now()
    
    def simular_lectura_humedad(self):
        # Simula lectura entre 30% y 80%
        return random.uniform(30, 80)
    
    def ejecutar_ciclo_monitoreo(self):
        self.humedad_actual = self.simular_lectura_humedad()
        
        if self.humedad_actual < 50:
            # Regar por 5 minutos
            agua_usada = 25
            self.consumo_agua += agua_usada
            riego = {
                "timestamp": self.obtener_hora_bogota().strftime('%Y-%m-%d %H:%M:%S'),
                "motivo": f"Humedad baja ({self.humedad_actual:.1f}%)",
                "duracion": 5,
                "agua": agua_usada,
                "activo": True
            }
            self.historial_riego.append(riego)
            return f"✅ Regando - {riego['motivo']}"
        else:
            return f"✅ Humedad OK ({self.humedad_actual:.1f}%) - No se necesita riego"

# Creamos el sistema
sistema = SistemaRiegoBogota()

# Página web simple
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sistema de Riego - Bogotá</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 40px; 
            background: #f0f8f0;
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 { color: #2c5530; }
        .card { 
            background: #f8f9fa; 
            padding: 20px; 
            margin: 15px 0; 
            border-radius: 10px;
            border-left: 5px solid #2c5530;
        }
        .btn {
            background: #2c5530;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            display: inline-block;
            margin: 5px;
        }
        .btn:hover {
            background: #1e3a24;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚰 Sistema de Riego Automatizado - Bogotá</h1>
        <p><em>Sistema funcionando en la nube ☁️</em></p>
        
        <div class="card">
            <h2>📊 Estado Actual</h2>
            <p><strong>🕒 Hora Bogotá:</strong> {{hora_actual}}</p>
            <p><strong>💧 Humedad Actual:</strong> {{humedad_actual}}%</p>
            <p><strong>💦 Consumo Agua Total:</strong> {{consumo_agua}} litros</p>
            <p><strong>🔢 Total Riegos:</strong> {{total_riegos}}</p>
        </div>

        <div class="card">
            <h2>🔄 Acciones</h2>
            <a class="btn" href="/ejecutar-ciclo">🔍 Ejecutar Monitoreo</a>
            <a class="btn" href="/reporte">📊 Ver Reporte</a>
            <a class="btn" href="/reiniciar">🔄 Reiniciar</a>
        </div>

        {% if mensaje %}
        <div class="card" style="background: #e8f5e8;">
            <h3>📝 Última Acción:</h3>
            <p>{{mensaje}}</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Página principal"""
    hora_actual = sistema.obtener_hora_bogota().strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template_string(HTML_TEMPLATE,
        hora_actual=hora_actual,
        humedad_actual=round(sistema.humedad_actual, 1),
        consumo_agua=sistema.consumo_agua,
        total_riegos=len(sistema.historial_riego)
    )

@app.route('/ejecutar-ciclo')
def ejecutar_ciclo():
    """Ejecuta un ciclo de monitoreo"""
    mensaje = sistema.ejecutar_ciclo_monitoreo()
    
    hora_actual = sistema.obtener_hora_bogota().strftime('%Y-%m-%d %H:%M:%S')
    return render_template_string(HTML_TEMPLATE,
        hora_actual=hora_actual,
        humedad_actual=round(sistema.humedad_actual, 1),
        consumo_agua=sistema.consumo_agua,
        total_riegos=len(sistema.historial_riego),
        mensaje=mensaje
    )

@app.route('/reporte')
def reporte():
    """Muestra reporte"""
    mensaje = sistema.muestra_reporte()
    return render_template_string(HTML_TEMPLATE,
        "fecha_reporte": sistema.obtener_hora_bogota().isoformat(),
        "area_cancha": sistema.area_total,
        "consumo_agua_total": sistema.consumo_agua,
        "total_riegos": len(sistema.historial_riego),
        "humedad_actual": sistema.humedad_actual,
        "historial_riegos": sistema.historial_riego[-5:]  # Últimos 5
        mensaje=mensaje
    }
    
    return jsonify(reporte_data)

@app.route('/reiniciar')
def reiniciar():
    """Reinicia el sistema"""
    global sistema
    sistema = SistemaRiegoBogota()
    return jsonify({"status": "success", "message": "✅ Sistema reiniciado"})

@app.route('/health')
def health_check():
    """Para verificar que está funcionando"""
    return jsonify({"status": "healthy", "timestamp": datetime.datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
