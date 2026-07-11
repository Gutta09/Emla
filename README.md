# Emla — Real-time ASL Recognition

Sign into a webcam, get spoken English out. Emla recognizes American Sign Language in real time — both fingerspelling (A–Z) and full word signs — and turns the recognized sequence into a natural English sentence, read aloud.

## How it works

```
webcam ──▶ MediaPipe (hands + pose, in-browser) ──▶ landmark stream over WebSocket
                                                            │
                                              pause detector segments signs
                                                            │
                              ┌─────────────────────────────┴──────────────┐
                              │ fingerspell model (A–Z, static hand shapes) │
                              │ word-sign Transformer (100 WLASL classes)   │
                              └─────────────────────────────┬──────────────┘
                                                            │
                                  sign sequence ──▶ LLM ──▶ natural English sentence
                                                            │
                                              spoken via browser speech synthesis
```

- **Landmarks, not pixels.** The browser extracts hand + pose landmarks with MediaPipe and streams compact 225-dim feature vectors over a WebSocket — no video ever leaves the client.
- **Two models, one session.** Static fingerspelling shapes and dynamic word signs (30-frame sequences) are handled by separate models; a pause detector segments the stream so signs don't bleed into each other.
- **Custom Transformer.** The word-sign model is a 2-block Transformer (d_model 128, 4 heads) with positional encoding over landmark sequences, trained on WLASL-100.
- **Signs → sentences.** Recognized glosses are converted to grammatical English by an LLM (Gemini), with a deterministic fallback so recognition still produces readable output offline.

## Training pipeline (`ml_pipeline/`)

Numbered, resumable scripts — each stage checkpoints so long extraction runs can be interrupted:

1. `1_download_data.py` — ASL Alphabet (Kaggle) for fingerspelling, WLASL-100 for word signs
2. `2_extract_landmarks.py` — MediaPipe hand + pose landmark extraction, normalized and resampled to fixed-length sequences
3. `4_train_fingerspell.py` — static hand-shape classifier (A–Z)
4. `5_train_word_model.py` — word-sign Transformer with sequence augmentation
5. `6_evaluate_models.py` — held-out evaluation for both models

## Stack

- **Frontend** — React + TypeScript + Vite; MediaPipe Tasks running in-browser; WebSocket streaming; speech synthesis; pages for live recognition, practice mode, sign dictionary, and history
- **Backend** — FastAPI with WebSocket landmark handling, model manager, pause detection
- **ML** — TensorFlow/Keras, MediaPipe, custom Transformer layers; trained on ASL Alphabet + WLASL-100

## Run locally

```bash
# backend
cd backend
pip install -r requirements.txt
python run.py

# frontend
cd frontend
npm install
npm run dev
```

Set `GEMINI_API_KEY` in `.env` (see `.env.example`) for sentence generation; without it, Emla falls back to direct gloss-to-text output.
