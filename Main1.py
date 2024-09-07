import streamlit as streamlit
import pickle
import pandas as pd
import requests

streamlit.markdown(
    """
    <style>
    /* Set background color to a lighter black */
    .main {
        background-color: #1c1c1c;
    }

    /* Set header color to white */
    h1 {
        color: white;
    }

    /* Set the select box label text and button text to white */
    .stText, .stSelectbox label {
        color: white;
    }

    /* Style the Show Recommendation button */
    .stButton button {
        background-color: #4CAF50; /* Green background */
        color: white; /* White text */
        border-radius: 8px; /* Rounded corners */
        padding: 10px;
        font-size: 16px;
    }

    /* Remove the orange hover effect and set a dark green hover effect */
    .stButton button:hover {
        background-color: #45a049 !important; /* Darker green on hover */
        color: white !important; /* White text */
    }
    </style>
    """,
    unsafe_allow_html=True
)


anime_data = pd.read_csv("anime.csv")
Data = pickle.load(open("list.pkl", 'rb'))
similarity = pickle.load(open("similarity.pkl", 'rb'))


Data_list = Data['name'].values


streamlit.header("Anime Recommendation")  # This will now be white
selectedVal = streamlit.selectbox("Choose an anime you like!", Data_list)


JIKAN_API_URL = "https://api.jikan.moe/v4/anime"

def fetch_poster(anime_name):
    try:
        search_url = f"{JIKAN_API_URL}?q={anime_name}&limit=1"
        response = requests.get(search_url)
        data = response.json()
        poster_url = data['data'][0]['images']['jpg']['image_url']
        return poster_url
    except Exception as e:
        print(f"Error fetching poster for {anime_name}: {e}")
        return None

def suggest(anime_name):
    def clean_name(name):
        return name.lower().replace(' ', '').strip()

    index = Data[Data['name'] == anime_name].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])

    suggested_anime = []
    printed_prefixes = set()
    base_name = clean_name(anime_name)

    count = 0
    for i in distance:
        name = Data.iloc[i[0]]['name']
        cleaned_name = clean_name(name)
        prefix = cleaned_name[:5]

        if prefix not in printed_prefixes and cleaned_name != base_name:
            suggested_anime.append(name)
            printed_prefixes.add(prefix)
            count += 1

        if count == 5:
            break

    return suggested_anime

if streamlit.button("Show Recommendation"):
    anime_recommendations = suggest(selectedVal)

    if anime_recommendations:
        cols = streamlit.columns(5)

        for idx, col in enumerate(cols):
            if idx < len(anime_recommendations):
                anime_name = anime_recommendations[idx]
                poster_url = fetch_poster(anime_name)

                with col:
                    streamlit.text(anime_name)
                    if poster_url:
                        streamlit.image(poster_url, use_column_width=True)
