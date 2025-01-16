import os
import pillow_avif
#import pillow_heif
from PIL import Image

MAX_DIMENSION = 1600

#pillow_heif.register_avif_opener()

# Load the image
original_image = Image.open("2.jpg")

# Resize the image to MAX_DIMENSION width or height
original_width, original_height = original_image.size
if original_width > original_height:
    new_width = MAX_DIMENSION
    new_height = int(original_height*(new_width/original_width))
else:
    new_height = MAX_DIMENSION
    new_width = int(original_width*(new_height/original_height))
resized_image = original_image.resize((new_width, new_height), resample=Image.BICUBIC)

# Save the resized image
resized_image.save("resized_image.png")
resized_image.save(
    "resized_image.avif", 
    quality=60,             # quality level (0-100)  
#    speed=0,                # encoding speed (-1 default, 0 slowest, 10 fastest)
#    range="limited",        # limited range (16-235 for luma, 16-240 for chroma)
    subsampling='4:2:0',    # chroma subsampling, 4:0:0 for grayscale
)

from wand.image import Image

with Image(filename='"resized_image.png"') as original:
    with original.convert('avif') as converted:
        converted.save(filename='pikachu.avif')

# https://github.com/manoreken2/pillow-avif-plugin-HDR10




# Display the resized image
#resized_image.show()
#Image.open("resized_image.avif").show()

import os
print(os.stat("resized_image.avif").st_size)
#print(os.stat("resized_image.webp").st_size)