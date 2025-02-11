import feedparser
import os

from openai import OpenAI
from typing import List
from dotenv import load_dotenv
from datetime import datetime
from src.email import send_custom_email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google_auth_wrapper import credentials


class Paper:
    def __init__(self, entry, subject) -> None:
        self.title = entry.title
        self.authors = entry.author
        self.abstract = entry.summary.split("Abstract: ")[1]
        self.published = entry.published
        self.link = entry.link
        self.subject = subject

        self.score = 0

    def query_string(self):
        return f"Title: {self.title}\nSubject: {self.subject}\nAuthors: {self.authors}\n\n{self.abstract}"

    def __repr__(self) -> str:
        return f"Paper(title={self.title}, link={self.link}, authors={self.authors}, score={self.score})"


class PaperGrader:
    def __init__(self):
        load_dotenv()

        with open("context/prompt.txt", "r") as f:
            prompt = f.read()

        self.context_messages = [
            {
                "role": "system",
                "content": f"Your purpose is to score research papers according to their relevance to the user's prompt. Scores must be between 0 and 1. Higher scores indicate higher relevance. Do not reply with anything other than a score. Here is some information about the user:\n\n{prompt}",
            },
        ]

        api_key = os.getenv("OPENAI_API_KEY")

        self.client = OpenAI(api_key=api_key)

    def score(self, paper: Paper):
        paper_query = {
            "role": "user",
            "content": paper.query_string(),
        }

        chat_completion = self.client.chat.completions.create(
            messages=self.context_messages + [paper_query],
            model="gpt-4o",
        )

        response = chat_completion.choices[0].message.content

        try:
            return float(response)
        except:
            return 0


def get_arxiv_papers(subject: str, num_papers: int = 10):
    feed = feedparser.parse("http://export.arxiv.org/rss/" + subject)

    papers: List[Paper] = []

    for entry in feed.entries[:num_papers]:
        papers.append(Paper(entry, subject))

    return papers


def get_abstract_email(papers: List[Paper]):
    email = os.getenv("EMAIL")

    now = datetime.now().strftime("%Y-%m-%d")

    message = MIMEMultipart("related")

    message["from"] = email
    message["to"] = email
    message["subject"] = f"ArXiv Paper abstract {now}"

    papers_abstract = "<p>"

    for paper in papers:
        papers_abstract += f"""
        <h2>{paper.title}</h2>

        <p><b>Score:</b> {paper.score}</p>
        <p><b>Authors:</b> {paper.authors}</p>
        <p><b>Subject:</b> {paper.subject}</p>
        <a href="{paper.link}">{paper.link}</a>
        
        <br>

        <p>{paper.abstract}</p>
        <hr>
        """

    papers_abstract += "</p>"

    html_content = f"""
<!DOCTYPE html>
<html>
<body>
    {papers_abstract}
</body>
</html>

    """
    message.attach(MIMEText(html_content, "html"))

    return message


if __name__ == "__main__":
    creds = credentials(
        scopes=[os.getenv("GOOGLE_SCOPE")],
        client=os.getenv("GOOGLE_CLIENT_ID"),
        secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    )

    with open("context/subjects.txt", "r") as f:
        subjects = f.readlines()

    papers = []

    for subject in subjects:
        subject_papers = get_arxiv_papers(subject.strip())
        papers.extend(subject_papers)

    grader = PaperGrader()

    for paper in papers:
        paper.score = grader.score(paper)
        print(paper)

    papers.sort(key=lambda x: x.score, reverse=True)

    print("\n\nTop 5 papers:\n\n")

    for paper in papers[:5]:
        print(paper)

    message = get_abstract_email(papers)
    send_custom_email(message, creds)
