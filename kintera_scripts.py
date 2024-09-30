import requests
from bs4 import BeautifulSoup  # type: ignore
import os
import urllib.request
import ssl
from urllib.parse import urljoin, urlparse

# Disable SSL verification for image downloads
ssl._create_default_https_context = ssl._create_unverified_context

# Create a folder to store the images
if not os.path.exists('kinteraequipment_images'):
    os.makedirs('kinteraequipment_images')

# Set of visited URLs to avoid re-crawling
visited_urls = set()

# Base URL of the website
base_url = 'https://kinteraequipment.com'

# Function to download images from a given page
def download_images(soup, page_url):
    for img in soup.find_all('img'):
        img_url = img.get('src')

        # Skip if img_url is None
        if not img_url:
            continue

        # Construct the full URL for relative paths
        full_url = urljoin(page_url, img_url)

        # Download the image
        image_name = os.path.basename(full_url)
        image_path = os.path.join('kinteraequipment_images', image_name)

        try:
            urllib.request.urlretrieve(full_url, image_path)
            print(f"Downloaded: {image_name}")
        except Exception as e:
            print(f"Could not download {image_name}: {e}")

# Function to crawl pages and download images
def crawl(url):
    # Avoid revisiting the same URL
    if url in visited_urls:
        return

    # Add the current URL to the visited set
    visited_urls.add(url)

    try:
        # Send a request to fetch the HTML content
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract page title and other content (optional)
        page_title = soup.title.string if soup.title else 'No Title'
        print(f"Page Title: {page_title}")

        # Download images from the current page
        download_images(soup, url)

        # Find all anchor tags with href attributes
        for link in soup.find_all('a', href=True):
            href = link['href']

            # Construct full URL for relative links
            full_link = urljoin(url, href)

            # Parse the URL to check if it's within the same domain
            parsed_url = urlparse(full_link)

            # Only follow links within the same domain
            if parsed_url.netloc == urlparse(base_url).netloc:
                # Recursively crawl subdirectories
                crawl(full_link)

    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve the webpage: {e}")

# Start crawling from the base URL
crawl(base_url)
