import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def scrape_ps_plus_games():
    url = "https://blog.playstation.com/category/ps-plus/"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Fetched page: {soup.title.text if soup.title else 'No title'}")
        
        articles = soup.select('article') or soup.find_all('div', class_=re.compile('post|article'))
        print(f"Found {len(articles)} articles")
        
        current_month = datetime.now().strftime("%B")  # "March"
        current_year = datetime.now().year  # 2025
        
        free_games = []
        
        for article in articles:
            title_elem = article.find('h2') or article.find('a', href=True)
            if not title_elem:
                continue
                
            title = title_elem.text.strip().lower()
            print(f"Checking article: {title}")
            
            if ("plus" in title and "games" in title and 
                (current_month.lower() in title or str(current_year) in title)):
                article_url = title_elem.get('href', article.find('a', href=True)['href'])
                print(f"Found potential match: {article_url}")
                
                article_response = requests.get(article_url, headers=headers)
                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                
                content = article_soup.select_one('div.entry-content') or article_soup.find('div', class_=re.compile('content|post'))
                if content:
                    print(f"Article content snippet: {content.text[:200]}...")
                    
                    intro_para = content.find('p')
                    if intro_para:
                        intro_text = intro_para.get_text(strip=True)
                        print(f"Intro text: {intro_text}")
                        
                        # Extract the game list portion after "March!"
                        game_section = re.search(r'March! (.+?)(?: will be available|$)', intro_text)
                        if game_section:
                            game_text = game_section.group(1)
                            print(f"Game section: {game_text}")
                            
                            # Split by commas and "and" to isolate titles
                            potential_games = re.split(r',| and ', game_text)
                            print(f"Potential games: {potential_games}")
                            
                            for game in potential_games:
                                game = game.strip()
                                # Filter: 10-60 chars, uppercase, no intro phrases
                                if (10 < len(game) < 60 and 
                                    any(c.isupper() for c in game) and 
                                    not re.search(r'playstation|plus|games|for|with|march|lineup|available|members|team|defy|speed|battle|clan|gods|enjoy', game.lower())):
                                    free_games.append(game)
                
                break
        
        if free_games:
            print(f"PS Plus Free Games for {current_month} {current_year}:")
            for game in set(free_games):
                print(f"- {game}")
        else:
            print("No free games detected. Check blog manually or adjust script logic.")
            
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    scrape_ps_plus_games()