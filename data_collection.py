from dotenv import load_dotenv
load_dotenv()
import os
import requests
from PIL import Image
import datetime
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
import json
from streamlit_lottie import st_lottie


#Loading Animation Configuration
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

#Github api access configuartion
access_token = os.getenv("access_token")
headers = {"Authorization": "token {}".format(access_token)}


def user_data(username):
    """Gets the user name and returns Four user details dictionaries
       1.user_data_dict, 
       2.repo_data_dict, 
       3.commits_data_dict,
       4.recommendation_data_dict """
    
    #Displaying Loading animation
    placeholder = st.empty()
    with placeholder.container():
      UI_communication("Collecting User Basic Info...")

    # Fetching user basic details
    user_url = f"https://api.github.com/users/{username}"
    response = requests.get(user_url, headers=headers)
    user_json = response.json()
    login = user_json.get("login","")
    name = user_json.get("name","")
    bio = user_json.get("bio", "")
    public_repos = user_json.get("public_repos", "")
    following_count = user_json.get("following", "")
    followers_count = user_json.get("followers", "")
    created_at = user_json.get("created_at", "")
    avatar_url = user_json.get("avatar_url", "")
    profile_url = user_json.get("html_url", "")
    company = user_json.get("company","")

    #Trimming url
    def url_trim(url):
        """Gets the url and returns trimmed url"""
        ind = url.find("{/",0,len(url))
        if ind != -1:
            url = url[0:ind]
        return url

    #Function to Request and fetch required parameters 
    def fetch_parameter(url,parameters_list):
        """Gets the url and parameter list.
           Returns the dictionary with paramters and its values"""
        response_dict = {}
        while(url):
            response = requests.get(url, headers=headers)
            data = response.json()
            if isinstance(data,list):
                for res in data:
                  for parameter in parameters_list:
                    if parameter in response_dict:
                      response_dict[parameter].append(res.get(parameter,""))
                    else:
                      response_dict[parameter] = [res.get(parameter,"")]
            link_header = response.headers.get('link')
            url = ""
            next_link = ""
            if link_header:
                link = link_header.split(",")
                for i in link:
                    if i.__contains__('rel="next"'):
                        next_link = i.split(";")
                        break
            if next_link:
                url = next_link[0][i.index("https"):-1]
        return response_dict 

    #Collecting Repository info
    placeholder.empty()
    with placeholder.container():
      UI_communication("Collecting User Repository Info...")
    starred_url = user_json.get("starred_url", "")
    starred_url = url_trim(starred_url)
    star_list = fetch_parameter(starred_url,"html_url")

    parameters_list = ["name", "html_url", "description", "stargazers_count",
                       "created_at", "commits_url", "languages_url", "forks_count",
                       "watchers", "open_issues","topics"]
    repos_url = user_json.get("repos_url", "")
    repos_url = url_trim(repos_url)
    reponse_dict = fetch_parameter(repos_url, parameters_list)
    repos_name = reponse_dict.get("name",[])
    repo_html_url = reponse_dict.get("html_url",[])
    repos_description = reponse_dict.get("description",[])
    repos_star_count = reponse_dict.get("stargazers_count",[])
    repos_created_at = reponse_dict.get("created_at",[])
    commits_url = reponse_dict.get("commits_url",[])
    languages_url = reponse_dict.get("languages_url",[])
    forks_count = reponse_dict.get("forks_count",[])
    watchers_count = reponse_dict.get("watchers",[])
    open_issues_count = reponse_dict.get("open_issues",[])
    
    #Collecting Commits info
    placeholder.empty()
    with placeholder.container():
      UI_communication("Collecting User Commits Info...")

    repo_commit_count = []
    total_commit_count = 0
    commits_date = []
    commit_quarter = []
    commit_year = []
    for url in commits_url:
        url = url_trim(url)
        list_ = ["commit", "author"]
        commit_dict = fetch_parameter(url,list_)
        commit = commit_dict.get("commit",[])
        date = []
        quarter = []
        years = []
        count = 0
        for ind in range(len(commit)):
            if commit[ind]["author"]["name"] in name or commit[ind]["author"]["name"] in login:
              count += 1
              iso_date = commit[ind]["author"]["date"]
              commit_date = datetime.datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%SZ")
              year = commit_date.year
              month = commit_date.month
              if month in [1,2,3]:
                  qua = 1
              elif month in [4,5,6]:
                  qua = 2
              elif month in [7,8,9]:
                  qua = 3
              else:
                  qua = 4
              date.append(iso_date)
              quarter.append(qua)
              years.append(year)
        repo_commit_count.append(count)
        total_commit_count += count
        commits_date.append(date)
        commit_quarter.append(quarter)
        commit_year.append(years)
    
    #Collecting languages info
    languages = []
    lang_top = []
    for url in languages_url:
        url = url_trim(url)
        response = requests.get(url, headers=headers)
        languages.append(list(response.json().keys()))
        if response.json().keys():
          lang_top.append(list(response.json().keys())[0])
        else:
          lang_top.append("null")
    
    #Collecting repo topics
    repos_topics = reponse_dict.get("topics",[])
    for cnt in range(len(repos_topics)):
        string = ", ".join(repos_topics[cnt])
        repos_topics[cnt] = string

    #Collecting readme 
    placeholder.empty()
    with placeholder.container():
      UI_communication("Collecting User Recommendation Info...")

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless') # this is must
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    readme = []
    for html_url in repo_html_url:
      driver.get(html_url)
      search_box = driver.find_elements(By.TAG_NAME, 'p')
      string = ""
      for i in search_box:
        string += i.text
      readme.append(string)
   
    placeholder.empty()

    #Creating dictionaries based on collected data
    user_data_dict = { "login": login,
                        "name": name,
                        "bio": bio,
                        "company":company,
                        "public_repos": public_repos,
                        "following_count": following_count,
                        "followers_count": followers_count,
                        "created_at": created_at,
                        "avatar_url": avatar_url,
                        "starred_url": star_list,
                        "profile_url": profile_url,
                        "total_commits": total_commit_count,
                    }
    repo_data_dict ={"login": login,   
                    "languages": languages,
                    "repos_name" : repos_name,
                    "repos_description": repos_description,
                    "repos_created_at": repos_created_at,
                    "repo_commit_count": repo_commit_count,
                    "star_list": repos_star_count,
                    "repos_topics": repos_topics,
                    "forks_count": forks_count,
                    "watchers_count": watchers_count,
                    "open_issues_count": open_issues_count
                    }
    commits_data_dict = {
        "login":login,
        "repos_fullname": repos_name,
        "commit_date":commits_date,
        "commit_quarter": commit_quarter,
        "commit_year": commit_year
    }
    recommendation_data_dict ={
      "login":login,
      "repos_name":repos_name,
      "language":lang_top,
      "readme":readme,
      "repo_description":repos_description
    }
    return user_data_dict, repo_data_dict, commits_data_dict,recommendation_data_dict

#Gets Avatar url,image details and returns the image
def get_avatar(avatar_url,image_name, image_size):
    """Gets the avatar url, image_name, image_size.
       Returns the avatar image"""
    response = requests.get(avatar_url, headers = headers)
    if response.status_code == 200:
        filename = image_name
        with open(filename, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        img = Image.open(image_name)  
        newsize = image_size
        img = img.resize(newsize)
    return img

#Gets username, repos list and returns the user avatar url, user html url and repos html url
def get_userinfo(username,repos_list):
  """Gets the username and reponames list.
     Returns the avatar_url, user_html_url, repos_html_url"""
  user_url = f"https://api.github.com/users/{username}"
  response = requests.get(user_url, headers = headers)
  response = response.json()
  avatar_url = response.get("avatar_url")
  user_html_url = response.get("html_url")
  repos_html_url = {}
  for repo_name in repos_list:
    repo_name = repo_name.replace(" ","-")
    repo_url = f"https://api.github.com/repos/{username}/{repo_name}"
    response = requests.get(repo_url, headers = headers)
    response = response.json()
    if response.get("html_url"):
      repos_html_url[repo_name] = response.get("html_url")
  return avatar_url, user_html_url, repos_html_url








