import io
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image

app = FastAPI(title="Image to ICO Converter", description="Микросервис для конвертации JPEG/PNG в формат ICO")

@app.post("/convert")
async def convert_image_to_ico(
    file: UploadFile = File(...),
    size: str = Form("all")
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением (JPEG или PNG)")
    
    try:
        image_data = await file.read()
        img = Image.open(io.BytesIO(image_data))
        
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            
        sizes_map = {
          "16": [(16, 16)],
          "32": [(32, 32)],
          "48": [(48, 48)],
          "256": [(256, 256)],
          "all": [(16, 16), (32, 32), (48, 48), (256, 256)]
        }
        
        target_sizes = sizes_map.get(size, sizes_map["all"])
        
        ico_io = io.BytesIO()
        img.save(ico_io, format="ICO", sizes=target_sizes)
        ico_io.seek(0)
        
        filename = file.filename.rsplit(".", 1)[0] + ".ico"
        
        return StreamingResponse(
            ico_io, 
            media_type="image/x-icon", 
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка конвертации: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()
