from playwright.sync_api import Page, Locator, expect
from config.config import get_environment

TODO_URL = get_environment().get("todo_url")


class TodoAppPage:
    def __init__(self, page: Page):
        self.page: Page = page
        self.new_todo: Locator = page.get_by_placeholder("What needs to be done?")
        self.todo_titles: Locator = page.get_by_test_id("todo-title")
        self.todo_items: Locator = page.get_by_test_id("todo-item")
        self.todo_count: Locator = page.get_by_test_id("todo-count")
        self.toggle_all: Locator = page.get_by_label("Mark all as complete")
        self.clear_completed_button: Locator = page.get_by_role("button", name="Clear completed")
        self.filter_all: Locator = page.get_by_role("link", name="All")
        self.filter_active: Locator = page.get_by_role("link", name="Active")
        self.filter_completed: Locator = page.get_by_role("link", name="Completed")

    def goto(self):
        """Navigate to the TodoMVC demo app."""
        self.page.goto(TODO_URL)
        expect(self.page).to_have_url(TODO_URL)

    def add_todo(self, title: str):
        """Add a single todo item."""
        self.new_todo.fill(title)
        self.new_todo.press("Enter")

    def add_todos(self, titles: list[str]):
        """Add multiple todo items."""
        for title in titles:
            self.add_todo(title)

    def mark_all_as_completed(self):
        """Mark all todos as completed."""
        self.toggle_all.check()

    def unmark_all_as_completed(self):
        """Unmark all todos."""
        self.toggle_all.uncheck()

    def get_todo_titles(self) -> list[str]:
        """Return all todo titles as a list of strings."""
        return self.todo_titles.all_text_contents()
