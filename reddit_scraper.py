import praw
import csv
import datetime
import argparse
import os
from dotenv import load_dotenv

def setup_reddit_client():
    """Set up and return a Reddit API client using credentials from environment variables."""
    load_dotenv()  # Load environment variables from .env file
    
    return praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT', 'KeywordScraper v1.0 by /u/YourUsername')
    )

def search_reddit(reddit, keywords, subreddit=None, limit=100, time_filter='week'):
    """
    Search Reddit for posts containing the specified keywords.
    
    Args:
        reddit: PRAW Reddit instance
        keywords: List of keywords to search for
        subreddit: Specific subreddit to search in (None for all of Reddit)
        limit: Maximum number of results to return
        time_filter: 'hour', 'day', 'week', 'month', 'year', 'all'
        
    Returns:
        List of dictionaries containing post information
    """
    results = []
    
    for keyword in keywords:
        query = f'"{keyword}"'  # Search for exact matches
        
        # Determine where to search
        if subreddit:
            submissions = reddit.subreddit(subreddit).search(query, sort='new', time_filter=time_filter, limit=limit)
        else:
            submissions = reddit.subreddit('all').search(query, sort='new', time_filter=time_filter, limit=limit)
        
        # Process each submission
        for submission in submissions:
            # Basic post data
            post_data = {
                'keyword': keyword,
                'title': submission.title,
                'author': str(submission.author),
                'subreddit': submission.subreddit.display_name,
                'score': submission.score,
                'url': f'https://www.reddit.com{submission.permalink}',
                'created_utc': datetime.datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                'post_id': submission.id,
                'is_self_post': submission.is_self,
                'content_type': 'submission'
            }
            
            # Add text content if it's a self post
            if submission.is_self and submission.selftext:
                post_data['content'] = submission.selftext
            else:
                post_data['content'] = '[External link]'
                
            results.append(post_data)
            
            # Get comments for this submission
            submission.comments.replace_more(limit=0)  # Skip "load more comments" links
            for comment in submission.comments.list():
                if keyword.lower() in comment.body.lower():
                    comment_data = {
                        'keyword': keyword,
                        'title': submission.title,
                        'author': str(comment.author) if comment.author else '[deleted]',
                        'subreddit': submission.subreddit.display_name,
                        'score': comment.score,
                        'url': f'https://www.reddit.com{submission.permalink}{comment.id}/',
                        'created_utc': datetime.datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                        'post_id': comment.id,
                        'is_self_post': True,
                        'content': comment.body,
                        'content_type': 'comment'
                    }
                    results.append(comment_data)
    
    return results

def save_to_csv(results, filename='reddit_keyword_results.csv'):
    """Save the search results to a CSV file."""
    if not results:
        print("No results found.")
        return
    
    # Get all possible keys from all dictionaries
    fieldnames = set()
    for result in results:
        fieldnames.update(result.keys())
    
    fieldnames = sorted(list(fieldnames))
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Results saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Scrape Reddit for keyword mentions')
    parser.add_argument('--keywords', '-k', required=True, help='Comma-separated list of keywords to search for')
    parser.add_argument('--subreddit', '-s', help='Specific subreddit to search (default: all of Reddit)')
    parser.add_argument('--limit', '-l', type=int, default=100, help='Maximum number of results per keyword (default: 100)')
    parser.add_argument('--time', '-t', default='week', choices=['hour', 'day', 'week', 'month', 'year', 'all'],
                        help='Time filter for results (default: week)')
    parser.add_argument('--output', '-o', default='reddit_keyword_results.csv', 
                        help='Output CSV filename (default: reddit_keyword_results.csv)')
    
    args = parser.parse_args()
    
    # Parse keywords
    keywords = [k.strip() for k in args.keywords.split(',')]
    
    print(f"Searching Reddit for: {', '.join(keywords)}")
    if args.subreddit:
        print(f"In subreddit: r/{args.subreddit}")
    else:
        print("Across all of Reddit")
    
    # Set up Reddit client and perform search
    reddit = setup_reddit_client()
    results = search_reddit(reddit, keywords, args.subreddit, args.limit, args.time)
    
    print(f"Found {len(results)} mentions")
    save_to_csv(results, args.output)

if __name__ == "__main__":
    main() 