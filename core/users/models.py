from sqlalchemy import Column, String, Integer, Boolean, func, DateTime
from core.database import Base
from sqlalchemy.orm import relationship
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)

    username = Column(String(150), nullable=False)
    password = Column(String, nullable=False)
    isActive = Column(Boolean, default=True)
    created_date = Column(DateTime, server_default=func.now())
    updated_date = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    tasks = relationship("TaskModel", back_populates="user")


    def hash_password(self, plain_password: str) -> str:
        return pwd_context.hash(plain_password)
    

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.password)
    

    def set_password(self, plain_text: str) -> None:
        self.password = self.hash_password(plain_text)


    def verify_and_update_password(self, plain_password: str) -> tuple[bool, str | None]:
        """
        اگر هش قدیمی باشد (مثلا bcrypt)، new_hash برمی‌گرداند
        تا همان لحظه در DB با argon2 آپدیت شود.
        """
        return pwd_context.verify_and_update(plain_password, self.password)