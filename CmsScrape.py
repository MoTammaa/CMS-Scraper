from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import os
import time
import json
import re
import shutil
from requests_ntlm import HttpNtlmAuth

# Your login credentials & Variables
username = ""
password = ""
cms = 'cms.guc.edu.eg'
cms_student = f'{cms}/apps/student'
cms_courses = f'{cms_student}/ViewAllCourseStn'
course_default_link = f'https://{cms_student}/CourseViewStn.aspx?id=XIDPLACEHOLDER&sid=XSIDPLACEHOLDER'
CoursesDirectory = ""
DefaultDownloadsInC = ""
Downloads = {}
NewDownloads = {}

# 0 for latest, 1 for previous, 2 for the one before that, etc.
default_latest_semester = 0


def check_updates():
    global Downloads, NewDownloads

    # URL of the login page
    def login_to_cms():
        # Start a session
        session = requests.Session()

        # Set up NTLM authentication
        auth = HttpNtlmAuth(username, password)

        # Step 1: Access the CMS page with NTLM authentication
        url = f"https://{cms_courses}"
        try:
            response = session.get(url, auth=auth)
            response.raise_for_status()  # Raise an error for bad status codes
        except requests.exceptions.RequestException as e:
            print(f"Failed to access the CMS: {e}")
            return None

        # Step 2: Check if login was successful
        if response.status_code == 200:
            print("Login successful!")
            return session
        else:
            print(f"Login failed with status code: {response.status_code}")
            return None

    session = login_to_cms()
    if session:
        # Now you can use the session to access protected pages
        scrape_url = f"https://{cms_courses}"
        response = session.get(scrape_url)
        if response.status_code == 200:
            print("Successfully accessed the CMS!")
        else:
            print("Failed to access the CMS after login")
        # Now navigate to the page you're interested in
        scrape_url = f"https://{cms_courses}"
        response = session.get(scrape_url)

        if response.status_code != 200:
            print("Failed to retrieve the page")
            return

        getCourses(session, response.text)
    else:
        print("Login failed")


def getCourses(session, html_content):
    global Downloads, NewDownloads

    loadPreviousDownloads()
    soup: BeautifulSoup = BeautifulSoup(html_content, 'html.parser')

    def updateCourseLinks(soup: BeautifulSoup):
        # Find the table by its ID
        table = soup.find('table', {
                          'id': f'ContentPlaceHolderright_ContentPlaceHoldercontent_r1_GridView1_{default_latest_semester}'})

        if table:
            # Find all rows in the table body
            rows = table.find('tbody')
            if not rows:
                rows = table.find_all('tr')
            else:
                rows = rows.find_all('tr')

            # remove the first row (header)
            if len(rows) == 0:
                print("No courses found!")
                return None, None
            rows = rows[1:]
            # Extract the course codes (second <td> in each row)
            coursecodes = [row.find_all('td')[1].text.strip() for row in rows]

            # Extract the course links (fourth <td> in each row)
            courses_ids = [row.find_all('td')[3].text.strip() for row in rows]
            # Extract the course links (fifth <td> in each row)
            course_season_ids = [row.find_all(
                'td')[4].text.strip() for row in rows]

            courses_links = [course_default_link.replace('XIDPLACEHOLDER', course_id).replace(
                'XSIDPLACEHOLDER', course_season_id) for course_id, course_season_id in zip(courses_ids, course_season_ids)]

            print("Course Links:", courses_links)
        else:
            print("Table not found!")

        return courses_links, coursecodes

    courses, coursecodes = updateCourseLinks(soup)

    for i in range(len(courses)):
        course = courses[i]
        crcode = getCode(coursecodes[i])
        courseprefix = getPrefix(coursecodes[i])

        print("\n\n\n############# ", coursecodes[i], "\n")
        downloadAllCourseFiles(session, course, crcode, courseprefix)
        saveDownloadsState()

    with open("lastrunsummary.txt", "w") as f:
        print("\n\n Summary - Downloaded: \n")
        f.write("\n\n Summary - Downloaded: \n")

        for key in NewDownloads:
            print("*-", NewDownloads[key])
            f.write("*- " + NewDownloads[key] + "\n")
        print("\n.....\n\nDone!")
        f.write("\n.....\n\nDone!")


def downloadAllCourseFiles(session, course, coursecode, courseprefix):
    global Downloads, NewDownloads

    response = session.get(course)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all download links
    link_prefix = f"https://{cms}"
    download_links = soup.select(
        'div > div > div > div > div > div > div > div > div > div > div > div > div > a')
    downloads = [(link.text, f"{link_prefix}{link['href']}")
                 for link in download_links if 'href' in link.attrs]

    # Find all filenames
    filename_elements = soup.select(
        'div > div > div > div > div > div > div > div > div > div > div > div > strong')
    filenames = [element.text.strip() for element in filename_elements]

    for i in range(len(filenames)):
        filenames[i] = fix_filename(filenames[i])

    for i in range(len(downloads)):
        if "download" not in str(downloads[i][0]).lower():
            continue
        link = downloads[i][1]
        oldname = link.split("/")[-1]

        print("downloading files ", (i+1), "/", len(downloads))
        if oldname in Downloads:
            if filenames[i] + "." + oldname.split(".")[-1] == Downloads[oldname]:
                print(" # Skipped File (already exists).")
                continue

        if DownloadFile(session, link, oldname, filenames[i] + "." + oldname.split(".")[-1], coursecode, courseprefix, CoursesDirectory):
            continue
        print("Failed to download file: ", filenames[i])


def fix_filename(filename: str) -> str:
    filename = re.sub(r"^\s*\d\s*-\s*", "", filename)
    filename = filename.strip().replace("/", "_").replace("\\", "_").replace(":", " - ").replace(
        "*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")
    return filename


def DownloadFile(session, link, oldname, newname, coursecode, courseprefix, directory):
    filenames = os.listdir(directory)
    directories = [filename for filename in filenames if os.path.isdir(
        os.path.join(directory, filename))]

    try:
        subject = [
            folder for folder in directories
            if coursecode.lower() in folder.lower() and courseprefix.lower() in folder.lower()
        ][0]
    except Exception:
        print("CANNOT FIND COURSE Associated")
        subject = courseprefix + " " + coursecode
        os.makedirs(os.path.join(directory, subject))

    course_folder = os.path.join(directory, subject)
    file_path = os.path.join(course_folder, newname)

    # Download the file directly into the course folder
    response = session.get(link, stream=True)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded: {newname} -> {file_path}")

        # Update Downloads and NewDownloads
        Downloads[oldname] = newname
        saveDownloadsState()
        NewDownloads[oldname] = f"{courseprefix} {coursecode} -> {newname}"
        return True
    else:
        print(
            f"Failed to download: {newname} (Status Code: {response.status_code})")
        return False


def getCode(coursename):
    if "Bachelor" in coursename:
        return "Bachelor"
    if "|" not in coursename:
        return coursename

    possible = coursename.split("|")[1]
    return re.sub('[^0-9]', '', possible)


def getPrefix(coursename):
    if "Bachelor" in coursename:
        return "Bachelor"
    if "|" not in coursename:
        return "Others"

    possible = coursename.split("|")[1]
    return re.sub('[0-9]', '', possible)


def delay(seconds):
    time.sleep(seconds)


def loadPreviousDownloads():
    global Downloads
    try:
        with open("metadata/downloads.json") as f:
            try:
                Downloads = json.load(f)
            except Exception:
                Downloads = None
    except Exception:
        Downloads = None
        print("No previous downloads found.")

    if Downloads == None:
        Downloads = {}


def saveDownloadsState():
    global Downloads
    with open("metadata/downloads.json", "w") as f:
        json.dump(Downloads, f)


def env__init():
    import sys
    global username, password, CoursesDirectory

    # Create .env file if it doesn't exist
    if not os.path.exists('metadata/.env'):
        with open('metadata/.env', 'w') as file:
            file.write("""USERNAME=\"\"
PASSWORD=\"\"
COURSES_DIRECTORY=\"\"
""")
        print("Created .env file. Please fill in your credentials.")
        raise FileNotFoundError(
            "Please fill in your credentials in the .env file.")

    # Load environment variables
    load_dotenv('metadata/.env')

    # Get environment variables
    username = os.getenv('GUC_USERNAME')
    password = os.getenv('GUC_PASSWORD')
    CoursesDirectory = os.getenv('COURSES_DIRECTORY')

    # Validate required environment variables
    if not all([username, password, CoursesDirectory]):
        print("Error: Missing required environment variables in .env file.")
        print("Please make sure to set:\nUSERNAME\nPASSWORD\nCOURSES_DIRECTORY")
        sys.exit()


if __name__ == "__main__":
    try:
        env__init()
        check_updates()
    except Exception as e:
        print("An error occurred:", e)
        print("Exiting...")
    # wait for 300 seconds before exiting
    delay(300)
