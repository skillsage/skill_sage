from flask import Flask
from routes.user_routes import user_route
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///main.sqlite"

db = SQLAlchemy(app)


app.register_blueprint(user_route)

@app.get("/")
def hello_world():
    # user = User("hello", "user@email.com", "pass", Role.EMPLOYER)
    return "Hello"