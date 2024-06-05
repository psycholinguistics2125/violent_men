import yaml
import os
import pandas as pd

from src.preprocessing import add_special_features


def load_config(config_path):
    with open(config_path, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config


import re

def remove_text_inside_parentheses(text):
    return re.sub(r'\s*\([^)]*\)', '', text)

def load_data(config):
    text_database_path = os.path.join(config["data"]["folder"], config["data"]["text_database"])
    df = pd.read_hdf(text_database_path, key="df")
    df = df.drop(columns = ["source"])
    #df['code'] = df['code'].apply(lambda x: x.split('_')[1])#

    metadata_path = os.path.join(config["data"]["folder"], config["data"]["metadata_file"])
    metadata_df = pd.read_csv(metadata_path,sep = "\t")

    df = df.merge(metadata_df, on="code")
    df = df.rename(columns=lambda x: x.strip())
    try : 
        df = df.drop(columns = ["Unnamed: 0"])

    except :
        pass
    try :
        df['ABS_PRE_DISSOCIATION'] = df['ABS_PRE_DISSOCIATION'].apply(lambda x: int(x))
    except :
        pass


    
    return df

def load_merged_features(config):
    df = load_data(config)
    for source in ['Q1','Q2','Q3','Q4',"text"]:
       # loading and merging features
       feature_name = f"sentiment_passive_graph_morph_tag_dysfluences_custom_ner_{source}_features.csv"
       features_path = os.path.join(config["data"]["folder"], config["data"]["features_folder"], feature_name)
       features_df = pd.read_csv(features_path,sep="\t",index_col=0 )
       features_df['code'] = features_df['code'].apply(lambda x: remove_text_inside_parentheses(x.split('_')[1]).replace("EXCLUS","").strip())
       features_df = features_df.rename(columns=lambda x: f"{source}_"+x.strip() if x !="code" else x)
       df = df.merge(features_df, on="code")

       # loading and merging text data
       text_name = f"text_{source}_spacy_trf_nlp_data.pkl"
       text_path = os.path.join(config["data"]["folder"], config["data"]["nlp_folder"], text_name)
       text_df = pd.read_pickle(text_path)
       text_df['code'] = text_df['id'].apply(lambda x: remove_text_inside_parentheses(x.split('_')[1]).replace("EXCLUS","").strip())
       text_df = text_df.rename(columns=lambda x: f"{source}_"+x.strip() if x !="code" else x)
       df = df.merge(text_df, on="code")

     


    #add features fot this dataset
    df = add_special_features(df)

    df["TRAUMATIC_SYMPTOMS_enc"] = df["TRAUMATIC_SYMPTOMS"].apply(encode_traumatic_symptoms)
    df["PROFILS"] = df["PROFILS"].fillna(0)
    df["CRITERE_A"] = df["CRITERE_A"].apply(lambda x: 2 if "?" in x else x)

    # add special diag
    diag = pd.read_excel('/home/robin/Data/Etude_telma/Critère_Analyse_Psycholinguistique_Q1_avril_2024.xlsx',sheet_name='Catégorie')
    diag["code"] = diag['Unnamed: 0'].apply(lambda x : x.strip())
    diag = diag.drop(columns=['Unnamed: 0'])
    df = df.merge(diag[['PCL_REVI_DISSO', "PCL_REVIVISCENCES","PCL_DISSO","TOTAL_PCL","TOTAL_DES","code","PA_Q2"]], on = "code")

    return df


dict_cols = {"Même réponse Q1 et Q3 ( 2 oui (tout ce qui a trait à leur femme) / 1 violence sur la conjointe + autres évènements cités à la Q1 / 0 non)":"Q1vsQ3",
             "DES_HYPERVIGILANCE": "DES_HYPERVIGILANCE",
             "DES_FASHBACK": "DES_FLASHBACKS",
             "DES_DISSOFLASHBACK": "DES_DISSOFLASHBACKS",
             "DES_DISSOCIATION": "DES_DISSOCIATION",
             "Profils": "PROFILS",
             "Traumatisme lié au passage à l'acte (violence, incarcération, perte de la garde, GAV) (1) / Traumatisme à l'enfance ou l'âge adulte (2)":"TRAUMA_ORIGINE",
             '"Trauma"': "TRAUMA_ORIGINE_DETAILS",
             "Trauma de la PCLS":"TRAUMA_RELATED_PCLS",
             "Attachement":"ATTACHEMENT",
             "Motif du PA - Q3":"MOTIF_PA",
             "Q1 - Trauma":"TRAUMA_Q1",
             "Analyse textuel très intuitive… cliniquement":"ANALYSE_TEXTUEL_YANN",
             "Emotions négatives":"EMOTIONS_NEGATIVES",
             "Violence extra-conjugale":"VIOLENCE_EXTRA_CONJUGALE",
             "Dissociaition (1) /Absence de dissociation (0)": "DISSOCIATION",
             "Risque suicidaire": "SUICIDE_RISK",
             "Symptôme dissociatif": "DISSOSIATION_SYMPTOMS",
             "Multiplicité":"MULTIPLICITY",
             "Symptôme traumatique":"TRAUMATIC_SYMPTOMS",
             "Exposition traumatique ( 1oui / 0 non)": "CRITERE_A",
             "Unnamed: 0": "code",
             "Consommation":"CONSOMMATION"
             }

def encode_traumatic_symptoms(x):
    if x.lower() == "pas de tspt":
        return 0
    elif x.lower() == "tspt":
        return 2
    elif x.lower() == "dimensions anxieuses et dépressives":
        return 1
    else :
        return 3


