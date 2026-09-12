import pytest
from selenium import webdriver
import requests
from config import Config

@pytest.fixture(scope="session")
def session():
    session = requests.Session()
    session.headers.update({"X-API-KEY": Config.API_TOKEN})
    return session


@pytest.fixture(scope="function")
def driver():
    """Фикстура для создания WebDriver"""
    driver = webdriver.Chrome()
    
    driver.maximize_window()

    yield driver
    driver.quit()
