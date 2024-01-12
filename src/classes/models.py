import random

import uuid as uuid
from enum import Enum

from pydantic import BaseModel, Field, computed_field
from typing import Optional, OrderedDict


class StatusEnum(str, Enum):
    """Статус для игры"""
    waiting = "waiting"  # игра создана, но никто не присоединился, играть нельзя

    picking = "picking"  # игрок выбирает вопрос, остальные ждут
    answering = "answering"  # игрок отвечает на вопрос, остальные ждут

    error = "error"  # что-то сломалось, предлагаем варианты
    over = "over"  # игра завершена


class Category(BaseModel):
    """Категории вопросов"""
    code: str
    title: str
    description: str


class Question(BaseModel):
    """Вопросы"""
    pk: int
    text: str
    cat: str


class Player(BaseModel):
    """Игроки"""
    uid: str = Field(default_factory=lambda: uuid.uuid4().hex)
    # sid: str = None
    game: Optional['Game'] = None
    is_online: bool = False

    @computed_field
    @property
    def game_uid(self) -> str | None:
        if self.game is not None:
            return self.game.uid
        return None


class Game(BaseModel):
    #  TODO добавить проверку уникальности кода через глобальный синглтон

    uid: str = Field(default_factory=lambda: uuid.uuid4().hex)
    category: str = "default"
    status: Enum = "waiting"
    players: OrderedDict[str, Player] = Field(default_factory=dict)
    questions: dict[int, "Question"] = Field(default_factory=dict)
    code_to_join: str = Field(default_factory=lambda: str(random.randint(1000, 9999)))
    current_question: Question = None

    @computed_field
    @property
    def players_count(self) -> int:
        """Возврашает количество игроков"""
        return len(self.players)

    @computed_field
    @property
    def current_player(self) -> Player | None:
        """Возвращает активного сейчас игрока (в начале игры это владелец комнаты)"""
        if len(self.players) == 0:
            return None
        first_uid = list(self.players.keys())[0]
        return self.players[first_uid]

    @computed_field
    @property
    def current_player_uid(self) -> str | None:
        player = self.current_player
        if player is None:
            return None
        else:
            return player.uid

    def start(self) -> None:

        self.status = StatusEnum("picking")

    def add_player(self, player: Player) -> None:
        """Добавляем нового игрока"""
        player.game = self
        self.players[player.uid] = player

        if len(self.players) >= 2:
            self.status = StatusEnum("picking")

    def remove_player(self, player: Player) -> None:
        player.game = None
        self.players.pop(player.uid)

    def shift_player(self) -> Player | None:
        """Переставляет первого игрока в конец словаря с игроками"""
        current_player = self.current_player
        if not current_player:
            return None

        moving_player = self.players.pop(current_player.uid)
        self.players[current_player.uid] = moving_player

    def get_players_except(self, uid) -> list[Player]:
        """Возвращает игроков кроме указанного """
        players_except = [p for p in self.players.values() if p.uid != uid]
        return players_except


    @computed_field
    @property
    def questions_count(self) -> int:
        """Возврашаем количество вопросов"""
        return len(self.questions)

    def add_questions(self, questions: list[Question]) -> None:
        """ Добавляем пачку вопросов в игру"""
        for q in questions:
            self.questions[q.pk] = q

    def pop_question(self, pk: int) -> Question:
        """Удаляем и возвращаем вопрос по его pk"""
        question: Question = self.questions.pop(pk)
        self.current_question = question
        return question

    def get_3_questions(self) -> list[Question]:
        """Получаем 3 случайных вопроса, а если трех нет, то сколько получится"""
        random_questions = random.sample(list(self.questions.values()), min(3, len(self.questions)))
        return random_questions

