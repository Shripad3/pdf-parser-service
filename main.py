from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader

app = FastAPI()

# Allow your Next.js app to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can lock this down later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/parse-pdf")
async def parse_pdf(file: UploadFile = File(...)):
    try:
        # Read PDF directly from the uploaded file object
        reader = PdfReader(file.file)
        text_parts = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)

        full_text = "\n\n".join(text_parts).strip()

        if not full_text:
            return {
                "error": "We couldn't extract text from this PDF. "
                "This sometimes happens with certain exported PDFs. "
                "Try exporting as .txt or copy-pasting your resume instead."
            }

        return {"text": full_text}
    except Exception as e:
        return {"error": f"Failed to parse PDF: {str(e)}"}
