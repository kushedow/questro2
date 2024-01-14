import socketio
import eventlet
from bidict import bidict

from loguru import logger

from src.service import QuestroService

service = QuestroService()

sid_to_uuid = bidict()

sio = socketio.Server(cors_allowed_origins="*", origins="*")

app = socketio.WSGIApp(sio, static_files={

        # Разрешаем открывать главную
        '/': {'content_type': 'text/html', 'filename': 'frontend/index.html'},
        '/assets/': 'frontend/assets/',

    },
)

def emit_error(sid, error_text):
    sio.emit("client/error", to=sid, data={"message": error_text})

#TODO update room

# TODO show questions

@sio.event
def connect(sid, environ):

    logger.info(f"Клиент {sid} подключился")
    # sio.emit("log", to=sid, data={"message": "OK"})

@sio.event
def disconnect(sid):

    player_uid = sid_to_uuid.get(sid, None)
    if player_uid is None:
        logger.debug(f"Отвалился клиент {player_uid} не являющийся игроком")

    game = service.deactivate_player(player_uid)
    if game is None:
        logger.debug("Неверный uid или отвалился игрок не входящий в игру")
        return

    game_uid = game["uid"]
    # вылетаем из комнаты на всякий случай
    sio.leave_room(sid, game["uid"])
    # отправляем остальным участникам новость и тормозим игру

    logger.debug(f"Клиент {sid} отвалился, оповещаем комнату")

    sio.emit("client/game/updated", room=game_uid, data=game)

@sio.on('server/debug/players')
def socket_debug_players(sid, data):
    sio.emit("debug", to=sid, data=dict(sid_to_uuid))

@sio.on('server/debug/reset_players')
def socket_reset_players(sid, data):
    sid_to_uuid.clear()

@sio.on('server/player/create')
def socket_player_create(sid, data):
    player = service.create_player()
    sio.emit("client/player/created", to=sid, data=player)

    sid_to_uuid[sid] = player.get("uid")
    logger.info(f"\nКлиент {sid} создал пользователя")

@sio.on('server/player/reconnect')
def socket_player_reconnect(sid, data):
    player_uid = data.get("player_uid")
    game_uid = data.get("game_uid")

    logger.debug(f"Восстанавливаем подключение для {player_uid}")

    if player_uid is None:
        emit_error(sid, "Player not specified")
        return

    if game_uid is None:
        emit_error(sid, "Game not specified")
        return

    game = service.reactivate_player(player_uid)

    if game is None:
        emit_error(sid, "Cound not reconnect, check_data")
        return

    logger.debug(f"Реактивировали пользователя {player_uid}")
    logger.debug(f"Вернули в игру {game_uid}")

    sid_to_uuid.inverse[player_uid] = sid

    # добавляем в комнату
    logger.debug(f"Добавляем в сокет-рум {game_uid} и рассылаем всем внутри")
    sio.enter_room(sid, game_uid)
    sio.emit("client/game/updated", room=game_uid, data=game)


@sio.on('server/game/create')
def socket_game_create(sid, data):

    # создаем игру

    player_uid = data.get("player_uid")
    category_code = data.get("category", "default")

    if player_uid is None:
        emit_error(sid, "Player not specified")
        return

    if category_code is None:
        emit_error(sid, "Category not specified")
        return

    game = service.create_game(category=category_code)
    logger.info(f"\nКлиент {sid} создал игру {game}")

    game_uid = game["uid"]
    # добавляем в игру сразу же игрока создавшего ее
    game = service.add_player_to_game(player_uid, game_uid)
    logger.info(f"\nКлиент {sid} добавился в игру {game}")

    # добавляем в комнату
    sio.enter_room(sid, game["uid"])
    logger.info(f"\nКлиент {sid} добавился в комнату {game_uid}")

    # оповещаем всех что клиент добавился
    sio.emit("client/game/updated",  room=game_uid, data=game)


@sio.on('server/game/join')
def socket_game_join(sid, data):
    player_uid = data.get("player_uid")
    code_to_join = data.get("code_to_join")

    logger.debug(f"Игрок {player_uid} пытается присоедниниться к комнате")
    game = service.join_game(player_uid, code_to_join)

    if game is None:
        emit_error(sid, f"Player {player_uid} Not connected to game")

    game_uid = game["uid"]

    # добавляем в комнату
    sio.enter_room(sid, str(game_uid))
    logger.debug(f"Игрок {player_uid} {sid} присоединился к комнате {game_uid}")

    sio.emit("client/game/updated", room=game_uid, data=game)

@sio.on('server/game/start')
def socket_game_start(sid, data):
    """Начинаем игру, меняя ее статус и оповещая всех"""
    game_uid = data.get("game_uid")
    logger.debug("Клиент просит начать игру")

    game = service.start_game(game_uid)

    if game is None:
        emit_error(sid, f"Cant start game{game}")

    sio.emit("client/game/updated", room=game_uid, data=game)
    logger.debug("Игра началась, клиенты оповещены!")


@sio.on('server/categories/list')
def socket_categories_list(sid, data):
    logger.debug(f"Клиент {sid} запрашивает категории")
    cats = service.get_categories()
    sio.emit("client/categories/list", to=sid, data=cats)


@sio.on('server/questions/list')
def socket_questions_list(sid, data):
    """Клиент запрашивает список вопросов"""
    game_uid = data.get("game_uid")

    logger.debug("Клиент запрашивает три вопроса")
    questions = service.list_3_questions(game_uid)

    sio.emit("client/questions/list", room=game_uid, data=questions)


@sio.on('server/questions/pick')
def socket_questions_pick(sid, data):

    player_uid = data.get("player_uid")
    game_uid = data.get("game_uid")
    question_pk = int(data.get("question_pk"))

    logger.debug(f"Игрок {player_uid} выбрал вопрос {question_pk}")

    # выкидываем вопрос
    question = service.pop_question(game_uid, question_pk)

    logger.debug(f"Использован вопрос {question['text']}")

    # передаем ход следующему игроку
    game = service.shift_player(game_uid)

    sio.emit("client/game/updated", room=game_uid, data=game)


# TODO reconnect by uuid

# TODO leave game


eventlet.wsgi.server(
    eventlet.listen(('', 80)), app
)
