import os
import uuid
import re
import io
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
import httpx
from server import get_db, now_iso, build_absolute_url, UPLOAD_ROOT

router = APIRouter()

OPENAI_IMAGE_EDITS_URL = "https://api.openai.com/v1/images/edits"
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY") or os.environ.get("EMERGENT_API_KEY") or os.environ.get("OPENAI_API_KEY")

os.makedirs(os.path.join(UPLOAD_ROOT, "visual"), exist_ok=True)

async def _save_uploadfile_to_path(uf: UploadFile, path: str):
    # Save UploadFile content to disk
    contents = await uf.read()
    with open(path, "wb") as f:
        f.write(contents)
    return contents

async def _download_to_path(url: str, path: str):
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.get(url)
        if r.status_code >= 400:
            raise HTTPException(status_code=502, detail=f"Failed to download rendered image: {r.text}")
        with open(path, "wb") as f:
            f.write(r.content)

@router.post("/api/visual-upgrades/render")
async def visual_render(
    request: Request,
    prompt: str = Form(...),
    lead_id: Optional[str] = Form(None),
    size: str = Form("1024x1024"),
    response_format: str = Form("url"),
    image: UploadFile = File(...),
    mask: Optional[UploadFile] = File(None),
    db=Depends(get_db)
):
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="EMERGENT_LLM_KEY is not configured on the server")

    # Validate inputs
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid base image type")
    if mask and (not mask.content_type or not mask.content_type.startswith("image/")):
        raise HTTPException(status_code=400, detail="Invalid mask image type")

    # Persist originals (optional for audit)
    base_name = f"{uuid.uuid4()}_{re.sub(r'[^a-zA-Z0-9._-]', '_', image.filename or 'image')}"
    base_path = os.path.join(UPLOAD_ROOT, "visual", base_name)
    await _save_uploadfile_to_path(image, base_path)
    base_rel = f"/api/files/visual/{base_name}"
    base_url = build_absolute_url(request, base_rel)

    mask_rel = None
    mask_url = None
    mask_bytes = None
    if mask:
        mask_name = f"{uuid.uuid4()}_{re.sub(r'[^a-zA-Z0-9._-]', '_', mask.filename or 'mask.png')}"
        mask_path = os.path.join(UPLOAD_ROOT, "visual", mask_name)
        mask_bytes = await _save_uploadfile_to_path(mask, mask_path)
        mask_rel = f"/api/files/visual/{mask_name}"
        mask_url = build_absolute_url(request, mask_rel)

    # Prepare multipart for OpenAI
    files = {
        "image": (os.path.basename(base_path), open(base_path, "rb"), image.content_type or "image/png"),
    }
    data = {
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": size,
        "response_format": response_format,
    }
    if mask:
        files["mask"] = (os.path.basename(mask_rel or "mask.png"), open(os.path.join(UPLOAD_ROOT, "visual", os.path.basename(mask_rel)), "rb"), mask.content_type or "image/png")

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(
                OPENAI_IMAGE_EDITS_URL,
                headers={"Authorization": f"Bearer {EMERGENT_LLM_KEY}"},
                data=data,
                files=files,
            )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="OpenAI image edit timed out")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"OpenAI request failed: {str(e)}")
    finally:
        # Close file handles
        try:
            files["image"][1].close()
        except Exception:
            pass
        if "mask" in files:
            try:
                files["mask"][1].close()
            except Exception:
                pass

    if resp.status_code >= 400:
        # Bubble up OpenAI error
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise HTTPException(status_code=resp.status_code, detail=f"OpenAI error: {detail}")

    out = resp.json()
    data_arr = out.get("data") or []
    if not data_arr:
        raise HTTPException(status_code=502, detail="No image returned from OpenAI")

    # Save result to our storage
    final_name = f"{uuid.uuid4()}_render.png"
    final_path = os.path.join(UPLOAD_ROOT, "visual", final_name)
    if response_format == "b64_json":
        import base64
        b64 = data_arr[0].get("b64_json")
        if not b64:
            raise HTTPException(status_code=502, detail="No base64 image in response")
        with open(final_path, "wb") as f:
            f.write(base64.b64decode(b64))
    else:
        url = data_arr[0].get("url")
        if not url:
            raise HTTPException(status_code=502, detail="No URL in response")
        await _download_to_path(url, final_path)

    final_rel = f"/api/files/visual/{final_name}"
    final_url = build_absolute_url(request, final_rel)

    # Record in DB under visual_upgrades
    rec = {
        "id": str(uuid.uuid4()),
        "lead_id": lead_id,
        "prompt": prompt,
        "size": size,
        "base_image": {"url": base_url, "path": base_rel},
        "mask_image": ({"url": mask_url, "path": mask_rel} if mask_rel else None),
        "result": {"url": final_url, "path": final_rel},
        "created_at": now_iso(),
    }
    await db["visual_upgrades"].insert_one(rec)
    rec.pop("_id", None)

    return {"success": True, "upgrade": rec}

@router.get("/api/visual-upgrades/list")
async def visual_list(lead_id: Optional[str] = None, db=Depends(get_db)):
    q: Dict[str, Any] = {}
    if lead_id:
        q["lead_id"] = lead_id
    cursor = db["visual_upgrades"].find(q)
    items: List[Dict[str, Any]] = []
    async for it in cursor:
        it.pop("_id", None)
        items.append(it)
    return {"items": items}
