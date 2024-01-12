import pathlib

DOC_ID = '12SEc6ia2j2pezBGloOvV3RzS81vQ1_9ECmpnWvASnV4'
KEYFILE_PATH = pathlib.Path(__file__).parent.absolute() / "keyfile.json"

GAME_FIELDS = {
    "uid",
    "status",
    "players_count",
    "category",
    "code_to_join",
    "questions_count",
    "current_player_uid",
    "current_question",
}

PLAYER_FIELDS = {"uid", "sid", "is_online", "game_uid"}
QUESTION_FIELDS = {"pk", "text", "cat"}
CAT_FIELDS = {"code", "title", "description"}
