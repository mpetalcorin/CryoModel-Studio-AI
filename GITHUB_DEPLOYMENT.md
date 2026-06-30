
# GitHub deployment

Target repository:

https://github.com/mpetalcorin/CryoModel-Studio-AI

## Push from terminal

```bash
cd CryoModel_Studio_AI
chmod +x scripts/push_to_github.sh
./scripts/push_to_github.sh
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Optional Docker run

```bash
docker build -t cryomodel-studio-ai .
docker run -p 8501:8501 cryomodel-studio-ai
```
