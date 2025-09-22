import re
import time
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
        time.sleep(2)
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
    expect(todo_app.todo_count).to_have_text(re.compile("3"))
    expect(todo_app.todo_titles).to_have_text(TODO_ITEMS)
    check_number_of_todos_in_local_storage(page, 3)


# -------------------------------
# Mark All Completed
# -------------------------------
@pytest.fixture
def with_three_todos(page_context):
    page = page_context
    todo_app = TodoAppPage(page)
    todo_app.goto()
    todo_app.add_todos(TODO_ITEMS)
    check_number_of_todos_in_local_storage(page, 3)
    return todo_app, page


def test_should_allow_mark_all_completed(page_context, with_three_todos):
    todo_app, page = with_three_todos
    todo_app.mark_all_as_completed()
    expect(todo_app.todo_items).to_have_class(["completed", "completed", "completed"])
    check_number_of_completed_todos_in_local_storage(page, 3)


def test_should_allow_clear_completed_state(page_context, with_three_todos):
    todo_app, page = with_three_todos
    todo_app.mark_all_as_completed()
    todo_app.unmark_all_as_completed()
    expect(todo_app.todo_items).to_have_class(["", "", ""])


def test_toggle_checkbox_should_update_state(page_context,with_three_todos):
    todo_app, page = with_three_todos
    todo_app.mark_all_as_completed()
    expect(todo_app.toggle_all).to_be_checked()
    check_number_of_completed_todos_in_local_storage(page, 3)

    first_todo = todo_app.todo_items.nth(0)
    first_todo.get_by_role("checkbox").uncheck()
    expect(todo_app.toggle_all).not_to_be_checked()

    first_todo.get_by_role("checkbox").check()
    check_number_of_completed_todos_in_local_storage(page, 3)
    expect(todo_app.toggle_all).to_be_checked()




# -------------------------------
# Item Tests
# -------------------------------
def test_mark_items_complete(page_context):
    page = page_context
    todo_app = TodoAppPage(page)
    todo_app.goto()
    todo_app.add_todos(TODO_ITEMS[:2])

    first_todo = todo_app.todo_items.nth(0)
    first_todo.get_by_role("checkbox").check()
    expect(first_todo).to_have_class("completed")

    second_todo = todo_app.todo_items.nth(1)
    
    expect(second_todo).not_to_have_class("completed")
    second_todo.get_by_role("checkbox").check()

    expect(first_todo).to_have_class("completed")
    expect(second_todo).to_have_class("completed")


def test_unmark_items_complete(page_context):
    page = page_context
    todo_app = TodoAppPage(page)
    todo_app.goto()
    todo_app.add_todos(TODO_ITEMS[:2])

    first_todo = todo_app.todo_items.nth(0)
    second_todo = todo_app.todo_items.nth(1)
    first_checkbox = first_todo.get_by_role("checkbox")

    first_checkbox.check()
    expect(first_todo).to_have_class("completed")
    expect(second_todo).not_to_have_class("completed")
    check_number_of_completed_todos_in_local_storage(page, 1)

    first_checkbox.uncheck()
    expect(first_todo).not_to_have_class("completed")
    expect(second_todo).not_to_have_class("completed")
    check_number_of_completed_todos_in_local_storage(page, 0)


def test_edit_item(page_context):
    page = page_context
    todo_app = TodoAppPage(page)
    todo_app.goto()
    todo_app.add_todos(TODO_ITEMS)

    todo_items = todo_app.todo_items
    second_todo = todo_items.nth(1)

    second_todo.dblclick()
    expect(second_todo.get_by_role("textbox", name="Edit")).to_have_value(TODO_ITEMS[1])

    edit_box = second_todo.get_by_role("textbox", name="Edit")
    edit_box.fill("buy some sausages")
    edit_box.press("Enter")

    expect(todo_items).to_have_text([TODO_ITEMS[0], "buy some sausages", TODO_ITEMS[2]])
    check_todos_in_local_storage(page, "buy some sausages")


# -------------------------------
# Editing Tests
# -------------------------------



def test_hide_controls_when_editing(page_context, with_three_todos):
    todo_app, page = with_three_todos
    todo_item = todo_app.todo_items.nth(1)
    todo_item.dblclick()
    expect(todo_item.get_by_role("checkbox")).not_to_be_visible()
    expect(todo_item.locator("label", has_text=TODO_ITEMS[1])).not_to_be_visible()
    check_number_of_todos_in_local_storage(page, 3)


def test_save_edits_on_blur(page_context, with_three_todos):
    todo_app, page = with_three_todos
    todo_items = todo_app.todo_items
    todo_items.nth(1).dblclick()
    edit_box = todo_items.nth(1).get_by_role("textbox", name="Edit")
    edit_box.fill("buy some sausages")
    edit_box.dispatch_event("blur")

    expect(todo_items).to_have_text([TODO_ITEMS[0], "buy some sausages", TODO_ITEMS[2]])
    check_todos_in_local_storage(page, "buy some sausages")


def test_trim_entered_text(page_context, with_three_todos):
    todo_app, page = with_three_todos
    todo_items = todo_app.todo_items
    todo_items.nth(1).dblclick()
    edit_box = todo_items.nth(1).get_by_role("textbox", name="Edit")
    edit_box.fill("    buy some sausages    ")
    edit_box.press("Enter")

    expect(todo_items).to_have_text([TODO_ITEMS[0], "buy some sausages", TODO_ITEMS[2]])
    check_todos_in_local_storage(page, "buy some sausages")


def test_remove_item_if_empty_string(page_context, with_three_todos):
    todo_app, page = with_three_todos
    todo_items = todo_app.todo_items
    todo_items.nth(1).dblclick()
    edit_box = todo_items.nth(1).get_by_role("textbox", name="Edit")
    edit_box.fill("")
    edit_box.press("Enter")

    expect(todo_items).to_have_text([TODO_ITEMS[0], TODO_ITEMS[2]])


def test_cancel_edit_on_escape(page_context, with_three_todos):
    todo_app, page = with_three_todos
    todo_items = todo_app.todo_items
    todo_items.nth(1).dblclick()
    edit_box = todo_items.nth(1).get_by_role("textbox", name="Edit")
    edit_box.fill("buy some sausages")
    edit_box.press("Escape")
    expect(todo_items).to_have_text(TODO_ITEMS)


# -------------------------------
# Counter Tests
# -------------------------------
def test_display_todo_count(page_context):
    page = page_context
    todo_app = TodoAppPage(page)
    todo_app.goto() 
            
    new_todo = page.get_by_placeholder("What needs to be done?")
    todo_count = page.get_by_test_id("todo-count")

    new_todo.fill(TODO_ITEMS[0])
    new_todo.press("Enter")
    expect(todo_count).to_contain_text("1")

    new_todo.fill(TODO_ITEMS[1])
    new_todo.press("Enter")
    expect(todo_count).to_contain_text("2")

    check_number_of_todos_in_local_storage(page, 2)


# -------------------------------
# Clear Completed Button
# -------------------------------
@pytest.fixture
def with_completed_todos(page_context):
    page = page_context
    todo_app = TodoAppPage(page)
    todo_app.goto()
    todo_app.add_todos(TODO_ITEMS)
    return todo_app


def test_clear_button_visible_after_complete(page_context, with_completed_todos):
    with_completed_todos.todo_items.first.get_by_role("checkbox").check()
    expect(with_completed_todos.clear_completed_button).to_be_visible()


def test_clear_button_removes_completed(page_context, with_completed_todos):
    with_completed_todos.todo_items.nth(1).get_by_role("checkbox").check()
    with_completed_todos.clear_completed_button.click()
    expect(with_completed_todos.todo_items).to_have_count(2)
    expect(with_completed_todos.todo_items).to_have_text([TODO_ITEMS[0], TODO_ITEMS[2]])


def test_clear_button_hidden_when_no_completed(page_context, with_completed_todos):
    with_completed_todos.todo_items.first.get_by_role("checkbox").check()
    with_completed_todos.clear_completed_button.click()
    expect(with_completed_todos.clear_completed_button).to_be_hidden()


# -------------------------------
# Persistence Tests
# -------------------------------
def test_should_persist_data(page_context):
    page = page_context
    todo_app = TodoAppPage(page)
    todo_app.goto()

    for item in TODO_ITEMS[:2]:
        todo_app.add_todo(item)

    first_check = todo_app.todo_items.nth(0).get_by_role("checkbox")
    first_check.check()
    expect(todo_app.todo_items).to_have_text([TODO_ITEMS[0], TODO_ITEMS[1]])
    expect(first_check).to_be_checked()
    expect(todo_app.todo_items).to_have_class(["completed", ""])

    check_number_of_completed_todos_in_local_storage(page, 1)

    page.reload()
    expect(todo_app.todo_items).to_have_text([TODO_ITEMS[0], TODO_ITEMS[1]])
    expect(first_check).to_be_checked()
    expect(todo_app.todo_items).to_have_class(["completed", ""])


# -------------------------------
# Routing Tests
# -------------------------------
@pytest.fixture
def with_routing_todos(page_context):
    page = page_context
    todo_app = TodoAppPage(page)
    todo_app.goto()
    todo_app.add_todos(TODO_ITEMS)
    check_todos_in_local_storage(page, TODO_ITEMS[0])
    return todo_app


def test_display_active_items(page_context, with_routing_todos):
    page = page_context
    with_routing_todos.todo_items.nth(1).get_by_role("checkbox").check()
    check_number_of_completed_todos_in_local_storage(page, 1)

    page.get_by_role("link", name="Active").click()
    expect(with_routing_todos.todo_items).to_have_count(2)
    expect(with_routing_todos.todo_items).to_have_text([TODO_ITEMS[0], TODO_ITEMS[2]])


def test_respect_back_button(page_context, with_routing_todos):
    page = page_context
    with_routing_todos.todo_items.nth(1).get_by_role("checkbox").check()
    check_number_of_completed_todos_in_local_storage(page, 1)

    page.get_by_role("link", name="All").click()
    expect(with_routing_todos.todo_items).to_have_count(3)

    page.get_by_role("link", name="Active").click()
    page.get_by_role("link", name="Completed").click()
    expect(with_routing_todos.todo_items).to_have_count(1)

    page.go_back()
    expect(with_routing_todos.todo_items).to_have_count(2)
    page.go_back()
    expect(with_routing_todos.todo_items).to_have_count(3)


def test_display_completed_items(page_context, with_routing_todos):
    page = page_context
    with_routing_todos.todo_items.nth(1).get_by_role("checkbox").check()
    check_number_of_completed_todos_in_local_storage(page, 1)
    page.get_by_role("link", name="Completed").click()
    expect(with_routing_todos.todo_items).to_have_count(1)


def test_display_all_items(page_context, with_routing_todos):
    page = page_context
    with_routing_todos.todo_items.nth(1).get_by_role("checkbox").check()
    check_number_of_completed_todos_in_local_storage(page, 1)
    page.get_by_role("link", name="Active").click()
    page.get_by_role("link", name="Completed").click()
    page.get_by_role("link", name="All").click()
    expect(with_routing_todos.todo_items).to_have_count(3)


def test_highlight_current_filter(page_context, with_routing_todos):
    page = page_context
    expect(with_routing_todos.filter_all).to_have_class("selected")
    with_routing_todos.filter_active.click()
    expect(with_routing_todos.filter_active).to_have_class("selected")
    with_routing_todos.filter_completed.click()
    expect(with_routing_todos.filter_completed).to_have_class("selected")
