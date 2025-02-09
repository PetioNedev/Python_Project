"""Module for handling JSON file operations related to car images."""

import json
import os
from typing import Dict, List, Union

JSON_PATH = "src\car_images.json"
IMG_FOLDER_PATH = "src\static\cars_img"


def load_images() -> Dict[str, List[str]]:
    """Load the images from the JSON file. If the file does not exist, return an empty dictionary."""
    if not os.path.exists(JSON_PATH):
        return {}
    with open(JSON_PATH, "r") as f:
        return json.load(f)


def save_images(data: Dict[str, List[str]]) -> None:
    """Save the given images data into the JSON file."""
    with open(JSON_PATH, "w") as f:
        json.dump(data, f, indent=4)


def upload_images_json(car_id: Union[int, str], data: List[str]) -> None:
    """Upload images related to a specific car ID into the JSON file."""
    images = load_images()
    if str(car_id) in images:
        images[str(car_id)].append(data)
    else:
        images[str(car_id)] = data

    save_images(images)

    print("File uploaded successfully")


def delete_single_image_json(car_id: Union[int, str], filename: str) -> None:
    """Delete a specific image from the JSON file and remove the corresponding file from storage."""
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


def delete_car_json(car_id: Union[int, str]) -> None:
    """Delete all images related to a specific car ID from the JSON file and remove them from storage."""
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


def get_single_car_images(car_id: Union[int, str]) -> List[str]:
    """Retrieve the list of images for a specific car ID."""
    all_images = load_images()

    if str(car_id) in all_images:
        return all_images[str(car_id)]

    return []
