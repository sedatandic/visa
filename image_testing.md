## TEST AGENT PROMPT – IMAGE INTEGRATION RULES ##
You are the Test Agent responsible for validating image integrations.
Follow these rules exactly. Do not overcomplicate.

*** Image Handling Rules ***
- Always use base64-encoded images for all tests and requests.
- Accepted formats: JPEG, PNG, WEBP only.
- Do not use SVG, BMP, HEIC, or other formats.
- Do not upload blank, solid-color, or uniform-variance images.
- Every image must contain real visual features — such as objects, edges, textures, or shadows.
- If the image is not PNG/JPEG/WEBP, transcode it to PNG or JPEG before upload.
  ## Fix Example:
    If you read a .jpg but the content is actually PNG after conversion or compression — this is invalid.
    Always re-detect and update the MIME after transformations.
- If the image is animated (e.g., GIF, APNG, WEBP animation), extract the first frame only.
- Resize large images to reasonable bounds (avoid oversized payloads).

## Bu projedeki gorsel AI uclari
- `POST /api/passport/read` (Form: file_id) — pasaport kimlik sayfasindan alan cikarimi (gpt-5.4 vision).
- `POST /api/photo/check` (Form: file_id) — vesikalik fotograf uygunluk denetimi (gpt-5.4 vision).
- `POST /api/photo/match` (Form: passport_file_id, photo_file_id) — pasaporttaki vesikalik ile
  yuklenen vesikaligin ayni kisiye ait gorunup gorunmedigi (gpt-5.4 vision, iki goruntu tek istekte).
  Yanit: `{checked, same_person: true|false|null, confidence, note, message}`. Uyari amaclidir,
  basvuruyu engellemez; model cevap veremezse `checked: false` doner.

Notlar:
- Dosyalar once `POST /api/uploads` (multipart: file, doc_type) ile yuklenir, donen `file_id` kullanilir.
- PDF pasaportlar backend'de pymupdf ile goruntuye cevrilir (`_prepare_images`).
- Gunluk kotalar: `PASSPORT_OCR_DAILY_LIMIT`, `PHOTO_CHECK_DAILY_LIMIT`, `PHOTO_MATCH_DAILY_LIMIT`.
