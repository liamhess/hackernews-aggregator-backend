import pytest
import os
from dotenv import load_dotenv

from api.backend_logic import BackendLogic

load_dotenv()

@pytest.fixture(scope="class")
def backend_instance():
    openai_api_key = os.environ["OPENAI_API_KEY"]
    postgres_password = os.environ["POSTGRES_PASSWORD"]
    return BackendLogic(openai_api_key, postgres_password)

def test__embed_interests(backend_instance):
    interest_embeddings = backend_instance._embed_interests(["ai", "cloud"])
    assert len(interest_embeddings) == 2
    assert len(interest_embeddings[0][1]) == 1536

    interest_embeddings = backend_instance._embed_interests([])
    assert interest_embeddings == None
