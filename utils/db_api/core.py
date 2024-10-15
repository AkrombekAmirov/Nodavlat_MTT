from .models import User, FileChunk, FileRepository, UserGroup
from sqlmodel import SQLModel, create_engine, Session, select
from typing import Optional, List
from datetime import datetime


class DatabaseService:
    def __init__(self, engine):
        self.engine = engine

    def __add(self, instance):
        """Helper method to add an instance to the session and commit."""
        with Session(self.engine) as session:
            session.add(instance)
            session.commit()
            session.refresh(instance)
            print(f"Added: {instance}")
        return instance.id

    def add_user(self, telegram_id: str, name: str, username: str, telegram_number: Optional[str] = None):
        return self.__add(User(name=name, username=username, telegram_id=telegram_id, telegram_number=telegram_number))

    def _update(self, instance):
        """Helper method to update an instance in the session and commit."""
        with Session(self.engine) as session:
            session.merge(instance)  # Yoki add bilan bir xil instance kiritishingiz mumkin
            session.commit()
            session.refresh(instance)
            print(f"Updated: {instance}")
        return instance.id

    def get_user_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        """Foydalanuvchini telegram_id orqali olish funksiyasi."""
        with Session(self.engine) as session:
            statement = select(User).where(User.telegram_id == telegram_id)
            result = session.exec(statement)
            user = result.one_or_none()  # Agar topilsa bitta foydalanuvchini qaytaradi, aks holda None qaytaradi
            return user
