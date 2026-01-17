import feedparser
import logging

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        self.sources = [
            "https://cointelegraph.com/rss",
            "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "https://cryptoslate.com/feed/"
        ]

    def get_latest_news(self, limit=5):
        """
        Fetches the latest news headlines from configured RSS sources.
        Returns a list of strings formatted as "Title (Source)".
        """
        news_items = []
        for url in self.sources:
            try:
                feed = feedparser.parse(url)
                if not feed.entries:
                    logger.warning(f"No entries found for {url}")
                    continue
                
                # Take top 2 from each source to mix it up
                for entry in feed.entries[:2]:
                    source_name = "Unknown"
                    if "cointelegraph" in url:
                        source_name = "CoinTelegraph"
                    elif "coindesk" in url:
                        source_name = "CoinDesk"
                    elif "cryptoslate" in url:
                        source_name = "CryptoSlate"
                        
                    news_items.append(f"{entry.title} ({source_name})")
                    
            except Exception as e:
                logger.error(f"Error fetching news from {url}: {e}")

        # Return the top 'limit' items (flattened list)
        return news_items[:limit]

if __name__ == "__main__":
    # Test run
    service = NewsService()
    news = service.get_latest_news()
    print("Fetched News:")
    for item in news:
        print("-", item)
