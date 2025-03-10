import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from src.data_handling.input import get_timestamped_jpeg_paths
from src.data_handling.processing import ocr
from src.utils.form import (
    click_element,
    fill_text_field,
    select_dropdown_field,
    upload_attachments,
    wait_seconds,
)
from src.utils.ui import status_print, StatusLevel


def _accepting_terms(driver):
    """
    Accept the terms and conditions of the form.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance
    """
    # Remove status print - parent function will handle this

    # Navigate to the terms and conditions page
    driver.get("https://policemail.kcg.gov.tw/Statement.aspx")

    # Wait for page to load
    WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "#ContentPlaceHolder1_chk1"))
    )

    # Click all required checkboxes to accept terms
    click_element(driver, "#ContentPlaceHolder1_chk1")
    click_element(driver, "#ContentPlaceHolder1_chk2")
    click_element(driver, "#ContentPlaceHolder1_chk3")
    click_element(driver, "#ContentPlaceHolder1_chk4")

    # Proceed to the next page
    click_element(driver, "#ContentPlaceHolder1_IWantToReport")

    # Wait for the next page to load by checking for the name field
    WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "#ContentPlaceHolder1_Name"))
    )


def _fill_personal_info(driver, personal_info):
    """
    Fill the personal information fields on the form.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance
        personal_info (object): Object containing the user's personal information
    """
    # Remove status print - parent function will handle this

    # Fill all personal info fields without individual status updates
    fill_text_field(driver, "#ContentPlaceHolder1_Name", personal_info.name)
    fill_text_field(driver, "#ContentPlaceHolder1_txtCardID", personal_info.ssn)
    fill_text_field(
        driver, "#ContentPlaceHolder1_ucsAddress_txtAddress", personal_info.home_address
    )
    fill_text_field(driver, "#ContentPlaceHolder1_EMail", personal_info.email)
    fill_text_field(driver, "#ContentPlaceHolder1_Phone", personal_info.phone)


def _fill_incident_details(driver, report_data):
    """
    Fill the incident details on the form, including images, location, vehicle info,
    violation details, and solve the CAPTCHA.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance
        report_data (object): Object containing incident report data
    """
    # Remove individual status prints for each form section
    image_paths = get_timestamped_jpeg_paths()
    upload_attachments(driver, "#ContentPlaceHolder1_fl_File", image_paths)
    click_element(driver, "#ContentPlaceHolder1_btnMailFile")
    wait_seconds(driver, 5)

    # Fill location
    fill_text_field(
        driver,
        "#ContentPlaceHolder1_uscPlace_txtAddress",
        report_data.incident_address["formatted_address"],
    )

    # Fill time
    fill_text_field(
        driver, "#ContentPlaceHolder1_ViolationDate", report_data.incident_datetime
    )

    # Fill vehicle information
    fill_text_field(driver, "#ContentPlaceHolder1_LicenseNo", report_data.licence_first)
    fill_text_field(
        driver, "#ContentPlaceHolder1_LicenseNo2", report_data.licence_second
    )
    click_element(driver, f"#ContentPlaceHolder1_rblCarType_{report_data.vehicle_type}")

    # Fill violation details
    # Use JavaScript to fill the multiline text field
    driver.execute_script(
        'document.querySelector("#ContentPlaceHolder1_Content").value = arguments[0]',
        report_data.complaint_description,
    )
    select_dropdown_field(
        driver, "#ContentPlaceHolder1_ViolationArea", report_data.police_station
    )
    select_dropdown_field(
        driver,
        "#ContentPlaceHolder1_ddlViolationEventCategory",
        report_data.category_parent,
    )
    select_dropdown_field(
        driver, "#ContentPlaceHolder1_TitleDropDownList", report_data.category_child
    )


def _submit_report(driver):
    """
    Submit the report form.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance
    """
    # Remove intermediate status prints
    captcha_img = WebDriverWait(driver, 5).until(
        ec.presence_of_element_located(
            (By.CSS_SELECTOR, "#ContentPlaceHolder1_imgCaptcha")
        )
    )

    img_src = captcha_img.get_attribute("src")
    captcha_text = ocr(requests.compat.urljoin(driver.current_url, img_src))
    fill_text_field(driver, "#ContentPlaceHolder1_txtCode", captcha_text)

    # Click submit
    click_element(driver, "#ContentPlaceHolder1_IWantToSympathetic")
    wait_seconds(driver, 5)

    # Check for successful submission by looking for the Continue button
    try:
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, "#ContentPlaceHolder1_Continue")
            )
        )
    except:
        raise Exception("Report submission failed")


def auto_report(personal_info, report_data):
    """
    Automate the entire reporting process from start to finish.

    Args:
        personal_info (object): Object containing the user's personal information
        report_data (object): Object containing incident report data

    Returns:
        bool: True if the report was submitted successfully, False otherwise
    """
    status_print("Submitting report to authorities...", StatusLevel.INFO)
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)

    try:
        _accepting_terms(driver)
        _fill_personal_info(driver, personal_info)
        _fill_incident_details(driver, report_data)
        _submit_report(driver)
        status_print("Report submitted successfully", StatusLevel.SUCCESS)

    except Exception as e:
        status_print(f"Error during reporting: {e}", StatusLevel.ERROR)
        raise e

    finally:
        # Clean up
        wait_seconds(driver, 30)
        driver.quit()
