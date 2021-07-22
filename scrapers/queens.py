import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from models import Course, Timeslot, Section
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

driver = webdriver.Chrome(ChromeDriverManager().install())
wait = WebDriverWait(driver, 10)

hotfix_flip = True


def login():
    driver.get('https://saself.ps.queensu.ca/psc/saself/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.CLASS_SEARCH.GBL?Page=SSR_CLSRCH_ENTRY&Action=U')
    element = wait.until(EC.presence_of_element_located((By.ID, 'username')))
    element.send_keys(os.environ['QUEENS_USERNAME'])
    element = driver.find_element_by_id('password')
    element.send_keys(os.environ['QUEENS_PASSWORD'])
    element = driver.find_element_by_name('_eventId_proceed')
    element.click()


def get_subjects(semester):
    semester_string = "{} {}".format(semester['year'], semester['term'])
    driver.get("https://saself.ps.queensu.ca/psc/saself/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.CLASS_SEARCH.GBL?Page=SSR_CLSRCH_ENTRY&Action=U")
    # Semester Selection
    element = wait.until(EC.presence_of_element_located(
        (By.ID, 'CLASS_SRCH_WRK2_STRM$35$')))
    for option in element.find_elements_by_tag_name('option'):
        if option.text == semester_string:
            option.click()
            break

    # Wait for semester to be fetched
    wait.until(EC.invisibility_of_element_located((By.ID, "WAIT_win0")))
    element = driver.find_element_by_id('SSR_CLSRCH_WRK_SUBJECT_SRCH$0')
    return element.find_elements_by_tag_name('option')


'''
HOTFIX: WINTER 2021 NEEDS APPLIED SCIENCE < and > 150
'''


def get_search(semester, subject_idx):
    global hotfix_flip

    semester_string = "{} {}".format(semester['year'], semester['term'])
    driver.get("https://saself.ps.queensu.ca/psc/saself/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.CLASS_SEARCH.GBL?Page=SSR_CLSRCH_ENTRY&Action=U")
    # Semester Selection
    element = wait.until(EC.presence_of_element_located(
        (By.ID, 'CLASS_SRCH_WRK2_STRM$35$')))
    for option in element.find_elements_by_tag_name('option'):
        if option.text == semester_string:
            option.click()
            break

    # Wait for semester to be fetched and pick subject
    wait.until(EC.invisibility_of_element_located((By.ID, "WAIT_win0")))
    element = driver.find_element_by_id('SSR_CLSRCH_WRK_SUBJECT_SRCH$0')
    option = element.find_elements_by_tag_name('option')[subject_idx]
    option.click()

    hotfix = option.text == "Applied Science"
    if hotfix:
        # Less than OR greater than
        element = driver.find_element_by_id(
            'SSR_CLSRCH_WRK_SSR_EXACT_MATCH1$1')
        element.send_keys("l" if hotfix_flip else "g")
        hotfix_flip = not hotfix_flip
        # Boundry point
        element = driver.find_element_by_id(
            'SSR_CLSRCH_WRK_CATALOG_NBR$1')
        element.send_keys("150")
    else:
        # Contains ""
        element = driver.find_element_by_id(
            'SSR_CLSRCH_WRK_SSR_EXACT_MATCH1$1')
        element.send_keys("c")

    # Undergrad only
    element = driver.find_element_by_id('SSR_CLSRCH_WRK_ACAD_CAREER$2')
    option = element.find_elements_by_tag_name('option')[0]
    option.click()
    # Main campus only
    element = driver.find_element_by_id('SSR_CLSRCH_WRK_CAMPUS$3')
    element.send_keys("m")
    # In person instruction only
    # element = driver.find_element_by_id('SSR_CLSRCH_WRK_INSTRUCTION_MODE$4')
    # element.send_keys("i")
    # Show non open classes
    element = driver.find_element_by_id('SSR_CLSRCH_WRK_SSR_OPEN_ONLY$5')
    if element.is_selected():
        element.click()

    # Click search
    element = driver.find_element_by_id('CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH')
    element.click()

    # See if search gets results
    try:
        wait.until(lambda driver:
                   driver.find_elements(
                       By.ID, 'CLASS_SRCH_WRK2_SSR_PB_MODIFY$5$')
                   or
                   driver.find_elements(
                       By.XPATH, "//*[contains(text(), 'The search returns no results that match the criteria specified.')]")
                   )
    except:
        return "Error with search"

    engine = create_engine('sqlite:///data/queens.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Once search loads, parse html for classes and times
    courses = driver.find_elements_by_xpath(
        "//div[starts-with(@id,'win0divSSR_CLSRSLT_WRK_GROUPBOX2$')]")
    for course_div in courses:
        # Extract course info
        course_desc = course_div.find_element_by_tag_name(
            'a').get_attribute('title')
        course_code = course_desc[17:course_desc.index(" -")].replace(" ", "")
        course_code = course_code[:-
                                  1] if course_code[-1] == "A" or course_code[-1] == "B" else course_code
        course_name = course_desc[course_desc.index(" -") + 2:].strip()
        new_course = Course(code=course_code, name=course_name,
                            semester=semester_string)
        session.add(new_course)

        sections = course_div.find_elements_by_xpath(
            ".//tr[starts-with(@id,'trSSR_CLSRCH_MTG1$')]")
        for section_div in sections:
            # Extract section info
            section_desc = section_div.find_element_by_xpath(
                ".//a[starts-with(@id,'MTG_CLASSNAME$')]").text.splitlines()[0]
            section_code = section_desc[:section_desc.index("-")].strip()
            section_kind = section_desc[section_desc.index("-") + 1:].strip()
            new_section = Section(code=section_code,
                                  kind=section_kind)
            new_section.course = new_course
            session.add(new_section)
            timeslots = section_div.find_element_by_xpath(
                ".//span[starts-with(@id,'MTG_DAYTIME$')]").text.splitlines()
            for timeslot in timeslots:
                if timeslot == 'TBA':
                    continue
                # Extract timeslot info
                timeslot_times = timeslot[timeslot.index(' ') + 1:]
                start_string, end_string = timeslot_times.split(" - ")
                start_time = datetime.strptime(start_string, '%I:%M%p').time()
                end_time = datetime.strptime(end_string, '%I:%M%p').time()
                timeslot_string = timeslot[:timeslot.index(' ')]
                timeslot_days = [timeslot_string[i:i+2]
                                 for i in range(0, len(timeslot_string), 2)]
                for timeslot_day in timeslot_days:
                    new_timeslot = Timeslot(
                        day=timeslot_day,
                        start_time=start_time,
                        end_time=end_time)
                    new_timeslot.section = new_section
                    session.add(new_timeslot)
        try:
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()

    return "Success"


login()
semester = {
    "year": "2019",
    "term": "Fall"
}

subjects = get_subjects(semester)
subject_names = [subject.text for subject in subjects]
print("Found {} subjects".format(str(len(subjects))))
for idx, subject_name in enumerate(subject_names):
    if subject_name == " ":
        continue

    status = get_search(semester, idx)
    print("{} - {} - {}".format(str(idx).zfill(3),
          subject_name.ljust(30), status))

    if subject_name == "Applied Science":
        status = get_search(semester, idx)
        print("{} - {} - {}".format(str(idx).zfill(3),
                                    (subject_name + " (Batch 2)").ljust(30), status))


driver.quit()
