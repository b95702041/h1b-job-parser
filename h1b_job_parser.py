#!/usr/bin/env python3
"""
H1B Job Parser for DevOps/SRE/Infrastructure Engineer Positions

This script scrapes job postings and identifies positions that mention H1B sponsorship
for DevOps, Site Reliability Engineer, and Infrastructure Engineer roles.
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from urllib.parse import urljoin, urlparse
import csv
from datetime import datetime
from typing import List, Dict, Optional

class H1BJobParser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Keywords for job titles
        self.target_roles = [
            'devops', 'dev ops', 'site reliability', 'sre', 'infrastructure engineer',
            'platform engineer', 'cloud engineer', 'systems engineer', 'reliability engineer'
        ]
        
        # Keywords indicating H1B sponsorship
        self.h1b_keywords = [
            'h1b', 'h-1b', 'visa sponsorship', 'work authorization', 'sponsor visa',
            'eligible to work', 'visa sponsor', 'immigration sponsor', 'work visa',
            'employment authorization', 'opt', 'cpt', 'f1', 'green card'
        ]
        
        # Keywords that indicate NO sponsorship
        self.no_sponsorship_keywords = [
            'no sponsorship', 'no visa sponsorship', 'must be authorized to work',
            'us citizen', 'permanent resident', 'green card required',
            'no h1b', 'no visa support', 'authorized to work without sponsorship'
        ]

    def is_target_role(self, job_title: str, job_description: str = "") -> bool:
        """Check if job title/description matches target roles"""
        text = f"{job_title} {job_description}".lower()
        return any(role in text for role in self.target_roles)

    def check_h1b_sponsorship(self, job_description: str) -> Dict[str, any]:
        """Analyze job description for H1B sponsorship mentions"""
        text = job_description.lower()
        
        # Check for explicit no sponsorship first
        no_sponsorship = any(keyword in text for keyword in self.no_sponsorship_keywords)
        if no_sponsorship:
            return {"sponsors_h1b": False, "confidence": "high", "keywords_found": []}
        
        # Check for H1B sponsorship keywords
        found_keywords = [keyword for keyword in self.h1b_keywords if keyword in text]
        
        if found_keywords:
            # Determine confidence based on specific keywords
            high_confidence_keywords = ['h1b', 'h-1b', 'visa sponsorship', 'sponsor visa']
            confidence = "high" if any(kw in found_keywords for kw in high_confidence_keywords) else "medium"
            return {"sponsors_h1b": True, "confidence": confidence, "keywords_found": found_keywords}
        
        return {"sponsors_h1b": None, "confidence": "unknown", "keywords_found": []}

    def scrape_indeed(self, query: str, location: str = "United States", max_pages: int = 5) -> List[Dict]:
        """Scrape Indeed for job postings within last 24 hours"""
        jobs = []
        base_url = "https://www.indeed.com/jobs"
        
        for page in range(max_pages):
            params = {
                'q': query,
                'l': location,
                'start': page * 10,
                'fromage': '1'  # Filter for jobs posted within last 1 day
            }
            
            try:
                response = self.session.get(base_url, params=params)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                for card in job_cards:
                    job_data = self.extract_indeed_job_data(card)
                    if job_data and self.is_target_role(job_data['title'], job_data['description']):
                        h1b_info = self.check_h1b_sponsorship(job_data['description'])
                        job_data.update(h1b_info)
                        jobs.append(job_data)
                
                time.sleep(2)  # Be respectful to the server
                
            except Exception as e:
                print(f"Error scraping Indeed page {page}: {e}")
        
        return jobs

    def extract_indeed_job_data(self, job_card) -> Optional[Dict]:
        """Extract job data from Indeed job card"""
        try:
            title_elem = job_card.find('h2', class_='jobTitle')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"
            
            company_elem = job_card.find('span', class_='companyName')
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            
            location_elem = job_card.find('div', class_='companyLocation')
            location = location_elem.get_text(strip=True) if location_elem else "Unknown"
            
            # Extract posting date
            date_elem = job_card.find('span', class_='date')
            if not date_elem:
                date_elem = job_card.find('span', attrs={'data-testid': 'job-age'})
            posting_date = date_elem.get_text(strip=True) if date_elem else "Unknown"
            
            # Validate if job is within 24 hours
            if not self.is_within_24_hours(posting_date):
                return None  # Skip jobs older than 24 hours
            
            # Get job link for full description
            link_elem = title_elem.find('a') if title_elem else None
            job_url = urljoin("https://www.indeed.com", link_elem['href']) if link_elem else ""
            
            # Get job description snippet
            summary_elem = job_card.find('div', class_='summary')
            description = summary_elem.get_text(strip=True) if summary_elem else ""
            
            # Try to get full description if we have a URL
            if job_url:
                full_description = self.get_full_job_description(job_url)
                if full_description:
                    description = full_description
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'url': job_url,
                'source': 'Indeed',
                'posting_date': posting_date,
                'scraped_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error extracting job data: {e}")
            return None

    def is_within_24_hours(self, posting_date_text: str) -> bool:
        """Check if job posting is within the last 24 hours"""
        if not posting_date_text or posting_date_text == "Unknown":
            return False
        
        posting_date_text = posting_date_text.lower().strip()
        
        # Handle different date formats
        if any(keyword in posting_date_text for keyword in ['today', 'just posted', '0 days ago']):
            return True
        elif any(keyword in posting_date_text for keyword in ['1 day ago', 'yesterday', '24 hours ago']):
            return True
        elif 'hours ago' in posting_date_text:
            # Extract number of hours
            import re
            hours_match = re.search(r'(\d+)\s*hours?\s*ago', posting_date_text)
            if hours_match:
                hours = int(hours_match.group(1))
                return hours <= 24
            return True  # If we can't parse, assume it's recent
        elif any(keyword in posting_date_text for keyword in ['2 days ago', '3 days ago', 'days ago']):
            # Extract number of days
            import re
            days_match = re.search(r'(\d+)\s*days?\s*ago', posting_date_text)
            if days_match:
                days = int(days_match.group(1))
                return days <= 1
            return False
        elif any(keyword in posting_date_text for keyword in ['week', 'month', 'year']):
            return False
        
        # Try to parse specific date formats
        try:
            from datetime import datetime, timedelta
            current_time = datetime.now()
            
            # Common date patterns
            date_patterns = [
                '%m/%d/%Y',  # 01/15/2024
                '%Y-%m-%d',  # 2024-01-15
                '%b %d',     # Jan 15
                '%B %d',     # January 15
            ]
            
            for pattern in date_patterns:
                try:
                    parsed_date = datetime.strptime(posting_date_text, pattern)
                    # Add current year if not specified
                    if parsed_date.year == 1900:
                        parsed_date = parsed_date.replace(year=current_time.year)
                    
                    time_diff = current_time - parsed_date
                    return time_diff.total_seconds() <= 24 * 3600  # 24 hours in seconds
                except ValueError:
                    continue
                    
        except Exception:
            pass
        
        # If we can't determine, default to False (don't include)
        return False

    def scrape_with_date_filter(self, base_scrape_func, *args, **kwargs) -> List[Dict]:
        """Wrapper to add additional date filtering after scraping"""
        jobs = base_scrape_func(*args, **kwargs)
        
        # Additional filtering for 24-hour requirement
        filtered_jobs = []
        for job in jobs:
            posting_date = job.get('posting_date', '')
            if self.is_within_24_hours(posting_date):
                filtered_jobs.append(job)
        
        return filtered_jobs
        """Get full job description from job URL"""
        try:
            response = self.session.get(job_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Indeed job description container
            desc_elem = soup.find('div', class_='jobsearch-jobDescriptionText')
            if desc_elem:
                return desc_elem.get_text(strip=True)
            
            time.sleep(1)  # Rate limiting
            return None
            
        except Exception as e:
            print(f"Error getting full description from {job_url}: {e}")
            return None

    def scrape_glassdoor(self, query: str, location: str = "United States", max_pages: int = 3) -> List[Dict]:
        """Scrape Glassdoor for recent job postings"""
        jobs = []
        base_url = "https://www.glassdoor.com/Job/jobs.htm"
        
        for page in range(max_pages):
            params = {
                'q': query,
                'l': location,
                'p': page + 1,
                'fromAge': 1  # Jobs from last 1 day
            }
            
            try:
                response = self.session.get(base_url, params=params)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job cards (Glassdoor structure may vary)
                job_cards = soup.find_all('div', class_='react-job-listing')
                if not job_cards:
                    job_cards = soup.find_all('li', attrs={'data-test': 'jobListing'})
                
                for card in job_cards:
                    job_data = self.extract_glassdoor_job_data(card)
                    if job_data and self.is_target_role(job_data['title'], job_data['description']):
                        h1b_info = self.check_h1b_sponsorship(job_data['description'])
                        job_data.update(h1b_info)
                        jobs.append(job_data)
                
                time.sleep(3)  # Glassdoor is more strict about rate limiting
                
            except Exception as e:
                print(f"Error scraping Glassdoor page {page}: {e}")
        
        return jobs

    def extract_glassdoor_job_data(self, job_card) -> Optional[Dict]:
        """Extract job data from Glassdoor job card"""
        try:
            title_elem = job_card.find('a', attrs={'data-test': 'job-title'})
            if not title_elem:
                title_elem = job_card.find('a', class_='jobLink')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"
            
            company_elem = job_card.find('div', attrs={'data-test': 'employer-name'})
            if not company_elem:
                company_elem = job_card.find('div', class_='employerName')
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            
            location_elem = job_card.find('div', attrs={'data-test': 'job-location'})
            if not location_elem:
                location_elem = job_card.find('div', class_='loc')
            location = location_elem.get_text(strip=True) if location_elem else "Unknown"
            
            # Extract posting date
            date_elem = job_card.find('div', attrs={'data-test': 'job-age'})
            if not date_elem:
                date_elem = job_card.find('div', class_='jobAge')
            posting_date = date_elem.get_text(strip=True) if date_elem else "Unknown"
            
            # Validate if job is within 24 hours
            if not self.is_within_24_hours(posting_date):
                return None
            
            # Get job URL
            job_url = ""
            if title_elem and title_elem.get('href'):
                job_url = urljoin("https://www.glassdoor.com", title_elem['href'])
            
            # Get job description (usually limited in listing page)
            desc_elem = job_card.find('div', class_='jobDescriptionContent')
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'url': job_url,
                'source': 'Glassdoor',
                'posting_date': posting_date,
                'scraped_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error extracting Glassdoor job data: {e}")
            return None

    def get_full_job_description(self, job_url: str) -> Optional[str]:
        """
        Scrape LinkedIn Jobs (Note: LinkedIn has strict anti-scraping measures)
        This is a basic example - you may need to use LinkedIn's API instead
        """
        print("Note: LinkedIn scraping is limited due to anti-bot measures.")
        print("Consider using LinkedIn's Jobs API or manual search instead.")
        return []

    def save_results(self, jobs: List[Dict], filename: str = None):
        """Save results to CSV and JSON files"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"h1b_jobs_{timestamp}"
        
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
        h1b_jobs = []
        for job in jobs:
            if job.get('sponsors_h1b') is True:
                h1b_jobs.append(job)
        return h1b_jobs

    def generate_report(self, jobs: List[Dict]):
        """Generate a summary report"""
        total_jobs = len(jobs)
        h1b_sponsors = len([j for j in jobs if j.get('sponsors_h1b') is True])
        no_sponsors = len([j for j in jobs if j.get('sponsors_h1b') is False])
        unknown = len([j for j in jobs if j.get('sponsors_h1b') is None])
        
        print(f"\n{'='*60}")
        print(f"H1B JOB PARSING REPORT - LAST 24 HOURS")
        print(f"{'='*60}")
        print(f"Total jobs found (last 24h): {total_jobs}")
        print(f"Likely H1B sponsors: {h1b_sponsors}")
        print(f"No sponsorship: {no_sponsors}")
        print(f"Unknown/Unclear: {unknown}")
        
        # Show posting time distribution
        posting_times = {}
        for job in jobs:
            posting_date = job.get('posting_date', 'Unknown')
            posting_times[posting_date] = posting_times.get(posting_date, 0) + 1
        
        if posting_times:
            print(f"\nPosting time distribution:")
            for time_desc, count in sorted(posting_times.items(), key=lambda x: x[1], reverse=True):
                print(f"  {time_desc}: {count} jobs")
        
        if h1b_sponsors > 0:
            print(f"\nTop companies sponsoring H1B (last 24h):")
            companies = {}
            for job in jobs:
                if job.get('sponsors_h1b') is True:
                    company = job.get('company', 'Unknown')
                    companies[company] = companies.get(company, 0) + 1
            
            for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {company}: {count} jobs")
                
        # Show source breakdown
        sources = {}
        for job in jobs:
            source = job.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        if sources:
            print(f"\nJobs by source:")
            for source, count in sources.items():
                print(f"  {source}: {count} jobs")


def main():
    """Main function to run the job parser"""
    parser = H1BJobParser()
    
    # Define search queries for different role types
    queries = [
        "DevOps Engineer H1B sponsorship",
        "Site Reliability Engineer visa sponsorship",
        "Infrastructure Engineer H1B",
        "Platform Engineer visa sponsor",
        "Cloud Engineer H1B sponsorship"
    ]
    
    all_jobs = []
    
    print("Starting job search for positions posted in the last 24 hours...")
    
    for query in queries:
        print(f"\nSearching for: {query} (last 24 hours)")
        
        # Search Indeed
        indeed_jobs = parser.scrape_indeed(query, max_pages=3)
        all_jobs.extend(indeed_jobs)
        print(f"Found {len(indeed_jobs)} relevant jobs from Indeed")
        
        # Search Glassdoor
        glassdoor_jobs = parser.scrape_glassdoor(query, max_pages=2)
        all_jobs.extend(glassdoor_jobs)
        print(f"Found {len(glassdoor_jobs)} relevant jobs from Glassdoor")
    
    # Remove duplicates based on URL
    unique_jobs = []
    seen_urls = set()
    for job in all_jobs:
        url = job.get('url', '')
        if url not in seen_urls:
            unique_jobs.append(job)
            seen_urls.add(url)
    
    print(f"\nTotal unique jobs found: {len(unique_jobs)}")
    
    # Filter for H1B sponsors
    h1b_jobs = parser.filter_h1b_jobs(unique_jobs)
    
    # Generate report
    parser.generate_report(unique_jobs)
    
    # Save results
    if unique_jobs:
        parser.save_results(unique_jobs)
        
        if h1b_jobs:
            parser.save_results(h1b_jobs, "h1b_sponsors_only")
            print(f"\nH1B sponsoring jobs saved separately: {len(h1b_jobs)} jobs")
    
    print("\nJob parsing completed!")


if __name__ == "__main__":
    main()