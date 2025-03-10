import time
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from typing import List

DEFAULT_ELEMENT_WAIT_TIME: float = 2.5


def wait_seconds(driver: WebDriver, seconds: float = DEFAULT_ELEMENT_WAIT_TIME) -> None:
    time.sleep(seconds)


def wait_for_element(driver: WebDriver, selector: str) -> WebDriver:
    return WebDriverWait(driver, DEFAULT_ELEMENT_WAIT_TIME).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, selector))
    )


def fill_text_field(driver: WebDriver, selector: str, value: str) -> None:
    element = wait_for_element(driver, selector)
    element.clear()
    element.send_keys(value)
    wait_seconds(driver, DEFAULT_ELEMENT_WAIT_TIME)


def select_dropdown_field(driver: WebDriver, selector: str, value: str) -> None:
    element = wait_for_element(driver, selector)
    for option in element.find_elements(By.TAG_NAME, "option"):
        if option.get_attribute("value") == value:
            option.click()
            break
    wait_seconds(driver, DEFAULT_ELEMENT_WAIT_TIME)


def upload_attachments(driver: WebDriver, selector: str, file_paths: List[str]) -> None:
    element = wait_for_element(driver, selector)
    element.send_keys("\n".join(file_paths))
    wait_seconds(driver, DEFAULT_ELEMENT_WAIT_TIME)


def click_element(driver: WebDriver, selector: str) -> None:
    element = wait_for_element(driver, selector)
    element.click()
    wait_seconds(driver, DEFAULT_ELEMENT_WAIT_TIME)
