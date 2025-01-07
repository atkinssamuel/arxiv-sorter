import feedparser


def get_arxiv_papers(subject: str, num_papers: int = 5):
    # Define the RSS feed URL for the given subject
    base_url = "http://export.arxiv.org/rss/"
    subject_url = base_url + subject

    # Parse the RSS feed
    feed = feedparser.parse(subject_url)

    # Extract and display the papers from the feed
    papers = []

    for entry in feed.entries[:num_papers]:  # Limit to `num_papers` papers
        paper_info = {
            "title": entry.title,
            "summary": entry.summary,
            "published": entry.published,
            "link": entry.link,
        }
        papers.append(paper_info)

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
