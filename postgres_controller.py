import psycopg
from typing import List, Tuple
from itertools import repeat

class PostgresController():
    
    def __init__(self, postgres_password: str):
        connection_string: str = f"user=postgres.heinzmsorpxajsfacrpj password={postgres_password} host=aws-0-eu-central-1.pooler.supabase.com port=5432 dbname=postgres"
        self.conn = psycopg.connect(connection_string)
        
    def get_existing_interests(self, interests: List[str]) -> List[str]:
        with self.conn.cursor() as cur:
            cur.execute("""
            select interest_text from interests
            where interest_text = any(%s);
            """, (interests, ))
            existing_interests = cur.fetchall()
            existing_interests = [x[0] for x in existing_interests]
            return existing_interests
        
    def insert_interests(self, interests: List[Tuple[str, List[int]]]) -> None:
        with self.conn.cursor() as cur:
            insert_query = """
                insert into interests(interest_text, interest_vector) values (%s, %s);
            """
            cur.executemany(
                insert_query, (interests)
            )
        self.conn.commit()
        
    def interests_text_to_id(self, interests: List[str]) -> List[int]:
        with self.conn.cursor() as cur:
            cur.execute("""
            select interest_id from interests
            where interests.interest_text = any(%s);
            """, (interests, ))
            interest_ids = [x[0] for x in cur.fetchall()]
            return interest_ids
        
    def add_user(self, email: str) -> int:
        with self.conn.cursor() as cur:
            insert_query = """
            insert into users(email)
            values (%s)
            returning user_id;
            """
            cur.execute(insert_query, (email, ))
            self.conn.commit()
            id_of_new_user = cur.fetchone()[0]
            return id_of_new_user
        
    def add_users_interests(self, user_id: int, interest_ids: List[int]):
        values = list(zip(repeat(user_id, len(interest_ids)), interest_ids))
        with self.conn.cursor() as cur:
            insert_query = """
            insert into users_interests(user_id, interest_id)
            values (%s, %s);
            """
            cur.executemany(insert_query, values)
            self.conn.commit()
            
    def remove_user(self, email: str) -> int:
        with self.conn.cursor() as cur:
            delete_query = """
            delete from users
            where email = %s
            returning user_id;
            """
            cur.execute(delete_query, (email, ))
            self.conn.commit()

if __name__ == "__main__":
    import os
    postgres_password = os.environ.get("POSTGRES_PASSWORD")
    pg = PostgresController(postgres_password)
    pg.remove_user("mail@liamhess.de")

