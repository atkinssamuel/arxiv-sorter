import feedparser

from typing import List


class Paper:
    def __init__(self, entry) -> None:
        self.title = entry.title
        self.summary = entry.summary
        self.published = entry.published
        self.link = entry.link

        self.score = None

    def __repr__(self):
        return (
            f"Paper(title={self.title}, published={self.published}, link={self.link})"
        )


def get_arxiv_papers(subject: str, num_papers: int = 10):
    feed = feedparser.parse("http://export.arxiv.org/rss/" + subject)

    papers: List[Paper] = []

    for entry in feed.entries[:num_papers]:
        papers.append(Paper(entry))

    return papers


if __name__ == "__main__":
    with open("context/subjects.txt", "r") as f:
        subjects = f.readlines()

    print(subjects)

    papers = get_arxiv_papers("cs.LG", 5)
    for idx, paper in enumerate(papers):
        print(f"Paper {idx + 1}:")
        print(f"Title: {paper['title']}")
        print(f"Published: {paper['published']}")
        print(f"Link: {paper['link']}")
        print(f"Summary: {paper['summary']}\n")
