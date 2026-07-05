from fastapi.testclient import TestClient
from sqlalchemy import StaticPool
from core.database import Base, create_engine, sessionmaker, get_db
from main import app
import pytest
from faker import Faker
from users.models import UserModel
from tasks.models import TaskModel
from auth.jwt_auth import generate_access_token


fake = Faker()

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
    )

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# module
@pytest.fixture(scope="package")
def db_session():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# module
@pytest.fixture(scope="module", autouse=True)
def override_dependancies(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.pop(get_db, None)


# session
@pytest.fixture(scope="session", autouse=True)
def tearup_and_down_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="package")
def anon_client():
    client = TestClient(app)
    yield client


@pytest.fixture(scope="package")
def auth_client(db_session):
    client = TestClient(app)
    user = db_session.query(UserModel).filter_by(username="testuser").one()
    access_token = generate_access_token(user.id)
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    yield client


@pytest.fixture(scope="package", autouse=True)
def generate_mock_data(db_session):
    user = UserModel(username="testuser")
    user.set_password("12345678")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    print(f"User created with username: {user.username} and ID: {user.id}")

    tasks_list = []
    for _ in range(10):
        tasks_list.append(
            TaskModel(
                userID= user.id,
                title= fake.sentence(nb_words=6),
                description= fake.text(max_nb_chars=150),
                is_completed= fake.boolean(),
            )
        )
    db_session.add_all(tasks_list)
    db_session.commit()
    print(f"Added 10 tasks for userID: {user.id}")


@pytest.fixture(scope="package", autouse=True)
def random_task(db_session):
    user = db_session.query(UserModel).filter_by(username="testuser").one()
    task = db_session.query(TaskModel).filter_by(userID=user.id).first()
    return task