"""
The selenium firefox driver only works when the geckodriver executable is in PATH.
Here is more about that (need to write a short docs or something):
https://stackoverflow.com/questions/40208051/selenium-using-python-geckodriver-executable-needs-to-be-in-path
"""
import os
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
import time

def get_js():
    """
    This needs some jinja templating!
    """

    return 'file:///' + os.path.join(os.path.dirname(__file__),
                                     'js_template.html') 


def main(outname):
    """
    Needs yaml config!
    """
    url = get_js()

    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Firefox(firefox_options=options)
    driver.get(url)
    time.sleep(5) # there must be a better way to do this!

    data = driver.get_screenshot_as_png() # thats a first step.

    # Here should be the image processing! :D

    f = open(outname,'wb')
    f.write(data)
    f.close()


    return driver


if __name__ == '__main__':
    data = main('a_cool_map.png')



