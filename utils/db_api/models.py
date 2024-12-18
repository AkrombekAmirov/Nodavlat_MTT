from sqlmodel import SQLModel, Field
from datetime import datetime
from pytz import timezone


class User(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True)
    username: str
    telegram_id: str
    telegram_name: str
    telegram_number: str
    name: str = Field(default="")
    tuman: str = Field(default="")
    viloyat: str = Field(default="")
    passport: str = Field(default="")
    contract_number: str = Field(default="")
    telegram_file_id: str = Field(default="")
    telegram_ariza_id: str = Field(default="")
    ariza_id: str = Field(default="")
    file_id: str = Field(default="")
    faculty: str = Field(default="")
    group: str = Field(default='001')
    status: str = Field(default="False")
    created_date: str
    created_time: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Hozirgi vaqtdagi o'zgaruvchilarni o'rnatamiz
        now = datetime.now(timezone('Asia/Tashkent'))
        self.created_date = now.strftime("%Y-%m-%d")
        self.created_time = now.strftime("%H:%M:%S")


class FileChunk(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True)
    file_id: str
    chunk: bytes


class FileRepository(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True)
    user_id: str
    contract_number: str
    content_type: str
    file_id: str
    date: str = Field(default=datetime.now().strftime("%Y-%m-%d"))
    time: str = Field(default=datetime.now().strftime("%H:%M:%S"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Hozirgi vaqtdagi o'zgaruvchilarni o'rnatamiz
        now = datetime.now(timezone('Asia/Tashkent'))
        self.date = now.strftime("%Y-%m-%d")
        self.time = now.strftime("%H:%M:%S")


class UserGroup(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True)
    faculty_name: str
    group_name: str
    group_id: str
    date: str = Field(default=datetime.now().strftime("%Y-%m-%d"))
    time: str = Field(default=datetime.now().strftime("%H:%M:%S"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Hozirgi vaqtdagi o'zgaruvchilarni o'rnatamiz
        now = datetime.now(timezone('Asia/Tashkent'))
        self.date = now.strftime("%Y-%m-%d")
        self.time = now.strftime("%H:%M:%S")
