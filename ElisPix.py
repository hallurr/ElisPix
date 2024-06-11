from ImageProcessor import ImageProcessor
import warnings


def submit():
    image_processor = ImageProcessor('input', 'output')
    image_processor.process_images()


if __name__ == "__main__":
    warnings.filterwarnings('ignore')  # Suppress warnings
    submit()
