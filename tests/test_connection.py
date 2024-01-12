from loguru import logger

from fixtures import sio, sio_2

class TestConnection:
    player_1: dict = None
    player_2: dict = None
    game: dict = None

    def test_connect_2_players(self, sio, sio_2):
        # зачищаем игроков
        sio.emit('server/debug/reset_players', {})

        # создаем игрока
        sio.emit('server/player/create', {})
        response = sio.receive()
        assert response[0] == "client/player/created"
        self.__class__.player_1 = response[1]

        # создаем игрока
        sio_2.emit('server/player/create', {})
        response = sio_2.receive()
        assert response[0] == "client/player/created"
        self.__class__.player_2 = response[1]

    def test_create_game_join(self, sio, sio_2):
        # создаем игру
        sio.emit('server/game/create', {
            "category": "default",
            "player_uid": self.__class__.player_1['uid']
        })

        response = sio.receive()
        assert response[0] == "client/game/updated"
        game = response[1]

        # подключаем игрока 1 к игре

        sio.emit('server/game/join', {
            "player_uid": self.__class__.player_1["uid"],
            "code_to_join": game["code_to_join"],
        })
        response = sio.receive()
        assert response[0] == "client/game/updated"
        game = response[1]

        assert game["status"] == "waiting"

        # подключаем игрока 2 к игре

        sio_2.emit('server/game/join', {
            "player_uid": self.__class__.player_2["uid"],
            "code_to_join": game["code_to_join"],
        })
        response = sio_2.receive()
        assert response[0] == "client/game/updated"

        game = response[1]
        assert game["players_count"] == 2
        assert game["status"] == "picking"

        self.__class__.game = game

    def test_player_leaves_game(self, sio, sio_2):
        """Проверяем что будет если отключим одного пользователя"""

        sio_2.disconnect()

        response = sio.receive()
        assert response[0] == "client/game/updated"
        game = response[1]

        assert game["status"] == "waiting"
        self.__class__.game = game

    def test_player_rejoin_game(self, sio, sio_2):
        """Проверяем, что статус переключится после возвращения в игру"""

        player_uid = self.__class__.player_2["uid"]
        game_uid = self.__class__.game["uid"]

        print(player_uid, game_uid)

        sio_2.connect('ws://0.0.0.0:80')

        sio_2.emit('server/player/reconnect', {
            "player_uid": player_uid,
            "game_uid": game_uid,
        })

        # ожидаем сообщения об обновлении игры
        response = sio.receive()
        assert response[0] == "client/game/updated"

        game = response[1]
        assert game["status"] == "picking"

        self.__class__.game = game

