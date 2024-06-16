import numpy as np
import cv2
import pathlib
from scipy.optimize import minimize
import math

SPLIT_THRESH = 200
CORNER_THRESH = 235
WHITE = 255
PAD_RATIO = 0.1
MIN_OBJECT_RATIO = 0.1


def pixel_diff(angle, img):
    """Calculate pixel difference after rotating the image."""
    try:
        M = cv2.getRotationMatrix2D(
            (img.shape[1] / 2, img.shape[0] / 2), angle[0], 1)
        rotated_img = cv2.warpAffine(
            img, M, (img.shape[1], img.shape[0]), borderValue=(WHITE, WHITE, WHITE))

        pixel_difference = np.sum(img == 0) - np.sum(rotated_img == 0)
        if pixel_difference > 0:
            return 1e4 * pixel_difference

        rotated_img = crop_img(rotated_img)
        nonpixel_difference = np.sum(img == 255) - np.sum(rotated_img == 255)

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


def optimal_rotation(mask):
    """Find the optimal rotation angle to minimize pixel difference."""
    starting_angle = get_starting_angle(mask)
    result = minimize(pixel_diff, [starting_angle], args=(mask,),  bounds=[(-45, 45)],
                      options={'finite_diff_rel_step': 0.5, 'accuracy': 0.01, 'eps': 0.1})
    return result.x[0] if result.success else 0


def get_mask(img, lower_threshold, upper_threshold):
    """Generate mask for the image within the threshold range."""
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
    cv2.drawContours(mask, filtered_contours, -1, WHITE, thickness=cv2.FILLED)
    mask = cv2.bitwise_not(mask)
    return mask


def get_contours(img, lower_threshold, upper_threshold):
    """Get contours within the threshold range."""
    lower_threshold = np.array([lower_threshold] * 3)
    upper_threshold = np.array([upper_threshold] * 3)
    mask = cv2.inRange(img, lower_threshold, upper_threshold)
    mask = cv2.bitwise_not(mask)
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_width = MIN_OBJECT_RATIO * img.shape[1]
    filtered_contours = [cnt for cnt in contours if cv2.boundingRect(cnt)[
        2] >= min_width]
    return filtered_contours


def add_border(img, pad_height, pad_width):
    """Add a white border to the image."""
    return cv2.copyMakeBorder(img, pad_height, pad_height, pad_width, pad_width, cv2.BORDER_CONSTANT, value=[WHITE, WHITE, WHITE])


def create_rectangle(cnt):
    """Create a bounding rectangle from contour."""
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    return cv2.boundingRect(np.int0(box))


def get_split_images(img):
    """Get the coordinates of split images."""
    height, width, _ = img.shape
    pad_height = int(height * PAD_RATIO)
    pad_width = int(width * PAD_RATIO)
    img = add_border(img, pad_height, pad_width)
    contours = get_contours(img, SPLIT_THRESH, WHITE)
    rectangles = [cnt for cnt in contours if create_rectangle(
        cnt)[2] >= width * MIN_OBJECT_RATIO and create_rectangle(cnt)[3] >= height * MIN_OBJECT_RATIO]
    rectangle_coordinates = [(y - pad_height, y - pad_height + h, x - pad_width,
                              x - pad_width + w) for x, y, w, h in map(create_rectangle, rectangles)]
    return rectangle_coordinates


def rotate_img(img):
    """Rotate the image based on the optimal angle."""
    img = crop_img(img)
    mask = get_mask(img, CORNER_THRESH, WHITE)
    angle = optimal_rotation(mask)
    M = cv2.getRotationMatrix2D((img.shape[1] / 2, img.shape[0] / 2), angle, 1)
    img = cv2.warpAffine(
        img, M, (img.shape[1], img.shape[0]), borderValue=(WHITE, WHITE, WHITE))
    img = crop_img(img)
    return img


def crop_img(img):
    """Crop the white borders of the image."""
    for _ in range(4):
        while np.all(img[0] >= CORNER_THRESH):
            img = img[1:]
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    return img


def get_current_image(image, coordinates):
    """Get the current image based on coordinates."""
    y1, y2, x1, x2 = coordinates
    image = cv2.cvtColor(image[y1:y2, x1:x2], cv2.COLOR_BGR2RGB)
    image = crop_img(image)
    return image


class ImageProcessor:
    def __init__(self, input_folder, output_folder):
        self.input_folder = pathlib.Path(input_folder)
        self.output_folder = pathlib.Path(output_folder)
        self.initialize_folders()

    def initialize_folders(self):
        """Create input and output folders if they don't exist."""
        self.input_folder.mkdir(parents=True, exist_ok=True)
        self.output_folder.mkdir(parents=True, exist_ok=True)

    def process_images(self):
        """Process all images in the input folder."""
        pic_list = list(self.input_folder.glob('*.tif'))
        for pic_index, pic in enumerate(pic_list):
            print(f'Working on {pic}: {pic_index + 1} of {len(pic_list)}')
            img = cv2.imread(str(pic))
            image_coordinates = get_split_images(img)
            for index, coordinates in enumerate(image_coordinates):
                try:
                    curr_image = get_current_image(img, coordinates)
                    curr_image = rotate_img(curr_image)
                    curr_image = cv2.cvtColor(curr_image, cv2.COLOR_BGR2RGB)
                    cv2.imwrite(str(self.output_folder /
                                f'{pic.stem}_{index + 1}.png'), curr_image)
                except Exception as e:
                    print(f'Error with {index + 1} from {pic} : {e}')
                    continue


if __name__ == "__main__":
    image_processor = ImageProcessor('input', 'output')
    image_processor.process_images()
