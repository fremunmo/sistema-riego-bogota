import requests
import os

class TelegramNotifier:
    def __init__(self):
        # Reemplaza estos valores con los tuyos
        self.bot_token = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"  # Tu token real
        self.chat_id = "987654321"  # Tu chat ID real
    
    def enviar_notificacion(self, mensaje):
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': mensaje,
            'parse_mode': 'HTML'
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print("✅ Notificación enviada a Telegram")
            else:
                print(f"❌ Error al enviar: {response.text}")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")

# Ejemplo de uso
if __name__ == "__main__":
    bot = TelegramNotifier()
    bot.enviar_notificacion("🤖 <b>Bot configurado correctamente!</b>")
