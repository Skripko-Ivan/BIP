import logging
from typing_extensions import Annotated, List
from fastapi import FastAPI, Response, Cookie, File, UploadFile, Form, Query
from fastapi import HTTPException
from keycloak import KeycloakOpenID
from starlette.responses import RedirectResponse
from models import create_article, article_from_db, get_description, update_article, delete_article
from pydantic import BaseModel

from settings import settings
from GPT import retelling


logger = logging.getLogger(__name__)
app = FastAPI(root_path="/api/v1")

keycloak_openid = KeycloakOpenID(
    server_url=settings.KEYCLOAK_URL,
    realm_name=settings.REALM,
    client_id=settings.CLIENT_ID,
    client_secret_key=settings.CLIENT_SECRET_KEY
)

options = {"verify_signature": True, "verify_aud": False, "verify_exp": True}


def decode_token(token: str):
    KEYCLOAK_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\n" + keycloak_openid.public_key() + "\n-----END PUBLIC KEY-----"
    try:
        token_info = keycloak_openid.decode_token(token, key=KEYCLOAK_PUBLIC_KEY, options=options)
    except Exception as e:
        logger.error(e)
        token_info = None
    return token_info


@app.get("/auth/check")
def check_auth(access_token: Annotated[str, Cookie()] = ""):
    if access_token:
        token_info = decode_token(access_token)
        redirect = token_info is None
    else:
        redirect = True
    url = keycloak_openid.auth_url(scope="openid+profile", redirect_uri=settings.REDIRECT_URL)
    return {
        "url": url,
        "redirect": redirect
    }


@app.get("/auth/logout")
def logout(refresh_token: Annotated[str | None, Cookie()] = None):
    keycloak_openid.logout(refresh_token)
    response = RedirectResponse("/")
    response.set_cookie(key="access_token", value="")
    response.set_cookie(key="refresh_token", value="")
    return response


@app.get("/auth/callback")
def auth_callback(code: str = "", ):
    access_token = keycloak_openid.token(
        grant_type='authorization_code',
        code=code,
        redirect_uri=settings.REDIRECT_URL)
    response = RedirectResponse("/")
    response.set_cookie(key="access_token", value=access_token["access_token"])
    response.set_cookie(key="refresh_token", value=access_token["refresh_token"])
    return response

@app.get("/get_current_user")
def get_user(access_token: Annotated[str, Cookie()] = ""):
    if not access_token:
        raise HTTPException(status_code=401, detail="Need authenticate")
    
    token_info = decode_token(access_token)
    print(f"token_info {token_info}")
    username = token_info['preferred_username']
    print(f"usernae - {username}")

    return {"username": username}

# на главной странице
@app.get("/create-article")
def create_article_page(access_token: Annotated[str, Cookie()] = ""):
    if access_token:
        token_info = decode_token(access_token)
        if token_info:
            # Пользователь авторизован, и токен валиден
            return RedirectResponse(url="/article.html")
        else:
            # Токен недействителен или истек. Перенаправить на страницу входа
            return RedirectResponse(url=keycloak_openid.auth_url(scope="openid profile", redirect_uri=settings.REDIRECT_URL))
    else:
        # Нет токена доступа. Перенаправить на страницу входа
        return RedirectResponse(url=keycloak_openid.auth_url(scope="openid profile", redirect_uri=settings.REDIRECT_URL))
    

class ArticleCreate(BaseModel):
    title: str
    description: str

# создание статьи
@app.post("/articles/create")
async def create_article_handler(article: ArticleCreate, access_token: Annotated[str, Cookie()] = ""):
    # Проверяем наличие токена доступа
    if not access_token:
        raise HTTPException(status_code=401, detail="Need authenticate")
    
    token_info = decode_token(access_token)
    print(f"token_info {token_info}")
    author_name = token_info['preferred_username']

    print(f"Author name + {author_name}")

    # Создаем статью в базе данных
    created_article = create_article(article.title, article.description, author_name)

    return {"message": "Article was created successful", "article": created_article}


@app.post("/articles/update")
async def update_article_handler(article: ArticleCreate, access_token: Annotated[str, Cookie()] = ""):
    # Проверяем наличие токена доступа
    if not access_token:
        raise HTTPException(status_code=401, detail="Need authenticate")
    
    token_info = decode_token(access_token)
    print(f"token_info {token_info}")
    author_name = token_info['preferred_username']

    print(f"Author name + {author_name}")

    # Создаем статью в базе данных
    updated_article = update_article(article.title, article.description, author_name)

    return {"message": "Article was updated successful", "article": updated_article}


@app.post("/articles/delete")
async def delete_article_handler(article: ArticleCreate, access_token: Annotated[str, Cookie()] = ""):
    # Проверяем наличие токена доступа
    if not access_token:
        raise HTTPException(status_code=401, detail="Need authenticate")
    
    token_info = decode_token(access_token)
    print(f"token_info {token_info}")
    author_name = token_info['preferred_username']

    print(f"Author name + {author_name}")

    # Создаем статью в базе данных
    deleted_article = delete_article(article.title, article.description, author_name)

    return {"message": "Article was deleted successful", "article": deleted_article}

# Маршрут для получения списка статей
@app.get("/articles")
def get_articles(access_token: Annotated[str, Cookie()] = ""):
    if not access_token:
       raise HTTPException(status_code=401, detail="Need authenticate")
    
    token_info = decode_token(access_token)
    print(f"token_info {token_info}")
    author_name = token_info['preferred_username']
        
    return article_from_db(author_name)

# Маршрут для получения списка статей
@app.get("/all_articles")
def get_articles(access_token: Annotated[str, Cookie()] = ""):

    if not access_token:
        raise HTTPException(status_code=401, detail="Need authenticate")
    
        
    return article_from_db("")

@app.get("/article/description")
def get_article_by_title(title: str = Query(...), access_token: Annotated[str, Cookie()] = ""):

    if not access_token:
        raise HTTPException(status_code=401, detail="Need authenticate")

    print(f'title: {title}')
    return get_description(title)

#пересказ
@app.get("/retelling")
def retelling_url(title: str = Query(...), access_token: Annotated[str, Cookie()] = ""):
    print("Retelling zahod")
    if not access_token:
        raise HTTPException(status_code=401, detail="Need authenticate")
    
    print(f"retelling ok")

    description = get_description(title)
    return retelling(description.description)
