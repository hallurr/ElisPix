import cv2
import numpy as np
import base64
from scipy.optimize import minimize

CORNER_THRESHOLD = 200
WHITE_COLOR = (255, 255, 255)
PAD_RATIO = 0.01
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

    # subtract 1% from each side to remove border
    height, width, _ = rotated_subimage.shape
    # border = int(
    #    min(rotated_subimage.shape[0], rotated_subimage.shape[1]) * 0.002)
   # rotated_subimage = rotated_subimage[border:height -
   #                                    border, border:width - border]
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
    img_without_border = img[pad_height:height -
                             pad_height, pad_width:width - pad_width]
    img_with_border = add_border_to_image(
        img_without_border, pad_height, pad_width)
    contours = find_contours_in_range(
        img_with_border, CORNER_THRESHOLD, WHITE_COLOR[0])
    rectangles = [create_rectangle_from_contour(cnt) for cnt in contours if create_rectangle_from_contour(
        cnt)[2] >= width * MIN_OBJECT_RATIO and create_rectangle_from_contour(cnt)[3] >= height * MIN_OBJECT_RATIO]
    return [(y, y + h, x, x + w) for x, y, w, h in rectangles]


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
    result = minimize(pixel_diff, [starting_angle], args=(mask,), method='L-BFGS-B', bounds=[(-45, 45)],
                      options={'finite_diff_rel_step': starting_angle, 'eps': starting_angle / 2})
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
        return ratio
    except Exception as e:
        print(f"Error in pixel_diff: {e}")
        return 1e9


def get_starting_angle(mask):
    POS_ROTATION = 0.5
    NEG_ROTATION = POS_ROTATION * -1
    neg_rotation_result = pixel_diff([NEG_ROTATION], mask)
    pos_rotation_result = pixel_diff([POS_ROTATION], mask)
    rotation_total = neg_rotation_result + pos_rotation_result
    if neg_rotation_result < pos_rotation_result:
        print('neg', (neg_rotation_result / rotation_total) * POS_ROTATION - 1)
        return (neg_rotation_result / rotation_total) * POS_ROTATION - 1
    else:
        print('pos', (pos_rotation_result / rotation_total) * NEG_ROTATION - 1)
        return (pos_rotation_result / rotation_total) * NEG_ROTATION + 1


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
