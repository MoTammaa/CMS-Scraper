# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
from selenium.webdriver.common.by import By
import time,os
from selenium.webdriver import Edge
from selenium.webdriver.edge.service import Service




driver = None
# Your login credentials & Variables
username = ""
password = ""
EdgeDriverPath = ""
Downloads = {}
scrape_url = ""
cms = 'cms.guc.edu.eg/apps/student/HomePageStn.aspx'
CoursesDirectory = ""
DefaultDownloadsInC = ""


def check_updates():
    global driver, scrape_url, cms

    # URL of the login page
    login_url = f"https://{username}:{password}@{cms}"

    # URL of the page you want to scrape
    scrape_url = login_url

    
    

    # Set Edge options to download files to the specified directory
    # options = EdgeOptions()
    # options.use_chromium = True
    # options.add_experimental_option('prefs', {
    #     "download.default_directory": download_dir,
    #     "download.prompt_for_download": False,
    #     "download.directory_upgrade": True,
    #     "plugins.always_open_pdf_externally": False
    # })
    
    # Initialize the Edge driver
    service = Service(executable_path=EdgeDriverPath)
    driver = Edge(service=service)#,options=options)
    
    
    # Now navigate to the page you're interested in
    driver.get(scrape_url)
    
    getCourses()
    
    # Remember to close the driver when finished
    driver.quit()
    
    
def getCourses():
    global scrape_url
    
    delay(1)
    
    loadPreviousDownloads()
    olddownloads = Downloads.copy()
    
    def updateCoursesLinks():
    
        courses = driver.find_elements(By.XPATH, 
            "/html/body/form/div[3]/div[2]/div[2]/div/div/div/div[2]/div[2]/div[1]/div[2]/div[2]/div/div/table/tbody/tr[*]/td[1]/input")
        
        coursecodes = driver.find_elements(By.XPATH, 
            "/html/body/form/div[3]/div[2]/div[2]/div/div/div/div[2]/div[2]/div[1]/div[2]/div[2]/div/div/table/tbody/tr[*]/td[2]")
        return courses, coursecodes
    # print(coursecodes[2].text)
    
    update = updateCoursesLinks()
    courses = update[0]
    coursecodes = update[1]
    
    from threading import Thread
    for i in range(0, len(courses)):
        c = courses[i]
        crcode = getCode(coursecodes[i].text)
        
        booldict = {"stop" : False}
        scrollthread = Thread(target=keepScrollUntillFalse, args=(booldict,1,))
        
        scrollthread.start()
        delay(1)
        booldict['stop'] = True
        
        
        print("\n\n\n############# ",coursecodes[i].text, "\n")
        downloadAllCourseFiles(c, crcode)
        saveDownloadsState()
        driver.get(scrape_url)
        
        update = updateCoursesLinks()
        courses = update[0]
        coursecodes = update[1]
    with open("lastrunsummary.txt", "w") as f:
        print("\n\n Summary - Downloaded: \n")
        f.write("\n\n Summary - Downloaded: \n")

        for key in Downloads:
            if key not in olddownloads:
                print("*-", Downloads[key])
                f.write("*- "+ Downloads[key] + "\n")
        print("\n.....\n\nDone!")
        f.write("\n.....\n\nDone!")                   
    
    

def downloadAllCourseFiles(coursebtn, coursecode):
    global Downloads
    coursebtn.click()  
    
    downloads = driver.find_elements(By.XPATH, 
                "/html/body/form/div[3]/div[2]/div[2]/div/div/div/div[2]/div[*]/div[2]/div[3]/div[*]/div/div[3]/div[1]/a")

    filenames = driver.find_elements(By.XPATH,
                    "/html/body/form/div[3]/div[2]/div[2]/div/div/div/div[2]/div[*]/div[2]/div[3]/div[*]/div/div[1]/strong")
    # if len(downloads) > 0:
    #     for d in downloads:
    #         print(d.text)
    #     print('-------------')
    #     return True

    for i in range(0, len(filenames)):
        filenames[i] = filenames[i].text     if "-" not in filenames[i].text else     filenames[i].text.split("-")[1]
        filenames[i] = filenames[i]     if not filenames[i].startswith(" ") else      filenames[i][1:]
                     

    link = downloads[0].get_attribute('href')
   
    
    # download course files:
    for i in range(0,len(downloads)):
        
        if "Download" not in downloads[i].text:
            continue
        link = downloads[i].get_attribute('href')
        oldname = link.split("/")[-1]
        
        print("downloading files ", (i+1) , "/" , len(downloads))
        if oldname in Downloads:
            print(" # Skipped File (already exists).")
            continue

        # if "Bach" in coursecode:
        downloads[i].click()    

    
        if moveDndFile(oldname, filenames[i] +"."+ oldname.split(".")[1], coursecode) != -1 :
            Downloads[oldname] = filenames[i]+ "." + oldname.split(".")[1]
            saveDownloadsState()
    
    
    import threading
    
    booldict = {"stop" : False}
    scrollthread = threading.Thread(target=keepScrollUntillFalse, args=(booldict,10,))
    
    scrollthread.start()
    delay(1)
    booldict['stop'] = True
    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    

  

def keepScrollUntillFalse(booldict, amount):
    while not booldict['stop']:
        driver.execute_script(f"window.scrollBy(0,{amount});")

    
def moveDndFile(oldfilename, newfilename, coursecode):
    import shutil
     
    directory = CoursesDirectory
    
# =============================================================================
#   if "Bach" not in coursecode:
#       return 0
# =============================================================================

    # get all files and folders' names in the directory
    filenames = os.listdir(directory)
    directories = [filename for filename in filenames if os.path.isdir(os.path.join(directory, filename))]
    
    try :
        subject = [folder for folder in directories if coursecode in folder][0]
    except Exception:
        print("CANNOT FIND COURSE Associated")
        return -1
    
    
    print("Waiting for file downloading...", end="")
    
    while(True):
        delay(1)
        try :
            shutil.move(f"{DefaultDownloadsInC}/{oldfilename}", f"{CoursesDirectory}/{subject}/{newfilename}")
            print("\nDownloaded Successfully!")
            return True
        except Exception:
            print(".", end="")
    

def getCode(coursename):
    if "Bachelor" in coursename:
        return "Bachelor"
    if "|" not in coursename:
        return "Others"
    
    possible = coursename.split("|")[1]  #ex. (|CSEN603|)Whatever Subject)
    import re
    return re.sub('[^0-9]', '', possible)

    
def delay(seconds):
    time.sleep(seconds)
    
    
    
    
def loadPreviousDownloads():
    global Downloads
    import json
    try :
        with open("metadata/downloads.json") as f:
            try :
                Downloads = json.load(f)
            except Exception:
                Downloads = None
    except Exception:
        Downloads = None
        print("No previous downloads found.")
        
    if Downloads == None:
        Downloads = {}

    # print(Downloads)
    
def saveDownloadsState():
    global Downloads
    import json
    with open("metadata/downloads.json", "w") as f:
        json.dump(Downloads,f)
    

def env__init():
    global username,password,EdgeDriverPath, CoursesDirectory, DefaultDownloadsInC
    try :
        with open('metadata/.env', 'r') as file:
            Environment_Variables = file.read()
    except Exception:
        # create .env file
        with open('metadata/.env', 'w') as file:
            file.write("[username]\n[password]\n[EdgeDriverPath]\n[CoursesDirectory]\n[Default Downloads Folder Path In C: Drive... Example: C:/Users/YourUserName/Downloads]")
    try:
        Environment_Variables = Environment_Variables.split('\n')
        username = Environment_Variables[0]
        password = Environment_Variables[1]
        EdgeDriverPath = Environment_Variables[2]
        CoursesDirectory = Environment_Variables[3]
        DefaultDownloadsInC = Environment_Variables[4]
    except Exception:
        print("Error in .env file.\n Please make sure to follow the format:\n---------\nusername\npassword\nEdgeDriverPath\nCoursesDirectory\nDefault Downloads Folder Path In C: Drive... Example: C:/Users/YourUserName/Downloads")
        import sys
        sys.exit()
    
    

# =============================================================================
# def send_email(notifications):
#     # Set up your email server
#     server = smtplib.SMTP('smtp.office365.com', 587)
#     server.starttls()
#     
#     # Your email credentials
#     email_username = 'your_email_username'
#     email_password = 'your_email_password'
#     
#     server.login(email_username, email_password)
# 
#     # Set up your message
#     msg = MIMEMultipart()
#     msg['From'] = email_username
#     msg['To'] = 'recipient@example.com'
#     msg['Subject'] = 'New notifications from university portal'
#     
#     body = '\n'.join(notification.text for notification in notifications)
#     
#     msg.attach(MIMEText(body, 'plain'))
# 
#     text = msg.as_string()
#     
#     server.sendmail(email_username, 'recipient@example.com', text)
# =============================================================================
    
    
    
def main():
    env__init()
    check_updates()
    


if __name__ =='__main__':
    main()
