import os
from pathlib import Path
import pillow_avif
from PIL import Image, ImageOps, UnidentifiedImageError, ExifTags

def downscale_to_max_dimension(image: Image, max_dimension) -> Image:
    """Scale the image dimensions down proportionally to fit within a maximum dimension."""
    width, height = image.size
    if width <= max_dimension and height <= max_dimension:
        return image
    else:
        return ImageOps.contain(
            image=image,
            size=(max_dimension, max_dimension),
            method=Image.LANCZOS,  # LANCZOS is currently Pillow's highest quality resampling filter
        )

def filter_exif(exif: Image.Exif) -> Image.Exif:
    """Filter out all but a few whitelisted tags from the image's Exif data."""
    filtered_exif = Image.Exif()
    IFD0_whitelist = [
        ExifTags.Base.Make,
        ExifTags.Base.Model,
        ExifTags.Base.Orientation,
        ExifTags.Base.DateTime,
        ExifTags.Base.DateTimeOriginal,
        ExifTags.Base.Software,
        ExifTags.Base.Artist,
        ExifTags.Base.Copyright,
        ExifTags.Base.UserComment,
    ]
    for tag in IFD0_whitelist:
        if tag in exif:
            filtered_exif[tag] = exif[tag]
    filtered_exif[ExifTags.IFD.GPSInfo] = exif.get_ifd(ExifTags.IFD.GPSInfo)
    return filtered_exif

def compress_image(input_path: Path) -> Path:
    image = Image.open(input_path)
    image = downscale_to_max_dimension(image, 1600)
    exif = image.getexif()
    exif = filter_exif(exif)
    output_path = Path("output")/input_path.with_suffix('.avif').name
    image.save(
        output_path,
        format="AVIF",
        quality=50,             # quality level (0-100)  
        speed=0,                # encoding speed (-1 default, 0 slowest = best quality, 10 fastest)
        range="limited",        # YUV range (full, limited)
        subsampling='4:2:0',    # chroma subsampling (4:4:4, 4:2:2, 4:2:0, 4:0:0 = grayscale)
        advanced={
            "enable-qm": 1,     # quantization matrices (1 enable, 0 disable)
        },
        exif=exif,              # Exif data (use None to omit lest a thumbnail be included)
        xmp=None,               # XMP data
        icc_profile=None,       # ICC profile
    )
    return output_path

for image_path in Path("input").glob('*'):
    try:
        compressed_image_path = compress_image(image_path)
        print(f"{compressed_image_path.stat().st_size} ({compressed_image_path})")
    except UnidentifiedImageError:
        print(f"Warning: {image_path} is not a valid image file") 
