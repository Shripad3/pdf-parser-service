## PDF Resume Parsing (Python FastAPI service)

This project supports uploading **PDF resumes** in addition to plain text.  
PDF parsing is handled by a separate **Python FastAPI microservice**, not by the Next.js app itself.

### How it works

1. On the dashboard, when you upload a `.pdf` file:
   - The frontend sends the file to a Python service at  
     `POST $NEXT_PUBLIC_PDF_SERVICE_URL/parse-pdf`
2. The Python service uses **PyPDF2** to extract text from the PDF.
3. The extracted text is sent back as JSON:
   ```json
   { "text": "Extracted resume content..." }
````

4. That text is then used to auto-fill the **resume textarea** in the UI.

If text extraction fails (for example, some tricky PDFs), the app shows a friendly error and suggests uploading a `.txt` version or pasting the resume manually.

---

### Python service (FastAPI)

Repo: `pdf-parser-service` (separate from this Next.js app)

Key files:

* `main.py` – FastAPI app with a single endpoint:

  ```python
  @app.post("/parse-pdf")
  async def parse_pdf(file: UploadFile = File(...)):
      reader = PdfReader(file.file)
      text_parts = []

      for page in reader.pages:
          page_text = page.extract_text() or ""
          text_parts.append(page_text)

      full_text = "\n\n".join(text_parts).strip()

      if not full_text:
          return {
              "error": "We couldn't extract text from this PDF. "
                       "Try exporting as .txt or copy-pasting your resume instead."
          }

      return {"text": full_text}
  ```

* `requirements.txt` includes:

  ```txt
  fastapi
  uvicorn
  PyPDF2
  python-multipart
  ```

#### Running the Python service locally

```bash
cd pdf-parser-service
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# .\venv\Scripts\activate       # Windows

pip install -r requirements.txt

uvicorn main:app --reload --port 8000
```

Swagger UI (for testing uploads manually) will be available at:

```text
http://127.0.0.1:8000/docs
```

---

### Environment configuration

The Next.js app talks to the Python service via an environment variable:

```env
NEXT_PUBLIC_PDF_SERVICE_URL=https://pdf-parser-service-zle6.onrender.com
```

* In **local dev**, this is defined in `.env.local` at the root of the Next.js app.
* In **production**, this same variable is configured in Vercel → *Project Settings → Environment Variables*.

The frontend uses this value in its file upload handler:

```ts
const baseUrl =
  process.env.NEXT_PUBLIC_PDF_SERVICE_URL || "http://127.0.0.1:8000";

const res = await fetch(`${baseUrl}/parse-pdf`, {
  method: "POST",
  body: formData,
});
```

If the variable isn’t set, it falls back to `http://127.0.0.1:8000` for local development.