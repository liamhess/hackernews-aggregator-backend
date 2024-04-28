import psycopg
from typing import List, Tuple, Dict, Union
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
            
    def insert_articles(self, articles: List[Dict[str, Union[str, int, List[int]]]]):
        with self.conn.cursor() as cur:
            insert_query = """
            insert into articles(article_id, headline, points, website_url, article_vector)
            values (%s, %s, %s, %s, %s);
            """
            values = [(x["article_id"], x["headline"], x["points"], x["website_url"], x["article_vector"]) for x in articles]
            cur.executemany(insert_query, values)
            self.conn.commit()
            
    def create_articles_ranking_table(self):
        with self.conn.cursor() as cur:
            table_query = """
            create
             temp table interests_articles(
              interest_id int,
              article_id int,
              cosine_similarity float
            );"""
            cur.execute(table_query)
            
            insert_query = """
            insert into interests_articles
            select
              interests.interest_id,
              articles.article_id,
              1 - (interests.interest_vector <=> articles.article_vector) as cosine_similarity
            from interests, articles
            where interests.interest_id in (
              select distinct on (interest_id)
              interest_id
              from users_interests
            )
            and articles.inserted_at > now() - interval '24 hours'
            order by cosine_similarity desc;"""
            cur.execute(insert_query)
            self.conn.commit()
            
#             select_query = """
#             select * from interests_articles;"""
#             cur.execute(select_query)
    
    def get_articles_for_user(self, email: str):
        with self.conn.cursor() as cur:
            select_query = """
            select
              *
            from
              (
                select distinct
                  on (articles.headline)
                  articles.article_id,
                  articles.headline,
                  articles.points,
                  articles.website_url,
                  interests.interest_text,
                  ia.cosine_similarity
                from
                  users
                  join users_interests ui on ui.user_id = users.user_id
                  join interests on ui.interest_id = interests.interest_id
                  join interests_articles ia on ia.interest_id = ui.interest_id
                  join articles on articles.article_id = ia.article_id
                where
                  users.email = %s
                order by
                  articles.headline,
                  cosine_similarity desc
              ) sub
            order by
              cosine_similarity desc
            limit
              10;
            """
            cur.execute(select_query, (email, ))
            raw_articles = cur.fetchall()
            parsed_articles = [{
                "hackernews_url": f"https://news.ycombinator.com/item?id={x[0]}",
                "headline": x[1],
                "points": x[2],
                "website_url": x[3],
                "interest": x[4],
            } for x in raw_articles]
            
            return parsed_articles
    
    def get_all_users(self):
        with self.conn.cursor() as cur:
            select_query = """
            select users.email
            from users
            where users.created_at < current_date;
            """
            cur.execute(select_query)
            users = [x[0] for x in cur.fetchall()]
        return users

if __name__ == "__main__":
    import os
    postgres_password = os.environ.get("POSTGRES_PASSWORD")
    pg = PostgresController(postgres_password)
    pg.get_all_users()

