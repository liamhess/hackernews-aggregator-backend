import logging
logger = logging.getLogger(__name__)
from openai import OpenAI
from typing import List, Dict, Union, Tuple
from postgres_controller.postgres_controller import PostgresController
from itertools import repeat

class BackendLogic():
    
    def __init__(self, openai_api_key: str, postgres_password: str):
        self.openai_api_key = openai_api_key
        self.postgres_password = postgres_password
        
    def _embed_interests(self, interests: List[str]) -> List[Tuple[str, List[int]]]:
        if len(interests) == 0: return None
        
        client = OpenAI(api_key=self.openai_api_key)
        
        output = []
        for i in interests:
            vector = client.embeddings.create(input=i, model="text-embedding-3-small").data[0].embedding
            output.append((i, vector))
        return output
    
    def add_user(self, email: str, interests: str):
        pg = PostgresController(self.postgres_password)
        
        interests_list = [x.strip().lower() for x in interests.split(",")]
        existing_interests: List[str] = pg.get_existing_interests(interests_list)
        new_interests: List[str] = list(set(interests_list) - set(existing_interests))
        interests_to_be_inserted = self._embed_interests(new_interests)
        if interests_to_be_inserted: pg.insert_interests(interests_to_be_inserted)
        interest_ids: List[int] = pg.interests_text_to_id(interests_list)
        
        user_id: int = pg.add_user(email)
        
        pg.add_users_interests(user_id, interest_ids)
        
    def remove_user(self, email: str):
        pg = PostgresController(self.postgres_password)
        pg.remove_user(email)
        
if __name__ == "__main__":
    import os
    postgres_password = os.environ.get("POSTGRES_PASSWORD")
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    backend = BackendLogic(openai_api_key, postgres_password)
