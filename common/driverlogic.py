import os

from selenium import webdriver
from selenium.webdriver.firefox.webdriver import FirefoxProfile


def initialize():
    profile = FirefoxProfile(profile_directory=get_profile_dir())
    driver = webdriver.Firefox(firefox_profile=profile)
    return driver


def get_profile_dir():
    profiles_loc = os.environ['APPDATA'] + '\\Mozilla\\Firefox\\Profiles\\'
    for cat in os.listdir(profiles_loc):
        if 'logins.json' in os.listdir(profiles_loc + cat):
            return profiles_loc + cat
    else:
        assert False, 'No proper profile found'


def check(row):
    return not bool(row.find_elements_by_css_selector('.feed_friends_recomm')
                    + row.find_elements_by_css_selector('#ads_feed_placeholder'))


def get_rows(driver):
    unchecked_rows = []
    while not unchecked_rows:
        unchecked_rows = driver.find_elements_by_css_selector('.feed_row')
    checked_rows = list(filter(check, unchecked_rows))
    return checked_rows
