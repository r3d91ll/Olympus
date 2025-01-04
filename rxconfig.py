import reflex as rx

class Config(rx.Config):
    app_name = "OracleDelphi"  # Back to just OracleDelphi
    db_url = "sqlite:///reflex.db"
    env = "dev"
    frontend_port = 3001
    backend_port = 8081
    telemetry_enabled=False

# Create an instance of the Config class and assign it to config
config = Config()
