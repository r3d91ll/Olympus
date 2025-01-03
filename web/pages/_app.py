import reflex as rx

from src.frontend.app import app

def index():
    return app.index()

app = rx.App()
app.add_page(index, route="/")
