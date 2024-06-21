import cv2
import numpy as np
import base64
import math
from scipy.optimize import minimize


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
    rotated_subimage = rotate_image(subimage)
    return rotated_subimage


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


def rotate_image(img):
    img = crop_image(img)
    mask = get_mask(img, CORNER_THRESHOLD, 255)
    angle = optimal_rotation(mask)
    M = cv2.getRotationMatrix2D(
        (img.shape[1] / 2, img.shape[0] / 2), angle, 1)
    img = cv2.warpAffine(
        img, M, (img.shape[1], img.shape[0]), borderValue=(255, 255, 255))
    img = crop_image(img)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


def optimal_rotation(mask):
    starting_angle = get_starting_angle(mask)
    result = minimize(pixel_diff, [starting_angle], args=(mask,),  bounds=[(-45, 45)],
                      options={'finite_diff_rel_step': 0.5, 'accuracy': 0.01, 'eps': 0.1})
    return result.x[0] if result.success else 0


def pixel_diff(angle, img):
    try:
        M = cv2.getRotationMatrix2D(
            (img.shape[1] / 2, img.shape[0] / 2), angle[0], 1)
        rotated_img = cv2.warpAffine(
            img, M, (img.shape[1], img.shape[0]), borderValue=(255, 255, 255))

        pixel_difference = np.sum(img == 0) - np.sum(rotated_img == 0)
        if pixel_difference > 0:
            return 1e4 * pixel_difference

        rotated_img = crop_image(rotated_img)
        nonpixel_difference = np.sum(
            img == 255) - np.sum(rotated_img == 255)

        ratio = nonpixel_difference / \
            (pixel_difference if pixel_difference != 0 else 1)
        return ratio * math.copysign(1, angle[0])
    except Exception as e:
        print(f"Error in pixel_diff: {e}")
        return 1e9


def get_starting_angle(mask):
    left_result = pixel_diff([-0.5], mask)
    right_result = pixel_diff([0.5], mask)
    if left_result < right_result:
        return 0.5
    elif right_result > left_result:
        return -0.5
    else:
        return 0.5


def get_mask(img, lower_threshold, upper_threshold):
    lower_threshold = np.array([lower_threshold] * 3)
    upper_threshold = np.array([upper_threshold] * 3)
    mask = cv2.inRange(img, lower_threshold, upper_threshold)
    mask = cv2.bitwise_not(mask)
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_width = MIN_OBJECT_RATIO * img.shape[1]
    filtered_contours = [cnt for cnt in contours if cv2.boundingRect(cnt)[
        2] >= min_width]
    mask = np.zeros_like(mask)
    cv2.drawContours(mask, filtered_contours, -1,
                     255, thickness=cv2.FILLED)
    mask = cv2.bitwise_not(mask)
    return mask


def read_and_decode_image(scanned_image) -> np.ndarray:
    npimg = np.frombuffer(scanned_image.read(), np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    return img
