from uuid import UUID

from config.config import DOC_ID, PLAYER_FIELDS, GAME_FIELDS, QUESTION_FIELDS, CAT_FIELDS
from src.classes.models import Game, Player
from src.classes.sheet_question_importer import SheetQuestionImporter
from loguru import logger
logger.disable(None)


class QuestroService:

    def __init__(self):

        self.DOC_ID: str = DOC_ID
        self.importer = SheetQuestionImporter(doc_id=DOC_ID)
        self.games: dict[UUID: Game] = {}
        self.players: dict[UUID: Player] = {}

        self.categories = {}
        self._load_categories()

    def _load_categories(self):
        self.categories = self.importer.get_cats()
        logger.debug("Категории загружены")

    def get_categories(self):
        return [c.model_dump(include=CAT_FIELDS) for c in self.categories]


    def system_check(self):
        """ Проверяет здоровье системы """
        return self.importer.test_doc()

    def create_player(self, **data) -> dict:
        """ Подключить пользователя к сервису"""
        player = Player(**data)
        player.is_online = True
        self.players[player.uid] = player
        return player.model_dump(include=PLAYER_FIELDS)

    def deactivate_player(self, player_uid):
        """Вырубает отвалившегося игрока"""
        player = self.players.get(player_uid)
        if player is None:
            logger.debug("Игрок не найден")
            return None

        player.is_online = False

        game = player.game
        if game is not None:
            game.status = "waiting"
            return game.model_dump(include=GAME_FIELDS)
        else:
            return None

    def reactivate_player(self, player_uid):
        player = self.players.get(player_uid)
        if player is None:
            logger.debug("Игрок не найден")
            return False

        game = player.game
        if game is None:
            logger.debug("Игрок не прикреплен к игре")
            return False

        player.is_online = True
        game.status = "picking"

        return game.model_dump(include=GAME_FIELDS)


    #########################

    def create_game(self, category: str = "default"):
        """Создает игру, но никого в нее не добавляет"""
        questions: list = self.importer.get_questions(category)
        game = Game(category=category)
        self.games[game.uid] = game

        game.add_questions(questions)

        return game.model_dump(include=GAME_FIELDS)

    def add_player_to_game(self, player_uid, game_uid):

        """Добавляем игрока в комнату"""
        player = self.players.get(player_uid)
        if player is None:
            logger.debug("Игрок не найден")
            return None

        game = self.games.get(game_uid)
        if game is None:
            logger.debug("Игра не найдена")
            return None

        game.add_player(player)
        logger.debug(f"Игрок {player_uid} добавлен в игру")

        return game.model_dump(include=GAME_FIELDS)

    def join_game(self, player_uid, game_code):
        player = self.players.get(player_uid)

        if player is None:
            print("Игрок не найден")
            logger.debug("Игрок не найден")
            return None

        game = None

        for g in self.games.values():
            if g.code_to_join == game_code:
                game = g
                break

        if game is None:
            logger.debug("Игра не найдена")
            return None

        game_data: dict = self.add_player_to_game(player_uid, game.uid)
        logger.debug("Пользователь подсоединен к игре")

        return game_data

    def leave_game(self, player_uid):

        player = self.players.get(player_uid)

        if player is None:
            logger.debug("Игрок не найден")
            return None
        game = player.game
        if game is None:
            logger.debug("У игрока не указана игра")
            return None

        game.remove_player(player)
        logger.debug(f"Игрок {player_uid} покидает комнату {game.uid}")

    def update_game(self, game_uid, data):
        """Обновляем информацию в модели"""
        game = self.games.get(game_uid)

        if game is None:
            return False

        if "status" in data:
            try:
                game.status = data["status"]
                return True
            except ValueError:
                return False

        return game.model_dump(include=GAME_FIELDS)

    def start_game(self, game_uid):

        game = self.games.get(game_uid)
        if game is None:
            logger.debug("Игра не найдена")
            return None

        game.start()

        return game.model_dump(include=GAME_FIELDS)

    def end_game(self, game_uid):
        """Убирает игру с сервера"""
        game = self.games.get(game_uid)
        if game is None:
            return False
        del game
        return True

    def get_my_game_info(self, player_uid) -> dict | None:

        player = self.players.get(player_uid)
        if player is None:
            logger.debug("Игрок не найден")
            return None
        game = player.game
        if game is None:
            logger.debug("У игрока не указана игра")
            return None

        return game.model_dump(include=GAME_FIELDS)

    def get_game_info(self, game_uid: UUID) -> dict | None:

        game = self.games.get(game_uid)
        if game is None:
            return None

        return game.model_dump(include=GAME_FIELDS)

    ###########################

    def get_player_info(self, player_uid):

        player = self.players.get(player_uid)
        if player is None:
            logger.debug("Игрок не найден")
            return None

        return player.model_dump(include=PLAYER_FIELDS)

    def get_current_player(self, game_uid):
        """Показывает верхнего пользователя"""
        game = self.games.get(game_uid)
        if game is None:
            return None
        current_player = game.current_player
        return current_player.model_dump(include=PLAYER_FIELDS)

    def shift_player(self, game_uid):
        """Возвращает и переставляет текущего игрока в конец"""
        game = self.games.get(game_uid)
        if game is None:
            return None

        game.shift_player()
        game.status = "answering"
        return game.model_dump(include=GAME_FIELDS)

    #########################

    def list_3_questions(self, game_uid):

        game = self.games.get(game_uid)
        if game is None:
            return None

        game.status = "picking"
        questions = game.get_3_questions()
        return [q.model_dump(include=QUESTION_FIELDS) for q in questions]

    def pop_question(self, game_uid:str, question_pk: int):
        """Дергает вопрос из игры по его  pk"""
        game = self.games.get(game_uid)
        if game is None:
            return None

        question = game.pop_question(question_pk)

        return question.model_dump(include=QUESTION_FIELDS)




