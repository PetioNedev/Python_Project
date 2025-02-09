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
from json_file_logic import upload_images_json, get_single_car_images, delete_car_json

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


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
        user = User.query.filter_by(username=session_username).first_or_404()
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
        user_db_info = User.query.filter_by(username=user).first_or_404()
        cars = user_db_info.cars
    else:
        cars = Car.query.all()

    return render_template(
        "catalog.html", cars=cars, my_username=username, get_img=get_single_car_images
    )


@app.route("/add_listing/<my_username>")
def add_listing(my_username):
    session_username = session.get("username")
    if session_username and my_username == session_username:
        return render_template(
            "add_listing.html", title="User", my_username=session_username
        )
    else:
        return redirect(url_for("login", message="Log in your profile!"))


def allowed_file(filename):
    return "." in filename and filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS


@app.route("/add_listing_action", methods=["POST"])
def add_listing_action():
    if request.method != "POST":
        return redirect(url_for("/login", message="Invalid method"))
    new_brand = request.form["brand"]
    new_model = request.form["model"]
    new_category = request.form["category"]
    new_price = request.form["price"]
    new_description = request.form["description"]
    new_mileage = request.form["mileage"]
    new_year = int(request.form["year"])
    session_username = session.get("username")
    user = User.query.filter_by(username=session_username).first_or_404()
    new_car = Car(
        user_id=user.id,
        brand=new_brand,
        model=new_model,
        category=new_category,
        price=new_price,
        description=new_description,
        mileage=new_mileage,
        year=new_year,
    )
    db.session.add(new_car)
    db.session.commit()

    car_id = new_car.id

    if "images" not in request.files:
        app.flash("Provide images for your car brother!")

    imgs = request.files.getlist("images")
    uploaded_filenames = []

    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])

    for index, img in enumerate(imgs):
        if img.filename == "":
            continue

        if img and allowed_file(img.filename):
            file_extension = img.filename.split(".")[-1].lower()
            file_name = f"{car_id}_{index}_car.{file_extension}"
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_name)
            img.save(file_path)
            uploaded_filenames.append(file_name)

    upload_images_json(car_id, uploaded_filenames)

    return redirect(url_for("catalog", user=session_username))


@app.route("/my_listings/<my_username>")
def my_listings(my_username):
    session_username = session.get("username")
    if session_username and my_username == session_username:
        return redirect(url_for("catalog", user=session_username))
    else:
        return redirect(url_for("login", message="Log in your profile!"))


@app.route("/car/<car_id>")
def car(car_id):
    images = get_single_car_images(car_id)
    this_car = Car.query.get_or_404(car_id)

    return render_template(
        "listing.html", images=images, my_username=session.get("username"), car=this_car
    )


@app.route("/delete_action/<car_id>", methods=["POST"])
def delete(car_id):
    delete_car_json(car_id)

    car = Car.query.get_or_404(car_id)
    db.session.delete(car)
    db.session.commit()

    return redirect(url_for("catalog"))


@app.route("/delete_user_action/<user_name>", methods=["POST"])
def delete_user(user_name):
    session_username = session.get("username")
    if not (session_username and user_name == session_username):
        return redirect(url_for("login", message="Log in your profile!"))

    user_to_delete = User.query.filter_by(username=user_name).first_or_404()
    car_ids = [car.id for car in user_to_delete.cars]
    for car_id in car_ids:
        delete_car_json(car_id)

    db.session.delete(user_to_delete)
    db.session.commit()

    session.clear()
    return redirect(url_for("home"))
