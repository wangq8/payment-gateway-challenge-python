from pathlib import Path

from dotenv import load_dotenv


def pytest_configure():
    env_path = Path(__file__).resolve().parent.parent / ".env.test"
    load_dotenv(env_path)
