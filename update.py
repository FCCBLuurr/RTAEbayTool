import os
import requests
from dotenv import load_dotenv

def get_current_version():
    load_dotenv()
    return os.getenv("VERSION")

def get_latest_version(repo_owner, repo_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    response = requests.get(url)
    response.raise_for_status()
    latest_release = response.json()
    return latest_release['tag_name']

def check_for_updates(current_version):
    load_dotenv()
    repo_owner = os.getenv("REPO_OWNER")
    repo_name = os.getenv("REPO_NAME")
    latest_version = get_latest_version(repo_owner, repo_name)

    if current_version != latest_version:
        return True, latest_version
    else:
        return False, None
