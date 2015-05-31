#!/usr/bin/env python3

from selenium import webdriver
import http.cookiejar
import os
import re
import sys
import time
import urllib.request

def mywait(driver, selector, method, wait=30, retry_secs=1,
           selector_type="css"):
    elapsed_secs = 0
    while elapsed_secs <= wait:
        try:
            if selector_type == 'css':
                elem = driver.find_element_by_css_selector(selector)
            elif selector_type == 'xpath':
                elem = driver.find_element_by_xpath(selector)
            elif selector_type == 'xpaths':
                elem = driver.find_elements_by_xpath(selector)
            else:
                raise Exception("Unknown selector type.")

            if method == 'click':
                elem.click()
                return 1
            elif method == 'find':
                return elem
            else:
                raise Exception("Unknown method in function wait.")
        except:
            time.sleep(retry_secs)
            elapsed_secs += retry_secs
    raise Exception("Could not find {} on page.".format(selector))

def click(driver, xpath, wait=30, retry_secs=1):
    return mywait(driver, xpath, "click", wait, retry_secs)

def find(driver, xpath, wait=30, retry_secs=1):
    return mywait(driver, xpath, "find", wait, retry_secs)

def findxpaths(driver, xpath, wait=30, retry_secs=1):
    return mywait(driver, xpath, "find", wait, retry_secs,
                  selector_type='xpaths')

def get_workout_urls(driver, bottom_year='2011'):
    all_workout_urls = set()
    cur_year = None

    while True:
        page_date = find(driver, '#current_month_heading').text.strip()
        cur_year = page_date[-4:]
        if bottom_year in page_date:
            break
        raw_elems = findxpaths(driver, "//a[starts-with(@href,'/workout/')]")

        # Possibly more than necessary checking, but, easier than me testing
        # to see what happens if there is nothing.
        try:
            page_workout_urls = {i.get_attribute('href') for i in raw_elems
                                 if re.match(".*\/workout\/[^\/]+$",
                                             i.get_attribute('href'))}
        except:
            pass

        if len(page_workout_urls):
            all_workout_urls.update(page_workout_urls)

        # Go to the previous page.
        click(driver, '#month_left')
        for i in range(0, 60):
            # Make sure the page changes.
            if not find(driver, '#current_month_heading').text == page_date:
                # When date changes the page has changed.
                continue

    return all_workout_urls

script_path = os.path.dirname(os.path.realpath(__file__))
url_file_str = os.path.join(script_path, "workouturls.txt")
tcx_folder_str = os.path.join(script_path, "tcx_files")

try:
    cred_file_str = os.path.join(script_path, 'credentials.txt')
    f = open(cred_file_str, 'r')
    username = f.readline().strip()
    password = f.readline().strip()
    f.close()
except IOError as e:
    print(e)
    print("Quitting, unable to get credentials file.")
    sys.exit(1)

if not all([username, password]):
    print("Quitting, username or password is blank")
    sys.exit(1)

profile = webdriver.FirefoxProfile()

# In most circumstances I am quite against ad-blocking, I wish I could have
# left them on but the ads were messing up the page load times and
# dealing with pop-ups would have been extra work. Not to mention that
# pop-ups fall into the category of "I don't feel bad for blocking these
# because pop-up ads are ridiculous"
adblock_str = os.path.join(script_path, 'addon-1865-latest.xpi')
if not os.path.isfile(adblock_str):
    print("Downloading adblock.")
    r = urllib.request.urlopen('https://addons.mozilla.org/firefox/'
                               'downloads/latest/1865/addon-1865-latest.xpi')
    with open(adblock_str, 'wb') as f:
        f.write(r.read())

profile.add_extension(adblock_str)

driver = webdriver.Firefox(profile)
driver.get("http://www.mapmyride.com/auth/login")

find(driver, '#id_email').send_keys(username)
find(driver, '#id_password').send_keys(password)
click(driver, '#login_button')

workout_urls = []
if not os.path.isfile(url_file_str):
    driver.get("http://www.mapmyride.com/workouts/")

    # click to reveal list of calendar or list
    click(driver, '#planning_selector_chosen')

    # click to view workouts as list
    click(driver, 'li.active-result:nth-child(2)')

    workout_urls = list(get_workout_urls(driver, bottom_year="2011"))
    f = open(url_file_str, 'w')
    for i in workout_urls:
        f.write(i)
        f.write('\n')
    f.close()
else:
    for i in open(url_file_str, 'r'):
        i = i.strip()
        if i:
            workout_urls.append(i)

if os.path.isfile(tcx_folder_str):
    Exception("There is a file where we need a folder. "
              "Please remove {}".format(tcx_folder_str))

if not os.path.isdir(tcx_folder_str):
    try:
        os.mkdir(tcx_folder_str)
    except Exception as e:
        print(e)
        sys.exit(1)

# This is the coolest part of this script. Take the Selenium cookies and use
# them to download the files using urllib.
all_cookies = driver.get_cookies()
cj = http.cookiejar.CookieJar()

for i in all_cookies:
    cookie = http.cookiejar.Cookie(
        version=0,
        name=i['name'],
        value=i['value'],
        port='80',
        port_specified=False,
        domain=i['domain'],
        domain_specified=True,
        domain_initial_dot=False,
        path=i['path'],
        path_specified=True,
        secure=i['secure'],
        expires=i['expiry'],
        discard=False,
        comment=None,
        comment_url=None,
        rest=None,
        rfc2109=False
    )
    cj.set_cookie(cookie)

num_urls = len(workout_urls)
count = 0
for i in workout_urls:
    count += 1
    print("Getting workout {} of {}.".format(count, num_urls))
    workout_id = i[33:]
    out_str = os.path.join(tcx_folder_str, '{}.tcx'.format(workout_id))
    if os.path.isfile(out_str):
        # don't re-download files
        continue

    url = 'http://www.mapmyride.com/workout/export/{}/tcx'.format(workout_id)
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    with open(out_str, 'wb') as f:
        f.write(opener.open(url).read())
    time.sleep(1)

driver.close()
print("All Done")

