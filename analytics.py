import pymongo
from dotenv import load_dotenv
load_dotenv()
import os
import streamlit as st
import json
from streamlit_lottie import st_lottie

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

#Connecing to the database
db_user = os.getenv("db_user")
db_pass = os.getenv("db_pass")
connection_string = f"mongodb+srv://{db_user}:{db_pass}@cluster0.irtbklj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = pymongo.MongoClient(connection_string)
db = client.get_database("github")
user_collection = db.get_collection("user_data")
repo_collection = db.get_collection("repo_data")
commit_collection = db.get_collection("commit_data")
recommendation_coll = db.get_collection("recommendation_data")
dataset_col = db.get_collection("github_dataset")

#Inserting data to the database
def insert_to_db(user_data, repo_data, commit_data, recommendation_data):
    """Gets the user_data, repo_data, commit_data, recommendation_data as dictionaries.
       Inserts the input data to the database"""
    #Check if the user exists already
    existing_document = user_collection.find_one({"login": user_data["login"]})
    #if not insert the data to the database
    if not existing_document:
        placeholder = st.empty()
        with placeholder.container():
          UI_communication("Inserting User info...")
        user_collection.insert_one(user_data)

        with placeholder.container():
          UI_communication("Inserting Repository info...")
        for count in range(len(repo_data["repos_name"])):
            if repo_data["languages"][count]:
              for lang in repo_data["languages"][count]:
                  repo_collection.insert_one({
                      "repo_owner":repo_data["login"],
                      "repos_fullname":repo_data["repos_name"][count],
                      "repos_description":repo_data["repos_description"][count],
                      "repos_topics": repo_data["repos_topics"][count],
                      "repos_created_at": repo_data["repos_created_at"][count],
                      "language": lang,
                      "repo_commit_count":repo_data["repo_commit_count"][count],
                      "starred": repo_data["star_list"][count],
                      "forks_count":repo_data["forks_count"][count],
                      "watchers_count":repo_data["watchers_count"][count],
                      "open_issues_count": repo_data["open_issues_count"][count]
                  }
                  )
            else:
               repo_collection.insert_one({
                      "repo_owner":repo_data["login"],
                      "repos_fullname":repo_data["repos_name"][count],
                      "repos_description":repo_data["repos_description"][count],
                      "repos_topics": repo_data["repos_topics"][count],
                      "repos_created_at": repo_data["repos_created_at"][count],
                      "language": "",
                      "repo_commit_count":repo_data["repo_commit_count"][count],
                      "starred": repo_data["star_list"][count],
                      "forks_count":repo_data["forks_count"][count],
                      "watchers_count":repo_data["watchers_count"][count],
                      "open_issues_count": repo_data["open_issues_count"][count]
                  }
                  )
        
        with placeholder.container():
          UI_communication("Inserting Commits info...")
        for count in range(len(commit_data["repos_fullname"])):
            for com in range(len(commit_data["commit_date"][count])):
                commit_collection.insert_one({
                    "login": commit_data["login"],
                    "repos_fullname": commit_data["repos_fullname"][count],
                    "commit_date": commit_data["commit_date"][count][com],
                    "commit_year":commit_data["commit_year"][count][com],
                    "commit_quarter": commit_data["commit_quarter"][count][com]
                })  
        
        with placeholder.container():
          UI_communication("Inserting Recommendation info...")
        for count in range(len(recommendation_data["repos_name"])):
          recommendation_coll.insert_one({
            "username": recommendation_data["login"],
            "repo_name": recommendation_data["repos_name"][count],
            "repo_description":recommendation_data["repo_description"][count],
            "language":recommendation_data["language"][count],
            "readme":recommendation_data["readme"][count]
          })
        placeholder.empty()
           
def retrieve_user_info(user_name):
    """Gets the username and retrives the user data from user collection"""
    user_document = user_collection.find_one({"login": user_name})
    return user_document

def retrieve_repo_info(user_name):
    """Gets the username and returns the repo info of the user"""
    repo_document = repo_collection.find({"repo_owner":user_name})
    return repo_document

def retrieve_repo_lang(user_name):
    """Gets the username and returns the repo count per language of the user"""
    repo_document = repo_collection.aggregate([{"$match":{"repo_owner":user_name}},
                                               {"$group":{"_id":"$language", "repo_count":{"$count":{}}}}])
    return repo_document

def retrieve_lang_commits(user_name):
    """Gets the username and returns the repo commit count per language of the user"""
    repo_document = repo_collection.aggregate([{"$match":{"repo_owner":user_name}},
                                               {"$group":{"_id":"$language", "repo_commit_count":{"$sum":"$repo_commit_count"}}}])
    return repo_document

def retrieve_star_lang(user_name):
    """Gets the username and returns the start count per language of the user"""
    repo_document = repo_collection.aggregate([{"$match":{"repo_owner":user_name}},
                                               {"$group":{"_id":"$language", "star_count":{"$sum":"$starred"}}}])
    return repo_document

def retrieve_commits_repo(user_name):
    """Gets the username and returns the Top 10 Commits repo of the user"""
    repo_document = repo_collection.aggregate([{"$match":{"repo_owner":user_name}},
                                               {"$group":{"_id":"$repos_fullname", "repo_commit_count":{"$first":"$repo_commit_count"}}},
                                               {"$sort":{"repo_commit_count":-1}},
                                               {"$limit":10}])
    return repo_document

def retrieve_stars_repo(user_name):
    """Gets the username and returns the Top 10 starred repo of the user"""
    repo_document = repo_collection.aggregate([{"$match":{"repo_owner":user_name}},
                                               {"$group":{"_id":"$repos_fullname", "repo_stars_count":{"$first":"$starred"}}},
                                               {"$sort":{"starred":-1}},
                                               {"$limit":10}])
    return repo_document

def retrieve_commit_quarter(user_name):
    """Gets the username and returns the Commit count per year and quarter"""
    repo_document = commit_collection.aggregate([{"$match":{"login":user_name}},
                                                 {"$group":{"_id": {"commit_year":"$commit_year",
                                                                   "commit_quarter":"$commit_quarter"},
                                                            "commit_count":{"$count":{}}}
                                                 },
                                                 {"$sort":{"_id":1}}           
                                                 ])
    return repo_document

def retrieve_frameworks(user_name):
    """Gets the username and returns the repo description and topics of the user"""
    repo_document = repo_collection.aggregate([{"$match":{"repo_owner":user_name}},
                                               {"$group":{"_id":"$repos_fullname",
                                                         "repo_description": {"$first":"$repos_description"},
                                                         "repo_topics":{"$first":"$repos_topics"}}}
                                               ])
    return repo_document

def user_availability(user_name):
    """Gets the username and returns if the user available in database or not"""
    existing_document = user_collection.find_one({"login": user_name})
    return existing_document

def retrieve_forks(user_name):
  """Gets the username and returns the forkscount per repo of the user"""
  repo_document = repo_collection.aggregate([{"$match":{"repo_owner":user_name}},
                                               {"$group":{"_id":"$repos_fullname", "forks_count":{"$first":"$forks_count"}}}]
                                               )             
  return repo_document

def retrieve_open_issues(user_name):
  """Gets the username and returns the open issues count per repo of the user"""
  repo_document = repo_collection.aggregate([{"$match":{"repo_owner":user_name}},
                                               {"$group":{"_id":"$repos_fullname", "open_issues_count":{"$first":"$open_issues_count"}}}]
                                               )             
  return repo_document

def retrieve_watchers(user_name):
  """Gets the username and returns the watchers count per repo of the user"""
  repo_document = repo_collection.aggregate([{"$match":{"repo_owner":user_name}},
                                               {"$group":{"_id":"$repos_fullname", "watchers_count":{"$first":"$watchers_count"}}}]
                                               )             
  return repo_document

def retrieve_recommend_data(user_name):
    """Gets the username and returns the data required for recommendation
       1.username
       2.repo name
       3.repo description
       4.readme
       5.language"""
    repo_document = recommendation_coll.find({"username":user_name},{"_id":0})
    return repo_document
  
def retrieve_dataset():
  """Returns the dataset from the database"""
  repo_document = dataset_col.find({},{"_id":0,"username":1,"language":1,
                                       "repo_name_encoded":1, "readme_encoded":1,
                                       "repo_description_encoded":1, "repo_name":1})
  return repo_document

def insert_currentuser(df):
  """Gets the user dataframe and inserts it to the dataset Collection in database"""
  def converting_to_list(list_):
    return list_.tolist()
  df["repo_name_encoded"] = df["repo_name_encoded"].apply(converting_to_list)
  df["readme_encoded"] = df["readme_encoded"].apply(converting_to_list)
  df["repo_description_encoded"] = df["repo_description_encoded"].apply(converting_to_list)
  df["language"] = df["language"].apply(converting_to_list)
  existing_document = dataset_col.find_one({"username": df["username"][0]})
  if not existing_document:
    for index, row in df.iterrows():
      document = row.to_dict()
      dataset_col.insert_one(document)








    