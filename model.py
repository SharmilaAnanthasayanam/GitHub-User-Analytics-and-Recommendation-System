import pandas as pd
import nltk
from nltk import word_tokenize
nltk.download('punkt')
import pandas as pd
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize,pos_tag
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import json
from streamlit_lottie import st_lottie
import analytics

#Loading animation configuration
def load_lottiefile(filepath: str):
    """Gets the file path and returns the file in dict format"""
    with open(filepath, "r", encoding="utf8") as f:
        return json.load(f)

def UI_communication(value):
      """Gets the String and displays it with the animation"""
      st.markdown(f"<h4 style='text-align: center;'>{value}</h4>", unsafe_allow_html=True)
      lottie_streamlit = load_lottiefile("Animation - 1711522865345.json")
      st.lottie(lottie_streamlit, speed=1.0, reverse = False, height=200)
      st.markdown(f"<p style='text-align: center;'>please wait. Data might be huge</p>", unsafe_allow_html=True)

def remove_whitespace(text):
  """Gets the text and returns it without extra spaces"""
  return  " ".join(text.split())

def remove_urls(text):
  """Gets the text and returns """
  url_pattern = re.compile(r'https?://\S+|www\.\S+')
  return url_pattern.sub(r'', text)

def remove_stopwords(text):
  """Gets the text and returns it without stopwords"""
  en_stopwords = stopwords.words('english')
  result = []
  for token in text:
      if token not in en_stopwords:
          result.append(token)
  return result

def remove_punct(text):
  """Gets the text and returns it without punctuation marks"""
  tokenizer = RegexpTokenizer(r"\w+")
  lst = tokenizer.tokenize(' '.join(text))
  return lst

def lemmatization(text):
  """Gets the text and returns lematized text"""
  result=[]
  wordnet = WordNetLemmatizer()
  for token,tag in pos_tag(text):
    pos=tag[0].lower()
    if pos not in ['a', 'r', 'n', 'v']:
      pos = 'n'
    result.append(wordnet.lemmatize(token,pos))
  return result

def make_sentence(list_):
  """Gets a list and returns a string of elements in the list"""
  return " ".join(list_)


def cos_similarity(arr1,arr2):
  """Gets two arrays and returns their cosine similarity """
  D1 = [arr1]
  D2 = [arr2]
  similarity = cosine_similarity(D1,D2)[0][0]
  return similarity

def preprocessing_data(df_column):
  """Gets a column from a dataframe and returns the processed data """
  df_column = df_column.str.lower()
  df_column = df_column.apply(remove_whitespace)
  df_column = df_column.apply(remove_urls)
  df_column = df_column.apply(lambda X: word_tokenize(X))
  df_column = df_column.apply(remove_stopwords)
  df_column = df_column.apply(remove_punct)
  df_column = df_column.apply(lemmatization)
  df_column = df_column.apply(make_sentence)
  return df_column


def recommendations(recommend_data):
  """Gets the user details dataframe and returns the recommended users dictionary.
     The dictionary has matched usernames and repository names"""
  placeholder = st.empty()
  with placeholder.container(): 
    UI_communication("Preprocessing data...")
  
  #User data Preprocessing
  recommend_data = recommend_data.fillna("null")
  recommend_data['readme'] = preprocessing_data(recommend_data['readme'])
  recommend_data['repo_description'] = preprocessing_data(recommend_data['repo_description'])
  
  with placeholder.container():
    UI_communication("Encoding data...")
  #User Data Encoding/Vectorizing
  model = SentenceTransformer("all-MiniLM-L6-v2")
  recommend_data["repo_name_encoded"] = recommend_data["repo_name"].apply(model.encode)
  recommend_data["readme_encoded"] = recommend_data["readme"].apply(model.encode)
  recommend_data["repo_description_encoded"] = recommend_data["repo_description"].apply(model.encode)
  recommend_data["language"] = recommend_data["language"].apply(model.encode)

  #Retrieving dataset from the database
  dataset = analytics.retrieve_dataset()
  data_encoded_dict = {"username":[],"language":[],"repo_name_encoded":[],
                       "readme_encoded":[],"repo_description_encoded":[],"repo_name":[]} 
  for i in dataset:
    data_encoded_dict["username"].append(i["username"])
    data_encoded_dict["language"].append(i["language"])
    data_encoded_dict["repo_name_encoded"].append(i["repo_name_encoded"])
    data_encoded_dict["readme_encoded"].append(i["readme_encoded"])
    data_encoded_dict["repo_description_encoded"].append(i["repo_description_encoded"])
    data_encoded_dict["repo_name"].append(i["repo_name"])
  data_encoded = pd.DataFrame(data_encoded_dict)
  
  #Calculating similarity between each repo in dataset with the user's data
  with placeholder.container():
    UI_communication("Calculating...")
  repo_max_sim = []
  for i in recommend_data.index:
    t_reponame = recommend_data.loc[i]["repo_name_encoded"]
    t_language = recommend_data.loc[i]["language"]
    t_readme = recommend_data.loc[i]["readme_encoded"]
    t_desc = recommend_data.loc[i]["repo_description_encoded"]
    max_sim = [0]*10
    for j in data_encoded.index:
      p_reponame = data_encoded.loc[j]["repo_name_encoded"]
      p_language = data_encoded.loc[i]["language"]
      p_readme = data_encoded.loc[i]["readme_encoded"]
      p_desc = data_encoded.loc[i]["repo_description_encoded"]
      reponame_sim = cos_similarity(p_reponame,t_reponame)
      language_sim = cos_similarity(p_language,t_language)
      readme_sim = cos_similarity(p_readme, t_readme)
      desc_sim = cos_similarity(p_desc, t_desc)
      sum_sim = reponame_sim + language_sim + readme_sim + desc_sim
      for num in range(len(max_sim)):
        if sum_sim > max_sim[num]:
          max_sim.insert(num,j)
          max_sim.pop()
          break
    repo_max_sim.extend(max_sim)

  #Sorting the similarity dict in descing order
  from collections import Counter
  d = dict(Counter(repo_max_sim))
  d = sorted(d.items(),key = lambda x:x[1],reverse = True)

  #Picking the top users/Repositories
  with placeholder.container():
    UI_communication("Picking Top Users...")
  Top_users = {}
  for i,j in d:
    ind = i
    username = data_encoded.loc[ind]["username"]
    repo_name = data_encoded.loc[ind]["repo_name"]
    if username != recommend_data["username"][0]:
      if username in Top_users and len(Top_users[username]) < 10:
          Top_users[username].append(repo_name)
      else:
        Top_users[username] = [repo_name]
    if len(Top_users) >= 10:
      break
  #Inserting the current user to the database
  analytics.insert_currentuser(recommend_data)
  placeholder.empty()
  return Top_users

















