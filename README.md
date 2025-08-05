# H1B Job Parser for DevOps/SRE/Infrastructure Engineers

🚀 **Automated job parser that finds H1B sponsoring companies for DevOps, Site Reliability, and Infrastructure Engineer positions posted within the last 24 hours.**

⚡ **Now includes anti-blocking features and alternative parsing methods to handle site restrictions!**

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Active](https://img.shields.io/badge/Status-Active-green.svg)](https://github.com/b95702041/h1b-job-parser)

## 🎯 Features

- **🕐 Real-time Filtering**: Only finds jobs posted within the last 24 hours
- **🎯 Target Role Detection**: Specifically searches for DevOps, SRE, Infrastructure, Platform, and Cloud Engineering roles
- **🔍 H1B Sponsorship Analysis**: Intelligently detects H1B visa sponsorship mentions with confidence scoring
- **🛡️ Anti-blocking Technology**: Enhanced headers, random delays, and user agent rotation to avoid detection
- **📡 Multiple Search Methods**: RSS feeds, alternative job sites, and traditional web scraping
- **📊 Multi-source Scraping**: Searches Indeed, ZipRecruiter, Dice, and RSS feeds
- **💾 Export Options**: Saves results in both CSV and JSON formats
- **📈 Detailed Reports**: Generates comprehensive summary reports with statistics
- **⚡ Rate Limiting**: Respectful scraping with built-in delays
- **🔄 Alternative Parser**: Backup script for when main sites block requests

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Anti-blocking Solutions](#anti-blocking-solutions)
- [Alternative Parser](#alternative-parser)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Output Format](#output-format)
- [Troubleshooting 403 Errors](#troubleshooting-403-errors)
- [Customization](#customization)
- [Legal Considerations](#legal-considerations)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Install Dependencies

```bash
# Clone the repository
git clone https://github.com/b95702041/h1b-job-parser.git
cd h1b-job-parser

# Install required packages
pip install -r requirements.txt
```

### Requirements.txt
```
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
feedparser>=6.0.0
```

## ⚡ Quick Start

### Method 1: Standard Parser
1. **Run the main parser:**
```bash
python h1b_job_parser.py
```

### Method 2: Alternative Parser (Recommended if blocked)
1. **Run the anti-blocking parser:**
```bash
python h1b_alternative_parser.py
```

2. **View results:**
- Check generated CSV/JSON files in the current directory
- Review the console output for summary statistics

3. **Expected output files:**
- `h1b_jobs_YYYYMMDD_HHMMSS.csv` - All jobs found
- `h1b_jobs_YYYYMMDD_HHMMSS.json` - All jobs in JSON format
- `h1b_sponsors_only_YYYYMMDD_HHMMSS.csv` - Only H1B sponsoring jobs

## 🛡️ Anti-blocking Solutions

If you encounter **403 Forbidden** errors, try these solutions in order:

### Solution 1: Use Alternative Parser
```bash
# The alternative parser uses RSS feeds and different job sites
python h1b_alternative_parser.py
```

### Solution 2: Use VPN
1. Connect to a VPN to change your IP address
2. Run either parser:
```bash
python h1b_job_parser.py
# OR
python h1b_alternative_parser.py
```

### Solution 3: Wait and Retry
- Job sites may temporarily block your IP
- Wait 1-2 hours before trying again
- Try running at different times (early morning often works better)

### Solution 4: Manual Alternatives
- Use LinkedIn job alerts
- Search company career pages directly
- Check H1B database sites (MyVisaJobs.com, H1BGrader.com)

## 🔄 Alternative Parser

The `h1b_alternative_parser.py` script includes:

- **📡 RSS Feed Search**: Uses Indeed RSS feeds (often not blocked)
- **🔍 ZipRecruiter Integration**: Searches ZipRecruiter jobs
- **🎯 Dice.com Support**: Searches tech-focused Dice.com
- **🛡️ Enhanced Anti-detection**: 
  - Rotating user agents
  - Random delays (3-20 seconds)
  - Better request headers
  - Avoids explicit H1B terms in search queries

### Alternative Parser Usage
```bash
# Run the alternative parser
python h1b_alternative_parser.py

# Expected output sources:
# - Indeed RSS feeds
# - ZipRecruiter jobs  
# - Dice.com listings
```

## 🔧 Configuration

### Search Queries
Modify the `queries` list in the `main()` function:

**Main Parser (h1b_job_parser.py):**
```python
queries = [
    "DevOps Engineer",  # Simplified to avoid blocking
    "Site Reliability Engineer", 
    "Infrastructure Engineer",
    "Platform Engineer",
    "Cloud Engineer"
]
```

**Alternative Parser (h1b_alternative_parser.py):**
```python
queries = [
    "DevOps Engineer",
    "Site Reliability Engineer",
    "Infrastructure Engineer"
]
```

### Search Parameters
Adjust search scope in the `main()` function:

```python
# Increase pages for more results
jobs = parser.scrape_indeed(query, max_pages=5)  # Default: 3

# Change location
jobs = parser.scrape_indeed(query, location="San Francisco, CA")
```

### H1B Keywords
Customize detection keywords in the `__init__` method:

```python
# Add more H1B indicators
self.h1b_keywords = [
    'h1b', 'h-1b', 'visa sponsorship', 'work authorization',
    'sponsor visa', 'immigration sponsor', 'work visa',
    # Add your custom keywords here
]
```

## 📊 Usage Examples

### Basic Usage
```bash
# Main parser
python h1b_job_parser.py

# Alternative parser (recommended if blocked)
python h1b_alternative_parser.py
```

### Programmatic Usage
```python
# Main parser
from h1b_job_parser import H1BJobParser

# Initialize parser
parser = H1BJobParser()

# Search for specific role
jobs = parser.scrape_indeed("DevOps Engineer", max_pages=2)  # Reduced pages to avoid blocking

# Filter H1B sponsors
h1b_jobs = parser.filter_h1b_jobs(jobs)

# Generate report
parser.generate_report(jobs)

# Save results
parser.save_results(h1b_jobs, "devops_h1b_results")
```

### Alternative Parser Usage
```python
from h1b_alternative_parser import AlternativeH1BJobParser

# Initialize alternative parser
parser = AlternativeH1BJobParser()

# Search RSS feeds (often not blocked)
rss_jobs = parser.search_rss_feeds()

# Search ZipRecruiter
zip_jobs = parser.search_ziprecruiter("DevOps Engineer", max_pages=2)

# Search Dice
dice_jobs = parser.search_dice("Site Reliability Engineer", max_pages=2)

# Combine and analyze
all_jobs = rss_jobs + zip_jobs + dice_jobs
h1b_jobs = parser.filter_h1b_jobs(all_jobs)
```

## 📄 Output Format

### CSV Output
| Column | Description |
|--------|-------------|
| `title` | Job title |
| `company` | Company name |
| `location` | Job location |
| `description` | Job description |
| `url` | Job posting URL |
| `source` | Indeed/Glassdoor |
| `posting_date` | When job was posted |
| `sponsors_h1b` | True/False/None |
| `confidence` | high/medium/unknown |
| `keywords_found` | H1B keywords detected |
| `scraped_date` | When data was collected |

### Sample JSON Output
```json
{
  "title": "Senior DevOps Engineer",
  "company": "Tech Company Inc",
  "location": "Seattle, WA",
  "description": "We sponsor H1B visas for qualified candidates...",
  "url": "https://indeed.com/viewjob?jk=123456",
  "source": "Indeed",
  "posting_date": "today",
  "sponsors_h1b": true,
  "confidence": "high",
  "keywords_found": ["h1b", "visa sponsorship"],
  "scraped_date": "2025-08-05T10:30:00"
}
```

### Console Report
```
H1B JOB PARSING REPORT - LAST 24 HOURS
======================================
Total jobs found (last 24h): 23
Likely H1B sponsors: 15
No sponsorship: 5
Unknown/Unclear: 3

Posting time distribution:
  today: 18 jobs
  23 hours ago: 3 jobs
  1 day ago: 2 jobs

Top companies sponsoring H1B (last 24h):
  Microsoft: 3 jobs
  Amazon: 2 jobs
  Google: 2 jobs

Jobs by source:
  Indeed: 15 jobs
  Glassdoor: 8 jobs
```

## 🛠 Customization

### Adding New Job Sites

1. **Create a new scraping method:**
```python
def scrape_newsite(self, query: str, max_pages: int = 3) -> List[Dict]:
    jobs = []
    # Implementation here
    return jobs
```

2. **Add extraction method:**
```python
def extract_newsite_job_data(self, job_card) -> Optional[Dict]:
    # Extract job data
    return job_data
```

3. **Update main function:**
```python
# Add to search loop
newsite_jobs = parser.scrape_newsite(query, max_pages=2)
all_jobs.extend(newsite_jobs)
```

### Custom Date Filtering

Modify the `is_within_24_hours()` method to change the time window:

```python
def is_within_48_hours(self, posting_date_text: str) -> bool:
    # Change logic for 48-hour window
    # Implementation here
    return True/False
```

### Advanced Filtering

Add custom filters in the main loop:

```python
# Filter by salary range
high_salary_jobs = [job for job in jobs if 'salary' in job and int(job['salary']) > 100000]

# Filter by specific companies
target_companies = ['Google', 'Microsoft', 'Amazon']
big_tech_jobs = [job for job in jobs if job['company'] in target_companies]
```

## ⚖️ Legal Considerations

### ⚠️ Important Disclaimers

1. **Website Terms of Service**: Always check and comply with website terms of service before scraping
2. **Rate Limiting**: The script includes delays to be respectful to job sites
3. **Robot.txt**: Respect robots.txt files of target websites
4. **Personal Use**: This tool is intended for personal job searching purposes
5. **No Guarantee**: Results don't guarantee H1B sponsorship - always verify with employers

### Recommended Practices

- Use reasonable delays between requests (already implemented)
- Don't overload servers with excessive requests
- Consider using official APIs when available
- Respect website terms and conditions

### LinkedIn Limitation

LinkedIn has strict anti-scraping measures. Consider using:
- [LinkedIn Jobs API](https://docs.microsoft.com/en-us/linkedin/talent/)
- Manual LinkedIn searches
- LinkedIn Premium job alerts

## 🔧 Troubleshooting 403 Errors

### Common Error: 403 Forbidden
```
Error scraping Indeed page 0: 403 Client Error: Forbidden
```

**This means the job site is blocking your requests. Here's how to fix it:**

### ✅ **Immediate Solutions**

**1. Use the Alternative Parser**
```bash
python h1b_alternative_parser.py
```
*This uses RSS feeds and different job sites that are less restrictive.*

**2. Use a VPN**
```bash
# Connect to VPN first, then:
python h1b_job_parser.py
```

**3. Wait Before Retrying**
```bash
# Wait 1-2 hours, then try again
python h1b_job_parser.py
```

### 🛠️ **Advanced Solutions**

**Install Selenium for Browser Automation**
```bash
pip install selenium webdriver-manager
# Uses real browser - harder to detect but slower
```

**Use Proxy Servers**
```python
# Add to your script
proxies = {
    'http': 'http://proxy-server:port',
    'https': 'https://proxy-server:port'
}
```

### 📊 **Manual Backup Methods**

**1. Direct Company Searches**
- Google: `careers.google.com`
- Microsoft: `careers.microsoft.com` 
- Amazon: `amazon.jobs`
- Meta: `careers.meta.com`

**2. H1B Database Sites**
- MyVisaJobs.com - Search H1B sponsors
- H1BGrader.com - Company H1B data
- H1BData.info - Historical H1B information

**3. Set Up Job Alerts**
- LinkedIn job alerts for H1B keywords
- Indeed email notifications
- Google job alerts

### 🎯 **Prevention Tips**

1. **Don't run script too frequently** (max 2-3 times per day)
2. **Use random delays** between requests (already implemented)
3. **Try different times** (early morning often works better)
4. **Use VPN** to rotate IP addresses
5. **Reduce max_pages** to avoid overwhelming servers

### 📋 **Troubleshooting Checklist**

- [ ] Try alternative parser first
- [ ] Check internet connection
- [ ] Try with VPN connected
- [ ] Wait 1-2 hours if recently blocked
- [ ] Reduce number of search pages
- [ ] Check if sites are down (use downdetector.com)
- [ ] Try manual search to verify site is working

## 🔧 Troubleshooting Other Issues

### Common Issues

**Issue**: No jobs found (even without 403 errors)
```bash
# Solution: Website structure may have changed, check CSS selectors
# Debug with: print(len(job_cards)) in extract methods
```

**Issue**: Jobs are older than 24 hours
```bash
# Solution: Check date parsing logic or website structure changes
# Debug with: print(posting_date) in extract methods
```

**Issue**: Missing job descriptions
```bash
# Solution: Website structure may have changed
# Update CSS selectors in extract methods
```

**Issue**: Alternative parser not finding jobs
```bash
# Solution: RSS feeds may be down or changed
# Try individual components:
python -c "from h1b_alternative_parser import *; parser = AlternativeH1BJobParser(); jobs = parser.search_rss_feeds(); print(len(jobs))"
```

### Debug Mode

Add debugging to see what's happening:

```python
# Add at the beginning of scrape methods
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints
print(f"Found {len(job_cards)} job cards")
print(f"Parsing job: {title}")
print(f"Response status: {response.status_code}")
```

### Testing Individual Components

**Test RSS Feeds:**
```python
from h1b_alternative_parser import AlternativeH1BJobParser
parser = AlternativeH1BJobParser()
jobs = parser.search_rss_feeds()
print(f"RSS jobs found: {len(jobs)}")
```

**Test ZipRecruiter:**
```python
jobs = parser.search_ziprecruiter("DevOps Engineer", max_pages=1)
print(f"ZipRecruiter jobs found: {len(jobs)}")
```

**Test Dice:**
```python
jobs = parser.search_dice("Site Reliability Engineer", max_pages=1)
print(f"Dice jobs found: {len(jobs)}")
```

### Common Website Changes

Job sites frequently update their HTML structure. If scraping breaks:

1. **Inspect the webpage** to find new CSS selectors
2. **Update the extraction methods** with new selectors
3. **Test with a small number of pages** first

## 🤝 Contributing

We welcome contributions! Here's how to help:

### Development Setup

```bash
# Fork the repository
git clone https://github.com/your-username/h1b-job-parser.git
cd h1b-job-parser

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
```

### Contribution Guidelines

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/new-site-support`)
3. **Make** your changes
4. **Add** tests for new functionality
5. **Update** documentation
6. **Submit** a pull request

### Priority Contributions

- [ ] Add support for more job sites (Monster, LinkedIn API integration)
- [ ] Implement Selenium-based scraping for better reliability
- [ ] Add proxy rotation functionality
- [ ] Implement job description analysis for skills matching
- [ ] Add email notifications for new H1B jobs
- [ ] Create web interface for easier use
- [ ] Add database storage option
- [ ] Implement ML-based H1B detection
- [ ] Add support for more visa types (O1, L1, etc.)
- [ ] Create Docker container for easy deployment

## 📝 Changelog

### v1.3.0 (Current - Anti-blocking Update)
- ✅ Added alternative parser with RSS feeds and multiple job sites
- ✅ Enhanced anti-blocking with rotating user agents and random delays
- ✅ Added ZipRecruiter and Dice.com support
- ✅ Improved error handling for 403 blocks
- ✅ Updated headers to better mimic real browsers
- ✅ Added comprehensive troubleshooting guide

### v1.2.0
- ✅ Added 24-hour filtering requirement
- ✅ Added Glassdoor support
- ✅ Enhanced date parsing
- ✅ Improved reporting

### v1.1.0
- ✅ Added H1B keyword detection
- ✅ Implemented confidence scoring
- ✅ Added CSV/JSON export

### v1.0.0
- ✅ Initial release
- ✅ Indeed scraping
- ✅ Basic job filtering

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **BeautifulSoup** team for HTML parsing
- **Requests** library for HTTP handling
- **H1B database** sites for inspiration
- **Open source community** for best practices

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/b95702041/h1b-job-parser/issues)
- **Discussions**: [GitHub Discussions](https://github.com/b95702041/h1b-job-parser/discussions)

## 🆘 Getting Help

**If you encounter 403 errors:**
1. First try: `python h1b_alternative_parser.py`
2. Use VPN and retry
3. Check the troubleshooting section above
4. Open a GitHub issue with error details

**For other issues:**
1. Check the troubleshooting section
2. Enable debug mode to see what's happening
3. Test individual components
4. Open a GitHub issue with full error trace

## 🌟 Star History

If this project helped you, please consider giving it a ⭐!

---

**Disclaimer**: This tool is for educational and personal use. Always verify H1B sponsorship with employers directly. The authors are not responsible for any misuse or violations of website terms of service.