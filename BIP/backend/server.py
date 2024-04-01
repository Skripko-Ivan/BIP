import logging
from typing import Annotated, List
from fastapi import FastAPI, Response, Cookie, File, UploadFile, Form, Query
from keycloak import KeycloakOpenID
from starlette.responses import RedirectResponse
from models import create_article, article_from_db, get_description
from pydantic import BaseModel

from settings import settings

logger = logging.getLogger(__name__)
app = FastAPI()

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

@app.post("/articles/create")
async def create_article_handler(article: ArticleCreate, access_token: Annotated[str, Cookie()] = ""):
    # Проверяем наличие токена доступа
    if not access_token:
        raise HTTPException(status_code=401, detail="Требуется аутентификация")
    
    author_name = "topp"
    if access_token:
        token_info = decode_token(access_token)
        print(f"token_info {token_info}")
        #author_name = token_info['preferred_username']
    else:
        # Получаем информацию об авторе из токена
        author_name = "Unknown"  # Здесь можно добавить вашу логику получения имени автора

    print(f"Author name + {author_name}")

    # Создаем статью в базе данных
    created_article = create_article(article.title, article.description, author_name)

    return {"message": "Статья успешно создана", "article": created_article}

# Маршрут для получения списка статей
@app.get("/articles")
def get_articles(access_token: Annotated[str, Cookie()] = ""):

    #if not access_token:
     #   raise HTTPException(status_code=401, detail="Требуется аутентификация")
    
    author_name = "topp"
    if access_token:
        token_info = decode_token(access_token)
        print(f"token_info {token_info}")
        #author_name = token_info['preferred_username']
        
    return article_from_db(author_name)

@app.get("/article/description")
def get_article_by_title(title: str = Query(...)):
    print(f'title: {title}')
    return get_description(title)
