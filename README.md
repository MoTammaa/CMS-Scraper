# CMS-Scraper

A script to synchronize the CMS of the university with the local PC to be up to date especially with the secret updates that happens in past weeks. :)

---

---

## Version 2.0 is out now 🎉🎉

### New Features:

-   Webdriver removed from the project for more flexibility.
-   More secure Authentication.
-   More stable and faster scraping.
-   Better logic and error handling.

---

---

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites _(for all versions)_

You need to have Python installed on your machine.  
You can download Python [here](https://www.python.org/downloads/).

### Installing _(for all versions)_

1. Clone the repository

```bash
git clone https://github.com/MoTammaa/CMS-Scraper
```

2. Install the required packages

```bash
pip install -r requirements.txt
```

<!-- note to use another requirements for version 1 -->

> **_Note:_** for version 1.0, see the [requirements_V1_old.txt](requirements_V1_old.txt) file.

## Renaming and Configuring Environment Variables _(for all versions)_

1. Rename the `.env.example` file to `.env`.
2. Open the `.env` file and fill in your details.
3. make sure the `.env` file is in the `metadata` folder.

## .env File Format _(for Version 2.0)_

> **_An example of the file may look like this:_**

> ```
> GUC_USERNAME=Hamasa.hammoud
> GUC_PASSWORD=anypassword3&3youdesire
> COURSES_DIRECTORY=D:/GUC/10th Semester/Courses
> ```

#### The .env is having the following format (i.e. on each new line there is a variable):

1. your username.
2. your password.
3. the path of the courses folder that you will download the files to (and not ending in any slashes `> ../../folder`).

## Running the Script _(for all versions)_

To run the script, just run the `CmsScrape.exe` file, or run the Python File, `CmsScrape.py`, in your favourite IDE.

## Notes 📝 _(for Version 2.0)_

-   **All Paths in the `.env` shoud be with forward slashes "/path/to/file" not backslashes.**
-   `metadata` folder should exist in the same path the `CmsScrape.exe` or `CmsScrape.py` exists.
-   `.env file` with your credentials and variables should exist in the `metadata` folder.
-   All variables in the `.env` can be with or without qoutations.
-   Courses directory should not end in any slashes.

</br>
</br>

---

---

</br>
</br>
</br>

## Version 1.0 (differences only)

## .env File Format

> **_An example of the file may look like this:_**

> ```
> Hamasa.hammoud
> anypassword3&3youdesire
> D:/Projects/CMS-Scraper/Microsoft Edge Webdriver/MicrosoftWebDriver.exe
> D:/GUC/7th Semester/Courses
> C:/Users/hamasa/Downloads
> ```

#### The .env is having the following format (i.e. on each new line there is a variable):

1. your username
2. your password
3. the **Microsoft Edge Webdriver** path without any qoutations ("."), and not ending in any slashes.
    - Note 1 : you can use the provided WebDriver in the project (but you need to have Microsoft Edge v120.0.2210.133)
    - Note 2 : you can use your default one or download WebDriver corresponding to your Edge Version from [here](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/?form=MA13LH), but you need to check the version of your _Edge_ in the About Page.
4. the path of the courses folder that you will download the files to _(with the folders of the courses created)_, with the same constraints of number `3`.
5. The default downloads folder in your PC, which is regularly the `Downloads` Folder in the C:.
    - Note: if it is not and you don't know the path, you can:
        1. run the `metadata/MicrosoftWebDriver.exe`.
        2. try to download and image/sound/video/Lecture from CMS/...etc from any website without the **Save as** dialog and,
        3. open the folder where it was downloaded and get its path.

## Limitations and Notes ⚠️

-   **All Paths in the `.env` shoud be with forward slashes "/path/to/file" not backslashes.**
-   For now, you should create new Folders in the path you specify in the .env with each course, if the script didn't find the specific _folder_ for the specific _course_, it will put the corresponding files in the **_Others_** folder.
-   `metadata` folder should exist in the same path the `CmsScrape.exe` or `CmsScrape.py` exists.
-   `.env file` with your credentials and variables should exist in the `metadata` folder.
-   All variables in the `.env` should be without any qoutations ("."), and not ending in any slashes.

</br>
</br>
</br>
## Contributing

Feel free to contribute to this project by creating a pull request or submitting an issue.

```

```

---

---

---

---

> # Pray for Palestine
