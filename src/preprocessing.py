
import pandas as pd
import docx

import re

def get_interactions_from_content(content):
    interactions_list = []
    for line in content:
        if len(line) > 0:
            line = line.strip()
            if line.startswith("EXP") or line.startswith("EPX"):
                speaker = "experimenter"
                text = "".join(line.split(":")[1:])
            elif line.startswith("NAR"):
                speaker = "narrator"
                text = "".join(line.split(":")[1:])
            else:
                continue
            
            interaction = {"speaker":speaker, "text":text,}
        
            interactions_list.append(interaction)
    return interactions_list


def get_code_from_file_path(file_path):
    return file_path.split("/")[-1].split(".")[0]

def get_duration_from_content(content):
    pattern = r'(\d+)\s*min\s*(\d+)'
    text = " ".join(content[:3])
    # Use re.search to find the first match in the text
    match = re.search(pattern, text)
    if match == None:
        pattern = r'(\d+)\s*min\s*'
        match = re.search(pattern, text)
        if match == None:
            return None
        minutes = int(match.group(1))
        seconds = 0
        
    else :
        try :
            minutes = int(match.group(1))
            seconds = int(match.group(2))
        except :
            minutes = 0
            seconds = 0
    print(f"{minutes} minutes and {seconds} seconds")
    return minutes*60 + seconds

def get_comments_from_content(content):
    comments = []
    for line in content:
        if len(line) == 0:
            continue
        if line.startswith("EXP") or line.startswith("NAR") or line.startswith("EPX"):
            continue
        else :
            comments.append(line)
    return comments

def get_dict_from_file_path(file_path):
    code = get_code_from_file_path(file_path)
    my_doc = docx.Document(file_path)
    content = [p.text for p in my_doc.paragraphs]
    interactions = get_interactions_from_content(content)
    questions_dict = split_interaction_by_questions(interactions)
    duration = get_duration_from_content(content)
    comments = get_comments_from_content(content)
    basic_dict = {"code":code, "interactions":interactions, "duration":duration, "comments":comments}
    final_dict = {**basic_dict, **questions_dict}
    return final_dict


def split_interaction_by_questions(interaction_list):
    result_dict = {f"Q{i}": [] for i in range(1, 5)}

    current_keyword = None
    current_list = None

    for interaction in interaction_list:
        if interaction["speaker"] == "experimenter":
            for keyword in ["Q1", "Q2", "Q3", "Q4"]:
                if keyword in interaction["text"]:
                    current_keyword = keyword
                    current_list = result_dict[keyword]
                    break

        if current_keyword is not None:
            current_list.append(interaction)
        elif current_list is not None:
            current_list.append(interaction)

    return result_dict


def get_text_from_interactions(interactions, speaker = "narrator"):
    return "\n".join([interaction["text"] for interaction in interactions if interaction["speaker"] == speaker])



def count_elements(text, elements_list):
    element_count = {}
    total_count = 0
    
    for element in elements_list:
        count = text.count(element)
        total_count += count
        element_count[element] = count
    
    return total_count



co_que = ["pis","disons","là","mettons","fait que","faque","genre","ben","hein","tu sais","tsé","admettons","faque","fait que","là","t'sais","tsé","tu sais","admettons","dans le fond","anyway","whatever","tantôt","coudon","voyons"]

co_fr = ["mais", "donc","aussi","parce que","et","de plus","puis","en outre","non seulement",
"mais encore","de surcroît","ainsi que","également","quand","lorsque","avant que","après que",
"alors que","dès lors que","depuis que","tandis que","en même temps que","pendant que","au moment où",
"à savoir", "c'est-à-dire", "soit", "je veux dire", "je précise"]

def add_special_features(data): 
    for source in ['Q1',"Q2","Q3","Q4","text"]:
        for key, value in {"silent_break":['PS'], 
                           "filled_break": ["HUM" ,"EUH", "BEH", "BAH", "BIN", "BEN", "HEU"], # à changer 
                           "incomplete_sentence":['/'],
                            "incomplete_word": ['_'],
                            "long_vowell": ['ALL'],
                            "connecteur" : co_fr + co_que,
                            "non_understandable":['xxx']}.items():
            data[source+"_"+key] = data[source+"_token"].apply(lambda x: count_elements(x,value))/data[source+"_token"].apply(len)*100
    return data