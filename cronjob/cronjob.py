import requests
from typing import List, Union, Dict
from openai import OpenAI
import os
import time
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from postgres_controller import PostgresController
from string import Template

class Cronjob():
    def __init__(self):
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.pg = PostgresController(os.environ.get("POSTGRES_PASSWORD"))
    
    def _embed_headlines(self, articles: List[Dict[str, Union[str, int]]]):
        if len(articles) == 0: return None
        
        client = OpenAI(api_key=self.openai_api_key)
        
        for a in articles:
            vector = client.embeddings.create(input=a["headline"], model="text-embedding-3-small").data[0].embedding
            a["article_vector"] = vector
        return articles
    
    def _get_hackernews_articles(self):
        timestamp_24h_ago = int(time.time() - 86400)
        url = "http://hn.algolia.com/api/v1/search"
        querystring = {"tags":"front_page,(story,show_hn,ask_hn)","hitsPerPage":"30","numericFilters":f"created_at_i>{timestamp_24h_ago}"}
        
        response = requests.get(url, params=querystring)
        hits = response.json()["hits"]
        parsed_response = [{"article_id": int(x["story_id"]), "headline": x["_highlightResult"]["title"]["value"], "points": x["points"], "website_url": x["_highlightResult"]["url"]["value"]}  for x in hits]
        articles = self._embed_headlines(parsed_response)
        self.pg.insert_articles(articles)
        
    def _format_email(self,articles):
        with open("cronjob/mail_template.html") as f:
            html_template = Template(f.read())
        
        generated_html = html_template.substitute(
            WEBSITE_LINK1=articles[0]["website_url"],
            HEADLINE1=articles[0]["headline"],
            POINTS1=articles[0]["points"],
            HACKERNEWS_LINK1=articles[0]["hackernews_url"],
            INTEREST1=articles[0]["interest"],
            WEBSITE_LINK2=articles[1]["website_url"],
            HEADLINE2=articles[1]["headline"],
            POINTS2=articles[1]["points"],
            HACKERNEWS_LINK2=articles[1]["hackernews_url"],
            INTEREST2=articles[1]["interest"],
            WEBSITE_LINK3=articles[2]["website_url"],
            HEADLINE3=articles[2]["headline"],
            POINTS3=articles[2]["points"],
            HACKERNEWS_LINK3=articles[2]["hackernews_url"],
            INTEREST3=articles[2]["interest"],
            WEBSITE_LINK4=articles[3]["website_url"],
            HEADLINE4=articles[3]["headline"],
            POINTS4=articles[3]["points"],
            HACKERNEWS_LINK4=articles[3]["hackernews_url"],
            INTEREST4=articles[3]["interest"],
            WEBSITE_LINK5=articles[4]["website_url"],
            HEADLINE5=articles[4]["headline"],
            POINTS5=articles[4]["points"],
            HACKERNEWS_LINK5=articles[4]["hackernews_url"],
            INTEREST5=articles[4]["interest"],
            WEBSITE_LINK6=articles[5]["website_url"],
            HEADLINE6=articles[5]["headline"],
            POINTS6=articles[5]["points"],
            HACKERNEWS_LINK6=articles[5]["hackernews_url"],
            INTEREST6=articles[5]["interest"],
            WEBSITE_LINK7=articles[6]["website_url"],
            HEADLINE7=articles[6]["headline"],
            POINTS7=articles[6]["points"],
            HACKERNEWS_LINK7=articles[6]["hackernews_url"],
            INTEREST7=articles[6]["interest"],
            WEBSITE_LINK8=articles[7]["website_url"],
            HEADLINE8=articles[7]["headline"],
            POINTS8=articles[7]["points"],
            HACKERNEWS_LINK8=articles[7]["hackernews_url"],
            INTEREST8=articles[7]["interest"],
            WEBSITE_LINK9=articles[8]["website_url"],
            HEADLINE9=articles[8]["headline"],
            POINTS9=articles[8]["points"],
            HACKERNEWS_LINK9=articles[8]["hackernews_url"],
            INTEREST9=articles[8]["interest"],
            WEBSITE_LINK10=articles[9]["website_url"],
            HEADLINE10=articles[9]["headline"],
            POINTS10=articles[9]["points"],
            HACKERNEWS_LINK10=articles[9]["hackernews_url"],
            INTEREST10=articles[9]["interest"],
        )
        
        return generated_html
        
    def _send_mail(self, email: str, articles):
        formatted_mail = self._format_email(articles)
        message = Mail(
            from_email="hackernews-aggregator@liamhess.de",
            to_emails=email,
            subject="Daily Hacker News",
            plain_text_content="nice, it works",
            html_content=formatted_mail
        )
        sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        response = sg.send(message)
        
    def hackernews_to_mail_flow(self, daily_flow: bool = True, user_list: List[str] = None):
        if daily_flow:
            self._get_hackernews_articles()
        
        self.pg.create_articles_ranking_table()
        
        if not user_list:
            user_list = self.pg.get_all_users()
        
        for user in user_list:
            articles = self.pg.get_articles_for_user(user)
            self._send_mail(user, articles)
        
if __name__ == "__main__":
    c = Cronjob()
    c._get_hackernews_articles()
