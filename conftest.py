import logging
import json
import os.path
import pytest
import allure
from pytest import fixture, hookimpl
from playwright.sync_api import sync_playwright
from page_objects.application import App
from helpers.web_service import WebService
from settings import *
from helpers.db import DataBase


@fixture(autouse=True, scope='session')
def preconditions():
    logging.info('precondition started')
    yield
    logging.info('postcondition started')

@fixture(scope='session')
def get_web_service(request):
    base_url = request.config.getini('base_url')
    secure = request.config.getoption('--secure')
    config = load_config(secure)
    web = WebService(base_url)
    web.login(**config['users']['usersRole1'])
    yield web
    web.close()

@fixture(scope='session')
def get_db(request):
    path = request.config.getini('db_path')
    db = DataBase(path)
    yield db
    db.close()




@fixture(scope='session')
def get_playwright():
    with sync_playwright() as playwright:
        yield playwright

@fixture(scope='session', params=['chromium'])
def get_browser(get_playwright, request):
    browser = request.param
    os.environ['PWBROWSER'] = browser
    headless = request.config.getini('headless')
    if headless == 'True':
        headless = True
    else:
        headless = False

    if browser == 'chromium':
        bro = get_playwright.chromium.launch(headless=headless)
    elif browser == 'firefox':
        bro = get_playwright.firefox.launch(headless=headless)
    elif browser == 'webkit':
        bro = get_playwright.webkit.launch(headless=headless)
    else:
        assert False, 'unsupported browser type'

    yield bro
    bro.close()
    del os.environ['PWBROWSER']


@fixture(scope='session')
def desktop_app(get_browser, request):
    base_url = request.config.getini('base_url')
    app = App(get_browser, base_url=base_url, **BROWSER_OPTIONS)
    app.goto('/')
    yield app
    app.close()


@fixture(scope='session')
def desktop_app_auth(desktop_app, request):
    secure = request.config.getoption('--secure')
    config = load_config(secure)
    app = desktop_app
    app.goto('/login')
    app.login(**config['users']['usersRole1'])
    yield app


@fixture(scope='session')
def desktop_app_bob(get_browser, request):
    secure = request.config.getoption('--secure')
    config = load_config(secure)
    base_url = request.config.getini('base_url')
    app = App(get_browser, base_url=base_url, **BROWSER_OPTIONS)
    app.goto('/login')
    app.login(**config['users']['usersRole2'])
    yield app
    app.close()


@fixture(scope='session', params=['iPhone 11', 'Pixel 2'])
def mobile_app(get_playwright, get_browser, request):
    if os.environ.get('PWBROWSER') == 'firefox':
        pytest.skip()
    base_url = request.config.getini('base_url')
    device = request.param
    device_config = get_playwright.devices.get(device)
    if device_config is not None:
        device_config.update(BROWSER_OPTIONS)
    else:
        device_config = BROWSER_OPTIONS
    app = App(get_browser, base_url=base_url, **device_config)
    app.goto('/')
    yield app
    app.close()


@fixture(scope='session')
def mobile_app_auth(mobile_app, request):
    secure = request.config.getoption('--secure')
    config = load_config(secure)
    app = mobile_app
    app.goto('/login')
    app.login(**config['users']['usersRole1'])
    yield app


@hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()
    # result.when == "setup" >> "call" >> "teardown"
    setattr(item, f'result_{result.when}', result)


@fixture(scope='function', autouse=True)
def make_screenshots(request):
    yield
    if request.node.result_call.failed:
        for arg in request.node.funcargs.values():
            if isinstance(arg, App):
                allure.attach(body=arg.page.screenshot(),
                              name='screenshot',
                              attachment_type=allure.attachment_type.PNG)



def pytest_addoption(parser):
    parser.addoption('--secure', action='store', default='secure.json')
    parser.addini('base_url', help='base url of site under test', default='http://127.0.0.1:8000')
    parser.addini('db_path', help='path to sqlite db file', default='D:\\PlaywrightTestMe\\TestMe-TCM\\db.sqlite3')
    parser.addini('headless', help='run browser in headless mode', default='True')

def load_config(file):
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
    with open(config_file) as cfg:
        return json.loads(cfg.read())
