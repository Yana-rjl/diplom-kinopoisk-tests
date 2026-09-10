import pytest
from selenium import webdriver


@pytest.fixture(scope="function")
def driver():
    """Фикстура для создания WebDriver"""
    driver = webdriver.Chrome()
    
    driver.maximize_window()

    yield driver
    driver.quit()
