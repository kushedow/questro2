import socketio

# Нет авторизации и персональных данных – нет проблем с безопасностью!
sio = socketio.Server(cors_allowed_origins="*", origins="*")

# Сервим статику (хотя пока она нам и не нужна)
app = socketio.WSGIApp(sio, static_files={

        # Разрешаем открывать главную
        '/': {'content_type': 'text/html', 'filename': '../questro_frontend/dist/index.html'},

        # Разрешаем открывать все из папки ассетов
        '/assets/': '../questro_frontend/dist/assets/'

    },
)
