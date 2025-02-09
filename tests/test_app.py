import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from main import app
from utils import db
from models import User, Car
from src.json_file_logic import (
    load_images,
    save_images,
    upload_images_json,
    delete_single_image_json,
    delete_car_json,
)
import json


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

        with app.app_context():
            db.drop_all()


def test_user_model():
    with app.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com", password="testpass")
        db.session.add(user)
        db.session.commit()

        found_user = User.query.filter_by(username="testuser").first()
        assert found_user is not None
        assert found_user.email == "test@example.com"


def test_car_model():
    with app.app_context():
        db.create_all()

        user = User(username="carowner", email="owner@example.com", password="pass")
        db.session.add(user)
        db.session.commit()

        car = Car(
            user_id=user.id,
            mileage=10000,
            brand="BMW",
            model="X5",
            category="SUV",
            price=50000,
            year=2020,
        )
        db.session.add(car)
        db.session.commit()

        found_car = Car.query.filter_by(brand="BMW").first()
        assert found_car is not None
        assert found_car.user_id == user.id


def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Home" in response.data


def test_register_login_logout(client):
    client.post(
        "/register_action",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass",
        },
    )
    response = client.post(
        "/login_action", data={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert sess["username"] == "testuser"
    response = client.get("/logout")
    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert "username" not in sess


def test_json_operations():
    test_data = {"1": ["image1.jpg", "image2.jpg"]}
    save_images(test_data)
    loaded_data = load_images()
    assert loaded_data == test_data

    upload_images_json(2, ["car2_img.jpg"])
    loaded_data = load_images()
    assert "2" in loaded_data and "car2_img.jpg" in loaded_data["2"]

    delete_single_image_json(2, "car2_img.jpg")
    loaded_data = load_images()
    assert "2" not in loaded_data

    delete_car_json(1)
    loaded_data = load_images()
    assert "1" not in loaded_data
