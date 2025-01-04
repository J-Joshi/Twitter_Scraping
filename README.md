# Twitter Scraper with Proxy Support

This project is a **Twitter Trends Scraper** that automates the login process to Twitter (X), fetches trending topics, and stores them in a MongoDB database. It is designed to handle proxy authentication.

---

## **Key Features**
- **Proxy Integration**: Handles proxy authentication seamlessly using a dynamically created Chrome extension.
- **Selenium Automation**: Automates Twitter login and navigation to fetch trending topics.
- **MongoDB Integration**: Saves scraped trends along with metadata like timestamp and proxy IP address.
- **Environment-Specific Configurations**: Uses `.env` for secure storage of credentials and sensitive information.
- **Robust Error Handling**: Ensures smooth execution by handling exceptions at critical points.

---

## **Technologies Used**
- **Python**: The core programming language.
- **Selenium**: For web automation.
- **MongoDB**: As the database for storing trending topics.
- **ProxyMesh**: Proxy service for authenticated web scraping.
- **Requests**: For fetching the public IP address of the proxy.
- **UUID**: For generating unique identifiers for database records.
- **dotenv**: For environment variable management.

---

## **How It Works**
1. **Proxy Setup**:
   - A Chrome extension is dynamically generated to handle proxy authentication.
   - The proxy configuration allows anonymity and bypasses regional restrictions.

2. **Login Automation**:
   - Logs into Twitter using provided credentials via Selenium WebDriver.
   - Navigates through login prompts to access the trending page.

3. **Trend Scraping**:
   - Scrapes the top 5 trending topics from Twitter's "Explore" section.
   - Extracts the **4th `<span>` text** within specific trend containers to get the trend name. This approach ensures accuracy in identifying the trending topic's title.

4. **Data Storage**:
   - Each scraped record includes:
     - Trending topics (top 5)
     - Timestamp
     - Proxy IP address
   - Records are saved into a MongoDB collection for further analysis.

---
## **Project Structure**

project/

├── __pycache__/             # Compiled Python files

├── templates/               # HTML templates for web application
│   └── index.html           # Main HTML file for the web interface

├── .env                     # Environment variables 

├── .gitignore               # Specifies files and directories to ignore in Git

├── app.py                   # Main Flask application script

├── proxy_auth_plugin.zip    # Chrome extension for proxy authentication 

├── scrap.py                 # Script for scraping Twitter trends




