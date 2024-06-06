from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
    alternative_id: Mapped[str] = mapped_column(String(100), unique=True)

    def get_id(self):
        return self.alternative_id
