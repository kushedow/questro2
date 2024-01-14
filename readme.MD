# Questro 2 

Квестро– приложение для обмена вопросами. 
Вы с партнером запускаете приложение,  находите друг друга, 
вы выбираете вопрос для него, он для вас, и так далее, 
вы сидите за ужином или гуляете и общаетесь. 
Есть несколько наборов вопросов.

### Запуск

```python run.py```

### API

### Модель данных

player ```{"uid": str, "is_online": bool, "game_uid": str}```

question ```"pk":int, "text":str, "cat":str```

category ```"code": str, "title",: str "description": str```

game ```{"uid": str,"status": str, "players_count": int, "category": str, "code_to_join": "str"",
"questions_count": int, "current_player_uid": str, "current_question": str,```


Обработка ошибок:

```client/error {"message": "error text"}```

### Создание игрока

Клиент-серверу:
```server/player/create {}```

Сервер-клиенту:
```client/player/created {объект player}```

### Создание игры

Клиент-серверу:
```server/game/create {player_uid: str, category_code: str}```

```player_uid```  uid игрока
```category```  категория вопросов, например default

Сервер-клиенту:
```client/game/updated {объект game}```

или ```client/error {"message": "error text"}```

### Присоединиться к игре

Клиент-серверу:
```server/game/join {player_uid: str, code_to_join_str}```

Сервер всем клиентам::
```client/game/updated {объект game}```

или ```client/error {"message": "error text"}```

### Стартовать игру (кнопка начать)

Клиент-серверу:
```server/game/start {game_uid: str}```

Сервер клиентам:
```client/game/updated {объект game}```

или одному ```client/error {"message": "error text"}```

### Запросить категории

Клиент-серверу:
```server/categories/list {}```

Сервер-клиенту:
```client/categories/list {объект game}```

или ```client/error {"message": "error text"}```

### Запросить три вопроса

Клиент-серверу:
```server/questions/list {game_uid: str}```

Сервер-клиенту:
```client/questions/list {[question, question, question]}```

или ```client/error {"message": "error text"}```

### Выбрать вопрос

Клиент-серверу:
```server/questions/pick {game_uid: str}```

Сервер клиентам:
```client/game/updated {объект game}```

или запросившему ```client/error {"message": "error text"}```
