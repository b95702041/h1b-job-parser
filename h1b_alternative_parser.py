#!/usr/bin/env python3
"""
Alternative H1B Job Parser - Anti-blocking Version

This script uses alternative methods to find H1B jobs when direct scraping is blocked.
Uses RSS feeds, APIs, and alternative job sites.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import csv
import feedparser  # You'll need: pip install feedparser
import urllib.parse

class AlternativeH1BJobParser:
    def __init__(self):
        self.session = requests.Session()
        
        # Rotate User-Agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # H1B sponsorship keywords
        self.h1b_keywords = [
            'h1b', 'h-1b', 'visa sponsorship', 'work authorization', 'sponsor visa',
            'immigration sponsor', 'work visa', 'employment authorization',
            'opt', 'cpt', 'green card', 'visa support'
        ]
        
        # Target roles
        self.target_roles = [
            'devops', 'dev ops', 'site reliability', 'sre', 'infrastructure engineer',
            'platform engineer', 'cloud engineer', 'systems engineer', 'reliability engineer'
        ]

    def get_random_headers(self):
        """Get random headers to avoid detection"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def search_rss_feeds(self) -> List[Dict]:
        """Search job RSS feeds for H1B positions"""
        jobs = []
        
        # Indeed RSS feeds (sometimes work when web scraping doesn't)
        rss_urls = [
            'https://rss.indeed.com/rss?q=devops+engineer&l=&sort=date',
            'https://rss.indeed.com/rss?q=site+reliability+engineer&l=&sort=date',
            'https://rss.indeed.com/rss?q=infrastructure+engineer&l=&sort=date',
            'https://rss.indeed.com/rss?q=platform+engineer&l=&sort=date',
            'https://rss.indeed.com/rss?q=cloud+engineer&l=&sort=date'
        ]
        
        for rss_url in rss_urls:
            try:
                print(f"Fetching RSS feed: {rss_url.split('q=')[1].split('&')[0]}")
                
                # Parse RSS feed
                feed = feedparser.parse(rss_url)
                
                for entry in feed.entries[:10]:  # Limit to recent entries
                    # Check if recent (within 24 hours)
                    if hasattr(entry, 'published_parsed'):
                        pub_date = datetime(*entry.published_parsed[:6])
                        if datetime.now() - pub_date > timedelta(hours=24):
                            continue
                    
                    # Extract job info
                    job_data = {
                        'title': entry.title,
                        'company': entry.get('source', 'Unknown'),
                        'location': 'Various',
                        'description': entry.summary if hasattr(entry, 'summary') else '',
                        'url': entry.link,
                        'source': 'Indeed RSS',
                        'posting_date': entry.published if hasattr(entry, 'published') else 'Unknown',
                        'scraped_date': datetime.now().isoformat()
                    }
                    
                    # Check if it's a target role
                    if self.is_target_role(job_data['title'], job_data['description']):
                        h1b_info = self.check_h1b_sponsorship(job_data['description'])
                        job_data.update(h1b_info)
                        jobs.append(job_data)
                
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                print(f"Error fetching RSS feed: {e}")
        
        return jobs

    def search_ziprecruiter(self, query: str, max_pages: int = 3) -> List[Dict]:
        """Search ZipRecruiter (often less restrictive than Indeed/Glassdoor)"""
        jobs = []
        base_url = "https://www.ziprecruiter.com/jobs-search"
        
        for page in range(max_pages):
            try:
                params = {
                    'search': query,
                    'location': 'United States',
                    'days': '1',  # Last 1 day
                    'page': page + 1
                }
                
                headers = self.get_random_headers()
                
                time.sleep(random.uniform(3, 8))
                
                response = self.session.get(base_url, params=params, headers=headers, timeout=30)
                
                if response.status_code == 403:
                    print(f"ZipRecruiter blocked request on page {page}")
                    break
                
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', class_='job_content')
                if not job_cards:
                    job_cards = soup.find_all('article', class_='job_result')
                
                print(f"Found {len(job_cards)} job cards on ZipRecruiter page {page}")
                
                for card in job_cards:
                    job_data = self.extract_ziprecruiter_job_data(card)
                    if job_data and self.is_target_role(job_data['title'], job_data['description']):
                        h1b_info = self.check_h1b_sponsorship(job_data['description'])
                        job_data.update(h1b_info)
                        jobs.append(job_data)
                
            except Exception as e:
                print(f"Error scraping ZipRecruiter page {page}: {e}")
                if "403" in str(e):
                    break
        
        return jobs

    def extract_ziprecruiter_job_data(self, job_card) -> Optional[Dict]:
        """Extract job data from ZipRecruiter job card"""
        try:
            title_elem = job_card.find('h2') or job_card.find('a', class_='job_link')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"
            
            company_elem = job_card.find('a', class_='company_name')
            if not company_elem:
                company_elem = job_card.find('span', class_='company')
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            
            location_elem = job_card.find('span', class_='location')
            location = location_elem.get_text(strip=True) if location_elem else "Unknown"
            
            desc_elem = job_card.find('p', class_='job_snippet')
            if not desc_elem:
                desc_elem = job_card.find('div', class_='job_description')
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Get job URL
            url_elem = job_card.find('a', class_='job_link')
            if not url_elem:
                url_elem = title_elem.find('a') if title_elem else None
            job_url = url_elem['href'] if url_elem and url_elem.get('href') else ""
            
            if job_url and not job_url.startswith('http'):
                job_url = f"https://www.ziprecruiter.com{job_url}"
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'url': job_url,
                'source': 'ZipRecruiter',
                'posting_date': 'Recent',
                'scraped_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error extracting ZipRecruiter job data: {e}")
            return None

    def search_dice(self, query: str, max_pages: int = 2) -> List[Dict]:
        """Search Dice.com for tech jobs"""
        jobs = []
        print("Searching Dice.com for tech positions...")
        
        # Dice often has good tech job listings
        base_url = "https://www.dice.com/jobs"
        
        for page in range(max_pages):
            try:
                params = {
                    'q': query,
                    'location': 'United States',
                    'radius': '30',
                    'radiusUnit': 'mi',
                    'page': page + 1,
                    'pageSize': '20',
                    'filters.postedDate': 'ONE'  # Posted within 1 day
                }
                
                headers = self.get_random_headers()
                time.sleep(random.uniform(4, 9))
                
                response = self.session.get(base_url, params=params, headers=headers, timeout=30)
                
                if response.status_code == 403:
                    print(f"Dice blocked request on page {page}")
                    break
                
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job cards (Dice structure)
                job_cards = soup.find_all('div', class_='card-body')
                if not job_cards:
                    job_cards = soup.find_all('div', attrs={'data-testid': 'job-card'})
                
                print(f"Found {len(job_cards)} job cards on Dice page {page}")
                
                for card in job_cards:
                    job_data = self.extract_dice_job_data(card)
                    if job_data and self.is_target_role(job_data['title'], job_data['description']):
                        h1b_info = self.check_h1b_sponsorship(job_data['description'])
                        job_data.update(h1b_info)
                        jobs.append(job_data)
                
            except Exception as e:
                print(f"Error scraping Dice page {page}: {e}")
                if "403" in str(e):
                    break
        
        return jobs

    def extract_dice_job_data(self, job_card) -> Optional[Dict]:
        """Extract job data from Dice job card"""
        try:
            title_elem = job_card.find('h5') or job_card.find('a', attrs={'data-testid': 'job-title'})
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"
            
            company_elem = job_card.find('span', class_='employer-name')
            if not company_elem:
                company_elem = job_card.find('a', class_='employer')
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            
            location_elem = job_card.find('span', class_='location')
            location = location_elem.get_text(strip=True) if location_elem else "Unknown"
            
            desc_elem = job_card.find('div', class_='job-description')
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Get job URL
            url_elem = job_card.find('a', attrs={'data-testid': 'job-title'})
            if not url_elem:
                url_elem = title_elem.find('a') if title_elem else None
            job_url = url_elem['href'] if url_elem and url_elem.get('href') else ""
            
            if job_url and not job_url.startswith('http'):
                job_url = f"https://www.dice.com{job_url}"
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'url': job_url,
                'source': 'Dice',
                'posting_date': 'Recent',
                'scraped_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error extracting Dice job data: {e}")
            return None

    def is_target_role(self, job_title: str, job_description: str = "") -> bool:
        """Check if job matches target roles"""
        text = f"{job_title} {job_description}".lower()
        return any(role in text for role in self.target_roles)

    def check_h1b_sponsorship(self, job_description: str) -> Dict[str, any]:
        """Check for H1B sponsorship keywords"""
        text = job_description.lower()
        
        # Check for no sponsorship keywords first
        no_sponsorship_keywords = [
            'no sponsorship', 'no visa sponsorship', 'must be authorized to work',
            'us citizen', 'permanent resident', 'no h1b', 'authorized to work without sponsorship'
        ]
        
        if any(keyword in text for keyword in no_sponsorship_keywords):
            return {"sponsors_h1b": False, "confidence": "high", "keywords_found": []}
        
        # Check for H1B keywords
        found_keywords = [keyword for keyword in self.h1b_keywords if keyword in text]
        
        if found_keywords:
            high_confidence_keywords = ['h1b', 'h-1b', 'visa sponsorship', 'sponsor visa']
            confidence = "high" if any(kw in found_keywords for kw in high_confidence_keywords) else "medium"
            return {"sponsors_h1b": True, "confidence": confidence, "keywords_found": found_keywords}
        
        return {"sponsors_h1b": None, "confidence": "unknown", "keywords_found": []}

    def save_results(self, jobs: List[Dict], filename: str = None):
        """Save results to CSV and JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"h1b_jobs_alternative_{timestamp}"
        
        # Save as CSV
        csv_filename = f"{filename}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            if jobs:
                fieldnames = jobs[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(jobs)
        
        # Save as JSON
        json_filename = f"{filename}.json"
        with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(jobs, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"Results saved to {csv_filename} and {json_filename}")

    def filter_h1b_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Filter jobs that likely sponsor H1B"""
        return [job for job in jobs if job.get('sponsors_h1b') is True]

    def generate_report(self, jobs: List[Dict]):
        """Generate summary report"""
        total_jobs = len(jobs)
        h1b_sponsors = len([j for j in jobs if j.get('sponsors_h1b') is True])
        no_sponsors = len([j for j in jobs if j.get('sponsors_h1b') is False])
        unknown = len([j for j in jobs if j.get('sponsors_h1b') is None])
        
        print(f"\n{'='*60}")
        print(f"ALTERNATIVE H1B JOB SEARCH REPORT")
        print(f"{'='*60}")
        print(f"Total jobs found: {total_jobs}")
        print(f"Likely H1B sponsors: {h1b_sponsors}")
        print(f"No sponsorship: {no_sponsors}")
        print(f"Unknown/Unclear: {unknown}")
        
        # Show sources
        sources = {}
        for job in jobs:
            source = job.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        if sources:
            print(f"\nJobs by source:")
            for source, count in sources.items():
                print(f"  {source}: {count} jobs")
        
        # Show top H1B companies
        if h1b_sponsors > 0:
            print(f"\nTop companies likely sponsoring H1B:")
            companies = {}
            for job in jobs:
                if job.get('sponsors_h1b') is True:
                    company = job.get('company', 'Unknown')
                    companies[company] = companies.get(company, 0) + 1
            
            for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {company}: {count} jobs")


def main():
    """Main function"""
    parser = AlternativeH1BJobParser()
    
    print("🚀 Alternative H1B Job Parser - Anti-blocking Version")
    print("="*60)
    print("This version uses RSS feeds and alternative job sites to avoid blocking.\n")
    
    all_jobs = []
    
    # Method 1: RSS Feeds
    print("📡 Searching RSS feeds...")
    try:
        rss_jobs = parser.search_rss_feeds()
        all_jobs.extend(rss_jobs)
        print(f"Found {len(rss_jobs)} jobs from RSS feeds")
    except Exception as e:
        print(f"RSS search failed: {e}")
    
    # Method 2: Alternative job sites
    queries = ["DevOps Engineer", "Site Reliability Engineer", "Infrastructure Engineer"]
    
    for query in queries:
        print(f"\n🔍 Searching for: {query}")
        
        # ZipRecruiter
        try:
            zip_jobs = parser.search_ziprecruiter(query, max_pages=2)
            all_jobs.extend(zip_jobs)
            print(f"Found {len(zip_jobs)} jobs from ZipRecruiter")
        except Exception as e:
            print(f"ZipRecruiter search failed: {e}")
        
        # Dice
        try:
            dice_jobs = parser.search_dice(query, max_pages=2)
            all_jobs.extend(dice_jobs)
            print(f"Found {len(dice_jobs)} jobs from Dice")
        except Exception as e:
            print(f"Dice search failed: {e}")
        
        # Wait between searches
        if query != queries[-1]:
            print("⏱️  Waiting before next search...")
            time.sleep(random.uniform(10, 20))
    
    # Remove duplicates
    unique_jobs = []
    seen_urls = set()
    for job in all_jobs:
        url = job.get('url', '')
        if url and url not in seen_urls:
            unique_jobs.append(job)
            seen_urls.add(url)
        elif not url:  # Include jobs without URLs but avoid complete duplicates
            job_signature = f"{job.get('title', '')}-{job.get('company', '')}-{job.get('location', '')}"
            if job_signature not in seen_urls:
                unique_jobs.append(job)
                seen_urls.add(job_signature)
    
    print(f"\n📊 Total unique jobs found: {len(unique_jobs)}")
    
    # Filter H1B jobs
    h1b_jobs = parser.filter_h1b_jobs(unique_jobs)
    
    # Generate report
    parser.generate_report(unique_jobs)
    
    # Save results
    if unique_jobs:
        parser.save_results(unique_jobs)
        
        if h1b_jobs:
            parser.save_results(h1b_jobs, "h1b_sponsors_only_alternative")
            print(f"\n✅ H1B sponsoring jobs saved separately: {len(h1b_jobs)} jobs")
    
    print("\n🎉 Alternative job search completed!")
    print("\n💡 Tips to improve results:")
    print("   - Use a VPN to change your IP address")
    print("   - Run the script at different times")
    print("   - Check company career pages directly")
    print("   - Use LinkedIn job alerts as backup")


if __name__ == "__main__":
    main()