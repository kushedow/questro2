import random

import uuid as uuid
from pydantic import BaseModel, Field
from typing import Optional, OrderedDict


class Category(BaseModel):
    code: str
    title: str
    description: str


class Question(BaseModel):
    pk: int
    text: str
    cat: str


class Player(BaseModel):
    uid: uuid.UUID = Field(default_factory=uuid.uuid4)
    sid: str = None
    game: Optional["Game"] = None


class Game(BaseModel):
    uid: uuid.UUID = Field(default_factory=uuid.uuid4)
    category: str = "default"
    players: OrderedDict[uuid.UUID, Player] = Field(default_factory=dict)
    questions: dict[uuid.UUID, "Question"] = Field(default_factory=dict)

    # Магический метод для получения количества игроков
    @property
    def players_count(self) -> int:
        return len(self.players)

    # Добавление нового игрока
    def add_player(self, player: Player) -> None:
        player.game = self
        self.players[player.uid] = player

    def add_questions(self, questions: list[Question]) -> None:
        """ Добавление  вопросов в игру"""
        for q in questions:
            self.questions[q.pk] = q

    @property
    def questions_count(self) -> int:
        return len(self.questions)

    # Удаляем и возвращаем вопрос по pk
    def pop_question(self, pk: int) -> Question:
        return self.questions.pop(pk, None)

    def get_current_player(self) -> Player | None:
        """Возвращает активного сейчас игрока (в начале игры это владелец комнаты)"""
        if len(self.players) == 0:
            return None
        first_uid = list(self.players.keys())[0]
        return self.players[first_uid]

    def shift_player(self) -> Player | None:
        """Переставляет первого игрока в конец словаря с игроками"""
        current_player = self.get_current_player()
        if not current_player:
            return None

        moving_player = self.players.pop(current_player.uid)
        self.players[current_player.uid] = moving_player

    # Получаем 3 случайных вопроса
    def get_3_questions(self) -> list[Question]:
        random_questions = random.sample(list(self.questions.values()), min(3, len(self.questions)))
        return random_questions

