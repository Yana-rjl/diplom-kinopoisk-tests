Учебный репозиторий - Дипломная работа
Проект содержит 5 UI тестов и 5 api тестов
Ссылка нв финальный проект по ручному тестированию: https://kursovaya1.yonote.ru/doc/kursovaya-rabota-2-kurs-ruchnoe-testirovanie-8wmoIBbvt6
Структура проекта: Диплом: папка Pages(файлы: mainpage.py, tickets_page.py)
                           папка test (файлы: __init__.py, test_api.py, test_ui.py)
                           файл .gitignore
                           файл config.py
                           файл conftest.py
                           файл pytest.ini
                           файл README.md
                           файл requirements.txt

pytest==8.3.2
selenium==4.25.0
webdriver-manager==4.9.3
requests==2.32.3
allure-pytest==3.2.5
pytest-html==4.1.1

Запустить ui тесты командой: pytest test_ui.py
Запустить api тесты командой: pytest test_api.py
Запустить все тесты: pytest tests