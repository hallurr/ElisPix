from image_utils import get_image_json, get_images_after_splitting, extract_subimage_by_coordinates, read_and_decode_image
import logging
import os

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ImageProcessor:
    def __init__(self):
        self.results = []
        self.current_filename = None
        self.file_name = None
        self.scanned_img = None
        self.scanned_img_np = None

    def process_images(self, image_files):
        for scanned_image_index, scanned_image in enumerate(image_files):
            try:
                self.current_filename = scanned_image.filename
                self.file_name = os.path.splitext(scanned_image.filename)[
                    0] + '-' + str(scanned_image_index + 1)
                self.log_current_file(scanned_image_index, image_files)
                self.scanned_img_np = read_and_decode_image(scanned_image)
                self.process_single_image()
            except Exception as e:
                self.log_decoding_error(e)
        return self.results

    def process_single_image(self):
        if self.scanned_img_np is not None:
            image_coordinates = get_images_after_splitting(self.scanned_img_np)
            for index, coordinates in enumerate(image_coordinates):
                try:
                    curr_image = extract_subimage_by_coordinates(
                        self.scanned_img_np, coordinates, simple_anglefinder=True)
                    curr_file = self.file_name + "-" + str(index+1)
                    self.results.append(get_image_json(
                        curr_image, curr_file))
                except Exception as e:
                    self.log_processing_error(index, e)

    def log_current_file(self, index, count):
        logger.info(
            f'Working on {self.current_filename}: {index + 1} of {len(count)}')

    def log_processing_error(self, index, error):
        logger.error(
            f'Error processing {index + 1} from {self.current_filename}: {error}')

    def log_decoding_error(self, error):
        logger.error(
            f'Failed to read or decode {self.current_filename}: {error}')
