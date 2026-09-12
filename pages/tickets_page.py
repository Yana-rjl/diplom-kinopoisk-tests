from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TicketsPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def open_tickets_section(self, url="https://www.kinopoisk.ru/"):
        """Открывает раздел 'Билеты в кино'."""
        self.driver.get(url)

    def find_genre_dropdown_button(self):
        """Находит кнопку выпадающего списка жанров."""
        locator = (By.CSS_SELECTOR,
                   "[data-tid='genre_filter'], "
                   ".genre-dropdown-btn, "
                   "button[aria-label*='жанр'], "
                   ".filter-control[data-filter='genre']")
        return self.wait.until(EC.presence_of_element_located(locator))

    def select_genre_by_text(self, genre_name: str):
        """Выбирает жанр по тексту в выпадающем списке."""
        # Сначала убедимся, что список раскрыт (если нет — логика теста уже кликнула кнопку)
        list_locator = (By.CSS_SELECTOR,
                        ".genre-list li, .dropdown-menu li, "
                        "[data-tid='genre_list'] li")
        items = self.wait.until(
            EC.presence_of_all_elements_located(list_locator)
        )

        for item in items:
            text = item.text.strip()
            if text == genre_name or genre_name.lower() in text.lower():
                item.click()
                return item
        return None