import numpy as np
import matplotlib.image
import matplotlib.pyplot
import cv2
import pathlib
from scipy.optimize import minimize


SPLIT_THRESH = 200
CORNER_THRESH = 235
WHITE = 255
PAD_RATIO = 0.1
MIN_OBJECT_RATIO = 0.1


def get_boundary_values(img):
    height, width = img.shape
    top_half = img[:height//2, :]
    lowermost_y_top_half = np.where(top_half != 0)[0].max()
    bottom_half = img[height//2:, :]
    topmost_y_bottom_half = np.where(bottom_half != 0)[0].min() + height//2
    left_half = img[:, :width//2]
    rightmost_x_left_half = np.where(left_half != 0)[1].max()
    right_half = img[:, width//2:]
    leftmost_x_right_half = np.where(right_half != 0)[1].min() + width//2
    return lowermost_y_top_half, topmost_y_bottom_half, rightmost_x_left_half, leftmost_x_right_half


def pixel_diff(angle, img):
    try:
        M = cv2.getRotationMatrix2D(
            (img.shape[1] / 2, img.shape[0] / 2), angle[0], 1)
        rotated_img = cv2.warpAffine(
            img, M, (img.shape[1], img.shape[0]), borderValue=(255, 255, 255))
        top, bottom, left, right = get_boundary_values(rotated_img)

        pixel_sum_original = np.sum(img == 255)
        pixel_sum_rotated = np.sum(rotated_img == 255)

        if pixel_sum_rotated > pixel_sum_original:
            return 1e4 * (pixel_sum_rotated - pixel_sum_original + 2)
        return top + bottom + left + right
    except Exception as e:
        print(f"Error in pixel_diff: {e}")
        return 1e9


def optimal_rotation(mask):
    result = minimize(pixel_diff, [-3], args=(mask,),  bounds=[(-45, 45)],
                      options={'finite_diff_rel_step': 0.5, 'eps': 0.1})
    if result.success:
        return result.x[0]
    else:
        return 0


def get_mask(img, lower_threshold, upper_threshold):
    LOWER_THRESHOLD = np.array(
        [lower_threshold, lower_threshold, lower_threshold])
    UPPER_THRESHOLD = np.array(
        [upper_threshold, upper_threshold, upper_threshold])
    mask = cv2.inRange(img, LOWER_THRESHOLD, UPPER_THRESHOLD)
    mask = cv2.bitwise_not(mask)
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_width = MIN_OBJECT_RATIO * img.shape[1]
    filtered_contours = [cnt for cnt in contours if cv2.boundingRect(cnt)[
        2] >= min_width]
    mask = np.zeros_like(mask)
    cv2.drawContours(mask, filtered_contours, -1,
                     (WHITE), thickness=cv2.FILLED)
    mask = cv2.bitwise_not(mask)
    return mask


def get_contours(img, lower_threshold, upper_threshold):
    LOWER_THRESHOLD = np.array(
        [lower_threshold, lower_threshold, lower_threshold])
    UPPER_THRESHOLD = np.array(
        [upper_threshold, upper_threshold, upper_threshold])
    mask = cv2.inRange(img, LOWER_THRESHOLD, UPPER_THRESHOLD)
    mask = cv2.bitwise_not(mask)
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_width = MIN_OBJECT_RATIO * img.shape[1]
    filtered_contours = [cnt for cnt in contours if cv2.boundingRect(cnt)[
        2] >= min_width]
    return filtered_contours


def add_border(img, pad_height, pad_width):
    return cv2.copyMakeBorder(img, pad_height, pad_height, pad_width, pad_width, cv2.BORDER_CONSTANT, value=[WHITE, WHITE, WHITE])


def create_rectangle(cnt):
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    return cv2.boundingRect(np.int0(box))


def get_split_images(img):
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


def rotate_img(img, mask):
    angle = optimal_rotation(mask)
    M = cv2.getRotationMatrix2D(
        (img.shape[1] / 2, img.shape[0] / 2), angle, 1)
    rotated_img = cv2.warpAffine(
        img, M, (img.shape[1], img.shape[0]), borderValue=(WHITE, WHITE, WHITE))
    return rotated_img


def crop_img(img):
    for _ in range(4):
        while np.all(img[0] >= CORNER_THRESH):
            img = img[1:]
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    return img


def get_current_image(image, coordinates):
    y1, y2, x1, x2 = coordinates
    image = cv2.cvtColor(
        image[y1:y2, x1:x2], cv2.COLOR_BGR2RGB)
    return image


class ImageProcessor:
    def __init__(self, input_folder, output_folder):
        self.input_folder = pathlib.Path(input_folder)
        self.output_folder = pathlib.Path(output_folder)
        self.initialize_folders()

    def initialize_folders(self):
        self.input_folder.mkdir(parents=True, exist_ok=True)
        self.output_folder.mkdir(parents=True, exist_ok=True)

    def process_images(self):
        pic_list = list(self.input_folder.glob('*.tif'))
        for pic_index, pic in enumerate(pic_list):
            img = cv2.imread(str(pic))
            image_coordinates = get_split_images(img)
            print(f'Working on {pic}: {pic_index+1} of {len(pic_list)}')
            img = matplotlib.image.imread(pic)
            for index, coordinates in enumerate(image_coordinates):
                try:
                    curr_image = get_current_image(img, coordinates)
                    # cv2.imwrite(str(self.output_folder /
                    #                f'{pic.stem}_{index+1}_original.png'), curr_image)
                    curr_image = crop_img(curr_image)
                    curr_mask = get_mask(curr_image, CORNER_THRESH, WHITE)
                    curr_image = rotate_img(curr_image, curr_mask)
                    curr_image = crop_img(curr_image)
                    cv2.imwrite(str(self.output_folder /
                                    f'{pic.stem}_{index+1}.png'), curr_image)
                except Exception as e:
                    print(f'Error with {index + 1} from {pic} : { e }')
                    continue


if __name__ == "__main__":
    image_processor = ImageProcessor('input', 'output')
    image_processor.process_images()
