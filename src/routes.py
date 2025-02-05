from flask import (
    Flask,
    render_template,
    redirect,
    request,
    url_for,
    session,
    make_response,
)
import os
from flask_sqlalchemy import SQLAlchemy
from models import Car, User
from main import app, db


@app.errorhandler(404)
def page_not_found(e):
    return make_response(render_template("custom_404.html"), 404)


@app.route("/")
def home():
    username = session.get("username")  # Проверка за наличен потребител
    if username:
        return render_template("home.html", title="Home", my_username=username)
    else:
        return render_template("home.html", title="Home", my_username=None)


@app.route("/login")
def login(message=None):
    if "message" in request.args:
        message = request.args["message"]
    print(message)
    return render_template("login_form.html", title="Login", message=message)


@app.route("/login_action", methods=["POST"])
def login_action():
    if request.method != "POST":
        return redirect(url_for("/login", message="Invalid method"))

    form_username = request.form["username"]
    form_password = request.form["password"]

    this_user_in_db = User.query.filter_by(username=form_username).first()

    if this_user_in_db and this_user_in_db.password == form_password:
        session["username"] = form_username
        return redirect(url_for("home", name=form_username))
    else:
        return redirect(url_for("login", message="Invalid username or password"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/profile/<username>")
def user_page(username):
    session_username = session.get("username")
    if session_username and username == session_username:
        user = User.query.filter_by(username=session_username).first()
        return render_template(
            "user.html", title="User", my_username=session_username, user=user
        )
    else:
        return redirect(url_for("login", message="Log in your profile!"))


@app.route("/register")
def register(message=None):
    if "message" in request.args:
        message = request.args["message"]
    print(message)
    return render_template("register.html", title="Registration Form", message=message)


@app.route("/register_action", methods=["POST"])
def register_action():
    if request.method != "POST":
        return redirect(url_for("register", message="Invalid method"))

    new_username = request.form["username"]
    this_user_in_db = User.query.filter_by(username=new_username).first()
    if this_user_in_db:
        return redirect(url_for("register", message="This username already exists!"))

    new_email = request.form["email"]
    new_password = request.form["password"]

    new_user = User(
        username=new_username,
        email=new_email,
        password=new_password,
    )
    db.session.add(new_user)
    db.session.commit()

    session["username"] = new_username
    return redirect(url_for("home", name=new_username))


@app.route("/catalog")
def catalog(user=None):
    username = session.get("username")
    if "user" in request.args and username == request.args["user"]:
        user = request.args["user"]
        user_db_info = User.query.filter_by(username=user).first()
        cars = user_db_info.cars
    else:
        cars = Car.query.all()

    return render_template("catalog.html", cars=cars, my_username=username)


@app.route("/add_listing/<my_username>")
def add_listing(my_username):
    session_username = session.get("username")
    if session_username and my_username == session_username:
        return render_template(
            "add_listing.html", title="User", my_username=session_username
        )
    else:
        return redirect(url_for("login", message="Log in your profile!"))


@app.route("/add_listing_action", methods=["POST"])
def add_listing_action():
    if request.method != "POST":
        return redirect(url_for("/login", message="Invalid method"))
    new_brand = request.form["brand"]
    new_model = request.form["model"]
    new_category = request.form["category"]
    new_price = request.form["price"]
    new_description = request.form["description"]
    session_username = session.get("username")
    user = User.query.filter_by(username=session_username).first()
    new_car = Car(
        user_id=user.id,
        brand=new_brand,
        model=new_model,
        category=new_category,
        price=new_price,
        description=new_description,
    )
    db.session.add(new_car)
    db.session.commit()
    return redirect(url_for("catalog", user=session_username))


@app.route("/my_listings/<my_username>")
def my_listings(my_username):
    session_username = session.get("username")
    if session_username and my_username == session_username:
        return redirect(url_for("catalog", user=session_username))
    else:
        return redirect(url_for("login", message="Log in your profile!"))
