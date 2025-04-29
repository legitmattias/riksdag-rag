# WT2 - Parliamentary Debates Analysis and Semantic Search

## Project Description
This project is an interactive web application for exploring and analyzing speeches from the Swedish Parliament (Riksdagen). It includes a backend built with FastAPI for structured data access and semantic search, and a SvelteKit frontend for dynamic visualizations and user interaction.

The application enables users to:
- Filter and explore thousands (33k+) of parliamentary speeches.
- Visualize statistics about debates and speakers.
- Ask natural language questions using a RAG (Retrieval-Augmented Generation) pipeline.

The project is based on 338 parsed chamber protocols from 2022–2025, with potential for easy expansion to additional years.

## Links
- **Deployed Application:** [https://cscloud6-198.lnu.se/wt2/](https://cscloud6-198.lnu.se/wt2/)
- **Development Repository:** [https://gitlab.lnu.se/mu222cu/wt2-dev](https://gitlab.lnu.se/mu222cu/wt2-dev)

## Features
- Structured REST API for speech metadata, content, and statistical aggregations.
- RAG functionality combining ChromaDB vector search and OpenAI GPT-3.5-turbo.
- Interactive and responsive frontend (SvelteKit + TailwindCSS + Chart.js).
- Robust data processing pipeline with independent scripts.
- Dockerized MongoDB.
- Dev and production startup scripts.

## Frontend Pages
- **Översikt:** Dashboard displaying all graphs in a minimal version without controls/filtering.
- **Riksdagsboten:** Semantic search bot using RAG. User can ask a question and get a generated answer plus the 5 most relevant source speeches (with links to speech modals and original protocols).
- **Längd per anförande:** Graph showing average length (number of words) per speech for each party, colored by party color. Date range filtering with date pickers.
- **Aktiva talare:** Top speakers visualization showing speakers ranked by number of speeches.
- **Anföranden över tid:** Graph displaying how many speeches each party made per year. Date range filtering enabled. Colored by party.
- **Översikt över anföranden:** Paginated table (10/25/50 per page) showing summarized speech metadata, filtered by party using a drowndown. Each row links to the full speech modal, with further links to the full protocol in HTML or PDF.

## Tech Stack
- **Frontend:** SvelteKit, TypeScript, TailwindCSS, Vite, Chart.js
- **Backend:** FastAPI (Python)
- **Database:** MongoDB (Docker) + ChromaDB (local vector DB)
- **Embeddings:** OpenAI `text-embedding-ada-002`
- **LLM:** OpenAI `gpt-3.5-turbo`
- **Other:** Eslint, Prettier, Docker Compose, Python Scripts

---

## Setup Instructions

### Prerequisites
- Node.js + Yarn
- Python 3.11+
- Docker & Docker Compose
- OpenAI API key (for embeddings and RAG)

### Environment Variables

Create the following `.env` files:

#### `/backend/.env` (also used by `/pipeline` scripts)
```env
MONGO_URI=mongodb://localhost:27017/
DB_NAME=riksdagen
OPENAI_API_KEY=your_openai_api_key_here
```

#### `/frontend/.env`
```env
VITE_API_META=http://localhost:8000/meta
VITE_API_DATA=http://localhost:8000/data
VITE_API_RAG=http://localhost:8000/search
```

### Installation and Development
```bash
# Make executable if needed
chmod +x init.sh

# Install dependencies, run Docker MongoDB, and start dev servers
./init.sh
```
- Frontend available at: `http://localhost:5173`
- Backend API (Swagger UI) available at: `http://localhost:8000/docs`

### Production
```bash
# After setup and seeding, start production services
./start_prod.sh
```

---

## Data Pipeline and Seeding
All preprocessing scripts are located in `/pipeline`.

### Steps:
1. **Parse raw protocols:**
   ```bash
   python pipeline/parse_chamber_protocols.py
   ```
   - Output: `data/protocols.json` and `data/speeches.json`

2. **Seed MongoDB:**
   ```bash
   python pipeline/seed_mongodb.py
   ```

3. **Generate Embeddings and Seed ChromaDB:**
   ```bash
   python pipeline/embed_and_seed_chroma.py
   ```
   (Requires OpenAI API key with active credits)

Raw datasets are **not version-controlled**, only the intermediary parsed `.json` files.

Raw data can be downloaded from [Riksdagens öppna data](https://www.riksdagen.se/sv/dokument-och-lagar/riksdagens-oppna-data/dokument/) under the section:
**"Protokoll - Protokoll från kammarens sammanträden."**

---

## Backend API Endpoints (Examples)

### `/meta`
- `GET /meta/protocols`: List all parliamentary protocols.
- `GET /meta/parties`: List all party codes and labels.
- `GET /meta/top-speakers?limit=10`: Top 10 speakers by number of speeches.
- `GET /meta/date-range`: Earliest and latest speech date.

### `/data`
- `GET /data/speeches`: Get speeches (filters: speaker, party, date, clause title).
- `GET /data/speeches/summary`: Get summarized speeches (only metadata).
- `GET /data/speeches/{speech_id}`: Fetch a specific speech by ID.
- `GET /data/summary/speeches-per-party`: Speeches grouped by party.
- `GET /data/summary/speeches-over-time`: Speeches over time (year/month).
- `GET /data/summary/speech-lengths`: Average speech length.

### `/search/rag`
- `POST /search/rag/query`
  - Input JSON:
    ```json
    { "query": "What was said about nuclear power?", "top_k": 5 }
    ```
  - Output JSON:
    ```json
    {
      "answer": "Summary generated by LLM...",
      "sources": [ {"speaker": "", "party": "", "date": "", ...} ]
    }
    ```

> Full interactive docs: [Swagger UI](http://localhost:8000/docs)

---

## Retrieval-Augmented Generation (RAG) Explained
- **Chunking:** Speeches are split into manageable text chunks.
- **Embedding:** Each chunk is embedded using `text-embedding-ada-002`.
- **Storage:** Embeddings are stored locally in ChromaDB.
- **Semantic Search:** User queries are embedded, similar chunks are retrieved.
- **LLM Generation:** Retrieved chunks are sent to `gpt-3.5-turbo` to generate a coherent answer.

This enables users to ask flexible, high-level questions about the dataset.

### Example Queries:
- "How often was climate change discussed in 2023?"
- "Which parties supported nuclear power in 2024?"
- "Summarize the debates about electric vehicles."
- "Who spoke the most about healthcare in 2022?"

---

## Additional Features and Assignment Requirements

This project fulfills and exceeds the WT2 assignment requirements in several ways:

### Backend Enhancements
- Implemented an extensive set of REST endpoints under `/data`, `/meta`, and `/search`, far beyond the basic requirements.
- Each endpoint supports a variety of filters (speaker, party, date, clause title, etc.) and pagination options, allowing powerful and flexible data access.

### Frontend Enhancements
- Developed multiple interactive visualizations using Chart.js, each with dynamic filtering and/or pagination.
- Designed a clean, responsive UI with thoughtful UX details such as:
  - Party-colored charts for clarity.
  - Date pickers for range-based data exploration.
  - Dropdown filtering in the summarized speeches table.
  - Tooltips and labels for enhanced readability.
  - A dedicated "Speech Modal" for viewing complete speeches, including direct links to the original parliamentary protocols (HTML and PDF versions).

### Data Pipeline and Custom Dataset Creation
- Created a custom dataset by parsing and cleaning raw parliamentary protocols from Riksdagen's open data portal.
- Built a sophisticated preprocessing pipeline that:
  - Extracts and structures thousands of speeches from messy HTML-embedded metadata.
  - Outputs clean, structured JSON datasets used for seeding MongoDB and ChromaDB.

This ensures that the visualizations are based on rich, real-world, and correctly processed data, rather than using generic example datasets.

### Automation and Project Scripts
- Provided `init.sh` and `start_prod.sh` scripts to automate environment setup, Docker service management, and server startup.
- Designed the pipeline scripts to run independently in sequence, making it easy to preprocess, seed, and embed new data.

### RAG (Retrieval-Augmented Generation) Implementation (Optional VG Enhancement)
- Implemented a full RAG pipeline:
  - Speech data is split into manageable text chunks based on token limits.
  - Each chunk is embedded using OpenAI's `text-embedding-ada-002`.
  - Chunks are seeded into a local ChromaDB instance, with metadata attached.
  - Duplicate prevention and checkpointing are implemented to ensure robustness during seeding.
  - Users can submit free-text queries, retrieving semantically relevant speeches and generating an answer via `gpt-3.5-turbo`.

---

## License
This project uses publicly available data from [Riksdagens öppna data](https://data.riksdagen.se/).

Licensed under the [MIT License](https://opensource.org/licenses/MIT).

> Educational project for 1DV027 - Web for Data Science, Linnaeus University, 2025.
