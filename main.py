from utils import get_webpage_content, extract_params, process_model_output, filter_json
from utils import ai_assistance_error_explaining, ai_assistance_error_fixing, ai_assistance_summarize_beer
from json5 import loads
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

if __name__ == "__main__":

    print("\033[H\033[J")
    class Colors:
        USER = '\033[94m'  # blue
        AI = '\033[92m'    # green
        REQUEST = '\033[91m'    # red
        RESULT = '\033[93m'    # yellow
        END = '\033[0m'    # end color

    print(f"{Colors.AI}AI: what type of bear would you like to search for?{Colors.END}")
    print(f"{Colors.USER}USER: {Colors.END}", end='')
    user_input = input()
    counter = 0
    max_try_count = 3
    while counter < max_try_count:
        try:
            print(f"{Colors.AI}AI: I'm processing your request. Trying {counter + 1} out of {max_try_count}.{Colors.END}")
            processed_text_0 = extract_params(user_input)
            processed_text_1 = process_model_output(processed_text_0)
            processed_text_2 = loads(processed_text_1)
            processed_text_filtered, errors = filter_json(processed_text_2)
            while len(errors) > 0:
                counter = 0
                error_handling_response = ai_assistance_error_explaining(
                    user_input, errors)
                print(f"{Colors.AI}AI: " + error_handling_response + f"{Colors.END}")
                print(f"{Colors.USER}USER: {Colors.END}", end='')
                second_input = input()
                processed_text = ai_assistance_error_fixing(
                    processed_text_1, second_input, errors)
                processed_text_filtered, errors = filter_json(
                    loads(process_model_output(processed_text)))
            counter = max_try_count

        except Exception as e:
            counter += 1
            if counter == max_try_count:
                print("{Colors.AI}AI: I'm sorry, I didn't understand that. Please try another input.{Colors.END}")
                print(e)
                print(processed_text_0)
                print(processed_text_1)
                print(processed_text_2)
                print(processed_text_filtered)
                exit()

    query_string = "&".join(
        [f"{key}={value}" for key, value in processed_text_filtered.items()] + [f"per_page={80}"])
    api_call_list = []
    counter = 1
    state = True
    while state:
        try:
            URL = "https://api.punkapi.com/v2/beers?" + \
                query_string + f"&page={counter}"
            print(f"{Colors.REQUEST}AI: I'm making an API call to {URL}.{Colors.END}")
            content = get_webpage_content(URL)
            content = loads(content)
            if content == []:
                state = False
                break

            api_call_list.append(content)
            if len(content) < 80:
                state = False
                break

            counter += 1

        except Exception as e:
            print(e)
            break

    api_call_list_flattened = [
        item for sublist in api_call_list for item in sublist]

    keys_to_keep = ["beer_name", "yeast", "hops", "malt", "food"]
    keywords = [processed_text_2[key] for key in processed_text_2 if key in keys_to_keep]
    
    beer_descriptions = [str(description) for description in api_call_list_flattened]

    # join keywords into a single string
    keywords_string = ' '.join(keywords)

    # add it to the beer descriptions
    texts = beer_descriptions + [keywords_string]

    # initialize TfidfVectorizer
    vectorizer = TfidfVectorizer()

    # fit and transform the vectorizer on texts
    tfidf_matrix = vectorizer.fit_transform(texts)

    # calculate cosine similarity
    cosine_similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])

    # print beers with their similarity scores
    beer_list = []
    score_list = []
    for i, score in enumerate(cosine_similarities[0]):
        beer_list.append(api_call_list_flattened[i])
        score_list.append(score)

    df = pd.DataFrame({"Beer": beer_list, "Score": score_list}).sort_values(by="Score", ascending=False)
    df = df[df["Score"] > 0.0]
    if df.empty == True:
        print(f"{Colors.AI}AI: I'm sorry, I couldn't find any beers that match your request or I don't have enough data to make a recommendation.{Colors.END}")
        
    else:
        print(f"{Colors.AI}AI: I found the following beers that match your request:{Colors.END}")
        print("")
        non_zero_score_count = df.shape[0]
        min_count = min(non_zero_score_count, 3)
        for indx in range(min_count):
            print(f"{Colors.RESULT}Beer: {df.iloc[indx]['Beer']['name']}{Colors.END}")
            print(f"{Colors.RESULT}Score: {df.iloc[indx]['Score']}{Colors.END}")
            print(f"{Colors.RESULT}Description: {ai_assistance_summarize_beer(str(df.iloc[indx]['Beer']))}{Colors.END}")
            print("")

