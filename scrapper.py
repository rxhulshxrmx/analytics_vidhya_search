import requests
from bs4 import BeautifulSoup
import csv
import os

def extract_course_info(html_content, url):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract course name
    course_name = soup.title.string if soup.title else "Course name not found"
    
    # Extract key takeaways - Updated selector to match the provided HTML
    key_takeaways = []
    checklist_container = soup.find('div', class_='checklist__container')
    if checklist_container:
        takeaway_items = checklist_container.find_all('li', class_='checklist__list-item')
        for item in takeaway_items:
            p_tag = item.find('p')
            if p_tag:
                # Remove the icon and get clean text
                takeaway_text = p_tag.text.replace('\uf00c', '').strip()
                # Remove "fa fa-check" text if present
                takeaway_text = takeaway_text.replace('fa fa-check', '').strip()
                key_takeaways.append(takeaway_text)
    
    # Extract course time, ratings, and difficulty level - FIXED PART
    # Use safer method to handle NoneType and avoid errors
    course_time = soup.find('li', class_='text-icon__list-item')
    course_time_text = course_time.find('h4').text if course_time else "Course time not found"
    
    ratings = course_time.find_next_sibling('li').find('h4').text if course_time and course_time.find_next_sibling('li') else "Ratings not found"
    
    difficulty_sibling = course_time.find_next_sibling('li').find_next_sibling('li') if course_time and course_time.find_next_sibling('li') else None
    difficulty = difficulty_sibling.find('h4').text if difficulty_sibling else "Difficulty level not found"

    # Extract course description
    description = "Description not found"
    description_section = soup.find('div', class_='course-description')
    if description_section:
        first_p = description_section.find('p')
        if first_p:
            description = first_p.text.strip()
    
    return {
        "course_name": course_name,
        "key_takeaways": ', '.join(key_takeaways) if key_takeaways else "No key takeaways found",
        "course_time": course_time_text,
        "ratings": ratings,
        "difficulty": difficulty,
        "description": description,
        "website": url
    }

def append_to_csv(course_info, csv_filename="course_data.csv"):
    file_exists = os.path.isfile(csv_filename)
    
    with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow(["Course Name", "Key Takeaways", "Course Time", "Ratings", "Difficulty", "Description", "Website"])
        
        writer.writerow([
            course_info["course_name"],
            course_info["key_takeaways"],
            course_info["course_time"],
            course_info["ratings"],
            course_info["difficulty"],
            course_info["description"],
            course_info["website"]
        ])

# Add headers to help avoid blocking
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Updated list of URLs to process
urls = [
    "https://courses.analyticsvidhya.com/courses/genai-applied-to-quantitative-finance-for-control-implementation",
    "https://courses.analyticsvidhya.com/courses/navigating-llm-tradeoffs-techniques-for-speed-cost-scale-and-accuracy",
    "https://courses.analyticsvidhya.com/courses/creating-problem-solving-agents-using-genai-for-action-composition",
    "https://courses.analyticsvidhya.com/courses/improving-real-world-rag-systems-key-challenges",
    "https://courses.analyticsvidhya.com/courses/choosing-the-right-LLM-for-your-business",
    "https://courses.analyticsvidhya.com/courses/building-smarter-llms-with-mamba-and-state-space-model",
    "https://courses.analyticsvidhya.com/courses/genai-a-way-of-life",
    "https://courses.analyticsvidhya.com/courses/building-llm-applications-using-prompt-engineering-free",
    "https://courses.analyticsvidhya.com/courses/building-your-first-computer-vision-model",
    
    # New URLs
    "https://courses.analyticsvidhya.com/courses/bagging-boosting-ML-Algorithms",
    "https://courses.analyticsvidhya.com/courses/midjourney_from_inspiration_to_implementation",
    "https://courses.analyticsvidhya.com/courses/free-understanding-linear-regression",
    "https://courses.analyticsvidhya.com/courses/The%20Working%20of%20Neural%20Networks",
    "https://courses.analyticsvidhya.com/courses/free-unsupervised-ml-guide",
    "https://courses.analyticsvidhya.com/courses/building-first-rag-systems-using-llamaindex",
    "https://courses.analyticsvidhya.com/courses/data-preprocessing",
    "https://courses.analyticsvidhya.com/courses/exploring-stability-ai",
    "https://courses.analyticsvidhya.com/courses/free-building-textclassification-natural-language-processing",
    
    "https://courses.analyticsvidhya.com/courses/getting-started-with-llms",
    "https://courses.analyticsvidhya.com/courses/introduction-to-generative-ai",
    "https://courses.analyticsvidhya.com/courses/nano-course-dreambooth-stable-diffusion-for-custom-images",
    "https://courses.analyticsvidhya.com/courses/a-comprehensive-learning-path-for-deep-learning-in-2023",
    "https://courses.analyticsvidhya.com/courses/a-comprehensive-learning-path-to-become-a-data-scientist-in-twenty-twenty-four",
    "https://courses.analyticsvidhya.com/courses/building-large-language-models-for-code",
    "https://courses.analyticsvidhya.com//bundles/certified-ai-ml-blackbelt-plus",
    "https://courses.analyticsvidhya.com/courses/machine-learning-summer-training",
    "https://courses.analyticsvidhya.com/courses/ai-ethics-fractal",
    
    "https://courses.analyticsvidhya.com/courses/a-comprehensive-learning-path-to-become-a-data-engineer-in-2022",
    "https://courses.analyticsvidhya.com/bundles/certified-business-analytics-program",
    "https://courses.analyticsvidhya.com/bundles/certified-machine-learning-master-s-program-mlmp",
    "https://courses.analyticsvidhya.com/bundles/certified-natural-language-processing-master-s-program",
    "https://courses.analyticsvidhya.com/bundles/certified-computer-vision-masters-program",
    "https://courses.analyticsvidhya.com/courses/applied-machine-learning-beginner-to-professional",
    "https://courses.analyticsvidhya.com/courses/ace-data-science-interviews",
    "https://courses.analyticsvidhya.com/courses/writing-powerful-data-science-articles",
    "https://courses.analyticsvidhya.com/courses/machine-learning-certification-course-for-beginners",
    
    "https://courses.analyticsvidhya.com/courses/data-science-career-conclave",
    "https://courses.analyticsvidhya.com/courses/top-data-science-projects-for-analysts-and-data-scientists",
    "https://courses.analyticsvidhya.com/courses/getting-started-with-git-and-github-for-data-science-professionals",
    "https://courses.analyticsvidhya.com/courses/machine-learning-starter-program",
    "https://courses.analyticsvidhya.com/courses/data-science-hacks-tips-and-tricks",
    "https://courses.analyticsvidhya.com/courses/introduction-to-analytics",
    "https://courses.analyticsvidhya.com/courses/introduction-to-pytorch-for-deeplearning",
    "https://courses.analyticsvidhya.com/courses/introductory-data-science-for-business-managers",
    "https://courses.analyticsvidhya.com/courses/intro-to-nlp",
    
    "https://courses.analyticsvidhya.com/courses/getting-started-with-decision-trees",
    "https://courses.analyticsvidhya.com/courses/introduction-to-data-science",
    "https://courses.analyticsvidhya.com/courses/loan-prediction-practice-problem-using-python",
    "https://courses.analyticsvidhya.com/courses/big-mart-sales-prediction-using-r",
    "https://courses.analyticsvidhya.com/courses/twitter-sentiment-analysis",
    "https://courses.analyticsvidhya.com/courses/pandas-for-data-analysis-in-python",
    "https://courses.analyticsvidhya.com/courses/support-vector-machine-svm-in-python-and-r",
    "https://courses.analyticsvidhya.com/courses/evaluation-metrics-for-machine-learning-models"
]

# Process each URL
for url in urls:
    try:
        print(f"Processing {url}...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors

        html = response.content
        course_info = extract_course_info(html, url)
        append_to_csv(course_info)
        
        print(f"Data for {url} has been successfully appended.")
    except Exception as e:
        print(f"Failed to process {url}: {e}")
