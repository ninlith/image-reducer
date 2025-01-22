"""Image processing service."""

import asyncio
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse
from PIL import Image, ImageOps, ExifTags, UnidentifiedImageError
import pillow_avif  # noqa: F401  # pylint: disable=unused-import

app = FastAPI()
INVALID_MIME_ERROR="Invalid MIME type."
INVALID_IMAGE_ERROR="Invalid image file."


def downscale_to_max_dimension(image: Image, max_dimension) -> Image:
    """Scale the image dimensions down proportionally to fit within a maximum dimension."""
    width, height = image.size
    if width <= max_dimension and height <= max_dimension:
        return image
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


def process_image_blocking(file_content: bytes) -> io.BytesIO:
    """Verify, scale, and convert the image and return it as a BytesIO object."""
    image = Image.open(io.BytesIO(file_content))
    image.verify()  # "...after using this method, you must reopen the image file."
    image = Image.open(io.BytesIO(file_content))
    exif = filter_exif(image.getexif())
    image = downscale_to_max_dimension(image, 1600)
    output_buffer = io.BytesIO()
    image.save(
        output_buffer,
        format="AVIF",          # image format (set if using a file object instead of a filename)
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
    output_buffer.seek(0)  # rewind the buffer
    return output_buffer


@app.get("/", include_in_schema=False)
def read_root():
    """Redirect to the interactive API docs."""
    return RedirectResponse(url="/docs")


@app.post(
    "/process/",
    responses = {
        200: {
            "content": {"image/avif": {}}
        },
    },
    response_class=StreamingResponse,  # https://github.com/tiangolo/fastapi/issues/3258
)
async def process_image(file: UploadFile = File(...)):
    """Return the processed image."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=422, detail=INVALID_MIME_ERROR)
    file_content = await file.read()  # read the file into memory
    try:
        output_buffer = await asyncio.to_thread(process_image_blocking, file_content)
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=422, detail=INVALID_IMAGE_ERROR) from exc
    return StreamingResponse(content=output_buffer, media_type="image/avif")
