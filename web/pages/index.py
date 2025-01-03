import reflex as rx

def index():
    return rx.vstack(
        rx.heading("Welcome to Olympus", font_size="2em"),
        rx.text("This is the main page of your Reflex application."),
        padding="2em",
        spacing="1.5em"
    )

app = rx.App()
app.add_page(index, route="/")
