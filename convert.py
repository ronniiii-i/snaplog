from PIL import Image
import numpy as np

def convert_binn_to_png(binn_file_path, output_path):
    with open(binn_file_path, "rb") as f:
        # Read the raw bytes
        raw_data = f.read()

    # The width and height of the screen for this example
    # You should match these to the screen resolution or the monitor you're capturing
    screen_width = 1920
    screen_height = 1080

    # Convert raw data to a numpy array (it should be in RGB format)
    img_array = np.frombuffer(raw_data, dtype=np.uint8)
    img_array = img_array.reshape((screen_height, screen_width, 3))  # RGB image

    # Create an Image from the array
    img = Image.fromarray(img_array)

    # Save the image as PNG
    img.save(output_path)
    print(f"Image saved to {output_path}")

# Example usage:
convert_binn_to_png("../screenshots/screen_20250414_162649.binn", "output_image.png")
