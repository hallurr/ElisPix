import numpy as np
import cv2
from scipy.optimize import minimize
import math
import base64


class ImageProcessor:
    def __init__(self):
        self.split_threshold = 200
        self.corner_threshold = 235
        self.white = 255
        self.pad_ratio = 0.1
        self.min_object_ratio = 0.1

    def process_images(self, image_files):
        """Process and return the images."""
        output_images = []
        for pic_index, pic in enumerate(image_files):
            print(
                f'Working on {pic.filename}: {pic_index + 1} of {len(image_files)}')
            npimg = np.fromstring(pic.read(), np.uint8)
            img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
            image_coordinates = self.get_split_images(img)
            for index, coordinates in enumerate(image_coordinates):
                try:
                    curr_image = self.get_current_image(img, coordinates)
                    curr_image = self.rotate_img(curr_image)
                    curr_image = cv2.cvtColor(curr_image, cv2.COLOR_BGR2RGB)
                    _, buffer = cv2.imencode('.png', curr_image)
                    b64_string = base64.b64encode(buffer).decode('utf-8')
                    output_images.append(b64_string)
                except Exception as e:
                    print(f'Error with {index + 1} from {pic.filename} : {e}')
                    continue
        return output_images

    def pixel_diff(self, angle, img):
        """Calculate pixel difference after rotating the image."""
        try:
            M = cv2.getRotationMatrix2D(
                (img.shape[1] / 2, img.shape[0] / 2), angle[0], 1)
            rotated_img = cv2.warpAffine(
                img, M, (img.shape[1], img.shape[0]), borderValue=(255, 255, 255))

            pixel_difference = np.sum(img == 0) - np.sum(rotated_img == 0)
            if pixel_difference > 0:
                return 1e4 * pixel_difference

            rotated_img = self.crop_img(rotated_img)
            nonpixel_difference = np.sum(
                img == 255) - np.sum(rotated_img == 255)

            ratio = nonpixel_difference / \
                (pixel_difference if pixel_difference != 0 else 1)
            return ratio * math.copysign(1, angle[0])
        except Exception as e:
            print(f"Error in pixel_diff: {e}")
            return 1e9

    def get_starting_angle(self, mask):
        left_result = self.pixel_diff([-0.5], mask)
        right_result = self.pixel_diff([0.5], mask)
        if left_result < right_result:
            return 0.5
        elif right_result > left_result:
            return -0.5
        else:
            return 0.5

    def optimal_rotation(self, mask):
        """Find the optimal rotation angle to minimize pixel difference."""
        starting_angle = self.get_starting_angle(mask)
        result = minimize(self.pixel_diff, [starting_angle], args=(mask,),  bounds=[(-45, 45)],
                          options={'finite_diff_rel_step': 0.5, 'accuracy': 0.01, 'eps': 0.1})
        return result.x[0] if result.success else 0

    def get_mask(self, img, lower_threshold, upper_threshold):
        """Generate mask for the image within the threshold range."""
        lower_threshold = np.array([lower_threshold] * 3)
        upper_threshold = np.array([upper_threshold] * 3)
        mask = cv2.inRange(img, lower_threshold, upper_threshold)
        mask = cv2.bitwise_not(mask)
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_width = self.min_object_ratio * img.shape[1]
        filtered_contours = [cnt for cnt in contours if cv2.boundingRect(cnt)[
            2] >= min_width]
        mask = np.zeros_like(mask)
        cv2.drawContours(mask, filtered_contours, -1,
                         255, thickness=cv2.FILLED)
        mask = cv2.bitwise_not(mask)
        return mask

    def get_contours(self, img, lower_threshold, upper_threshold):
        """Get contours within the threshold range."""
        lower_threshold = np.array([lower_threshold] * 3)
        upper_threshold = np.array([upper_threshold] * 3)
        mask = cv2.inRange(img, lower_threshold, upper_threshold)
        mask = cv2.bitwise_not(mask)
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_width = self.min_object_ratio * img.shape[1]
        filtered_contours = [cnt for cnt in contours if cv2.boundingRect(cnt)[
            2] >= min_width]
        return filtered_contours

    def add_border(self, img, pad_height, pad_width):
        """Add a white border to the image."""
        return cv2.copyMakeBorder(img, pad_height, pad_height, pad_width, pad_width, cv2.BORDER_CONSTANT, value=[255, 255, 255])

    def create_rectangle(self, cnt):
        """Create a bounding rectangle from contour."""
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        return cv2.boundingRect(np.int0(box))

    def get_split_images(self, img):
        """Get the coordinates of split images."""
        height, width, _ = img.shape
        pad_height = int(height * self.pad_ratio)
        pad_width = int(width * self.pad_ratio)
        img = self.add_border(img, pad_height, pad_width)
        contours = self.get_contours(img, self.split_threshold, 255)
        rectangles = [cnt for cnt in contours if self.create_rectangle(
            cnt)[2] >= width * self.min_object_ratio and self.create_rectangle(cnt)[3] >= height * self.min_object_ratio]
        rectangle_coordinates = [(y - pad_height, y - pad_height + h, x - pad_width,
                                  x - pad_width + w) for x, y, w, h in map(self.create_rectangle, rectangles)]
        return rectangle_coordinates

    def rotate_img(self, img):
        """Rotate the image based on the optimal angle."""
        img = self.crop_img(img)
        mask = self.get_mask(img, self.corner_threshold, 255)
        angle = self.optimal_rotation(mask)
        M = cv2.getRotationMatrix2D(
            (img.shape[1] / 2, img.shape[0] / 2), angle, 1)
        img = cv2.warpAffine(
            img, M, (img.shape[1], img.shape[0]), borderValue=(255, 255, 255))
        img = self.crop_img(img)
        return img

    def crop_img(self, img):
        """Crop the white borders of the image."""
        for _ in range(4):
            while np.all(img[0] >= self.corner_threshold):
                img = img[1:]
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        return img

    def get_current_image(self, image, coordinates):
        """Get the current image based on coordinates."""
        y1, y2, x1, x2 = coordinates
        image = cv2.cvtColor(image[y1:y2, x1:x2], cv2.COLOR_BGR2RGB)
        image = self.crop_img(image)
        return image
