from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey

Base = declarative_base()

class BookTable(Base):
    __tablename__ = "books"
    isbn = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    publisher = Column(String, nullable=False)
    author = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    category = Column(String, nullable=False)
    publication_date = Column(DateTime, nullable=False)

class TagTable(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

class SentenceTable(Base):
    __tablename__ = "sentences"
    id = Column(Integer, primary_key=True, autoincrement=True)
    isbn = Column(String, ForeignKey("books.isbn"), nullable=False)
    sentence = Column(String, nullable=False)

class BookTagTable(Base):
    __tablename__ = "book_tags"
    isbn = Column(String, ForeignKey("books.isbn"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)

class UserResponseTable(Base):
    __tablename__ = "user_responses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    question_number = Column(Integer, nullable=False)
    sentence_id = Column(Integer, ForeignKey("sentences.id"), nullable=False)
    is_positive = Column(Boolean, nullable=False)
    datetime = Column(DateTime, nullable=True)
