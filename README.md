1) change all IP in program (192.168.159.144) on your
2) set up keycloack and set up backend/settings.py
// start frontend and authorization server
3) docker compose up --build
4) cd backend
5) python3 install -r requirements.txt
// start backend
6) uvicorn server:app --host=0.0.0.0 --port 8000