from setuptools import setup, find_packages

setup(
    name="task-app",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "alembic",
        "databases",
        "asyncpg",
        "python-dotenv",
    ],
) 