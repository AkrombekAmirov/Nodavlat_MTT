from .models import User, UserGroup
from sqlmodel import SQLModel, create_engine, Session, select
from typing import Optional, List
from datetime import datetime
from sqlalchemy import exists


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

    def add_user(self, telegram_id: str, username: str, telegram_number: Optional[str] = None,
                 telegram_name: Optional[str] = None):
        return self.__add(User(username=username, telegram_id=telegram_id, telegram_number=telegram_number,
                               telegram_name=telegram_name))

    def _update(self, instance):
        """Helper method to update an instance in the session and commit."""
        with Session(self.engine) as session:
            session.merge(instance)  # Yoki add bilan bir xil instance kiritishingiz mumkin
            session.commit()
            session.refresh(instance)
            print(f"Updated: {instance}")
        return instance.id

    def update_user(self, telegram_id: str, name: str, passport: str, faculty: str, viloyat: str, tuman: str):
        """Foydalanuvchi ma'lumotlarini yangilash funksiyasi."""
        with Session(self.engine) as session:
            # Foydalanuvchini telegram_id orqali qidiramiz
            user = session.exec(select(User).where(User.telegram_id == telegram_id)).one_or_none()

            if not user:
                print(f"User with telegram_id {telegram_id} not found.")
                return None

            # Foydalanuvchining ma'lumotlarini dinamik tarzda yangilaymiz
            updated_fields = {"name": name, "passport": passport, "faculty": faculty, "viloyat": viloyat, "tuman": tuman}
            for field, value in updated_fields.items():
                if value:  # Faqat bo'sh bo'lmagan qiymatlarni yangilash
                    setattr(user, field, value)

            # O'zgarishlarni saqlash
            session.commit()
            session.refresh(user)
            print(f"Updated user: {user}")
            return user.id

    def update_(self, telegram_id: str, updated_fields):
        with Session(self.engine) as session:
            user = session.exec(select(User).where(User.telegram_id == telegram_id)).one_or_none()
            for field, value in updated_fields.items():
                if value:  # Faqat bo'sh bo'lmagan qiymatlarni yangilash
                    setattr(user, field, value)

            session.commit()
            session.refresh(user)
            print(f"Updated user: {user}")
            return user.id

    def get_user_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        """Foydalanuvchini telegram_id orqali olish funksiyasi."""
        with Session(self.engine) as session:
            statement = select(User).where(User.telegram_id == str(telegram_id))
            result = session.exec(statement)
            user = result.one_or_none()  # Agar topilsa bitta foydalanuvchini qaytaradi, aks holda None qaytaradi
            return user
    def get_user_exists(self, telegram_id: str) -> Optional[User]:
        with Session(self.engine) as session:
            if not session.exec(select(exists().where(User.telegram_id == str(telegram_id)))).one():
                return None
            elif session.exec(select(exists().where(User.telegram_id == str(telegram_id)))).one():
                return True

    def get_max_contract_number(self):
        try:
            with Session(self.engine) as session:
                next_contract_number = f"{int(session.query(User).order_by(User.contract_number.desc()).first().contract_number) + 1:03d}"  # 3 xonalik raqamga o'tkazish
                return str(next_contract_number)
        except Exception as e:
            return e
        finally:
            session.close()

    def get_faculty_number(self, faculty: str):
        try:
            with Session(self.engine) as session:
                statement1 = session.exec(select(User).where(User.faculty == str(faculty))).all()
                return statement1
        except Exception as e:
            return e
        finally:
            session.close()
