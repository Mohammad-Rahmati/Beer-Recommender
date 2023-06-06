import requests
from bs4 import BeautifulSoup
import json
from datetime import date
import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

today = date.today()
current_year = today.year
current_month = today.month

def extract_params(input_text: str) -> str:
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a text processing model and extracting the following API parameters and providing concise and specific answers.\n\\\
                    You are converting natural language text into parameters suitable for the following API: https://api.punkapi.com/v2/beers\n\\\
                "
            },
            {
                "role": "user",
                "content": "Given the following rules, summarize the text by extracting the API parameters and present them in JSON-like {Param: value} format \\\
                    without any additional text or any further explanation,\n\\\
                    You are converting natural language text into parameters only mentioned in the following:\n\\\
                    abv_gt is a number and means beers with ABV greater than the supplied number,\n\\\
                    abv_lt is a number and means beers with ABV less than the supplied number,\n\\\
                    ibu_gt is a number and means beers with IBU greater than the supplied number,\n\\\
                    ibu_lt is a number and means beers with IBU less than the supplied number,\n\\\
                    ebc_gt is a number and means beers with EBC greater than the supplied number,\n\\\
                    ebc_lt is a number and means beers with EBC less than the supplied number,\n\\\
                    brewed_before is a mm-yyyy format date and means beers brewed before this date,\n\\\
                    brewed_after is a mm-yyyy format date and beers brewed after this date,\n\\\
                    beer_name is a string and means the name of the bear,\n\\\
                    yeast is a string and means the yeast name,\n\\\
                    hops is a string and means the hops type,\n\\\
                    malt is a string and means the malt name,\n\\\
                    food is a string and means what goes well with bear\n\\\
                    The output parameters only include abv_gt, abv_lt, ibu_gt, ibu_lt, ebc_gt, ebc_lt, brewed_before, brewed_after, beer_name, yeast, hops, malt, food.\n\\\
                    Pay extra attention to the text to detect if any part of the text mentions brewed after parameter.\n\\\
                    If the date is not mentioned return None,\n\\\
                    If the date is mentioned relative to the current date, return the correct date in mm-yyyy format,\n\\\
                    If the input text mention any of the parameters, but does not provide a correct value such as number of date, do not include it in the output.\n\\\
                    If the input is not presents for a specific parameter do not include it in the output." + "Today date is" + str(today) + ". Here is the text:" + input_text
            },
        ],
        temperature=0.05,
    )

    model_output = completion.choices[0]["message"]["content"]
    return model_output

def ai_assistance_error_explaining(input_text: str, error_text: str) -> str:
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistance that helps users to find the error in the input and help them to identify the error.\n\\\
                "
            },
            {
                "role": "user",
                "content": "First mention there is an error in the input. Then explain the error in the input and help the user to identify it/them in one or two short sentence." + error_text + "Here is the text:" + input_text  
            },
        ],
        temperature=0.05,
    )

    model_output = completion.choices[0]["message"]["content"]
    return model_output

def ai_assistance_error_fixing(input_text: str, second_input: str, error_text: str) -> str:
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistance that fixes the invalid parameters based on user input. Provide only concise and specific answers.\n\\\
                "
            },
            {
                "role": "user",
                "content": "Consider this text: " + input_text + "\n This text has the following invalid parameter" + error_text + 
                "\n Here is a text to fix the invalid parameter: " + second_input + "\nFix the invalid parameter based on the feedback with minimum change." +
                "Only modify the following text based on the feedback and the error adn return teh modified and corrected version:" + input_text
            },
        ],
        temperature=0.05,
    )

    model_output = completion.choices[0]["message"]["content"]
    return model_output

def process_model_output(input_text: str) -> str:
    model_output = input_text.split("{")[1].split("}")[0]
    return "{" + model_output + "}"


def filter_json(sample: json) -> json:
    try:
        error_string = ''
        json_input = sample
        keys_to_keep = ["abv_gt", "abv_lt", "ibu_gt", "ibu_lt",
                        "ebc_gt", "ebc_lt", "brewed_before", "brewed_after"]
        json_input = {key: json_input[key] for key in json_input if key in keys_to_keep and json_input[key] not in [
            None, "", " ", "  ", "   "]}
        # check the numeric values are numbers and are in the correct range
        for num_key in ["abv_gt", "abv_lt", "ibu_gt", "ibu_lt", "ebc_gt", "ebc_lt"]:
            if num_key in json_input:
                try:
                    float(json_input[num_key])
                except:
                    error_string += "Error: Invalid number format, " + num_key + " is not a number\n"
                if float(json_input[num_key]) < 0:
                    error_string += "Error: Invalid number format, " + num_key + " is below 0\n"
        # check abv_gt or abv_lt is below 100
        if "abv_gt" in json_input and float(json_input["abv_gt"]) > 100:
            error_string += "Error: Invalid number format, abv_gt is above 100\n"
        if "abv_lt" in json_input and float(json_input["abv_lt"]) > 100:
            error_string += "Error: Invalid number format, abv_lt is above 100\n"
        # check ibu_gt or ibu_lt is below 1000
        if "ibu_gt" in json_input and float(json_input["ibu_gt"]) > 150:
            error_string += "Error: Invalid number format, ibu_gt is above 150\n"
        if "ibu_lt" in json_input and float(json_input["ibu_lt"]) > 150:
            error_string += "Error: Invalid number format, ibu_lt is above 150\n"


        for date_key in ["brewed_before", "brewed_after"]:
            if date_key in json_input:
                split_date = json_input[date_key].split("-")
                if len(split_date) != 2 or len(split_date[0]) != 2 or len(split_date[1]) != 4:
                    error_string += "Error: Invalid date format, " + date_key + " is not in mm-yyyy format\n"
                elif int(split_date[0]) > 12:
                    error_string += "Error: Invalid date format, " + date_key + " has an invalid month and it should be in mm-yyyy format\n"
                elif int(split_date[1]) > current_year and int(split_date[0]) == current_month:
                    error_string += "Error: Invalid date format, " + date_key + " is in the future and it should be in mm-yyyy format\n"
                elif int(split_date[0]) > current_month and int(split_date[1]) == current_year:
                    error_string += "Error: Invalid date format " + date_key + " is in the future and it should be in mm-yyyy format\n"
                elif int(split_date[1]) > current_year:
                    error_string += "Error: Invalid date format, " + date_key + " is in the future and it should be in mm-yyyy format\n"
                # check if the mm and yyyy are numbers
                try:
                    int(split_date[0])
                    int(split_date[1])
                except:
                    error_string += "Error: Invalid date format, " + date_key + " is not a number and it should be in mm-yyyy format\n"

        return json_input, error_string

    except Exception as e:
        return json_input, e

def get_webpage_content(url):
    try:
        response = requests.get(url, timeout=5)
        # Check if the request was successful
        response.raise_for_status()
    except requests.RequestException as err:
        print(f"Request Error: {err}")
        return None
    except requests.Timeout as err:
        print(f"Timeout Error: {err}")
        return None
    except requests.TooManyRedirects as err:
        print(f"TooManyRedirects Error: {err}")
        return None
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
        return None

    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get the text
    text = soup.get_text()

    return text