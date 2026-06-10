# 📄 DjangoDocQA — API Reference Documentation

Welcome to the backend API documentation for the DjangoDocQA RAG (Retrieval-Augmented Generation) pipeline. This system allows clients to manage text-based `.docx` policy files, automate vector synchronization with ChromaDB, and execute context-aware Q&A histories.

## 🚀 Base URL
During local development, the API is accessible at:
`http://localhost:8000`

---

## 🗺️ Endpoints Summary

| Method | Endpoint | Description | Content-Type |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/documents/upload/` | Uploads a `.docx` document and saves its vector index. | `multipart/form-data` |
| `POST` | `/api/documents/update/<int:pk>/` | Replaces a doc and re-indexes its vectors automatically. | `multipart/form-data` |
| `DELETE` | `/api/documents/<int:pk>/` | Deletes a document and purges its vectors from ChromaDB. | None |
| `POST` | `/api/qa/ask/` | Submits a new question, runs RAG matching, and returns an AI answer. | `application/json` |
| `PUT` | `/api/qa/<int:pk>/` | Modifies an existing question, re-runs the RAG pipeline. | `application/json` |
| `DELETE` | `/api/qa/<int:pk>/` | Permanently deletes a Q&A record from history. | None |

---

## 🛠️ Endpoints Detail

### 1. Upload Document
* **URL:** `/api/documents/upload/`
* **Method:** `POST`
* **Data Format:** `multipart/form-data`

#### Example cURL Request
```bash
curl -X POST http://localhost:8000/api/documents/upload/ \
  -F "title=Operations Manual" \
  -F "file=@/path/to/policy.docx"

```

#### Expected Response (`201 Created`)

```json
{
  "message": "Document uploaded and vectorized successfully.",
  "document_id": 5,
  "title": "Operations Manual"
}

```

---

### 2. Update Document

Replaces an existing document's file/title and triggers a purge-and-reindex sequence for the associated vector chunks via Django signals.

* **URL:** `/api/documents/update/<int:pk>/`
* **Method:** `POST`
* **Data Format:** `multipart/form-data`

#### Example cURL Request

```bash
curl -X POST http://localhost:8000/api/documents/update/1/ \
  -F "title=Updated Manual v2" \
  -F "file=@/path/to/new_policy.docx"

```

#### Expected Response (`200 OK`)

```json
{
  "message": "Document updated and vectors refreshed successfully.",
  "document_id": 1
}

```

---

### 3. Delete Document

Removes the relational data entry and purges all embedded text chunks out of the local vector engine to prevent stale context lookups.

* **URL:** `/api/documents/<int:pk>/`
* **Method:** `DELETE`

#### Example cURL Request

```bash
curl -X DELETE http://localhost:8000/api/documents/5/

```

#### Expected Response (`200 OK` / `204 No Content`)

```json
{
  "message": "Document record and associated vectors successfully deleted."
}

```

---

### 4. Ask Question (Execute RAG Pipeline)

* **URL:** `/api/qa/ask/`
* **Method:** `POST`
* **Data Format:** `application/json`

#### Request Payload

```json
{
  "question": "What is the exact budget for Project Aria?"
}

```

#### Example cURL Request

```bash
curl -X POST http://localhost:8000/api/qa/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the exact budget for Project Aria?"}'

```

#### Expected Response (`200 OK`)

```json
{
  "qa_id": 12,
  "question": "What is the exact budget for Project Aria?",
  "answer": "Based on the company documentation, Project Aria has an allocated total budget of $150,000."
}

```

---

### 5. Update Question (Re-run RAG)

Updates an existing question string, resets the contextual search boundary, and requests a fresh response block via the LLM routing sequence.

* **URL:** `/api/qa/<int:pk>/`
* **Method:** `PUT`
* **Data Format:** `application/json`

#### Request Payload

```json
{
  "question": "Who is the project manager for Project Aria?"
}

```

#### Example cURL Request

```bash
curl -X PUT http://localhost:8000/api/qa/12/ \
  -H "Content-Type: application/json" \
  -d '{"question": "Who is the project manager for Project Aria?"}'

```

#### Expected Response (`200 OK`)

```json
{
  "qa_id": 12,
  "message": "Question updated and pipeline re-executed successfully.",
  "question": "Who is the project manager for Project Aria?",
  "answer": "The designated project manager overseeing all operational milestones for Project Aria is Sarah Jenkins."
}

```

---

### 6. Delete Question Record

* **URL:** `/api/qa/<int:pk>/`
* **Method:** `DELETE`

#### Example cURL Request

```bash
curl -X DELETE http://localhost:8000/api/qa/12/

```

#### Expected Response (`200 OK`)

```json
{
  "message": "Question history record permanently removed."
}
