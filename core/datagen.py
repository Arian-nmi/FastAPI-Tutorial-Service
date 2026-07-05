from core.database import SessionLocal
from sqlalchemy.orm import Session
from users.models import UserModel
from tasks.models import TaskModel
from faker import Faker


fake = Faker()

def seed_user(db):
    user = UserModel(username=fake.user_name())
    user.set_password("12345")
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"User created with username: {user.username} and ID: {user.id}")
    return user


def seed_tasks(db, user, count=10):
    tasks_list = []
    for _ in range(count):
        tasks_list.append(
            TaskModel(
                userID= user.id,
                title= fake.sentence(nb_words=6),
                description= fake.text(),
                is_completed= fake.boolean(),
            )
        )
    db.add_all(tasks_list)
    db.commit()
    print(f"Added 10 tasks for userID: {user.id}")




def main():
    db = SessionLocal()
    try:
        user = seed_user(db)
        seed_tasks(db, user)
    finally:
        db.close()


if __name__ == "__main__":
    main()