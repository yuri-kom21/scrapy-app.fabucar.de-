from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import csv
import json


from api import api_get_items, api_get_details, fetch_all_posts

# Create a new instance of the Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))  # or webdriver.Firefox()

def select_by_keys(list_obj, keys):
    return [
        {key: record[key] for key in keys if key in record}
        for record in list_obj
    ]

try:
    # Navigate to a page
    driver.get("https://app.fabucar.de/beitraege")

    # Use execute_script() to run JavaScript
    js_code = "return document.title;"  # Example: getting the page title
    title = driver.execute_script(js_code)
    print(f"Page title is: {title}")
    cookies = driver.execute_script("return document.cookie;")
    print(cookies)

    # Manipulate elements using JavaScript
    # For example, fetching data from an API
    
    res = fetch_all_posts(cookies)
    print("Done fetching")
    list_data = [
        {
            "id": list_item["id"],
            "title": list_item["title"],
            "user_input": list_item["message"],
            "already_checked": list_item["already_tested_description"],
            "category": list_item["categories"],
            "error_codes": list_item["error_codes"],
            "car_title": f'{list_item["car_data"].get("manufacturer", "")} {list_item["car_data"].get("model", "")}'
        } for list_item in res if len(list_item["id"]) > 4
    ]

    final_list = list()

    for index, item in enumerate(list_data):
        print(f"Processing item {index + 1}")
        details = api_get_details(cookies, item["id"])
        solution = {}
        solved_flag = False
        if(type(details) is str):
            continue
        else:
            for index, detail in enumerate(details["posts"]):
                if detail["is_solution"]:
                    solution["cited_message"] = details["posts"][index - 1] if index > 1 else {}
                    solution["solution_comment"] = details["posts"][index]
                    solved_flag = True
                    break
        if not solved_flag:
            continue

        item["solutions"] = {}
        cited_message = select_by_keys(
            [solution["cited_message"]], 
            ["author_username", "message"]
            )
        item["solutions"]["cited_message"] = cited_message[0] if len(cited_message) > 0 else {}
        
        solution_comment = select_by_keys(
            [solution["solution_comment"]], 
            ["author_username", "message"]
            )
        item["solutions"]["solution_comment"] = solution_comment[0] if len(solution_comment) > 0 else {}
        # print(item["post"])
        final_list.append(item)

   # Specify the filename
    filename = 'data.json'

    # Open a file for writing
    with open(filename, 'w') as json_file:
        # Use json.dump to write the data
        json.dump(final_list, json_file, indent=4)  # indent=4 for pretty printing

   
finally:
    # Close the browser
    driver.quit()