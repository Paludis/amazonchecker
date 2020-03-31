# -*- coding: utf-8 -*-
from datetime import datetime
import sys
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time


def run(url, refresh_interval):

    try:
        f = open("pw.txt", "r")
    except IOError:
        print("ERROR: Please create pw.txt file in the root folder with your Amazon email as the first line, and password as the second line.")
        sys.exit(1)

    email = ""
    password = ""
    lines = f.readlines()
    try:
        email = lines[0]
        password = lines[1]
    except IndexError:
        print("ERROR: Email or password missing in pw.txt")
        sys.exit(1)

    f.close()

    if email.isspace() or password.isspace():
        print("ERROR: Email or password missing in pw.txt")
        sys.exit(1)

    # remove trailing newline chars
    email = email.rstrip('\r\n')
    password = password.rstrip('\r\n')

    driver = webdriver.Chrome()
    driver.get('https://amazon.co.jp')

    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#nav-signin-tooltip > .nav-action-button")))
    element.click()

    email_field = wait.until(EC.presence_of_element_located((By.ID, "ap_email")))
    email_field.send_keys(email)
    email_field.send_keys(Keys.ENTER)

    pw_field = wait.until(EC.presence_of_element_located((By.ID, "ap_password")))
    pw_field.send_keys(password)
    pw_field.send_keys(Keys.ENTER)

    wait.until(EC.presence_of_element_located((By.ID, "nav-orders")))

    while True:
        wait = WebDriverWait(driver, 10)
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.ID, "add-to-wishlist-button-submit")))
        try:
            buy_now = driver.find_element_by_id("buy-now-button")
        except NoSuchElementException:
            print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + " ITEM OUT OF STOCK. REFRESH")
            time.sleep(refresh_interval)
            continue
        else:
            print("ITEM IN STOCK!!! BUY!!!")
            buy_now.click()
            time.sleep(5)
            if '/gp/buy/spc/handlers' in driver.current_url:

                # redirected to checkout page
                print("REDIRECTED TO CHECKOUT PAGE")
                wait2 = WebDriverWait(driver, 10)
                try:
                    checkout_btn = wait2.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "input.place-your-order-button")))
                except TimeoutException:
                    print("CHECKOUT BUTTON NOT FOUND! REFRESH PAGE")
                    continue
                else:
                    print("CHECKOUT!")
                    checkout_btn.click()
                    time.sleep(60)
                    break
            else:
                # shown popup
                print("POPUP SHOWN")

                try:
                    iframe = driver.find_element_by_id('turbo-checkout-iframe')
                    driver.switch_to.frame(iframe)
                    checkout_btn = driver.find_element_by_id("turbo-checkout-pyo-button")
                    checkout_btn.click()
                    time.sleep(60)
                    break
                except Exception as e:
                    print("ERROR CHECKING OUT FROM POPUP! REFRESH PAGE")
                    print(e)
                    continue

