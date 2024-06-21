import cv2
import numpy as np
import base64

SPLIT_THRESHOLD = 200
CORNER_THRESHOLD = 235
WHITE_COLOR = (255, 255, 255)
PAD_RATIO = 0.1
MIN_OBJECT_RATIO = 0.1
THUMBNAIL_MAX_DIMENSION = 200


def crop_image(img):
    for _ in range(4):
        while np.all(img[0] >= CORNER_THRESHOLD):
            img = img[1:]
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    return img


def add_border_to_image(img, pad_height, pad_width):
    return cv2.copyMakeBorder(img, pad_height, pad_height, pad_width, pad_width, cv2.BORDER_CONSTANT, value=WHITE_COLOR)


def extract_subimage_by_coordinates(image, coordinates):
    y1, y2, x1, x2 = coordinates
    subimage = cv2.cvtColor(image[y1:y2, x1:x2], cv2.COLOR_BGR2RGB)
    subimage = crop_image(subimage)
    return subimage


def find_contours_in_range(img, lower_threshold, upper_threshold):
    lower_threshold = np.array([lower_threshold] * 3)
    upper_threshold = np.array([upper_threshold] * 3)
    mask = cv2.inRange(img, lower_threshold, upper_threshold)
    mask = cv2.bitwise_not(mask)
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_width = MIN_OBJECT_RATIO * img.shape[1]
    return [cnt for cnt in contours if cv2.boundingRect(cnt)[2] >= min_width]


def create_rectangle_from_contour(cnt):
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    return cv2.boundingRect(np.int0(box))


def get_images_after_splitting(img):
    height, width, _ = img.shape
    pad_height, pad_width = int(height * PAD_RATIO), int(width * PAD_RATIO)
    img_with_border = add_border_to_image(img, pad_height, pad_width)
    contours = find_contours_in_range(
        img_with_border, SPLIT_THRESHOLD, WHITE_COLOR[0])
    rectangles = [create_rectangle_from_contour(cnt) for cnt in contours if create_rectangle_from_contour(
        cnt)[2] >= width * MIN_OBJECT_RATIO and create_rectangle_from_contour(cnt)[3] >= height * MIN_OBJECT_RATIO]
    return [(y - pad_height, y - pad_height + h, x - pad_width, x - pad_width + w) for x, y, w, h in rectangles]


def encode_image_to_base64(image):
    _, buffer = cv2.imencode('.png', image)
    return base64.b64encode(buffer).decode('utf-8')


def get_image_json(image):
    thumbnail = generate_thumbnail(image)
    return {
        "image": encode_image_to_base64(image),
        "thumbnail": encode_image_to_base64(thumbnail)
    }


def generate_thumbnail(image):
    max_dimension = max(image.shape[:2])
    scale = THUMBNAIL_MAX_DIMENSION / max_dimension
    return cv2.resize(image, None, fx=scale, fy=scale)
