from utils import get_webpage_content, extract_params, process_model_output, filter_json, ai_assistance_error_explaining, ai_assistance_error_fixing
from json5 import loads


if __name__ == "__main__":
    
    print("\033[H\033[J")
    print("AI: what type of bear would you like to search for?")
    print('user: ', end='')
    # user_input = input()
    user_input = "I'm searching for beers with ABV greater than 6%, IBU less than 80, EBC greater than 15, brewed after 01-2025, using yeast named Brettanomyces, hops named Nugget, malt named Chocolate, that go well with fish_and_chips, and named Punk_IPA."
    processed_text = extract_params(user_input)
    processed_text = process_model_output(processed_text)
    processed_text = loads(processed_text)
    processed_text_filtered, errors = filter_json(processed_text)
    while errors != '':
        error_handling_response = ai_assistance_error_explaining(user_input, errors)
        print("AI: " + error_handling_response)
        print('user: ', end='')
        second_input = input()
        processed_text = ai_assistance_error_fixing(str(processed_text), second_input, errors)
        processed_text_filtered, errors = filter_json(loads(process_model_output(processed_text)))
    
    print("AI: congrates you have successfully fixed the invalid parameter:\n", process_model_output(processed_text), processed_text_filtered, errors)

