from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()

engine = create_engine(
    "sqlite:///db.sqlite3",
    connect_args={"check_same_thread": False},
    echo=True,
)


class KitchenSink(Base):
    __tablename__ = "kitchen_sink"
    id = Column(Integer, primary_key=True)
    bootstra_show_password = Column(String, nullable=False)
    ckeditor4 = Column(Text, nullable=False)
    ckeditor5 = Column(Text, nullable=False)
    simplemde = Column(Text, nullable=False)
