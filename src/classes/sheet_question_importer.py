import gspread
from oauth2client.service_account import ServiceAccountCredentials

from src.classes.models import Category, Question


class SheetQuestionImporter:
    def __init__(self, doc_id: str) -> None:
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        # Если вы используете другой способ аутентификации, укажите его здесь
        self.creds = ServiceAccountCredentials.from_json_keyfile_name('config/questro-bd8c31385bfc.json', self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open_by_key(doc_id)

    def test_doc(self) -> bool:
        try:
            # Пробуем получить все данные с первого листа
            self.sheet.worksheet('question')
            self.sheet.worksheet('categories')
            return True
        except:
            return False

    def get_cats(self) -> list[Category]:
        """Загружает список категорий со вкладки Категории"""
        categories_sheet = self.sheet.worksheet('categories')
        # Примерное получение данных, но нужно учесть, что первая строка - это заголовки
        categories_records = categories_sheet.get_all_records()
        categories = [Category.model_validate(record) for record in categories_records]
        return categories

    def get_questions(self, category) -> list[Question]:

        questions_sheet = self.sheet.worksheet('questions')
        all_records = questions_sheet.get_all_records()

        filtered_questions = [
            Question.model_validate(record)
            for record in all_records
            if record['cat'] == category
            and type(record['pk']) == int
        ]

        return filtered_questions
