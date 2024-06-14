import logging
from typing import List
from typing_extensions import Annotated
from fastapi import FastAPI, Response, Cookie, File, UploadFile, Form, Query, Request
from fastapi import HTTPException
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from fastapi import APIRouter

from webapps.Blog.models import create_article, article_from_db, get_description, update_article, delete_article
from pydantic import BaseModel

from webapps.Blog.GPT import retelling


logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="templates")
server = APIRouter(include_in_schema=False)

current_user = ""

def set_user(value):
    global current_user
    print(f"value {value}")
    current_user = value

def get_current_user():
    print(f"curr {current_user}")
    return current_user

@server.get("/auth/logout")
def logout():
    global current_user
    current_user = ""
    response = RedirectResponse("/login/")
    return response


@server.get("/get_current_user")
def get_user():
    return {"username": current_user}


# на главной странице
@server.get("/create-article")
def create_article_page(request: Request):
    #return templates.TemplateResponse("home/article.html")#, {"request": request, "email": user.email})

    return templates.TemplateResponse("home/article.html", {"request": request})


@server.get("/AllArticles")
def allArticles(request: Request):
    return templates.TemplateResponse("home/AllArticles.html", {"request": request})


class ArticleCreate(BaseModel):
    title: str
    description: str

# создание статьи
@server.post("/articles/create")
async def create_article_handler(article: ArticleCreate):
    author_name = current_user
    print(f"Author name + {author_name}")
    # Создаем статью в базе данных
    created_article = create_article(article.title, article.description, author_name)

    return {"message": "Статья успешно создана", "article": created_article}


@server.post("/articles/update")
async def update_article_handler(article: ArticleCreate):
    author_name = current_user
    print(f"Author name + {author_name}")
    # Создаем статью в базе данных
    updated_article = update_article(article.title, article.description, author_name)

    return {"message": "Статья успешно updated", "article": updated_article}


@server.post("/delete")
async def delete_article_handler(article: ArticleCreate):
    author_name = current_user
    print(f"Author name + {author_name}")
    # Создаем статью в базе данных
    deleted_article = delete_article(article.title, article.description, author_name)
    return RedirectResponse("/login/")

# Маршрут для получения списка статей
@server.get("/articles")
def get_articles():
    print(f"Author name + {current_user}")
    return article_from_db(current_user)

@server.route("/fullArticle")
def fullart(request: Request, title: str = Form(...)):
    return templates.TemplateResponse("/home/fullArticle.html", {"request": request, "title": title})


# Маршрут для получения списка статей
@server.get("/all_articles")
def get_articles():
    return article_from_db("")


@server.get("/article/description")
def get_article_by_title(title: str = Query(...)):
    print(f'title: {title}')
    return get_description(title)


#пересказ
@server.get("/retelling")
def retelling_url(title: str = Query(...)):
    print("Retelling zahod")
    
    print(f"retelling ok")

    description = get_description(title)
    return retelling(description.description)
