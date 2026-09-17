import pytest
import requests
from config import Config
import allure
import json

def search_by_name(session, query, page=1, limit=10):
    """Поиск фильмов по названию через /v1.4/movie/search."""
    url = f"{Config.BASE_URL_API}/movie/search"
    return session.get(
        url,
        params={"query": query, "page": page, "limit": limit},
    )
    


def search_by_id(session, movie_id):
    """Получение фильма по ID через /v1.4/movie/{id}."""
    url = f"{Config.BASE_URL_API}/movie/{movie_id}"
    return session.get(url)


def search_with_filters(session, **params):
    """Универсальный поиск с фильтрами через /v1.4/movie."""
    url = f"{Config.BASE_URL_API}/movie"
    return session.get(url, params=params)


# --- Тест-кейсы --


@allure.feature("API Кинопоиск")
@allure.story("Поиск фильмов")

def test_search_movie_by_name(session):
    """Тест 1: Поиск фильма по названию."""
    query = "Зелёная миля"

    with allure.step(f"Шаг 1: Подготовка параметров поиска"):
        allure.attach(query, name="Поисковый запрос", attachment_type=allure.attachment_type.TEXT)
        assert query, "Запрос на поиск не может быть пустым"

    with allure.step(f"Шаг 2: Отправка GET-запроса к эндпоинту /movie/search"):
        response = search_by_name(session, query=query)
        
        # Добавляем детали запроса в отчет
        allure.attach(response.url, name="URL запроса", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response.status_code), name="Статус код ответа", attachment_type=allure.attachment_type.TEXT)

    with allure.step(f"Шаг 3: Проверка статуса ответа"):
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}: {response.text}"

    with allure.step(f"Шаг 4: Валидация содержимого ответа"):
        data = response.json()
        assert "docs" in data, "В ответе отсутствует поле 'docs'"
        assert len(data["docs"]) > 0, "Список найденных фильмов пуст"

        # Проверяем, что хотя бы один результат содержит искомое название
        movie = data["docs"][0]
        movie_name = movie.get("name") or movie.get("alternativeName") or ""
        
        allure.attach(
            json.dumps(movie, ensure_ascii=False, indent=2), 
            name=f"Найденный фильм: {movie_name}", 
            type=allure.attachment_type.JSON
        )

        assert "миля" in movie_name.lower(), (
            f"Найденный фильм '{movie_name}' не совпадает с запросом '{query}'"
        )


@allure.feature("API Кинопоиск")
@allure.story("Поиск фильмов по ID")
def test_search_movie_by_id(session):
   """Тест-кейс 2: Поиск фильма по ID."""
   movie_id = 326  # Побег из Шоушенка

   with allure.step(f"Шаг 1: Формирование URL для получения фильма по ID {movie_id}"):
        url = f"{Config.BASE_URL_API}/movie/{movie_id}"
        allure.attach(url, name="Целевой URL", attachment_type=allure.attachment_type.TEXT)

   with allure.step(f"Шаг 2: Выполнение запроса к ресурсу /movie/{{id}}"):
        response = session.get(url)
        allure.attach(str(response.status_code), name="Статус код", attachment_type=allure.attachment_type.TEXT)

   with allure.step(f"Шаг 3: Проверка успешности запроса"):
        assert response.status_code == 200, f"Ошибка при получении фильма: {response.text}"

   with allure.step(f"Шаг 4: Проверка соответствия ID в ответе запрошенному"):
        data_resp = response.json()
        
        allure.attach(
            json.dumps(data_resp, ensure_ascii=False, indent=2), 
            name="Данные фильма", 
            type=allure.attachment_type.JSON
        )

        assert data_resp.get("id") == movie_id, f"ID не совпадает: ожидалось {movie_id}, получено {data_resp.get('id')}"
        assert data_resp.get("name") is not None, "Поле 'name' в ответе равно None"



@allure.feature("API Кинопоиск")
@allure.story("Поиск фильмов")
def test_search_movie_by_partial_name(session):
    """Тест-кейс 3: Поиск по неполному названию."""
    query = "Шоушенк"

    with allure.step(f"Шаг 1: Отправка запроса с частичным названием '{query}'"):
        response = search_by_name(session, query=query)
        allure.attach(response.url, name="URL запроса", attachment_type=allure.attachment_type.TEXT)

    with allure.step(f"Шаг 2: Проверка статуса ответа"):
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

    with allure.step(f"Шаг 3: Валидация результатов поиска"):
        data = response.json()
        assert "docs" in data, "В ответе отсутствует поле 'docs'"
        assert len(data["docs"]) > 0, "По неполному названию не найдено ни одного фильма"

        found = False
        for movie in data["docs"]:
            name = (movie.get("name") or "").lower()
            if "шоушенк" in name:
                found = True
                allure.attach(
                    json.dumps(movie, ensure_ascii=False, indent=2),
                    name=f"Найдена карточка: {movie.get('name')}",
                    type=allure.attachment_type.JSON
                )
                break
        
        assert found, "Среди результатов нет фильма со словом 'шоушенк'"


@allure.feature("API Кинопоиск")
@allure.story("Обработка ошибок")
def test_search_movie_without_name(session):
    """Тест-кейс 4: Поиск фильма без названия (пустой запрос)."""
    query = ""

    with allure.step(f"Шаг 1: Попытка поиска с пустым запросом"):
        response = search_by_name(session, query=query)
        allure.attach(str(response.status_code), name="Полученный статус код", attachment_type=allure.attachment_type.TEXT)

    with allure.step(f"Шаг 2: Проверка ожидаемой ошибки API"):
        # API может вернуть 400 (параметр обязателен) — это корректное поведение
        assert response.status_code in (400, 404), (
            f"Ожидался статус 400 или 404 для пустого запроса, "
            f"получен {response.status_code}: {response.text}"
        )

    with allure.step(f"Шаг 3: Проверка тела ответа на наличие описания ошибки"):
        data = response.json()
        allure.attach(json.dumps(data, ensure_ascii=False, indent=2), name="Тело ошибки", attachment_type=allure.attachment_type.JSON)
        assert "message" in data or "error" in data, (
            "В ответе нет поля 'message' или 'error' с описанием ошибки"
        )


@allure.feature("API Кинопоиск")
@allure.story("Фильтрация данных")
def test_search_movie_with_invalid_year(session):
    """Тест-кейс 5: Поиск фильма с некорректным значением года."""
    year = "999999"

    with allure.step(f"Шаг 1: Отправка запроса с некорректным годом {year}"):
        response = search_with_filters(session, year=year, page=1, limit=10)
        allure.attach(response.url, name="URL с фильтром года", attachment_type=allure.attachment_type.TEXT)

    with allure.step(f"Шаг 2: Анализ ответа API на некорректный год"):
        if response.status_code == 200:
            data = response.json()
            allure.attach(json.dumps(data, ensure_ascii=False, indent=2), name="Ответ API (200)", attachment_type=allure.attachment_type.JSON)
            # Если API возвращает 200, список должен быть пустым
            assert len(data.get("docs", [])) == 0, (
                "Найдены фильмы с несуществующим годом 999999 — некорректное поведение API"
            )
        elif response.status_code == 400:
            data = response.json()
            allure.attach(json.dumps(data, ensure_ascii=False, indent=2), name="Ответ API (400)", attachment_type=allure.attachment_type.JSON)
            # Если API возвращает 400 — это тоже допустимая реакция
            assert "message" in data or "error" in data, (
                "В ответе нет описания ошибки для некорректного года"
            )
        else:
            pytest.fail(
                f"Неожиданный статус {response.status_code} для некорректного года: {response.text}"
            )