from models import Car
from main import db,app

if __name__=="__main__":
    with app.app_context():
        cars = Car.query.all()  # Връща всички записи от таблицата `Car`
        for car in cars:
            print(f"{car.id}: {car.brand} {car.model} - ${car.price}")
