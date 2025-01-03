import reflex as rx

from components.chat import chat_component
from components.model_selection import model_selection_component

def index():
    return rx.vstack(
        model_selection_component(),
        chat_component(),
        padding="2em",
        spacing="1.5em"
    )

app = rx.App()
app.add_page(index, route="/")
app._compile()
