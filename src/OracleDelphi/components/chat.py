import reflex as rx

def chat_component():
    return rx.vstack(
        rx.box("Chat Component Placeholder", font_size="1.5em"),
        padding="1em",
        border="1px solid #ccc",
        border_radius="8px"
    )
