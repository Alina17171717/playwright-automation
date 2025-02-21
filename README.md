**Playwright automation with Python**

Test project to show:
- features of MS Playwright
- automation project structure using Pytest

Tools:
- [Playwright](https://playwright.dev/)
- [Pytest](https://pytest.org/)
- [PyCharm](https://www.jetbrains.com/pycharm/)

**Install guide**

1. Install Python
2. Install PyCharm
3. Install Python dependencies `pip install -r requirements.txt` 
4. Make sure Playwright version 1.8+ installed

**Project structure**

- [conftest.py](https://docs.pytest.org/en/stable/fixture.html#conftest-py-sharing-fixtures-across-multiple-files) file contains main fixtures to work
- Page objects stored in page_object folder
- Tests stored in test folder
- Settings are spread between:
  - pytest.ini
  - settings.py

**Run guide**

1. Create file `secure.json` for logins and passwords. Structure:
    ```json
    {
        "login": "login",
        "password": "password"
    }
2. Install software to test [Test-Me](http://127.0.0.1:8000/tests/)
3. Run Test-Me (check guide in it`s repo)
4. Run tests using command `pytest`
