import os
import uuid
from fastapi import APIRouter, UploadFile, File
from main import UPLOAD_DIR

router = APIRouter(prefix="/api")


@router.post("/upload")
async def upload_images(files: list[UploadFile] = File(...)):
    if len(files) < 2:
        return {"error": "At least 2 images required for multi-angle estimation"}, 400

    saved = []
    for f in files:
        ext = f.filename.split(".")[-1] if "." in (f.filename or "") else "jpg"
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        contents = await f.read()
        with open(filepath, "wb") as out:
            out.write(contents)
        saved.append({"id": uuid.uuid4().hex[:12], "path": filepath, "filename": f.filename})

    return {"images": saved, "count": len(saved)}
