import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse
from PIL import Image, UnidentifiedImageError
import pillow_avif
from kollikissa.image_processing import downscale_to_max_dimension, filter_exif

app = FastAPI()

"""
asyncio
https://github.com/python-pillow/Pillow/discussions/5831
https://github.com/PogoDigitalism/PillowInAsync/blob/main/examples/async_example.py
https://github.com/PogoDigitalism/SyncInAsync/blob/main/example.py
https://stackoverflow.com/questions/53557304/pil-and-blocking-calls-with-asyncio

docker/pdm/fastapi
https://stackoverflow.com/questions/79010715/how-to-run-a-fastapi-application-on-a-multi-stage-build-using-pdm-as-dependency
https://gist.github.com/martimors/86d72f955944c757a1b0c8b2146f16a3

fastapi responses
https://stackoverflow.com/questions/55873174/how-do-i-return-an-image-in-fastapi
https://stackoverflow.com/questions/62359413/how-to-return-an-image-in-fastapi
https://cloudbytes.dev/snippets/received-return-a-file-from-in-memory-buffer-using-fastapi
"""

@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url='/docs')


@app.post(
    "/convert/",
    responses = {
        200: {
            "content": {"image/avif": {}}
        },
    },
    response_class=StreamingResponse,
)
async def convert_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=422, detail="MIME type needs to be an image.")
    try:
        # Read the file into memory
        file_content = await file.read()
        image = Image.open(io.BytesIO(file_content))
        image.verify()  # "...after using this method, you must reopen the image file."
        image = Image.open(io.BytesIO(file_content))
    except UnidentifiedImageError:
        raise HTTPException(status_code=422, detail="Uploaded file is not a valid image.")
        
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
    output_buffer.seek(0)
    return StreamingResponse(content=output_buffer, media_type="image/avif")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app) #, host="0.0.0.0", port=8000)    