import cv2
import numpy as np
import base64
from scipy.optimize import minimize

CROP_THRESHOLD = 160
SPLIT_THRESHOLD = 220
CORNER_THRESHOLD = 220
WHITE_COLOR = (255, 255, 255)
PAD_RATIO = 0.01
MIN_OBJECT_RATIO = 0.1
THUMBNAIL_MAX_DIMENSION = 200


def crop_image(img):
    mask = get_mask(img, CROP_THRESHOLD, 255)
    # Convert image to grayscale by averaging the color channels
    img_bw = np.mean(img, axis=2)
    # Find columns and rows where not all pixels are above the threshold
    cols_to_keep = np.where(np.any(img_bw <= CROP_THRESHOLD, axis=0))[0]
    rows_to_keep = np.where(np.any(img_bw <= CROP_THRESHOLD, axis=1))[0]
    # Crop the image to keep only the desired rows and columns
    img_cropped = img[np.min(rows_to_keep):np.max(
        rows_to_keep)+1, np.min(cols_to_keep):np.max(cols_to_keep)+1, :]
    return img_cropped


def add_border_to_image(img, pad_height, pad_width):
    return cv2.copyMakeBorder(img, pad_height, pad_height, pad_width, pad_width, cv2.BORDER_CONSTANT, value=WHITE_COLOR)


def extract_subimage_by_coordinates(image, coordinates, simple_anglefinder=False):
    y1, y2, x1, x2 = coordinates
    subimage = cv2.cvtColor(image[y1:y2, x1:x2], cv2.COLOR_BGR2RGB)
    if simple_anglefinder:
        angle = find_angle(subimage)
        rotated_subimage = rotate_image(subimage, angle=angle)
    else:
        rotated_subimage = rotate_image(subimage)

    # subtract 1% from each side to remove border
    height, width, _ = rotated_subimage.shape
    border = int(
        min(rotated_subimage.shape[0], rotated_subimage.shape[1]) * 0.007)
    rotated_subimage = rotated_subimage[border:height -
                                        border, border:width - border]
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


def is_rectangle_inside(rect1, rect2):
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    return (x2 <= x1 < x2 + w2) and (x2 < x1 + w1 <= x2 + w2) and \
           (y2 <= y1 < y2 + h2) and (y2 < y1 + h1 <= y2 + h2)


def get_images_after_splitting(img):
    height, width, _ = img.shape
    pad_height, pad_width = int(height * PAD_RATIO), int(width * PAD_RATIO)
    img_without_border = img[pad_height:height -
                             pad_height, pad_width:width - pad_width]
    img_with_border = add_border_to_image(
        img_without_border, pad_height, pad_width)
    contours = find_contours_in_range(
        img_with_border, SPLIT_THRESHOLD, WHITE_COLOR[0])
    rectangles = [create_rectangle_from_contour(cnt) for cnt in contours if create_rectangle_from_contour(
        cnt)[2] >= width * MIN_OBJECT_RATIO and create_rectangle_from_contour(cnt)[3] >= height * MIN_OBJECT_RATIO]
    filtered_rectangles = []
    for rect in rectangles:
        if not any(is_rectangle_inside(rect, other_rect) for other_rect in rectangles if rect != other_rect):
            filtered_rectangles.append(rect)
    return [(y, y + h, x, x + w) for x, y, w, h in filtered_rectangles]


def encode_image_to_base64(image):
    _, buffer = cv2.imencode('.png', image)
    return base64.b64encode(buffer).decode('utf-8')


def get_image_json(image, filename):
    thumbnail = generate_thumbnail(image)
    return {
        "image": encode_image_to_base64(image),
        "thumbnail": encode_image_to_base64(thumbnail),
        "filename": filename
    }


def generate_thumbnail(image):
    max_dimension = max(image.shape[:2])
    scale = THUMBNAIL_MAX_DIMENSION / max_dimension
    return cv2.resize(image, None, fx=scale, fy=scale)


def rotate_image(img, angle=None):
    mask = get_mask(img, CORNER_THRESHOLD, 255)
    if angle is None:
        angle = optimal_rotation(mask)
    M = cv2.getRotationMatrix2D(
        (img.shape[1] / 2, img.shape[0] / 2), angle, 1)
    img = cv2.warpAffine(
        img, M, (img.shape[1], img.shape[0]), borderValue=(255, 255, 255))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = crop_image(img)
    return img


def pixel_diff(angle, mask):
    M = cv2.getRotationMatrix2D(
        (mask.shape[1] / 2, mask.shape[0] / 2), angle[0], 1)
    rotated_mask = cv2.warpAffine(
        mask, M, (mask.shape[1], mask.shape[0]), borderValue=(255, 255, 255))

    white_threshold = 0.9

    allwhiterowcount = sum(
        [1 for row in rotated_mask if np.mean(row == 255) >= white_threshold])
    allwhitecolcount = sum(
        [1 for col in rotated_mask.T if np.mean(col == 255) >= white_threshold])
    maxerror = rotated_mask.shape[0] + rotated_mask.shape[1]
    loss = 1 - (allwhiterowcount + allwhitecolcount) / maxerror
    return loss


def optimal_rotation(mask):
    starting_angle = get_starting_angle(mask)
    result = minimize(pixel_diff, [starting_angle], args=(mask,), method='L-BFGS-B', bounds=[(-45, 45)],
                      options={'finite_diff_rel_step': starting_angle, 'eps': starting_angle / 2})
    return result.x[0] if result.success else 0


def get_starting_angle(mask):
    POS_ROTATION = 0.25
    NEG_ROTATION = POS_ROTATION * -1
    neg_rotation_result = pixel_diff([NEG_ROTATION], mask)
    pos_rotation_result = pixel_diff([POS_ROTATION], mask)
    if neg_rotation_result < pos_rotation_result:
        return (1 - neg_rotation_result) * -3
    else:
        return (1 - pos_rotation_result) * 3


def get_mask(img, mask_1, mask_2):
    lower_threshold = np.array([mask_1] * 3)
    upper_threshold = np.array([mask_2] * 3)
    mask = cv2.inRange(img, lower_threshold, upper_threshold)
    mask = cv2.bitwise_not(mask)
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_width = MIN_OBJECT_RATIO * img.shape[1]

    # Filter contours based on width
    filtered_contours = [cnt for cnt in contours if cv2.boundingRect(cnt)[
        2] >= min_width]

    # Find the largest contour based on area
    if filtered_contours:
        largest_contour = max(filtered_contours, key=cv2.contourArea)
        mask = np.zeros_like(mask)
        cv2.drawContours(mask, [largest_contour], -
                         1, 255, thickness=cv2.FILLED)
    else:
        mask = np.zeros_like(mask)

    mask = cv2.bitwise_not(mask)
    return mask


def read_and_decode_image(scanned_image) -> np.ndarray:
    npimg = np.frombuffer(scanned_image.read(), np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    return img


def find_angle(image):
    angle_OG = 20
    M = cv2.getRotationMatrix2D(
        (image.shape[1] / 2, image.shape[0] / 2), angle_OG, 1)
    img = cv2.warpAffine(
        image, M, (image.shape[1], image.shape[0]), borderValue=(255, 255, 255))
    mask = cv2.inRange(
        img, (CORNER_THRESHOLD, CORNER_THRESHOLD, CORNER_THRESHOLD), (255, 255, 255))
    angles = []
    for _ in range(4):
        mask = cv2.rotate(mask, cv2.ROTATE_90_CLOCKWISE)
        sideA_length = np.argmax(mask[0, :] == 0)
        sideB_length = np.argmax(mask[:, 0] == 0)
        sideC_length = np.sqrt(sideA_length ** 2 + sideB_length ** 2)
        angle = angle_OG - \
            (np.arccos(sideA_length / sideC_length) * 180 / np.pi)
        angles.append(angle)
    return np.median(angles)
