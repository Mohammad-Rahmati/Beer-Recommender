import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import openai

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

def summarize_text(title: str, input_text: str) -> str:
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are ChatGPT, a large language model trained by OpenAI to summarize text in markdown format.",
            },
            {
                "role": "user",
                "content": "Generate a title as header and provide 10 bullet points short sentences \\\
                to summarize the following content in markdown format:" + input_text,
            },
        ],
    )

    summary = completion.choices[0]["message"]["content"]
    return summary