from _pytest.fixtures import fixture

from src.service import QuestroService
from loguru import logger
logger.disable(None)

class TestQuestroService:

    @fixture
    def service(self, scope="module"):
        return QuestroService()

    @fixture
    def player(self, service, scope="function"):
        player = service.create_player()
        player_uid = player["uid"]
        return player

    @fixture
    def player_2(self, service, scope="function"):
        player = service.create_player()
        player_uid = player["uid"]
        return player

    @fixture
    def game(self, service):
        game = service.create_game()
        return game

    @fixture
    def game_for_1(self, service, game, player, scope="function"):
        service.add_player_to_game(player["uid"], game["uid"])
        game = service.get_game_info(game["uid"])
        return game
    @fixture
    def game_for_2(self, service, game, player, player_2, scope="function"):

        service.add_player_to_game(player["uid"], game["uid"])
        service.add_player_to_game(player_2["uid"], game["uid"])
        game = service.get_game_info(game["uid"])
        return game

    ###  Категории и вопросы

    def test_categories(self, service):
        cats = service.categories
        assert type(cats) == list
        assert len(cats) > 0;

    ##### Игры и игроки

    def test_create_game(self, service, game, player):
        player_uid = player["uid"]
        game_uid = game["uid"]
        service.add_player_to_game(player_uid, game_uid)
        game_info = service.get_game_info(game_uid)
        assert int(game_info["code_to_join"]) >= 1000

    def test_game_with_2_players(self, game_for_2):
        assert game_for_2["players_count"] == 2

    def test_leave_game(self, service, player, game_for_1):
        """Проверяем что в игре с 2 игроками """
        player_uid = player['uid']
        player_info = service.get_player_info(player_uid)
        game_uid = player_info["game_uid"]

        service.leave_game(player_uid)
        player_info = service.get_player_info(player_uid)
        assert player_info["game_uid"] == None

        game_info = service.get_game_info(game_uid)
        assert game_info["players_count"] == 0

    ##### Вопросы

    def test_three_questions(self, service, game):
        """Проверяем, что можно получить три вопроса"""
        assert game["questions_count"] > 0
        questions = service.list_3_questions(game["uid"])
        assert type(questions) == list
        assert len(questions) == 3
        assert all([type(q) == dict for q in questions])

    def test_pop_question(self, service, game):
        """Убеждаемся что вопросы выдергиваются"""
        count_before = game["questions_count"]
        question = service.pop_question(game["uid"], 16)
        count_after = service.get_game_info(game["uid"])["questions_count"]

        assert count_before - count_after == 1

    def test_shift_player(self, service, game_for_2):

        game_uid = game_for_2["uid"]
        top_player_before = service.get_current_player(game_uid)
        service.shift_player(game_uid)
        top_player_after = service.get_current_player(game_uid)

        assert top_player_before != top_player_after








