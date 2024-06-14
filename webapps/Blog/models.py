from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from sqlalchemy import and_
import os


# Создание базового класса для объявления моделей
Base = declarative_base()

# Определение модели статьи
class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    author_name = Column(String)

# Создание базы данных SQLite и всех определенных таблиц
engine = create_engine('sqlite:///articles.db', connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)

# Создание сессии базы данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Проверка на существование файла базы данных
if os.path.exists("articles.db"):
    print(f"База данных  успешно создана.")
else:
    print(f"Не удалось создать базу данных .")

# Функция для создания статьи в базе данных
def create_article(title: str, description: str, author_name: str):
    db = SessionLocal()
    article = Article(title=title, description=description, author_name=author_name)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article

def update_article(title: str, description: str, author_name: str):
    print(title, description, author_name)
    db = SessionLocal()
    res = db.query(Article).filter(and_(Article.author_name == author_name, Article.title == title)).update({"description": description})
    print(res)
    db.commit()
    #db.refresh(article)
    return res

def delete_article(title: str, description: str, author_name: str):
    print(title, description, author_name)
    db = SessionLocal()
    #article = Article(title=title, description=description, author_name=author_name)
    res = db.query(Article).filter(and_(Article.author_name == author_name, Article.title == title)).delete()
    print(res)
    db.commit()
    #db.refresh(article)
    return res

def article_from_db(author_name: str):
    db = SessionLocal()
    if author_name != "":
        articles = db.query(Article).filter(Article.author_name == author_name).all()
    else:
        articles = db.query(Article).all()
    print(f"Articles - {articles}")
    return articles

def get_description(title: str):
    db = SessionLocal()
    description = db.query(Article).filter(Article.title == title).one()
    return description