import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from sklearn.tree import DecisionTreeClassifier

# Function to load data from the SQLite database
def load_data():
    conn = sqlite3.connect('climbing_routes.db')
    routes = pd.read_sql_query("SELECT * FROM routes", conn)
    conn.close()
    return routes

# Encode difficulty and style
def encode_data(routes_df):
    difficulty_mapping = {'Beginner': 0, 'Intermediate': 1, 'Advanced': 2}
    routes_df['difficulty_encoded'] = routes_df['difficulty'].map(difficulty_mapping)

    style_mapping = {'Sport': 0, 'Bouldering': 1, 'Trad': 2}
    routes_df['style_encoded'] = routes_df['style'].map(style_mapping)

    return routes_df

# Train decision tree classifier
def train_decision_tree(routes_df):
    X = routes_df[['difficulty_encoded', 'style_encoded']]
    y = routes_df['route_id']
    clf = DecisionTreeClassifier()
    clf.fit(X, y)
    return clf

# Function to recommend exactly 5 routes
def recommend_routes(user_skill_level, user_preferred_style, clf, routes_df, n_recommendations=5):
    difficulty_mapping = {'Beginner': 0, 'Intermediate': 1, 'Advanced': 2}
    style_mapping = {'Sport': 0, 'Bouldering': 1, 'Trad': 2}

    user_difficulty_encoded = difficulty_mapping.get(user_skill_level)
    user_style_encoded = style_mapping.get(user_preferred_style)

    # Create the user input dataframe
    user_input_df = pd.DataFrame({
        'difficulty_encoded': [user_difficulty_encoded],
        'style_encoded': [user_style_encoded]
    })

    # Get predicted route IDs based on the user's input
    predicted_route_ids = clf.predict(user_input_df)

    # Find the routes that match the predicted route IDs
    recommended_routes = routes_df[routes_df['route_id'].isin(predicted_route_ids)]

    # If there are less than 5 recommended routes, supplement with random routes
    if len(recommended_routes) < n_recommendations:
        additional_routes = routes_df[~routes_df['route_id'].isin(predicted_route_ids)].sample(n_recommendations - len(recommended_routes))
        recommended_routes = pd.concat([recommended_routes, additional_routes])

    # Ensure exactly 5 routes are returned (this also handles if the number is greater than 5 due to random sampling)
    return recommended_routes.head(n_recommendations)

# Streamlit dashboard layout
def main():
    # Load and encode the data
    routes_df = load_data()
    routes_df = encode_data(routes_df)
    clf = train_decision_tree(routes_df)

    st.title("Climbing Route Recommendation System")

    # User input for skill level and style
    user_skill_level = st.selectbox("Select your skill level", ["Beginner", "Intermediate", "Advanced"])
    user_preferred_style = st.selectbox("Select your preferred climbing style", ["Sport", "Bouldering", "Trad"])

    # Recommend routes based on user input
    if st.button("Get Recommendations"):
        recommended_routes = recommend_routes(user_skill_level, user_preferred_style, clf, routes_df)
        st.write("### Recommended Routes:")
        st.write(recommended_routes[['name', 'difficulty', 'style']])

    # Visualization 1: Bar chart showing the distribution of routes by difficulty
    difficulty_counts = routes_df['difficulty'].value_counts()
    st.write("### Route Distribution by Difficulty")
    fig = px.bar(difficulty_counts, x=difficulty_counts.index, y=difficulty_counts.values, labels={'x': 'Difficulty', 'y': 'Number of Routes'})
    st.plotly_chart(fig)

    # Visualization 2: Pie chart showing the distribution of routes by style
    style_counts = routes_df['style'].value_counts()

    # Optionally, combine small categories into an 'Other' category
    min_count = 5  # Set a threshold for minimum count per style
    small_styles = style_counts[style_counts < min_count].index
    routes_df['style'] = routes_df['style'].replace(small_styles, 'Other')

    # Recalculate counts and plot
    style_counts = routes_df['style'].value_counts()
    st.write("### Route Distribution by Style")
    fig = px.pie(names=style_counts.index, values=style_counts.values, title='Distribution of Routes by Style')
    st.plotly_chart(fig)

    # Visualization 3: Scatter plot showing difficulty vs. style
    st.write("### Difficulty vs Style")
    fig = px.scatter(routes_df, x='difficulty_encoded', y='style_encoded', color='style', hover_data=['name'])
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()
