By Jonas Pao
# What it does
Allows you to specify a list of keywords and a timeframe, and get back a csv of all reddit posts with those keywords in that timeframe.



# How to use:
In the command line, type:

"python3 reddit_scraper.py --keywords "WRITE YOUR KEYWORDS HERE IN A LIST" --time "WRITE YOUR TIME HERE""

Arguements:
        keywords: List of keywords to search for
        subreddit: Specific subreddit to search in (None for all of Reddit)
        limit: Maximum number of results to return
        time_filter: 'hour', 'day', 'week', 'month', 'year', 'all'
        
# things you could add after keywords (filters):
--limit "NUMBER_LIMIT_OF_POSTS_SCRAPED" (default is 100)
--subreddit "NAME_OF_SUBREDDIT" (default any)
--time "WHAT_LOOKBACK_PERIOD_IS" (default week)
--output "NAME_OF_OUTPUT" (default reddit_keyword_results.csv)
