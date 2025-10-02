from PIL import Image, ImageChops, ImageEnhance
import numpy as np
import os

def convert_to_ela_image(path, quality=90):
    temp_filename = "temp.jpg"
    ela_filename = "temp_ela.png"

    # Save the image at lower quality
    image = Image.open(path).convert('RGB')
    image.save(temp_filename, 'JPEG', quality=quality)

    # Open the temporary image and compare to original
    temp_image = Image.open(temp_filename)
    ela_image = ImageChops.difference(image, temp_image)

    # Find the max difference
    extrema = ela_image.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    scale = 255.0 / max_diff if max_diff != 0 else 1

    ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)
    ela_image.save(ela_filename)

    # Convert to array
    return np.array(ela_image) / 255.0
