import data_collection
import model
from numpy import e
import streamlit as st
import analytics
from dotenv import load_dotenv
load_dotenv()
import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

#Page layout Configuration
st.set_page_config(layout="wide")

#Getting user input
username = st.text_input("Enter Username")

if username:
    #Checking if user already exists in database
    user_available = analytics.user_availability(username)

    #If user not available collecting user info and storing in database
    if not user_available:
      user_data, repo_data, commit_data, recommendation_data = data_collection.user_data(username)
      analytics.insert_to_db(user_data, repo_data, commit_data, recommendation_data)

    #Fetching required info from the database
    user_info = analytics.retrieve_user_info(username)
    repo_info = analytics.retrieve_repo_info(username)
    repo_lang_info = analytics.retrieve_repo_lang(username)
    lang_commits_info = analytics.retrieve_lang_commits(username)
    star_lang_info = analytics.retrieve_star_lang(username)
    commits_repo_info =  analytics.retrieve_commits_repo(username)
    stars_repo_info = analytics.retrieve_stars_repo(username)
    commit_quarter_info = analytics.retrieve_commit_quarter(username)
    frameworks_info = analytics.retrieve_frameworks(username)
    forks_info = analytics.retrieve_forks(username)
    watchers_info = analytics.retrieve_watchers(username)
    open_issues_info =  analytics.retrieve_open_issues(username)
    recommend_info = analytics.retrieve_recommend_data(username)

    
    col1, col2, col3 = st.columns((0.8,1.1,3))
    #Displaying user avatar
    avatar_url = user_info.get("avatar_url")
    if avatar_url:
        avatar = data_collection.get_avatar(avatar_url,"avatar.jpg",(300,300))
        img_height = avatar.size
        with col1:
            st.image(avatar)

    #Displaying user basic details
    login = user_info.get("login")
    name =  user_info.get("name")
    public_repos =  user_info.get("public_repos")
    created_at = user_info.get("created_at")
    profile_url = user_info.get("profile_url")
    company = user_info.get("company")
    text = f''''''
    if login and name:
        text += f'''👨🏻‍💻 {login}({name})'''
    if public_repos:
        text += f'''\n🛢 {public_repos} public repos'''
    if created_at:
        d1 = datetime.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").date()
        d2 = datetime.datetime.strptime(str(datetime.date.today()), "%Y-%m-%d").date()
        duration = abs((d2 - d1).days)
        if duration >= 365:
            duration /= 365
            text += f'''\n🕓 Joined Github {int(duration)} years ago'''
        elif duration < 365:
            if d2.year == d1.year:
              months = d2.month - d1.month
              if d2.day <= d1.day:
                  months -= 1
            else:
              months = (12 - d1.month) + d2.month
              # st.write(months, 12-d1.month, d2.month)
              if d2.day < d1.day:
                months -= 1
            text += f'''\n🕓 Joined Github {months} months ago'''
        elif duration < 31:
            text  += f'''\n🕓 Joined Github {duration} days ago'''
    if company:
        text += f'''\n🏢 {company}'''
    st.markdown("""
    <style>
    [data-testid=column]:nth-of-type(2) [data-testid=stVerticalBlock]{
        gap: 0rem;
    }
    </style>
    """,unsafe_allow_html=True)
    with col2:
        st.text(f'''{text}''')
        st.write(f"🔗 [View profile on Github]({profile_url})")

    #Displaying Commits per quarter graph
    with col3:
        commit_quarter = {"commit_year_quarter":[], "commit_count":[]}
        for info in commit_quarter_info:
            commit_quarter["commit_year_quarter"].append(str(info["_id"]["commit_year"])+"_"+str(info["_id"]["commit_quarter"]))
            commit_quarter["commit_count"].append(info["commit_count"])
        commit_quarter = pd.DataFrame(commit_quarter)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=commit_quarter["commit_year_quarter"], y=commit_quarter["commit_count"], fill='tozeroy'))
        # fig = go.Figure(data=[go.area(commit_quarter, x="commit_year_quarter", y="commit_count",labels={"commit_count":""})])
        fig.update_layout(title="Commits per quarter",showlegend=False, yaxis={'side': 'right'}, xaxis={'visible': False},
                          title_x = 0.75, title_y = 1, autosize= False, height = 180,
                          margin = dict(l=0,r=0,b=0,t=0,pad=0))
        st.plotly_chart(fig)

    st.divider()
    
    #Displaying Repos per languages chart
    col1, col2, col3 = st.columns(3)
    with col1:
        repos_lang = {"Language":[],"repo_count":[]}
        for i in repo_lang_info:
            if i["_id"] != "":
              repos_lang["Language"].append(i["_id"])
              repos_lang["repo_count"].append(i["repo_count"])
        repos_lang = pd.DataFrame(repos_lang)
        fig = px.pie(repos_lang, values = "repo_count",names='Language',hole = 0.4,color_discrete_sequence=px.colors.qualitative.Plotly, title='Repos Per Language')
        fig.update_layout(autosize=False, width=350, height=410, showlegend=True, plot_bgcolor="white", margin={"l":0,"r":0,"t":30,"b":0,"pad":0})
        fig.update_traces(marker=dict(line=dict(color="white", width=2)))
        st.plotly_chart(fig)

    #Displaying Stars per languages chart
    with col2:
        star_lang = {"Language":[],"star_count":[]} 
        for i in star_lang_info:
            if i["_id"] != "":
              star_lang["Language"].append(i["_id"])
              star_lang["star_count"].append(i["star_count"])
        star_lang = pd.DataFrame(star_lang)
        fig = px.pie(star_lang, values = "star_count",names='Language', hole = 0.4,color_discrete_sequence=px.colors.qualitative.Plotly, title='Stars Per Language')
        fig.update_layout(autosize=False, width=350, height=410,showlegend=True, plot_bgcolor="white", margin = {"l":0,"r":0,"t":30,"b":0, "pad":0})
        fig.update_traces(marker=dict(line=dict(color="white", width=2)))
        st.plotly_chart(fig)
    
    #Displaying Commits per languages chart
    with col3:
        lang_commit = {"Language":[],"repo_commit_count":[]}
        for i in lang_commits_info:
            if i["_id"] != "":
              lang_commit["Language"].append(i["_id"])
              lang_commit["repo_commit_count"].append(i["repo_commit_count"])
        lang_commit = pd.DataFrame(lang_commit)
        fig = px.pie(lang_commit, values = "repo_commit_count",names='Language',hole = 0.4,color_discrete_sequence=px.colors.qualitative.Plotly, title='Commits Per Language')
        fig.update_layout(autosize=False, width=350, height=410, showlegend=True, plot_bgcolor="white",margin={"l":0,"r":0,"t":30,"b":0, "pad":0})
        fig.update_traces(marker=dict(line=dict(color="white", width=2)))
        st.plotly_chart(fig)

    st.divider()

    #Displaying Commits per Repo (Top 10)
    col1, col2 = st.columns(2)
    with col1:
        repo_commit = {"repo_name":[],"repo_commit_count":[]}
        for i in commits_repo_info:
            repo_commit["repo_name"].append(i["_id"])
            repo_commit["repo_commit_count"].append(i["repo_commit_count"])
        repo_commit = pd.DataFrame(repo_commit)
        fig = px.pie(repo_commit, values = "repo_commit_count",names='repo_name',hole = 0.4, title='Commits Per Repo(Top 10)')
        fig.update_layout(autosize=False, width=500, height=550,showlegend=True, plot_bgcolor="white", margin={"l":50,"r":0,"t":50,"b":0, "pad":0})
        fig.update_traces(marker=dict(line=dict(color="white", width=2)))
        st.plotly_chart(fig)
    
    #Displaying Stars per Repo (Top 10)
    with col2:
        stars_repo  = {"repo_name":[],"repo_stars_count":[]}
        for i in stars_repo_info:
            stars_repo["repo_name"].append(i["_id"])
            stars_repo["repo_stars_count"].append(i["repo_stars_count"])
        stars_repo = pd.DataFrame(stars_repo)
        fig = px.pie(stars_repo, values = "repo_stars_count",names='repo_name',hole=0.4, title='Stars Per Repo(Top 10)')
        fig.update_layout(autosize=False, width=500, height=550,showlegend=True, plot_bgcolor="white",margin={"l":50,"r":0,"t":50,"b":0,"pad":0})
        fig.update_traces(marker=dict(line=dict(color="white", width=2)))
        st.plotly_chart(fig)
    
    st.divider()

    #Displaying Watchers per Repo
    col1, col2 = st.columns(2)
    with col1:
      watchers = {"repo":[],"Watchers count":[]} 
      for i in watchers_info:
        watchers["repo"].append(i["_id"])
        watchers["Watchers count"].append(i["watchers_count"])
      watchers_df = pd.DataFrame(watchers)
      fig = px.bar(watchers_df, x = "repo", y ="Watchers count",title='Watchers per Repo',color_discrete_sequence=px.colors.qualitative.Pastel)
      fig.update_layout(autosize=False, xaxis={'visible': False},width=450, height=310,showlegend=True, plot_bgcolor="white", margin = {"l":0,"r":0,"t":30,"b":0, "pad":0})
      st.plotly_chart(fig)

    #Displaying Forks per Repo
    with col2:
      forks = {"repo":[],"Forks count":[]} 
      for i in forks_info:
        forks["repo"].append(i["_id"])
        forks["Forks count"].append(i["forks_count"])
      forks_df = pd.DataFrame(forks)
      fig = px.bar(forks_df, x = "repo", y ="Forks count", title='Forks per Repo')
      fig.update_layout(autosize=False,xaxis={'visible': False},width=450, height=310,showlegend=True, plot_bgcolor="white", margin = {"l":0,"r":0,"t":30,"b":0, "pad":0})
      st.plotly_chart(fig)

    #Displaying Frameworks Used
    frameworks =['django', 'flask', 'cherrypy', 'web2py', 'turbogears', 'pylons project', 'grok',
                 'fastapi', 'zope', 'jam', 'quixote', 'nevow', 'bottle', 'pyramid', 'tornado', 
                 'pyqt', 'tkinter', 'kivy', 'pyside', 'pysimplegui', 'scikit-learn', 'tensorflow', 
                 'pytorch', 'keras', 'numpy', 'scipy', 'pandas', 'matplotlib', 'pytest', 'unittest', 
                 'nose2', 'asyncio', 'aiohttp', 'cubicweb', 'django-hotsauce', 'giotto', 'reahl', 
                 'wheezy.web', 'hug', 'albatross', 'circuits', 'falcon', 'growler', 'pycnic', 'sanic',
                 'morepath', 'dash', 'uvloop', 'picnic', 'masonite','websauna', 'zope3', 'kisspy',
                 'lino', 'sencha extjs', 'nagare', 'pylatte', 'tipfy', 'watson-framework', 'webapp2', 
                 'webcore', 'webpy', 'werkzeug', 'quart', 'aquarium', 'appwsgi', 'backendpy', 'bluebream',
                 'bobo', 'clastic', 'divmod nevow', 'divmod athena', 'gunstar', 'klein', 'lona', 'python paste',
                 'pyweblib', 'spinne', 'weblayer', 'wsgiservlets', '4suite', 'bocadillo', 'crusader', 'cymbeline',
                 'enamel', 'gae', 'giotto', 'gizmo', 'glashammer', 'karrigell', 'maki', 'porcupine', 'pyroxide',
                 'python servlet pages', 'python servlet engine', 'qp', 'respose.bfg', 'responder', 'skunkweb',
                 'snakelets', 'spark', 'spiked', 'spyce', 'wasp', 'webbot', 'webstack', 'whiff', 'ajax', 'wxpython',
                 'pygtk', 'pygui', 'apache wicket', 'asp.net core', 'cakephp', 'catalyst', 'codeigniter', 'cppcms',
                 'grails', 'laravel', 'mojolicious', 'pop', 'ruby', 'sails.js', 'symfony', 'spring', 'wt',
                 'web toolkit', 'yii', 'zend', 'backbonejs', 'spring mvc', 'angularjs', 'angular', 'ember.js', 
                 'reactjs', 'jquery ui', 'svelte', 'vue', 'express', 'bootstrap', 'foundation', 'yaml', 'yui css grids',
                 'tailwind', 'gstreamer', 'directshow', 'ffmpeg', 'avfoundation', 'phonon', 'quicktime', 'vlc media player',
                 'qt', '.net, .net core', 'cocoa', 'ionic', 'flutter', 'xamarin', '.netmaui', 'electron', 'universal windows platform',
                 'windows forms', 'java', 'nw.js', 'swing', 'react native', 'tauri', 'haxe', 'xojo', 'wpf', 'neutralinojs',
                 'javafx', '8th dev', 'enact', 'windows forms', 'uwp', 'swiftui', 'gtk', 'osjs', 'slack', 'nativescript',
                 'sencha touch', 'solar2d', 'appcelerator titanium', 'kotlin multiplatform', 'cordova',
                 'node.js', 'firebase', 'ecere sdk', 'phonegap', 'swiftic', 'jQuery mobile', 'onsen ui',
                 'mobile angular ui', 'framework7', 'corona sdk', 'ruby on rails', 'asp.net', 'cakephp', 'play',
                 'asp.net mvc', 'nextjs', 'gatsby', 'meteor', 'spring boot', 'koa', 'phoenix', 'gin', 'jquery',
                 'preact', 'backbone', 'semantic ui', 'foundation', 'refine', 'asgi', 'starlette', 'dotnet']
    frameworks_dict = {}
    text = []
    for info in frameworks_info:
        full_name = info["_id"].split("/")
        for word in full_name:
            word = word.lower()
            if word in frameworks:
                text.append(word)
                frameworks_dict[word] = frameworks_dict.get(word,0) + 1
        description = info["repo_description"]
        if description:
            description = description.split(" ")
            for word in description:
                word = word.lower()
                if word in frameworks:
                    text.append(word)
                    frameworks_dict[word] = frameworks_dict.get(word,0) + 1
        topics = info["repo_topics"]
        if topics:
            topics = info["repo_topics"].split(", ")
            for word in topics:
                if word in frameworks:
                    text.append(word)
                    frameworks_dict[word] = frameworks_dict.get(word,0) + 1
    col1, col2 = st.columns(2)
    with col1:
      frameworks_df = pd.DataFrame({"Frameworks":list(frameworks_dict.keys()),"count":list(frameworks_dict.values())})
      fig = px.bar(frameworks_df, x = "Frameworks", y ="count",title='Frameworks used',color_discrete_sequence=px.colors.qualitative.Pastel)
      fig.update_layout(autosize=False,width=470, height=330,showlegend=True, plot_bgcolor="white", margin = {"l":0,"r":0,"t":30,"b":0, "pad":0})
      st.plotly_chart(fig)

    ##Displaying Open issues per Repo
    with col2:
      open_issues = {"repo":[],"Open issues count":[]} 
      for i in open_issues_info:
        open_issues["repo"].append(i["_id"])
        open_issues["Open issues count"].append(i["open_issues_count"])
      open_issues_df = pd.DataFrame(open_issues)
      fig = px.bar(open_issues_df, x = "repo", y ="Open issues count",title='Open issues per Repo',color_discrete_sequence=px.colors.qualitative.Pastel)
      fig.update_layout(autosize=False, xaxis={'visible': False},width=450, height=310,showlegend=True, plot_bgcolor="white", margin = {"l":0,"r":0,"t":30,"b":0, "pad":0})
      st.plotly_chart(fig)

    st.divider()

    #Displaying Recommended users
    st.markdown("**Recommendations**")
    recommend_list = []
    for i in recommend_info:
      recommend_list.append(i)
    recommend_df = pd.DataFrame(recommend_list)
    recommendation = model.recommendations(recommend_df)
    recommended_users = list(recommendation.keys())
    recommended_repos = list(recommendation.values())
    col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
    cols = [col1,col2,col3,col4,col5]
    num_of_recommendations = len(recommended_users)
    if num_of_recommendations >= 5:
      val = 5
    else:
      val = num_of_recommendations 
    for ind in range(val):
      r_username = recommended_users[ind]
      matched_repos = recommended_repos[ind]
      recommeded_user_info  = data_collection.get_userinfo(r_username, matched_repos)
      with cols[ind]:
          user_avatar = data_collection.get_avatar(recommeded_user_info[0],f"user{ind}.jpg",(220,220))
          st.image(user_avatar)
          style = "<style>[data-testid=column]:nth-of-type(" + str(ind) + ") " \
                  "[data-testid=stVerticalBlock]{gap: 1rem;}</style>"
          st.markdown(style,unsafe_allow_html=True)
          st.write(r_username)
          st.write(f"🔗 [View Profile on Github]({recommeded_user_info[1]})")
          with st.expander("Recommended Repositories"):
            for repo,repo_url in recommeded_user_info[2].items():
              st.write(f"🔗 [{repo}]({repo_url})")
    if num_of_recommendations > 5:
      col6, col7, col8, col9, col10 = st.columns([1,1,1,1,1])
      cols = [col6,col7,col8,col9,col10]
      for ind in range(5,num_of_recommendations):
        r_username = recommended_users[ind]
        matched_repos = recommended_repos[ind]
        recommeded_user_info  = data_collection.get_userinfo(r_username, matched_repos)
        user_avatar = data_collection.get_avatar(recommeded_user_info[0],f"user{ind}.jpg",(220,220))
        with cols[ind-5]:
            st.image(user_avatar)
            style = "<style>[data-testid=column]:nth-of-type(" + str(ind) + ") " \
                    "[data-testid=stVerticalBlock]{gap: 1rem;}</style>"
            st.markdown(style,unsafe_allow_html=True)
            st.write(r_username)
            st.write(f"🔗 [View Profile on Github]({recommeded_user_info[1]})")
            with st.expander("Recommended Repositories"):
              for repo,repo_url in recommeded_user_info[2].items():
                st.write(f"🔗 [{repo}]({repo_url})")

            
            
        




      


                



        

    





    
