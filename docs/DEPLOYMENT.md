# Backend Deployment Guide

This guide explains how to deploy the Visual DM backend for local development, as a standalone executable, or on common cloud platforms.

---

## 1. Local Development

### Prerequisites
- Python 3.10+
- (Recommended) Virtual environment: `python3 -m venv venv`
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- Set up environment variables (see `.env.example` or documentation)

### Running Locally
- Start the server:
  ```bash
  uvicorn app.main:app --reload
  ```
- Access API docs at `http://localhost:8000/docs`

---

## 2. Standalone Executable (PyInstaller)

- Install PyInstaller:
  ```bash
  pip install pyinstaller
  ```
- Build the executable:
  ```bash
  pyinstaller --onefile app/main.py
  ```
- The binary will be in the `dist/` folder. Run it directly:
  ```bash
  ./dist/main
  ```

---

## 3. Cloud Deployment Options

### PythonAnywhere
- Upload your code and requirements.txt
- Set up a WSGI app (see PythonAnywhere docs)
- Install dependencies:
  ```bash
  pip3 install --user -r requirements.txt
  ```

### Heroku
- Add a `Procfile`:
  ```
  web: uvicorn app.main:app --host=0.0.0.0 --port=${PORT:-5000}
  ```
- Push to Heroku and deploy (see Heroku docs)

### AWS Lambda (Serverless)
- Use AWS Lambda with API Gateway for serverless deployment
- Use `serverless` or `zappa` for packaging
- See AWS docs for details

---

## 4. Troubleshooting & FAQ

- **pip not working?**
  - Try using system `pip3` or recreate your virtual environment.
- **Database connection errors?**
  - Check your environment variables and database server status.
- **Cloud storage not syncing?**
  - Ensure AWS credentials and bucket names are set correctly.
- **API key errors?**
  - Set `OPENAI_API_KEY` and other required keys in your environment.

---

## 5. Additional Resources
- See `README.md` for project overview
- See code comments for configuration options
- For advanced deployment, consult the documentation for your chosen platform 