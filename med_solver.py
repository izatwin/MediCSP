from selenium import webdriver
from selenium.webdriver.common.by import By
import argparse
from csp import CSP
import pandas as pd


PREFIX = "https://go.drugbank.com/conditions/"
FILTER_NAME = "data/filtered_data.csv"


def _start_driver(link, browser="Firefox"):
    if browser == "Firefox":
        driver = webdriver.Firefox()
    elif browser == "Chrome":
        driver = webdriver.Chrome()
    else:
        raise ValueError("Invalid browser")
    driver.minimize_window()
    driver.get(link)
    return driver


def _stop_driver(driver):
    if driver:
        driver.quit()


def _get_condition_name(driver):
    page_title = driver.title

    return page_title.split(" (")[0]


def _get_full_drug_list(driver, condition):
    elements = driver.find_elements(
        By.XPATH, "/html/body/main/div/div[3]/dl[2]/dd[1]/table/tbody/tr[*]/td[1]/a"
    )

    drug_names = [e.text for e in elements]
    drug_ids = [e.get_attribute("href").split("/")[-1] for e in elements]

    return drug_names, drug_ids


# use this function
def get_full_drug_list(condition, browser="Firefox"):
    driver = _start_driver(PREFIX + condition, browser)

    drug_names, drug_ids = _get_full_drug_list(driver, condition)

    _stop_driver(driver)

    return drug_names, drug_ids


# run as script to test
def main():
    parser = argparse.ArgumentParser(
        description="Get a list of drugs indicated for a given condition"
    )
    parser.add_argument(
        "conditions", 
        type=str, 
        nargs="+", 
        help="Drugbank condition IDs (space-separated for multiple conditions)"
    )
    parser.add_argument(
        "--driver",
        "-d",
        type=str,
        help="Browser to use - Firefox or Chrome",
        default="Firefox",
        choices=["Firefox", "Chrome"],
    )

    args = parser.parse_args()

    prescriptions = {}

    for condition in args.conditions:
        print(f"\nProcessing condition: {condition}")
        driver = _start_driver(PREFIX + condition, args.driver)
        condition_name = _get_condition_name(driver)
        drug_names, drug_ids = _get_full_drug_list(driver, condition)
        _stop_driver(driver)

        print(f"\nCondition: {condition_name} ({condition})\n")
        for name, db_id in zip(drug_names, drug_ids):
            print(f"{name} ({db_id})")

        prescriptions[condition_name] = drug_names

    data = pd.read_csv(FILTER_NAME)

    print("\n")
    csp = CSP(data, prescriptions)
    csp.find_solution()




if __name__ == "__main__":
    main()