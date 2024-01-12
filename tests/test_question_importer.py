import pytest
from _pytest.fixtures import fixture
from gspread.exceptions import APIError, SpreadsheetNotFound, WorksheetNotFound

from src.classes.models import Category, Question
from src.classes.sheet_question_importer import SheetQuestionImporter


class TestQuestionImporter:

    correct_id = "12SEc6ia2j2pezBGloOvV3RzS81vQ1_9ECmpnWvASnV4"
    incorrect_id = "ABC"
    no_worksheet_id = "1hVNcZGZWeUu7MtssM_LWtlxyrcSYTL-P3YYlUNz-Hb0"

    @fixture
    def correct_importer(self):
        return SheetQuestionImporter(self.correct_id)

    def test_correct_id(self):
        importer = SheetQuestionImporter(self.correct_id)
        result = importer.test_doc()
        assert result is True, "Для верных документов тестирование должно проходить успешно"

    def test_incorrect_id(self):
        with pytest.raises(SpreadsheetNotFound) as error:
            SheetQuestionImporter(self.incorrect_id)

    def test_noworksheet_id(self):
        importer = SheetQuestionImporter(self.no_worksheet_id)
        result = importer.test_doc()
        assert result is False

    ###

    def test_get_cats(self, correct_importer):
        cats = correct_importer.get_cats()
        assert len(cats) > 0
        assert type(cats) is list
        assert all([type(c) == Category for c in cats])

    def test_get_questions(self, correct_importer):
        questions = correct_importer.get_questions(category="default")
        assert len(questions) > 0
        assert type(questions) == list
        assert all([type(q) == Question for q in questions])







