from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# создание класса
class MainPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

        """открыть главную страницу"""

    SOURCH_FIELD = (By.XPATH, "//input[@placeholder='Фильмы, сериалы, персоны']")


    def open_main_page(self, url="https://www.kinopoisk.ru/"):
        self.driver.get(url)

    def make_sourch(self, query):
        search_input = self.wait.until(
            EC.presence_of_element_located(
                (self.SOURCH_FIELD)
        )
    )
        search_input.clear()
        search_input.send_keys(query)
        search_input. send_keys(Keys.ENTER)

    def find_button(self, button_text):
        button = self.wait.until(
            EC.presence_of_element_located((By.XPATH, f"//span[text()='{button_text}']"))
        )
        return button

    def find_flag_button(self):
        """Находит значок флажка на карточке фильма в результатах поиска."""
        locator = (By.CSS_SELECTOR,
                   "[data-tid='flag_button'], .flag-icon, .watchlist-button, "
                   "button[aria-label*='Буду смотреть'], "
                   "button[aria-label*='watch']")
        element = self.wait.until(
            EC.presence_of_element_located(locator)
        )
        return element

    def go_to_watchlist(self):
        """Переходит в раздел 'Буду смотреть'."""
        locator = (By.XPATH,
                   "//a[contains(@href, '/myfilms/') or contains(@href, '/watchlist/')]"
                   " | //span[normalize-space()='Буду смотреть']"
                   " | //a[normalize-space()='Буду смотреть']")
        link = self.wait.until(
            EC.element_to_be_clickable(locator)
        )
        link.click()
    

    
