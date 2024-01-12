import time

# def test_connection(sio):
#     """Проверяем, что соединение устанавливается и логирование работает"""
#     received = sio.receive()
#     event = received[0]
#     data = received[1]
#     assert event == "log"
#     assert data == {"message": "OK"}


# def test_create_player(sio_connected):
#     """Проверяем, что игрок создается"""
#     sio_connected.emit('server/player/create', {})
#     received = sio_connected.receive()
#     event = received[0]
#     data = received[1]
#     assert event == "client/player/created"

from fixtures import sio, sio_2

class TestCategories:
    """Тестирует получение категорий и поиск вопросов в категории"""

    def test_list_categories(self, sio):
        # create player 1
        sio.emit('server/categories/list', {})
        response = sio.receive()
        assert response[0] == "client/categories/list"
        data = response[1]
        assert type(data) == list
        assert len(data) > 1


class TestTwoPlayersInGame:
    player_1: dict = None
    player_2: dict = None
    game: dict = None
    questions: list[dict] = []

    def test_create_player_1(self, sio):
        # create player 1
        sio.emit('server/player/create', {})
        response = sio.receive()
        print(response)
        assert response[0] == "client/player/created"
        player = response[1]
        self.__class__.player_1 = player

    def test_create_player_2(self, sio_2):
        # create player 2
        sio_2.emit('server/player/create', {})
        response = sio_2.receive()
        assert response[0] == "client/player/created"
        player = response[1]
        self.__class__.player_2 = player

    def test_create_game(self, sio):
        sio.emit('server/game/create', {
            "player_uid": self.__class__.player_1,
            "category": "default",
        })

        response = sio.receive()
        assert response[0] == "client/game/updated"
        self.__class__.game = response[1]

    def test_create_game_without_player(self, sio):
        sio.emit('server/game/create', {
            "category": "default",
        })
        response = sio.receive()
        assert response[0] == "client/error"

    def test_create_game_without_category(self, sio):
        sio.emit('server/game/create', {
            "player_uid": self.__class__.player_1,
        })
        response = sio.receive()
        assert response[0] == "client/error"

    def test_join_2_players_to_game(self, sio, sio_2):
        sio.emit('server/game/join', {
            "player_uid": self.__class__.player_1["uid"],
            "code_to_join": self.__class__.game["code_to_join"],
        })
        response = sio.receive()
        assert response[0] == "client/game/updated"

        sio_2.emit('server/game/join', {
            "player_uid": self.__class__.player_2["uid"],
            "code_to_join": self.__class__.game["code_to_join"],
        })
        response = sio_2.receive()
        assert response[0] == "client/game/updated"

        self.__class__.game = response[1]

        assert self.__class__.game["players_count"] == 2

    def test_get_questions(self, sio):
        game_uid: str = self.__class__.game["uid"]

        sio.emit('server/questions/list', {
            "game_uid": game_uid,
        })

        response = sio.receive()
        assert response[0] == "client/questions/list"

        questions = response[1]
        assert (len(questions) == 3)

        self.__class__.questions = questions

    def test_pick_question_works(self, sio):
        game_before: dict = self.__class__.game
        game_uid: str = game_before["uid"]
        current_player_uid = game_before["current_player_uid"]
        player_uid: str = self.__class__.player_1["uid"]
        question_pk: dict = self.__class__.questions[0]["pk"]

        sio.emit("server/questions/pick", {
            "game_uid": game_uid,
            "player_uid": player_uid,
            "question_pk": question_pk,
        })

        response = sio.receive()

        # проверяем что запрос сработал
        assert response[0] == "client/game/updated"

        # проверяем что вопросов в игре стало меньше
        game_after = response[1]
        print(game_before)
        print(game_after)
        assert game_before["questions_count"] - game_after["questions_count"] == 1

        # проверяем что игрок сменился
        assert current_player_uid != game_after["current_player_uid"]

        # запоминаем изменения в игре
        self.__class__.game = game_after

    def test_debug_players(self, sio):
        sio.emit("server/debug/players", {})
        response = sio.receive()
        assert response[0] == "debug"
        data = response[1]
        assert type(data) == dict
        assert (len(data)) == 2


