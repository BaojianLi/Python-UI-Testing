import pytest
from playwright.sync_api import sync_playwright, expect
from page_objects.todoAppPage import TodoAppPage

from lib.helper import (
    create_default_todos,
    check_number_of_todos_in_local_storage,
    check_number_of_completed_todos_in_local_storage,
    check_todos_in_local_storage,
)

TODO_ITEMS = [
    "buy some cheese",
    "feed the cat",
    "book a doctors appointment"
]



# Fixture to provide a Playwright page for each test
@pytest.fixture(scope="function")
def page_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        yield page
        browser.close()


# -------------------------------
# New Todo Tests
# -------------------------------
def test_should_allow_me_to_add_todo_items(page_context):
    page = page_context
    todo_app = TodoAppPage(page)
    todo_app.goto()
    todo_app.add_todos(TODO_ITEMS[:2])
    expect(todo_app.todo_titles).to_have_text([TODO_ITEMS[0], TODO_ITEMS[1]])
    check_number_of_todos_in_local_storage(page, 2)


def test_should_clear_input_after_add(page_context):
    page = page_context
    todo_app = TodoAppPage(page)
    todo_app.goto()
    todo_app.add_todo(TODO_ITEMS[0])
    expect(todo_app.new_todo).to_be_empty()
    check_number_of_todos_in_local_storage(page, 1)


def test_should_append_new_items_to_bottom(page_context):
    page = page_context
    todo_app = TodoAppPage(page)
    todo_app.goto()
    todo_app.add_todos(TODO_ITEMS)
    expect(page.get_by_text("3 items left")).to_be_visible()
    expect(todo_app.todo_count).to_have_text("3 items left")
    expect(todo_app.todo_count).to_contain_text("3")
    expect(todo_app.todo_titles).to_have_text(TODO_ITEMS)
    check_number_of_todos_in_local_storage(page, 3)
