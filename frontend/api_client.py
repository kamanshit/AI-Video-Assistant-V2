import requests

BASE_URL = "http://127.0.0.1:8000/api"


def register(username, password):
    response = requests.post(
        f"{BASE_URL}/register/",
        json={
            "username": username,
            "password": password
        }
    )

    return response


def login(username, password):
    response = requests.post(
        f"{BASE_URL}/login/",
        json={
            "username": username,
            "password": password
        }
    )

    return response


def get_videos(token):
    response = requests.get(
        f"{BASE_URL}/videos/",
        headers={
            "Authorization": f"Token {token}"
        }
    )

    return response


def create_video(token, title, source=None, video_file=None):
    headers = {
        "Authorization": f"Token {token}"
    }

    if source:
        response = requests.post(
            f"{BASE_URL}/videos/",
            headers=headers,
            json={
                "title": title,
                "source": source,
                "language": "english"
            }
        )

    else:
        response = requests.post(
            f"{BASE_URL}/videos/",
            headers=headers,
            data={
                "title": title,
                "language": "english"
            },
            files={
                "file": (
                    video_file.name,
                    video_file.getvalue(),
                    video_file.type
                )
            }
        )

    return response

def ask_question(token, video_id, question):
    response = requests.post(
        f"{BASE_URL}/questions/",
        headers={
            "Authorization": f"Token {token}"
        },
        json={
            "video": video_id,
            "question": question
        }
    )

    return response


def get_questions(token, video_id=None):
    params = {}

    if video_id:
        params["video"] = video_id

    response = requests.get(
        f"{BASE_URL}/questions/",
        headers={
            "Authorization": f"Token {token}"
        },
        params=params
    )

    return response