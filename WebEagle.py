import requests
from bs4 import BeautifulSoup, Comment
from time import sleep
import sys
import re
import whois
import socket
from PIL import Image
from urllib.parse import urlparse, urljoin
import signal, os
import dns.resolver
import argparse

def typewriter(text):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        sleep(0.05) 
        
def typewriter_2(text):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        sleep(0.02) 

sleep(1)
print("\n")
print("\r\t\t\t\t                      | ")
print("\r\t\t\t\t  ____________    __ -+-  ____________ ")
print("\r\t\t\t\t  \\_____     /   /_ \\ |   \\     _____/")
print("\r\t\t\t\t   \\_____    \\____/  \\____/    _____/")
print("\r\t\t\t\t    \\_____                    _____/")
print("\r\t\t\t\t       \\___________  ___________/")
print("\r\t\t\t\t                 /____\\")
sleep(1)
print("\n")

print("\t\t\t\t\tWelcome to THE WEB EAGLE")
print("\t\t\t\t\t\tBy ~ HM")
print("\n")


typewriter("Starting The Web Eagle....")
print("\n")
sleep(1)
typewriter("Getting environment ready for you...")
sleep(1)
print("\n\n")

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Web Eagle: Website Information Gathering & Scraping Tool",
        epilog="Example:\n  python3 WebEagle.py -u http://example.com\n "
    )
    parser.add_argument(
        '-u', '--url', help='Enter the URL to scan and scrape'
    )
    parser.add_argument(
        '-d', '--default', action='store_true', help='Use default option'
    )
    return parser

parser = parse_arguments()
args = parser.parse_args()

if not any(vars(args).values()):
    parser.print_help()
    print()
    

# FETCHING THE SOURCE CODE 
def fetch_html(url, folder_name):
    try:
        headers = {
            'User-Agent': 'Your User Agent String',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # Extract domain name from URL
            domain = re.search(r'(?<=://)[\w.-]+', url).group(0)
            file_name = f"{domain}.html"
            file_path = os.path.join(folder_name, file_name)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(response.text)
            
            print(f"HTML content saved to `{file_path}`")
            
            return response.text
        else:
            print(f"Failed to fetch URL: {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred while fetching URL {url}: {e}")
        return None


# GETTING EMAILS
def extract_emails(text):
    return re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)

def get_emails_from_pages(url):
    try:
        pages_to_scrape = ['/', 'about', 'contact', 'about.php', 'contact.php']

        email_addresses = set()  

        for page in pages_to_scrape:
            page_url = f"{url}/{page}" 
            headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            }
            response = requests.get(page_url, headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                for tag in soup.find_all(string=True):
                    if isinstance(tag, Comment):  
                        email_addresses.update(extract_emails(tag))
                    else:
                        email_addresses.update(extract_emails(tag))
            else:
                print(f"Page {page_url} returned status code {response.status_code}. Skipping.")

        return email_addresses

    except requests.RequestException as e:
        print("Error fetching page:", e)
        return None


# GETTING SOCIAL MEDIA ACCOUNTS
def get_social_media_links(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
        }
        if url.startswith('http://') or url.startswith('https://'):
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            soup = BeautifulSoup(response.text, 'html.parser')

            social_media_links = {}

            social_media_patterns = {
                'Facebook': 'facebook',
                'Twitter': 'twitter',
                'Instagram': 'instagram',
                'Youtube': 'youtube',
            }

            for platform, pattern in social_media_patterns.items():
                links = soup.find_all('a', href=lambda href: href and pattern in href.lower())
                social_media_links[platform] = [link['href'] for link in links]

            return social_media_links
        else:
            print("Invalid URL. Please provide a valid HTTP or HTTPS URL.")
            return None

    except requests.RequestException as e:
        print("Error fetching page:", e)
        return None


# FETCHING ROBOTS & HUMAN TXT OF WEBSITE
def fetch_robots_and_humans_txt(url):
    # Fetch robots.txt
    robots_url = url + "/robots.txt"
    robots_response = requests.get(robots_url, headers=headers)
    print("robots.txt:")
    print("-" * 20)
    if robots_response.status_code == 200:
        print("\n".join(robots_response.text.splitlines()[:50]))
    else:
        print("404 Not Found")

    # Fetch humans.txt
    sleep(1)
    humans_url = url + "/humans.txt"
    humans_response = requests.get(humans_url, headers=headers)
    print("\n")
    print("humans.txt:")
    print("-" * 20)
    if humans_response.status_code == 200:
        print("\n".join(humans_response.text.splitlines()[:50]))
    else:
        print("404 Not Found")
        
        
# BASIC INFO & OTHER INFO OF WEBSITE
def get_website_details(url, folder_name):
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
        }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.text.strip() if title_tag else "Title not found"
        print("Title of Website : ", title)
        
        # SERVER INFO
        server_info = response.headers.get('Server')
        print("Server : ", server_info if server_info else "Unknown")
        
        security_headers = {header: response.headers.get(header) for header in ['Content-Security-Policy', 'X-XSS-Protection', 'X-Content-Type-Options']}
        print("Security Headers : ", security_headers)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract OG tags
        og_title = soup.find('meta', property='og:title')
        og_description = soup.find('meta', property='og:description')
        og_image = soup.find('meta', property='og:image')
        if og_title:
            print("Open Graph Title : ", og_title['content'].strip())
        if og_description:
            print("Open Graph Description : ", og_description['content'].strip())
        if og_image:
            print("Open Graph Image : ", og_image['content'].strip())
        
        # Extract meta tags
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            if 'name' in tag.attrs and 'content' in tag.attrs:
                print("Meta : ", tag['name'], "-", tag['content'].strip())
        
        # Extract other relevant information as needed in future...
        
        # STORING THE RESULTS 
        try:
            
            file_path = os.path.join(folder_name, 'website_details.txt')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Title of Website : {title}\n")
                f.write(f"Server : {server_info if server_info else 'Unknown'}\n")
                f.write(f"Security Headers : {security_headers}\n")
                if og_title:
                    f.write(f"Open Graph Title : {og_title['content'].strip()}\n")
                if og_description:
                    f.write(f"Open Graph Description : {og_description['content'].strip()}\n")
                if og_image:
                    f.write(f"Open Graph Image : {og_image['content'].strip()}\n")
                for tag in meta_tags:
                    if 'name' in tag.attrs and 'content' in tag.attrs:
                        f.write(f"Meta : {tag['name']} - {tag['content'].strip()}\n")
            
            print("\n")
            sleep(1)
            typewriter(f"- Data Stored in {file_path}")
            sleep(1)
            print("\n")
        
        except Exception as e:
            print("There's a problem in saving file...", e)
        
    else:
        print("Failed to fetch website details. Status code:", response.status_code)


# BASIC DOMAIN INFO OF WEBSITE 
def get_domain_info(domain_name, folder_name):
    try:

        domain_info = whois.whois(domain_name)
        
        # Print the domain registration information
        typewriter("Domain Name: {}\n".format(domain_info.domain_name))
        typewriter("Registrar: {}\n".format(domain_info.registrar))
        typewriter("Creation Date: {}\n".format(domain_info.creation_date))
        typewriter("Expiration Date: {}\n".format(domain_info.expiration_date))
        typewriter("Updated Date: {}\n".format(domain_info.updated_date))
        typewriter("Name Servers: {}\n".format(domain_info.name_servers))
        
        # Other information available in domain_info
        typewriter_2("Status: {}\n".format(domain_info.status))
        typewriter_2("Registrant Name: {}\n".format(domain_info.name))
        typewriter_2("Registrant Organization: {}\n".format(domain_info.org))
        typewriter_2("Registrant Street: {}\n".format(domain_info.address))
        typewriter_2("Registrant City: {}\n".format(domain_info.city))
        typewriter_2("Registrant State: {}\n".format(domain_info.state))
        typewriter_2("Registrant ZIP Code: {}\n".format(domain_info.zipcode))
        typewriter_2("Registrant Country: {}\n".format(domain_info.country))
        typewriter_2("Registrant Email: {}\n".format(domain_info.email))
        typewriter_2("Registrant Phone: {}\n".format(domain_info.phone))
        typewriter_2("Admin Name: {}\n".format(domain_info.admin_name))
        typewriter_2("Admin Organization: {}\n".format(domain_info.admin_org))
        # And so on...
        
        # Write data to file
        file_name = f'domain_info.txt'
        file_path = os.path.join(folder_name, file_name)
        with open(file_path, 'w') as f:
            f.write(f"Domain Name: {domain_info.domain_name}\n")
            f.write(f"Registrar: {domain_info.registrar}\n")
            f.write(f"Creation Date: {domain_info.creation_date}\n")
            f.write(f"Expiration Date: {domain_info.expiration_date}\n")
            f.write(f"Updated Date: {domain_info.updated_date}\n")
            f.write(f"Name Servers: {domain_info.name_servers}\n")
            f.write(f"Status: {domain_info.status}\n")
            f.write(f"Registrant Name: {domain_info.name}\n")
            f.write(f"Registrant Organization: {domain_info.org}\n")
            f.write(f"Registrant Street: {domain_info.address}\n")
            f.write(f"Registrant City: {domain_info.city}\n")
            f.write(f"Registrant State: {domain_info.state}\n")
            f.write(f"Registrant ZIP Code: {domain_info.zipcode}\n")
            f.write(f"Registrant Country: {domain_info.country}\n")
            f.write(f"Registrant Email: {domain_info.email}\n")
            f.write(f"Registrant Phone: {domain_info.phone}\n")
            f.write(f"Admin Name: {domain_info.admin_name}\n")
            f.write(f"Admin Organization: {domain_info.admin_org}\n")
            # And so on...
        
        sleep(1)
        print("\n")
        typewriter(f"Domain information saved to: {file_path}\n")
        print("\n")
        
    except Exception as e:
        print("Failed to retrieve domain information:", e)


# GOING FOR SITEMAP XML :
def fetch_sitemap_xml(url, folder_name):
    variations = ["sitemap.xml", "sitemap", "smap"]
    
    for variation in variations:
        sitemap_url = f"{url}/{variation}"
        
        sitemap_response = requests.get(sitemap_url, headers=headers)
        
        print(f"Trying {variation}:")
        print("-" * 20)
        
        if sitemap_response.status_code == 200:
            print("\n".join(sitemap_response.text.splitlines()[:100])) 
        
            file_path = os.path.join(folder_name, 'sitemap.xml')
            with open(file_path, 'wb') as f:
                f.write(sitemap_response.content)
            print("\n")
            print("Sitemap found and stored.")
            print("\n")
        
            return
        
        sleep(1)  
        
    print("\n")
    print("404 Sitemap Not Found...")
    print("\n")
    
    
# GETTING IP ADDRESS 
def get_ip_address(url):
    try:
        domain_name = url.replace("https://", "").replace("http://", "").strip("/")
        
        ip_address = socket.gethostbyname(domain_name)
        print(f"The IP address of {url} is: < {ip_address} >")
        sleep(1)
        
    except Exception as e:
        sleep(1)
        print("\n")
        print(f"Failed to get IP address for {url}: {e}")
        print("\n")
        
        
# CAPTURING IMAGES 
continue_capture = True
scraping_images = False

def signal_handler(sig, frame):
    global continue_capture
    if scraping_images:
        print("\nCapturing images stopped. Going ahead...")
        continue_capture = False
    else:
        print("\n")
        print("\nCtrl+C pressed. Exiting... Thank you :)")
        print("\n")
        sys.exit(0)


# Function to scrape images
def scrape_images(url):
    global continue_capture, scraping_images
    scraping_images = True  # Set flag to indicate scraping images is running
    scraping_images = False  # Reset flag when scraping images is finished


signal.signal(signal.SIGINT, signal_handler)

def scrape_images(url):
    global continue_capture, scraping_images
    scraping_images = True 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        images_folder = os.path.join(folder_name, 'images')
        os.makedirs(images_folder, exist_ok=True)
        
        img_tags = soup.find_all('img')
        for idx, img_tag in enumerate(img_tags, start=1):
            if not continue_capture:
                scraping_images = False  # Set flag to False if Ctrl+C is pressed
                return
            img_url = img_tag.get('src')
            if img_url:
                # Check if the image URL has a valid scheme
                if not img_url.startswith(('http://', 'https://')):
                    img_url = urljoin(url, img_url)
                img_response = requests.get(img_url, headers=headers)
                if img_response.status_code == 200:
                    
                    img_filename = f'image_{idx}.jpg'
                    img_path = os.path.join(images_folder, img_filename)
                    with open(img_path, 'wb') as img_file:
                        img_file.write(img_response.content)
                    print(f"Image saved to : {img_path}")
                    # print("\n")
                    sleep(1)
                else:
                    print(f"Failed to download image: {img_url}")
            else:
                print("Image tag does not have a 'src' attribute")
            if not continue_capture:
                break  
        if continue_capture:
            show_images(folder_name)
    else:
        print(f"Failed to fetch page: {url}")
    
    scraping_images = False  # Reset flag when scraping images is finished

def show_images(folder_name):
    images_folder = os.path.join(folder_name, 'images')
    os.makedirs(images_folder, exist_ok=True)
    
    image_files = [f for f in os.listdir(images_folder) if f.endswith(('jpg', 'jpeg', 'png', 'gif', 'webp'))]
    if not image_files:
        print("No images found in the folder.")
        return
    print("Showing images saved in the folder:")
    
    for image_file in image_files:
        image_path = os.path.join(images_folder, image_file)
        img = Image.open(image_path)
        img.show()


## END OF FUNCTION


# GETTING WEBSITES OTHER INFO
def get_website_technologies(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract HTTP headers
            print("Server:", response.headers.get('Server'))
            print("X-Powered-By:", response.headers.get('X-Powered-By'))
            print("\n")
            # Extract meta tags
            meta_generator = soup.find('meta', attrs={'name': 'generator'})
            if meta_generator:
                # print("\n")
                print("Generator:", meta_generator['content'])
            # Extract JavaScript libraries and frameworks
            scripts = soup.find_all('script', src=True)
            js_libraries = [script['src'] for script in scripts if 'jquery' in script['src'].lower()]
            if js_libraries:
                print("\n")
                print("JavaScript Libraries:", ', '.join(js_libraries))
            # Extract CSS frameworks
            link_tags = soup.find_all('link', rel='stylesheet')
            css_frameworks = [tag['href'] for tag in link_tags if 'bootstrap' in tag['href'].lower()]
            if css_frameworks:
                print("\n")
                print("CSS Frameworks:", ', '.join(css_frameworks))
        else:
            print("Failed to fetch website:", response.status_code)
    except requests.RequestException as e:
        print("Error fetching page:", e)
        
## END OF FUNCTIONS


## TAKING ALL LINKS OF DOMAIN 
def links_of_domain(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
    }
    
    grab = requests.get(url, headers=headers)
    soup = BeautifulSoup(grab.text, 'html.parser')
    
    with open(f"{folder_name}/all_links_{folder_name}.txt", "w", encoding="utf-8") as f:
        # Traverse paragraphs from soup
        for link in soup.find_all("a"):
            href = link.get('href')
            if href:
                # Filter out relative URLs
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(url, href)
                f.write(href)
                f.write("\n")
                typewriter(f"The File is Stored as {folder_name}/all_links_{folder_name}.txt")
            else:
                print("Something went wrong...")
                print("\n")

        
# FETCHING ALL URLS OF WEBSITE 
def extract_links(url, folder_name):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)

        # Create a file path for storing links
        file_name = f"all_links_{folder_name}.txt"
        file_path = os.path.join(folder_name, file_name)

        # Write links to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            for link in links:
                file.write(link['href'] + '\n')

        print(f"- All links extracted from {url} and saved as `{file_name}`")
    
    except requests.RequestException as e:
        print(f"Failed to fetch webpage: {e}")
    
    except Exception as e:
        print(f"An error occurred: {e}")
         
         
# GETTING SUB DOMAINS OF WEBSITE :

def get_subdomains(url):
    subdomains = []
    try:
        # Parse the URL to extract the domain name
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Check if the domain is not empty
        if domain:
            # Resolve common subdomains
            common_subdomains = ['www', 'mail', 'blog', 'ftp', 'admin', 'news', 'mailman', 'ssh', 'new'] 
            for subdomain in common_subdomains:
                try:
                    answers = dns.resolver.resolve(f"{subdomain}.{domain}", 'A')
                    for rdata in answers:
                        subdomains.append(f"{subdomain}.{domain}")
                except dns.resolver.NXDOMAIN:
                    pass  # Subdomain does not exist
                except Exception as e:
                    print(f"Error: {e}")
        else:
            print("Error: Invalid URL format. Please provide a valid URL.")

    except Exception as e:
        print(f"Error: {e}")
    
    return subdomains
    
try:
    if args.url:
        typewriter("Scraping the Website & Gathering as much as possible information automatically...")
        sleep(1)
        print("\n")
        
        url = args.url
        
        typewriter(f"Scraping {url}")
        print("\n")
        sleep(1)
        print("Please Wait...")
        print("\n") 
        sleep(1)
        
        try:
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
            }
            
            r = requests.get(url, headers=headers)
            
            r.raise_for_status() 
            
            try:
                # THE ALL WORK WILL START FROM HERE
                if r.status_code == 200:
                    typewriter(f"Good News.. :) /!/ The website {url} is alive and returning status code <200>.")
                    sleep(1)
                    print("\n")
                    print(f"Creating the folder to save data for {url}")
                    sleep(2)    
                    # print("\n")
                    parsed_url = urlparse(url)
                    netloc = parsed_url.netloc
                    folder_name = netloc.replace('.', '_').replace(':', '_')
                    os.makedirs(folder_name, exist_ok=True)
                    print(f"Folder successfully created as : {folder_name}")
                    print("\n")
                    sleep(2)
                    get_ip_address(url)
                    print("\n")
                    sleep(2)
                    typewriter(f"Printing the Source Code of {url} :\n")
                    sleep(2)
                    print("\n")
                    html_content = fetch_html(url, folder_name)
                    if html_content:
                        print(html_content)
                    else:
                        pass
                    
                    print("\n")
                    sleep(1)
                    print(f"HTML Content saved to folder '{folder_name}'")
                    print("\n")
                    sleep(1)
                    print("\n")
                    typewriter("Yep.. I know that's not enough...")
                    print("\n")
                    typewriter("Let's do some interesting things...")
                    sleep(1)
                    print("\n")
                    typewriter("Scanning the whole website...")
                    print("\n")
                    sleep(1)
                    print("Please Wait...")
                    print("\n")
                    sleep(1)
                    
                    typewriter(f"The `Basic Information` of {url} : ")
                    print("\n")
                    sleep(1)
                    get_website_details(url, folder_name)
                    sleep(1)
                    print("\n")
                    sleep(1)
                    get_website_technologies(url)
                    print("\n")
                    sleep(1)
                    
                    sleep(2)
                    typewriter(f"The `Domain Info` of {url} :")
                    print("\n")
                    sleep(1)
                    get_domain_info(url, folder_name)
                    # print("\n")
                    sleep(1)
                    
                    print("\n")
                    sleep(1)
                    typewriter("Processing... Please wait...")
                    sleep(2)
                    print("\n")
                    print("\n")
                    
                    typewriter(f"Searching for a sitemap of {url}")
                    sleep(1)
                    print("\n")
                    fetch_sitemap_xml(url, folder_name)
                    print("\n")
                    sleep(1)
                    
                    typewriter(f"Let's try to find out the `Email Addresses` of {url} :")
                    sleep(1)
                    print("\n")
                    emails = get_emails_from_pages(url)
                    if emails:
                        print("\n")
                        print("Email addresses found on the website : \n")
                        for email in emails:
                            print("----- ")
                            typewriter(email)
                            print("\n----- ")
                            print("\n")
                            sleep(2)
                        print("Total email addresses found :", len(emails))
                        sleep(1)
                    else:
                        sleep(1)
                        print("No email addresses found on the website...")
                        print("\n")
                        typewriter("Process is going ahead...")
                    
                    print("\n")
                    sleep(1)
                    typewriter("Processing... Please wait...")
                    sleep(2)
                    print("\n")
                    print("\n")
                    typewriter(f"Taking `Social Media Accounts` of {url} :")
                    sleep(1)
                    print("\n")
                    
                    social_media_links = get_social_media_links(url)
                    if social_media_links:
                        print("Social media platforms and their links :")
                        for platform, links in social_media_links.items():
                            print(platform + ":")
                            for link in links:
                                print("- " + link)
                    else:
                        sleep(1)
                        print("No social media accounts found on the website...")
                        typewriter("Process is going ahead...")
                    
                    print("\n")
                    sleep(1)
                    typewriter("Processing... Please wait...")
                    sleep(2)
                    print("\n")
                    print("\n")
                    typewriter(f"Checking `robots.txt` & `human.txt` on {url} :")
                    print("\n")
                    sleep(1)
                    fetch_robots_and_humans_txt(url)
                    print("\n")
                    sleep(1)
                    typewriter("Processing... Please wait...")
                    sleep(2)
                    print("\n\n")
                    
                    ## IMAGES CAPTURING...
                    typewriter(f"Capturing the all images of {url}...")
                    sleep(1)
                    print("\n")
                    print("Press `Ctrl + C` to Stop Capturing...")
                    sleep(1)
                    print("\n")
                    scrape_images(url)      
                    # sleep(1)
                    print("\n")
                    sleep(1)
                    typewriter("Processing... Please wait...")
                    sleep(2)
                    print("\n")
                    ### END OF COMMENT OF IMAGES FUNCTION ###
                    
                    print("\n")
                    
                    ## GOING AHEAD FOR OTHER TASKS... ##
                    typewriter(f"----> Taking all URLs of {url}...")
                    sleep(1)
                    print("\n")
                    
                    parsed_url = urlparse(url)
                    netloc = parsed_url.netloc
                    folder_name = netloc.replace('.', '_').replace(':', '_')
        
                    os.makedirs(folder_name, exist_ok=True)
        
                    extract_links(url, folder_name)
                    
                    print("\n")
                    sleep(1)
                    typewriter("Processing... Please wait...")
                    sleep(2)
                    print("\n")
                    print("\n")
                    
                    typewriter(f"Trying to find `Sub Domains` of {url}")
                    sleep(1)
                    print("\n")
                    subdomains = get_subdomains(url)
                    print("Subdomains Found : ", subdomains)
                    sleep(2)
                    print("\n")
                    typewriter("Web Eagle has collected as much information as possible infromation.")
                    sleep(1)
                    print("\n")
                    typewriter_2("If you have any suggestions, please contact us.")
                    sleep(1)
                    print("\n")
                    print(" ;) Happy Hacking! \nGood Bye.")                    
                    # ENDS HERE THE CODE
            
                else:
                    print(f"The website {url} is alive but returned status code {r.status_code}.")
                    sleep(1)
                    print("Please Check the Website Manually...")
            except requests.RequestException as e:
                print(f"Error accessing the website {url}: {e}")
            # break
        
        except requests.RequestException as e:
            print("Error fetching page:", e)
            print("Please check the URL and try again.\n")
            # break    
    
    # THE DEFAULT LIST WORK OF SITES WILL WORK HERE
    elif args.default:
        print("YOU CHOSE 2")
        sleep(2)
        typewriter("This function is still under construction")
        print("\n")
        typewriter_2("Kindly check for updates")
    # AND ENDS HERE ...
    else:
        # print("PLEASE ENTER A VALID INPUT")
        pass
    
except ValueError:
        print("\n")
        sleep(1)
        print("Something went wrong...")
        print("\n") 