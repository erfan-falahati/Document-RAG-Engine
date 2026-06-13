# DjangoDocQA (RAG Pipeline Backend)

DjangoDocQA is a Retrieval-Augmented Generation (RAG) backend application built with Django. It allows users to manage Microsoft Word (`.docx`) documents, automatically extracts and vectorizes the text into a local **ChromaDB** instance, and uses LangChain to answer natural language questions based purely on the uploaded contextual documents.

## Features
* **Automated Document Parsing:** Extracts raw text safely from `.docx` files using `python-docx`.
* **Local Vector Storage:** Uses ChromaDB and HuggingFace sentence transformers (`all-MiniLM-L6-v2`) to embed and index document chunks locally.
* **Intelligent RAG Pipeline:** Connects to OpenRouter (using stable free endpoints like `nvidia/nemotron-3-super-120b-a12b:free`) via LangChain to generate context-aware answers.
* **Full CRUD Management:** Supports comprehensive creating, updating, and vector-synchronized dropping of both document and question profiles.
* **High-Availability Routing:** Features an automated fallback query list (`Nvidia` -> `OpenAI` -> `DeepSeek`) to maintain uptime during high traffic density loads.

---

## Network & Mirror Configuration

To bypass network limitations and regional API restrictions, this project is explicitly configured to handle two special network behaviors:

### 1. Docker Registry Mirror
Due to access restrictions on the default Docker Hub registries, you must use a local mirror to pull down base images. Ensure your host's Docker daemon is configured to use a reliable mirror in your `/etc/docker/daemon.json`:
```json
{
  "registry-mirrors": [
    "[https://docker.arvancloud.ir](https://docker.arvancloud.ir)",
    "[https://docker.iranserver.com](https://docker.iranserver.com)"
  ]
}

```

### 2. Outbound Proxy Routing (OpenRouter Integration)

Because upstream AI APIs like OpenRouter cannot be reached directly, all LLM traffic generated inside the isolated Docker containers is programmatically forced to bridge out into the host's proxy interface over the virtual gateway network interface (`http://172.17.0.1:10808`) by enabling **"Allow connections from LAN"** on your proxy application.

---

## Setup & Installation

Follow these steps to configure, build, and run the project using Docker.

### 1. Prerequisites

* **Docker & Docker Compose:** Installed and running on your host system.
* **OpenRouter API Key:** Get a free API key from [OpenRouter](https://openrouter.ai/).
* **Host Proxy Setup (v2rayN):** Ensure your proxy is running, configured with **Mixed Port** `10808`, and allows LAN connections.

### 2. Clone the Repository

```bash
git clone [https://github.com/yourusername/DjangoDocQA.git](https://github.com/yourusername/DjangoDocQA.git)
cd DjangoDocQA

```

### 3. Environment Variables

Create a `.env` file in the root directory and add your key:

```ini
# .env
OPENROUTER_API_KEY=your_openrouter_api_key_here

```

### 4. Build and Run the Docker Containers

```bash
sudo docker-compose up --build -d

```

### 5. Database Migrations & Superuser

```bash
sudo docker-compose exec web python manage.py migrate
sudo docker-compose exec web python manage.py createsuperuser

```

---

## 💻 Usage & Testing

### Document Management (CRUD)

* **Upload Document (Create):**
```bash
curl -X POST http://localhost:8000/api/documents/upload/ -F "title=Doc Title" -F "file=@file.docx"

```

* **Update Document**

```bash
curl -X POST http://localhost:8000/api/documents/update/1/ \
  -F "title=Updated Manual v2" \
  -F "file=@/path/to/new_policy.docx"

```

* **Delete Document (Delete & Vector Purge):**
```bash
curl -X DELETE http://localhost:8000/api/documents/1/

```



### RAG Q&A Execution (CRUD)

* **Ask Question (Create Response):**
```bash
curl -X POST http://localhost:8000/api/qa/ask/ -H "Content-Type: application/json" -d '{"question": "Who is the PM?"}'

```


* **Change Question (Update & Re-run RAG Pipeline):**
```bash
curl -X PUT http://localhost:8000/api/qa/1/ -H "Content-Type: application/json" -d '{"question": "What is the team budget?"}'

```


* **Remove Record (Delete History):**
```bash
curl -X DELETE http://localhost:8000/api/qa/1/

```



---

## Troubleshooting

**"No related documents found!"**

* Verify your uploaded file text extracted successfully in the admin panel view (`http://localhost:8000/admin`). Ensure you are uploading native `.docx` formats.

**"Connection error" on API calls**

* Ensure your proxy client has **Allow LAN** enabled and that the bridge IP (`172.17.0.1`) and port (`10808`) match your configuration.

---

*Built with Django, LangChain, and Docker.*

