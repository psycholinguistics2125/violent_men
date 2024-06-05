import pandas as pd
import numpy as np
import os



from src.preprocessing import get_dict_from_file_path, get_text_from_interactions
from src.utils import load_config


def get_df_from_file_list(file_list):
    df = pd.DataFrame(columns=["code", "duration", "interactions", "comments","Q1","Q2","Q3","Q4"])

    for i,file_path in enumerate(file_list):
        df.loc[i] = pd.Series(get_dict_from_file_path(file_path))
    return df

if __name__ =="__main__":

    config = load_config("config.yaml")
    data_folder = config["data"]['folder']
    interview_folder = config["data"]['interview_folder']
    quebec_interview_folder = config["data"]['quebec_interview_folder']
    file_list = [os.path.join(data_folder, interview_folder, file) for file in os.listdir(os.path.join(data_folder, interview_folder)) if file.endswith(".docx")]
    quebec_file_list = [os.path.join(data_folder, quebec_interview_folder, file) for file in os.listdir(os.path.join(data_folder, quebec_interview_folder)) if file.endswith(".docx") ]
    df = get_df_from_file_list(file_list)
    df['source'] = "france"
    df_quebec = get_df_from_file_list(quebec_file_list)
    df_quebec['source'] = "quebec"

    # concatenate the two dataframes
    df = pd.concat([df, df_quebec]).reset_index(drop=True)



    df['text'] = df['interactions'].apply(lambda x: get_text_from_interactions(x))
    for col in ["Q1","Q2","Q3","Q4"]:
        df[f"text_{col}"] = df[col].apply(lambda x: get_text_from_interactions(x))
    df.to_hdf(os.path.join(data_folder, "20240227_text_database.h5"), key="df")