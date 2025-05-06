from app import app, db, Candidate

# Створюємо контекст додатку для доступу до бази даних
with app.app_context():
    # Створюємо таблиці в базі даних
    db.create_all()

    # Додаємо кандидатів, якщо вони ще не існують
    if Candidate.query.count() == 0:
        db.session.add_all([
            Candidate(name='Władimir Putin'),
            Candidate(name='Aleksander Łukaszenka'),
            Candidate(name='Wołodymyr Zełenskyj'),
            Candidate(name='Kasim-Żomart Tokajew'),
            Candidate(name='Andrzej Duda')
        ])
        db.session.commit()
        print("Baza danych została utworzona, a kandydaci dodani!")
    else:
        print("Kandydaci już istnieją w bazie danych.")
