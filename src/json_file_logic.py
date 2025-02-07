import json
import os

JSON_PATH = "src\car_images.json"
IMG_FOLDER_PATH = "src\static\cars_img"


def load_images():
    if not os.path.exists(JSON_PATH):
        return {}
    with open(JSON_PATH, "r") as f:
        return json.load(f)


def save_images(data):
    with open(JSON_PATH, "w") as f:
        json.dump(data, f, indent=4)


def upload_images_json(car_id, data):
    images = load_images()
    if str(car_id) in images:
        images[str(car_id)].append(data)
    else:
        images[str(car_id)] = data

    save_images(images)

    print("File uploaded successfully")


def delete_single_image_json(car_id, filename):
    images = load_images()

    if str(car_id) in images and filename in images[str(car_id)]:
        images[str(car_id)].remove(filename)

        image_path = os.path.join(IMG_FOLDER_PATH, filename)
        if os.path.exists(image_path):
            os.remove(image_path)

        if not images[str(car_id)]:
            del images[str(car_id)]

        save_images(images)
        print("Image deleted successfully")


def delete_car_json(car_id):
    all_images = load_images()
    current_car_img = []
    if str(car_id) in all_images:
        current_car_img = all_images.pop(str(car_id))

    for img in current_car_img:
        image_path = os.path.join(IMG_FOLDER_PATH, img)
        if os.path.exists(image_path):
            os.remove(image_path)

    save_images(all_images)
    print("Car deleted successfully")


def get_single_car_images(car_id):
    all_images = load_images()

    if str(car_id) in all_images:
        return all_images[str(car_id)]

    return []
