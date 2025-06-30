from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import importlib.util, sys
from datetime import datetime
from io import BytesIO

from columns import BASE_COLUMNS, IA_COLUMNS
from data_io import read_file
from llm_utils import build_user_prompt, call_llm

app = FastAPI(title="Teract Enrichissement API")

@app.post("/preview")
async def preview(file: UploadFile = File(...)):
    df = read_file(file.file)
    df.columns = [c.replace("/", " ") for c in df.columns]
    missing = [c for c in BASE_COLUMNS if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Colonnes manquantes: {', '.join(missing)}")
    for col in IA_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return {
        "columns": df.columns.tolist(),
        "rows": df.head(5).to_dict(orient="records"),
    }

@app.post("/generate")
async def generate(file: UploadFile = File(...)):
    df = read_file(file.file)
    df.columns = [c.replace("/", " ") for c in df.columns]
    missing = [c for c in BASE_COLUMNS if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Colonnes manquantes: {', '.join(missing)}")
    for col in IA_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    errors = 0
    for i, row in df.iterrows():
        try:
            r = call_llm(build_user_prompt(row))
            df.at[i, "Description Marketing Client 1"] = r["desc"]
            df.at[i, "Plus produit 1"] = r["plus1"]
            df.at[i, "Plus produit 2"] = r["plus2"]
            df.at[i, "Plus produit 3"] = r["plus3"]
            df.at[i, "IA DATA"] = 1
            df.at[i, "Token"] = r["tokens"]
            df.at[i, "Date"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            df.at[i, "IAPLUS"] = 1
            df.at[i, "Commentaires"] = ""
        except Exception as e:
            errors += 1
            df.at[i, "IA DATA"] = 0
            df.at[i, "IAPLUS"] = 0
            df.at[i, "Commentaires"] = str(e)[:250]
    has_xlwt = importlib.util.find_spec("xlwt") and sys.version_info < (3, 12)
    eng, ext, mime = (
        ("xlwt", ".xls", "application/vnd.ms-excel") if has_xlwt else (
            "openpyxl", ".xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    )
    buf = BytesIO()
    df.to_excel(buf, index=False, engine=eng)
    buf.seek(0)
    headers = {"Content-Disposition": f"attachment; filename=catalogue_enrichi{ext}"}
    return StreamingResponse(buf, media_type=mime, headers=headers)
