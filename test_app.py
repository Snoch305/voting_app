import unittest
from app import app, users, votes  # Імпортуємо Flask додаток, список користувачів та голоси

class VotingAppTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Цей метод виконується один раз перед всіма тестами."""
        cls.client = app.test_client()  # Створюємо тестовий клієнт Flask

    def setUp(self):
        """Цей метод виконується перед кожним тестом."""
        users.clear()  # Очищаємо список користувачів
        for key in votes:
            votes[key] = 0  # Обнуляємо голоси

    def test_register_user(self):
        """Тестуємо реєстрацію користувача."""
        response = self.client.post('/', data={'username': 'user1', 'password': 'pass1'})
        self.assertEqual(response.status_code, 302)  # Очікуємо редирект на /register

    def test_vote(self):
        """Тестуємо голосування."""
        self.client.post('/', data={'username': 'user2', 'password': 'pass2'})
        self.client.post('/vote', data={'candidate': 'Кандидат 1'})
        self.assertEqual(votes['Кандидат 1'], 1)  # Перевіряємо, чи проголосували за кандидата 1

    def test_result(self):
        """Тестуємо сторінку результатів голосування."""
        response = self.client.get('/result')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Кандидат 1', response.data.decode('utf-8'))  # Перевіряємо, чи є кандидати в результатах

if __name__ == '__main__':
    unittest.main()

