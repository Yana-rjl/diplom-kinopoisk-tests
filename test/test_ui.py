import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium import webdriver
from config import Config  # Импорт из config.py
from pages.mainpage import MainPage
from pages.tickets_page import TicketsPage


# --- Вспомогательные функции ---

def take_screenshot(driver):
    """Делает скриншот и возвращает байты для Allure."""
    try:
        return driver.get_screenshot_as_png()
    except Exception:
        return None

def wait_for_element(driver, locator, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(locator)
    )

def wait_for_clickable(driver, locator, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(locator)
    )


# --- Тест-кейсы ---


@allure.feature("UI Кинопоиск")
@allure.story("Поиск и фильтрация")
@pytest.mark.smoke
def test_keywords_filter_finds_movies(driver):
    """Тест 1: Фильтр 'Ключевые слова' находит фильмы по ключевым словам."""
    query = "зеленая миля"
    main = MainPage(driver)
    with allure.step(f"Шаг 1: Переход на главную страницу {Config.BASE_URL_UI}"):
        main.open_main_page()
    

    with allure.step(f"Шаг 2: Ввод поискового запроса '{query}'"):
        main.make_search(query)
        allure.attach(query, name="Введённый запрос", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Шаг 3: Отправка запроса (нажатие Enter/Submit)"):
         main.search_input

    with allure.step("Шаг 4: Ожидание результатов поиска и проверка наличия карточек"):
        wait_for_element(driver, (By.CSS_SELECTOR, ".selection-card, .film-item"))
        results = driver.find_elements(By.CSS_SELECTOR, ".selection-card, .film-item")
        
        count = len(results)
        allure.attach(str(count), name="Количество найденных карточек", attachment_type=allure.attachment_type.TEXT)
        assert count > 0, f"Не найдены фильмы по запросу '{query}'. Найдено: {count}"

@allure.feature("UI Кинопоиск")
@allure.story("Магазин и покупки")
@pytest.mark.smoke
def test_store_button_leads_to_buy_page(driver):
    """Тест 2: Кнопка 'Магазин' ведёт на страницу покупки фильма."""
    main = MainPage(driver)

    with allure.step("Шаг 1: Переход на главную страницу"):
        main.open_main_page()

    with allure.step("Шаг 2: Найти кнопку 'Магазин'"):
        store_button = main.find_button("Магазин")
        assert store_button is not None, "Кнопка 'Магазин' не найдена"

    with allure.step("Шаг 3: Проверка, что кнопка кликабельна"):
        wait = WebDriverWait(driver, 10)
        try:
            wait.until(EC.element_to_be_clickable(store_button))
        except Exception:
            pytest.fail("Кнопка 'Магазин' не стала кликабельной за 10 секунд")

    with allure.step("Шаг 4: Нажать на кнопку и проверить переход на страницу покупки"):
        store_button.click()
        wait_for_element(driver, (By.CSS_SELECTOR, ".buy-film-page"))
        allure.attach(
            body="Переход на страницу покупки выполнен",
            name="Страница покупки фильма",
            attachment_type=allure.attachment_type.TEXT,
        )


@allure.feature("UI Кинопоиск")
@allure.story("Буду смотреть")
@pytest.mark.smoke
def test_flag_adds_to_watchlist(driver):
    """Тест 3: Значок флажка добавляет фильм в раздел 'Буду смотреть'."""
    main = MainPage(driver)

    with allure.step("Шаг 1: Переход на главную страницу"):
        main.open_main_page()
        wait_for_element(driver, (By.CSS_SELECTOR, "body"))

    with allure.step("Шаг 2: Ввод поискового запроса"):
        query = "зеленая миля"
        main.make_search(query)
        allure.attach(query, name="Введённый запрос", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Шаг 3: Ожидание результатов поиска"):
        wait_for_element(driver, (By.CSS_SELECTOR, ".selection-card, .film-item"))
        results = driver.find_elements(By.CSS_SELECTOR, ".selection-card, .film-item")
        assert len(results) > 0, "Результаты поиска не найдены"

    with allure.step("Шаг 4: Найти значок флажка на карточке фильма"):
        flag_button = main.find_flag_button()
        assert flag_button is not None, "Значок флажка не найден"

    with allure.step("Шаг 5: Проверить кликабельность флажка"):
        # Запоминаем класс/состояние до клика
        class_before = flag_button.get_attribute("class")
        allure.attach(class_before, name="Класс флажка до клика", attachment_type=allure.attachment_type.TEXT)

        wait_for_clickable(driver, (By.CSS_SELECTOR,
                            "[data-tid='flag_button'], .flag-icon, .watchlist-button"))

    with allure.step("Шаг 6: Нажать на значок флажка"):
        flag_button.click()

    with allure.step("Шаг 7: Проверить, что флажок изменил состояние (фильм добавлен)"):
        # Ждём изменения класса или появления индикатора добавления
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(
                By.CSS_SELECTOR,
                "[data-tid='flag_button'], .flag-icon, .watchlist-button"
            ).get_attribute("class") != class_before
        )

        flag_after = driver.find_element(
            By.CSS_SELECTOR,
            "[data-tid='flag_button'], .flag-icon, .watchlist-button"
        )
        class_after = flag_after.get_attribute("class")
        allure.attach(class_after, name="Класс флажка после клика", attachment_type=allure.attachment_type.TEXT)

        assert class_after != class_before, (
            "Состояние флажка не изменилось — фильм не добавлен в 'Буду смотреть'"
        )

    with allure.step("Шаг 8: Проверить появление уведомления или визуального подтверждения"):
        # Кинопоиск обычно показывает всплывашку или меняет иконку
        notification = driver.find_elements(
            By.CSS_SELECTOR,
            ".notification, .toast, [data-tid='watchlist_notification']"
        )
        # Даже если уведомление не появилось, изменение класса уже подтверждает добавление
        if len(notification) > 0:
            allure.attach("Уведомление о добавлении отображается", name="Результат", attachment_type=allure.attachment_type.TEXT)
        else:
            allure.attach("Уведомление не найдено, но класс флажка изменился", name="Результат", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Шаг 9: Перейти в раздел 'Буду смотреть' и проверить наличие фильма"):
        main.go_to_watchlist()
        wait_for_element(driver, (By.CSS_SELECTOR,
                         ".watchlist-item, .collection-item, [data-tid='watchlist_content']"))

        watchlist_items = driver.find_elements(
            By.CSS_SELECTOR,
            ".watchlist-item, .collection-item, [data-tid='watchlist_content']"
        )
        count = len(watchlist_items)
        allure.attach(str(count), name="Количество фильмов в Буду смотреть", attachment_type=allure.attachment_type.TEXT)

        assert count > 0, "Раздел 'Буду смотреть' пуст — фильм не добавлен"

        # Проверяем, что искомый фильм действительно в списке
        found = False
        for item in watchlist_items:
            if query.lower() in item.text.lower():
                found = True
                break

        assert found, f"Фильм '{query}' не найден в разделе 'Буду смотреть'"


@allure.feature("UI Кинопоиск: Билеты в кино")
@allure.story("Фильтрация и навигация")
@pytest.mark.smoke
def test_genre_dropdown_selection(driver):
    """Тест 4: Выбор жанра в выпадающем списке в разделе 'Билеты в кино'."""
    page = TicketsPage(driver)

    with allure.step("Шаг 1: Переход в раздел 'Билеты в кино'"):
        page.open_tickets_section()
        wait_for_element(driver, (By.CSS_SELECTOR, 'a[href="/lists/movies/movies-in-cinema/"]'))

    with allure.step("Шаг 2: Найти кнопку выпадающего списка жанров"):
        genre_btn = page.find_genre_dropdown_button()
        assert genre_btn is not None, "Кнопка выбора жанра не найдена"

    with allure.step("Шаг 3: Проверить кликабельность кнопки жанров"):
        wait_for_clickable(driver, (
            By.CSS_SELECTOR,
            "[data-tid='genre_filter'], .genre-dropdown-btn, button[aria-label*='жанр']"
        ))

    with allure.step("Шаг 4: Открыть выпадающий список жанров"):
        genre_btn.click()
        # Ждём появления списка жанров
        wait_for_element(driver, (By.CSS_SELECTOR,
                                  ".genre-list, .dropdown-menu, [data-tid='genre_list']"))

    with allure.step("Шаг 5: Выбрать жанр 'Комедия' из списка"):
        target_genre = "Комедия"
        selected_item = page.select_genre_by_text(target_genre)
        assert selected_item is not None, f"Жанр '{target_genre}' не найден в списке"
        allure.attach(target_genre, name="Выбранный жанр", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Шаг 6: Подтвердить закрытие выпадающего списка и применение фильтра"):
        # После клика список должен закрыться, фильтр примениться
        WebDriverWait(driver, 10).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR,
                                          ".genre-list, .dropdown-menu")) == 0
        )

        # Проверяем, что фильтр применился: ищем признак активного жанра
        active_filters = driver.find_elements(
            By.CSS_SELECTOR,
            ".genre-pill, .filter-tag, [data-tid='active_genre']"
        )
        filter_texts = [el.text.strip() for el in active_filters]
        allure.attach("\n".join(filter_texts), name="Активные фильтры", attachment_type=allure.attachment_type.TEXT)

        assert target_genre in filter_texts, (
            f"Фильтр по жанру '{target_genre}' не применился"
        )

    with allure.step("Шаг 7: Проверить, что результаты отфильтрованы по жанру"):
        results = driver.find_elements(By.CSS_SELECTOR,
                                       ".movie-card, .event-item, .schedule-row")
        count = len(results)
        allure.attach(str(count), name="Количество найденных событий", attachment_type=allure.attachment_type.TEXT)

        assert count > 0, "После фильтрации по жанру не найдено ни одного события"
        