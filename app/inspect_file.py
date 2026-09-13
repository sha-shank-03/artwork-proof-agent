"""Isolated decoder. Input: bytes on stdin. Output: bounded measurements/previews JSON."""
import base64
import io
import json
import sys
import warnings
from PIL import Image

MAX_BYTES = 10*1024*1024
MAX_PIXELS = 25_000_000

def inspect(data):
    if not data or len(data) > MAX_BYTES:
        raise ValueError("File must be between 1 byte and 10 MB")
    previews = []; pages = []
    def preview(im):
        im = im.convert("RGBA"); im.thumbnail((1200,1200))
        b = io.BytesIO(); im.save(b, "PNG")
        previews.append(base64.b64encode(b.getvalue()).decode())
    if data.startswith(b"%PDF-"):
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data), strict=True)
        if reader.is_encrypted or not 1 <= len(reader.pages) <= 5:
            raise ValueError("Only unencrypted PDFs with 1-5 pages are supported")
        import pypdfium2 as pdfium
        doc = pdfium.PdfDocument(data)
        for i in range(len(doc)):
            page = doc[i]; width, height = page.get_size()
            if width <= 0 or height <= 0 or width > 14400 or height > 14400:
                raise ValueError("PDF dimensions out of bounds")
            scale = min(2, 1200/max(width,height)); bitmap = page.render(scale=scale)
            image = bitmap.to_pil(); preview(image)
            pages.append({"widthPoints": round(width,2), "heightPoints": round(height,2)})
            image.close(); bitmap.close(); page.close()
        doc.close(); fmt = "PDF"
    else:
        if not (data.startswith(b"\x89PNG\r\n\x1a\n") or data.startswith(b"\xff\xd8\xff")):
            raise ValueError("Only PNG, JPEG and PDF are supported")
        Image.MAX_IMAGE_PIXELS = MAX_PIXELS
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(io.BytesIO(data)) as im:
            fmt = im.format
            if fmt not in ("PNG","JPEG") or im.width*im.height > MAX_PIXELS or max(im.size)>16000:
                raise ValueError("Image dimensions or format are not supported")
            if getattr(im,"n_frames",1) != 1:
                raise ValueError("Animated images are not supported")
            im.load(); rgba=im.convert("RGBA"); alpha=rgba.getchannel("A"); bounds=alpha.getbbox()
            margins = [bounds[0],bounds[1],im.width-bounds[2],im.height-bounds[3]] if bounds else [im.width,im.height,0,0]
            pages.append({"widthPixels": im.width,"heightPixels":im.height,"transparent":alpha.getextrema()[0]<255,"alphaMargins":margins})
            preview(rgba)
    return {"format":fmt,"pages":pages,"previews":previews}

if __name__ == "__main__":
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU,(10,10))
        if sys.platform.startswith("linux"):
            resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
        result=inspect(sys.stdin.buffer.read(MAX_BYTES+1))
        print(json.dumps(result))
    except Exception:
        print(json.dumps({"error":"File could not be decoded safely; use a valid PNG, JPEG or unencrypted 1-5 page PDF."}))
        sys.exit(1)
