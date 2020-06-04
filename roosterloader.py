from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from ics import Calendar, Event
from ics.alarm.display import DisplayAlarm
import time
from dateutil.tz import gettz
import datetime

klassen = ["BIN-3a", "BIN-3b", "BIN-3c", "BIN-3d", "BIN-3e"]


def main(klas):
    c = Calendar()

    option = webdriver.ChromeOptions()
    #option.add_argument("headless")
    option.add_argument(" — incognito")

    browser = webdriver.Chrome("/home/sander/webdrivers/chromedriver", options=option)

    browser.get(url="http://schoolplan.han.nl/SchoolplanFT_AS/rooster.asp")
    time.sleep(1)
    browser.find_element_by_id("username").send_keys("muluz")
    browser.find_element_by_id("password").send_keys("sg12whchtwoord")
    browser.find_element_by_class_name("button").click()

    browser.find_element_by_id("lestijden").click()
    browser.find_element_by_id("zaterdag").click()

    select = Select(browser.find_element_by_id("groep"))
    select.select_by_visible_text(klas)

    select = Select(browser.find_element_by_id("StartWeek"))
    options = select.options
    for index in range(0, len(options) - 1):
        select.select_by_index(index)
        select = Select(browser.find_element_by_id("StartWeek"))

        rooster = parserooster(browser)

        addevents(c, rooster)

    with open(f"{klas}_rooster.ics", 'w') as file:
        file.writelines(c)
    browser.close()

def parserooster(driver):
    table = []
    row_elements = driver.find_elements_by_xpath("//table[contains(@class, 'data')]//tbody/tr")

    for rowelement in row_elements:
        row = []
        for element in rowelement.find_elements_by_xpath(".//td[contains(@class, 'data')] | .//th"):
            row.append(element.text.rstrip())
        table.append(row)

    return table


def addevents(c, rooster):
    header = rooster[0][2:]
    rooster = rooster[1:]
    for events in rooster:
        tijd = events[1]
        tijd = tijd.split(":")
        events = events[2:]
        for i, event in enumerate(events):
            if event != '' and "vakantie" not in event.lower():
                jaar = datetime.datetime.now().year
                dag, maand = header[i].split("-")
                dag = dag.split(" ")[1]

                e = Event()
                startdate = datetime.datetime(year=jaar, month=int(maand), day=int(dag), hour=int(tijd[0]),
                                              minute=int(tijd[1]), tzinfo=gettz())
                e.begin = startdate
                e.duration = datetime.timedelta(minutes=45)
                e.name = event
                e.alarms.append(DisplayAlarm(trigger=datetime.timedelta(minutes=10)))
                c.events.add(e)


if __name__ == '__main__':
    tic = time.clock()
    for klas in klassen:
        main(klas)
    toc = time.clock()

    print(toc - tic)
