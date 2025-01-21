from PIL import Image, ImageOps, ExifTags


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
