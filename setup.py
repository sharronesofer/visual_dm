from setuptools import setup, find_packages

setup(
    name="visual_dm",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask",
        "flask-sqlalchemy",
        "flask-migrate",
        "flask-cors",
        "python-dotenv",
        "apscheduler",
        "firebase-admin",
        "chromadb",
        "openai",
        "sqlalchemy",
        "alembic",
        "pytest",
        "pytest-cov",
        "requests",
        "gunicorn",
    ],
    python_requires=">=3.11",
) 