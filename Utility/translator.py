from googletrans import Translator
import pandas as pd
import seaborn as sns
import math
import json

disease_df = pd.read_json('Data/medical.json', lines=True, encoding='utf8')[553:1000]
translated_df = pd.DataFrame(columns=disease_df.columns)
translator_obj = Translator()

dictionary_map = dict()
index = 0
for col in disease_df.columns:
    dictionary_map[index] = col
    index += 1

file = open("dataset.json", "a")

error_count = 1
for index, row in disease_df.iterrows():
    print("Processing index : ", index)
    try:
        new_record = dict()
        for i in range(24):
            cur_s = ""
            
            # id, get_prob
            if i in [0, 8]:  
                new_record[dictionary_map[i]] = row[i]
                continue
            
            # category, symptom, acompany, cure_department, cure_way, check, recommend_drug, drug_detail, common drug, do_eat, not_eat, recommend_eat
            elif i in [3, 6, 10, 11, 12, 16, 17, 18, 20, 21, 22, 23]: 
                if row[i] == [] or type(row[i]) == float and math.isnan(row[i]):
                    new_record[dictionary_map[i]] = []
                    cur_s = ""
                else:
                    for x in row[i]:
                        cur_s = cur_s + x + ','
            
            else:
                cur_s = row[i]
                if row[i] == None:
                    cur_s = ""
                    new_record[dictionary_map[i]] = None

            if cur_s == "" or type(row[i]) == float and math.isnan(row[i]):
                continue
            
            translated_string = translator_obj.translate(cur_s, dest='en').text     
            if i in [3, 6, 10, 11, 12, 16, 17, 18, 20, 21, 22, 23]:
                translated_string = translated_string.split(',')
                translated_string = translated_string[:len(translated_string)-1]
                
            new_record[dictionary_map[i]] = translated_string
        
        error_count = 1
        json.dump(new_record, file, indent=4)
        file.write("\n")
        

    except Exception as e:
        print("ERROR OCCOURED\n", e)
        error_count += 1
        if error_count == 5:
            print("Row reached : ", index)
            break
