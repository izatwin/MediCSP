import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Constants
LETTERS = ['A', 'B', 'D', 'H', 'L', 'P', 'R', 'V']
PREFIX = "https://go.drugbank.com/conditions/"

# Load DDInter data
def load_ddinter_data():
    """
    Load and combine DDInter data for all categories.
    """
    ddi_dfs = []
    for letter in LETTERS:
        ddi_dfs.append(pd.read_csv(f'data/ddinter_downloads_code_{letter}.csv'))
    ddi_data = pd.concat(ddi_dfs)
    ddi_data = ddi_data[ddi_data['Level'] != 'Unknown']
    print("\n\nHead of DDI Data\n", ddi_data.head())
    return ddi_data

# Selenium-based scraper
def _start_driver(link, browser="Firefox"):
    """
    Start a Selenium web driver session.
    """
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
    """
    Stop a Selenium web driver session.
    """
    if driver:
        driver.quit()

def search_condition(condition, browser="Firefox"):
    """
    Search for a condition on DrugBank and return the first result's URL.
    """
    driver = _start_driver("https://go.drugbank.com/", browser)
    try:
        # Search for the condition
        search_box = driver.find_element(By.NAME, "query")
        search_box.send_keys(condition)
        search_box.send_keys(Keys.RETURN)
        time.sleep(2)  # Wait for search results to load
        
        # Click the first condition link
        first_result = driver.find_element(By.XPATH, "//a[contains(@href, '/conditions/')]")
        condition_url = first_result.get_attribute("href")
    except Exception as e:
        print("Error during condition search:", e)
        condition_url = None
    finally:
        _stop_driver(driver)
    
    return condition_url

def _get_full_drug_list(driver):
    """
    Extract drug names and IDs from the webpage.
    """
    elements = driver.find_elements(By.XPATH, "/html/body/main/div/div[3]/dl[2]/dd[1]/table/tbody/tr[*]/td[1]/a")
    drug_names = [e.text for e in elements]
    drug_ids = [e.get_attribute("href").split("/")[-1] for e in elements]
    return drug_names, drug_ids

def fetch_drugs_for_condition(condition_name, browser="Firefox"):
    """
    Fetch a list of drugs for a given condition name using Selenium.
    """
    condition_url = search_condition(condition_name, browser)
    if not condition_url:
        print(f"No results found for condition: {condition_name}")
        return [], []

    print(f"Condition URL: {condition_url}")
    driver = _start_driver(condition_url, browser)
    drug_names, drug_ids = _get_full_drug_list(driver)
    _stop_driver(driver)
    return drug_names, drug_ids

# Filter interactions from DDInter dataset
def filter_interactions(ddinter, selected_drugs):
    """
    Filter out drug pairs with 'major' interactions.
    """
    for i in range(len(selected_drugs)):
        for j in range(i + 1, len(selected_drugs)):
            drug1, drug2 = selected_drugs[i], selected_drugs[j]
            interaction = ddinter[
                ((ddinter['Drug1_ID'] == drug1) & (ddinter['Drug2_ID'] == drug2)) |
                ((ddinter['Drug1_ID'] == drug2) & (ddinter['Drug2_ID'] == drug1))
            ]
            if not interaction.empty and interaction.iloc[0]['Level'] == "Major":
                return False
    return True

# CSP Backtracking solver
def csp_solver(drugs, ddinter):
    """
    Solve the CSP using backtracking.
    """
    def backtrack(assignment):
        # Check if all variables are assigned
        if len(assignment) == len(drugs):
            return assignment
        
        # Select next variable (drug)
        for drug in drugs:
            if drug not in assignment:
                # Try adding this drug
                new_assignment = assignment + [drug]
                if filter_interactions(ddinter, new_assignment):
                    result = backtrack(new_assignment)
                    if result:
                        return result
        return None
    
    return backtrack([])

# Main function to integrate all components
def main():
    # Load DDInter data
    ddi_data = load_ddinter_data()

    # Input the condition name
    condition_name = input("Enter condition name: ")

    # Fetch drugs for the condition
    print(f"Fetching drugs for condition: {condition_name}")
    drug_names, drug_ids = fetch_drugs_for_condition(condition_name)

    if not drug_names:
        print("No drugs found for the given condition.")
        return

    print(f"Fetched {len(drug_ids)} drugs for condition {condition_name}.")

    # Solve the CSP
    print("Solving the CSP to select a valid subset of drugs...")
    solution = csp_solver(drug_ids, ddi_data)

    if solution:
        print("\nSolution found:")
        for drug_id in solution:
            print(drug_id)
    else:
        print("\nNo valid solution exists.")

if __name__ == "__main__":
    main()
