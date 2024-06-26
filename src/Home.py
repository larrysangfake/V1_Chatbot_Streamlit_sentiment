import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from wordcloud import WordCloud, STOPWORDS
import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk


score_to_category = {
    1: 'Very Dissatisfied',
    2: 'Dissatisfied',
    3: 'Neutral',
    4: 'Satisfied',
    5: 'Very Satisfied'
}


def initialize_state():
    # Initialize session states with default values if not already present
    keys = ['previous_dashboard', 'selected_role', 'selected_function', 'selected_location', 'uploaded_file']
    defaults = [None, [], [], [], None]
    for key, default in zip(keys, defaults):
        if key not in st.session_state:
            st.session_state[key] = default


def reset_filters():
    st.session_state['selected_role'] = []
    st.session_state['selected_function'] = []
    st.session_state['selected_location'] = []


st.set_page_config(layout="wide")
initialize_state()


# Load and clean data
@st.cache_data(persist=True)
def load_data():
    # Load data and cache the DataFrame to avoid reloads on each user interaction
    url = 'https://github.com/001202ZHENG/V1_Chatbot_Streamlit/raw/main/data/Voice%20of%20Customer_Second%20data%20set.xlsx'
    data = pd.read_excel(url)
    return data


data = load_data()

# General Page Layout
st.markdown(
    '''
    <style>
        .main .block-container {
            padding-top: 0.25rem;
            padding-right: 0.25rem;
            padding-left: 0.25rem;
            padding-bottom: 0.25rem;
        }
        h1 {
            margin-top: 0rem;
            margin-bottom: 0rem;
        }
        h3 {
            margin-top: 0rem;
            margin-bottom: 0rem;
        }
    </style>
    ''',
    unsafe_allow_html=True
)


# Header Function
def render_header(title, subtitle=None):
    style = style = """
    <style>
        h1.header, h3.subheader {
            background-color: #336699; /* Steel blue background */
            color: white; /* White text color */
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
            padding: 15px 0;
            height: auto
        }
        h1.header {
            margin-bottom: 0;
            font-size: 30px;
        }
        h3.subheader {
            font-size: 20px;
            font-weight: normal;
            margin-top: 0;
        }
    </style>
    """
    st.markdown(style, unsafe_allow_html=True)
    st.markdown(f'<h1 class="header">{title}</h1>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<h3 class="subheader">{subtitle}</h3>', unsafe_allow_html=True)


# Sidebar for dashboard selection
dashboard = st.sidebar.radio("Select Dashboard", ('General Survey Results',
                                                  'Section 1: Employee Experience',
                                                  'Section 2: Recruiting & Onboarding',
                                                  'Section 3: Performance & Talent',
                                                  'Section 4: Learning',
                                                  'Section 5: Compensation',
                                                  'Section 6: Payroll',
                                                  'Section 7: Time Management',
                                                  'Section 8: User Experience'
                                                  ))

if dashboard != st.session_state['previous_dashboard']:
    reset_filters()  # Reset filters if dashboard changed
    st.session_state['previous_dashboard'] = dashboard


@st.cache_data
def get_unique_values(column):
    return data[column].unique()


roles = get_unique_values('What is your role at the company ?')
functions = get_unique_values('What function are you part of ?')
locations = get_unique_values('Where are you located ?')

st.sidebar.multiselect('Select Role', options=roles, default=st.session_state['selected_role'], key='selected_role')
st.sidebar.multiselect('Select Function', options=functions, default=st.session_state['selected_function'],
                       key='selected_function')
st.sidebar.multiselect('Select Location', options=locations, default=st.session_state['selected_location'],
                       key='selected_location')


def apply_filters(data, roles, functions, locations):
    filtered = data
    if roles:
        filtered = filtered[filtered['What is your role at the company ?'].isin(roles)]
    if functions:
        filtered = filtered[filtered['What function are you part of ?'].isin(functions)]
    if locations:
        filtered = filtered[filtered['Where are you located ?'].isin(locations)]
    return filtered


# Use the function with both a title and a subtitle
if dashboard == 'General Survey Results':
    render_header("General Survey Results")
elif dashboard == 'Section 1: Employee Experience':
    render_header("Employee Experience: General HR Services Evaluation")
elif dashboard == 'Section 2: Recruiting & Onboarding':
    render_header("Recruiting & Onboarding")
elif dashboard == 'Section 3: Performance & Talent':
    render_header("Performance & Talent")
elif dashboard == 'Section 4: Learning':
    render_header("Learning")
elif dashboard == 'Section 5: Compensation':
    render_header("Compensation")
elif dashboard == 'Section 6: Payroll':
    render_header("Payroll")
elif dashboard == 'Section 7: Time Management':
    render_header("Time Management")
elif dashboard == 'Section 8: User Experience':
    render_header("User Experience")


def prepare_summaries(data):
    continent_to_country_code = {
        'Asia': 'KAZ',
        'Oceania': 'AUS',
        'North America': 'CAN',
        'South America': 'BRA',
        'Europe': 'DEU',
        'Africa': 'TCD'
    }
    country_code_to_continent = {v: k for k, v in continent_to_country_code.items()}
    location_summary = pd.DataFrame(data['Where are you located ?'].value_counts()).reset_index()
    location_summary.columns = ['Continent', 'Count']
    location_summary['Country_Code'] = location_summary['Continent'].map(continent_to_country_code)
    location_summary['Label'] = location_summary['Continent'].apply(
        lambda x: f"{x}: {location_summary.loc[location_summary['Continent'] == x, 'Count'].iloc[0]}")

    role_summary = pd.DataFrame(data['What is your role at the company ?'].value_counts()).reset_index()
    role_summary.columns = ['Role', 'Count']
    function_summary = pd.DataFrame(data['What function are you part of ?'].value_counts()).reset_index()
    function_summary.columns = ['Function', 'Count']
    return location_summary, role_summary, function_summary


filtered_data = apply_filters(data, st.session_state['selected_role'], st.session_state['selected_function'],
                              st.session_state['selected_location'])


############ GENERAL DASHBOARD STARTS ############
if dashboard == "General Survey Results":
    st.markdown(
        """
        <style>
        .top-bar {
            background-color: #f0f2f6;  /* Light grey background */
            text-align: left;
            display: flex;
            justify-content: flex-start;
            align-items: center;
            height: auto;
        }
        </style>
        """, unsafe_allow_html=True
    )

    # The top bar with centered and styled text
    st.markdown(
        f'<div class="top-bar" style="font-weight: normal; font-size: 17px; padding: 10px 20px 10px 20px; color: #333333;"> The survey has  &nbsp;<strong>{len(data)}</strong>&nbsp; respondents in total, distributed among different locations, roles and function.</div>',
        unsafe_allow_html=True
    )


    # Data preparation for display of survey summary
    def prepare_summaries(data):
        # Create a dictionary to map continents to proxy countries
        continent_to_country_code = {
            'Asia': 'KAZ',
            'Oceania': 'AUS',
            'North America': 'CAN',
            'South America': 'BRA',
            'Europe': 'DEU',
            'Africa': 'TCD'
        }
        country_code_to_continent = {v: k for k, v in continent_to_country_code.items()}
        location_summary = pd.DataFrame(data['Where are you located ?'].value_counts()).reset_index()
        location_summary.columns = ['Continent', 'Count']
        location_summary['Country_Code'] = location_summary['Continent'].map(continent_to_country_code)
        location_summary['Label'] = location_summary['Continent'].apply(
            lambda x: f"{x}: {location_summary.loc[location_summary['Continent'] == x, 'Count'].iloc[0]}")

        role_summary = pd.DataFrame(data['What is your role at the company ?'].value_counts()).reset_index()
        role_summary.columns = ['Role', 'Count']
        function_summary = pd.DataFrame(data['What function are you part of ?'].value_counts()).reset_index()
        function_summary.columns = ['Function', 'Count']
        return location_summary, role_summary, function_summary


    location_summary, role_summary, function_summary = prepare_summaries(filtered_data)

    st.markdown(
        """
        <style>
        .text-container {
            font-size: 15px;
            padding: 10px 0px;
            color: #333333;
        }
        </style>
        """, unsafe_allow_html=True
    )

    # A text container for filtering instructions
    st.markdown(
        f"""
        <div class="text-container" style="font-style: italic;">
        Filter the data by selecting tags from the sidebar. The charts below will be updated to reflect the distribution of the&nbsp;
        <strong>{len(filtered_data)}</strong>&nbsp;filtered respondents.
        </div>
        """,
        unsafe_allow_html=True
    )

    map_ratio = 0.5
    barcharts_ratio = 1 - map_ratio
    mark_color = '#336699'  # Steel Blue

    map_col, barcharts_col = st.columns([map_ratio, barcharts_ratio])
    # Map visualization
    with map_col:
        fig_continent = px.scatter_geo(location_summary,
                                       locations="Country_Code",
                                       size="Count",
                                       hover_name="Continent",
                                       text="Label",  # The text labels with continent names and counts
                                       color_discrete_sequence=[mark_color])

        fig_continent.update_geos(
            projection_type="natural earth",
            showcountries=True, countrycolor="lightgrey",
            showcoastlines=False, coastlinecolor="lightgrey",
            showland=True, landcolor="#F0F0F0",
            showocean=True, oceancolor="white",
            lataxis_showgrid=True,
            lonaxis_showgrid=True,
            lataxis_range=[-90, 90],
            lonaxis_range=[-180, 180]
        )

        # Update the layout for title and margins
        fig_continent.update_layout(
            title='by Continent',
            margin=dict(l=0, r=0, t=50, b=0),
            geo=dict(bgcolor='white')  # Set the background color of the geo part of the map
        )

        fig_continent.update_traces(
            marker=dict(size=location_summary['Count'] * 2, line=dict(width=0)),
            # Remove the white border by setting the line width to 0
            textposition='top center',
            textfont=dict(color='#333333', size=14)  # Set label font color and size
        )

        fig_continent.update_layout(hovermode=False)

        # Display the plot with full width
        st.plotly_chart(fig_continent, use_container_width=True)

    with barcharts_col:
        left_margin = 200  # Adjust this as necessary to align y-axes
        total_height = 460  # This is the total height for both bar charts, adjust as necessary.
        role_chart_height = total_height * 0.45
        function_chart_height = total_height * 0.55

        # Horizontal bar chart for "by Role"
        fig_role = px.bar(role_summary, y='Role', x='Count', orientation='h')
        fig_role.update_layout(
            title="by Role",
            margin=dict(l=left_margin, r=0, t=50, b=0),  # Set the left margin
            height=role_chart_height,
            showlegend=False
        )
        fig_role.update_traces(marker_color=mark_color, text=role_summary['Count'], textposition='outside')
        fig_role.update_yaxes(showticklabels=True, title='')
        fig_role.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_role, use_container_width=True)

        # Horizontal bar chart for "by Function"
        fig_function = px.bar(function_summary, y='Function', x='Count', orientation='h')
        fig_function.update_layout(
            title="by Function",
            margin=dict(l=left_margin, r=0, t=50, b=0),  # Set the left margin, the same as for fig_role
            height=function_chart_height,
            showlegend=False
        )
        fig_function.update_traces(marker_color=mark_color, text=function_summary['Count'], textposition='outside')
        fig_function.update_yaxes(showticklabels=True, title='')
        fig_function.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_function, use_container_width=True)


############ GENERAL DASHBOARD ENDS ############

##### THIS SECTION FOR SATISFACTION SCORES START ####
# MARIAS SCORE DISTRIBUTION FUNCTION
def score_distribution(data, column_index):
    # Extract the data series based on the column index
    data_series = data.iloc[:, column_index]

    # Calculate the percentage of each response
    value_counts = data_series.value_counts(normalize=True).sort_index() * 100

    # Ensure the value_counts includes all categories with zero counts for missing categories
    value_counts = value_counts.reindex(range(1, 6), fill_value=0)

    # Create the DataFrame

    # Calculate the median score
    raw_counts = data_series.value_counts().sort_index()
    scores = np.repeat(raw_counts.index, raw_counts.values)
    median_score = np.median(scores)

    return value_counts, median_score


#### Function to plot satisfaction proportions -- OLD
def plot_satisfaction_proportions(data_series, title):
    # Calculate satisfaction proportions
    score_counts = data_series.value_counts().sort_index().astype(int)
    total_satisfied = score_counts.get(4, 0) + score_counts.get(5, 0)
    total_dissatisfied = score_counts.get(1, 0) + score_counts.get(2, 0) + score_counts.get(3, 0)

    # Calculate proportions
    dissatisfied_proportions = [score_counts.get(i, 0) / total_dissatisfied if total_dissatisfied > 0 else 0 for i in
                                range(1, 4)]
    satisfied_proportions = [score_counts.get(i, 0) / total_satisfied if total_satisfied > 0 else 0 for i in
                             range(4, 6)]

    # Create the plotly figure for stacked bar chart
    fig = go.Figure()

    # Add 'Dissatisfied' segments
    cumulative_size = 0
    colors_dissatisfied = sns.color_palette("Blues_d", n_colors=3)
    for i, prop in enumerate(dissatisfied_proportions):
        fig.add_trace(go.Bar(
            x=[prop],
            y=['Dissatisfied'],
            orientation='h',
            name=f'{i + 1}',
            marker=dict(
                color=f'rgb({colors_dissatisfied[i][0] * 255},{colors_dissatisfied[i][1] * 255},{colors_dissatisfied[i][2] * 255})'),
            base=cumulative_size
        ))
        cumulative_size += prop

    # Add 'Satisfied' segments
    cumulative_size = 0
    colors_satisfied = sns.color_palette("Greens_d", n_colors=2)
    for i, prop in enumerate(satisfied_proportions):
        fig.add_trace(go.Bar(
            x=[prop],
            y=['Satisfied'],
            orientation='h',
            name=f'{i + 4}',
            marker=dict(
                color=f'rgb({colors_satisfied[i][0] * 255},{colors_satisfied[i][1] * 255},{colors_satisfied[i][2] * 255})'),
            base=cumulative_size
        ))
        cumulative_size += prop

    # Update layout and display in Streamlit
    fig.update_layout(
        title=title,
        barmode='stack',
        annotations=[
            dict(x=1.05, y=0, text=f'Total: {total_dissatisfied}', showarrow=False),
            dict(x=1.05, y=1, text=f'Total: {total_satisfied}', showarrow=False)
        ]
    )
    fig.update_xaxes(title_text="", visible=True, showticklabels=False)
    fig.update_yaxes(title_text="")

    st.plotly_chart(fig)  # Display the plot in Streamlit


def filter_by_satisfaction(data, satisfaction_level, column_index):
    if satisfaction_level != 'Select a satisfaction level':
        data = data[data.iloc[:, column_index] == satisfaction_options.index(satisfaction_level)]
    return data

def filter_by_comfort(data, comfort_level, column_index):
    if comfort_level != 'Select a comfort level':
        data = data[data.iloc[:, column_index] == comfort_options.index(comfort_level)]
    return data

##### THIS SECTION FOR SATISFACTION SCORES ENDS ####


##### THIS SECTION FOR SIDEBAR AND SENTIMENT ANALYSIS CHARTS START START START START ####
# Function to create Streamlit sentiment dashboard
# Initialize VADER sentiment analyzer
# Make sure the VADER lexicon is downloaded
# nltk.download('vader_lexicon')
# sentiment_analyzer = SentimentIntensityAnalyzer()

############ SENTIMENT ANALYSIS FUNCTION STARTS ############
def generate_wordclouds(df, score_col_idx, reasons_col_idx, custom_stopwords):
    # Custom stopwords
    stopwords_set = set(STOPWORDS)
    stopwords_set.update(custom_stopwords)

    # Filter the DataFrame for scores 4 and 5
    df_high_scores = df[df.iloc[:, score_col_idx].isin([4, 5])]

    # Filter the DataFrame for scores 1, 2, and 3
    df_low_scores = df[df.iloc[:, score_col_idx].isin([1, 2, 3])]

    # Generate the text for word clouds
    text_high_scores = ' '.join(df_high_scores.iloc[:, reasons_col_idx].astype(str))
    text_low_scores = ' '.join(df_low_scores.iloc[:, reasons_col_idx].astype(str))

    # Generate the word clouds
    wordcloud_high_scores = WordCloud(width=800, height=400, background_color='white', stopwords=stopwords_set, collocations=False).generate(text_high_scores)
    wordcloud_low_scores = WordCloud(width=800, height=400, background_color='white', stopwords=stopwords_set, collocations=False).generate(text_low_scores)

    # Create columns for displaying the word clouds side by side
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3 style='text-align: center; font-size: 20px; font-weight: normal;'>Word Cloud for High Scores</h3>", unsafe_allow_html=True)
        fig_high_scores, ax_high_scores = plt.subplots(figsize=(10, 5))
        ax_high_scores.imshow(wordcloud_high_scores, interpolation='bilinear')
        ax_high_scores.axis('off')
        st.pyplot(fig_high_scores)

    with col2:
        st.markdown("<h3 style='text-align: center; font-size: 20px; font-weight: normal;'>Word Cloud for Low Scores</h3>", unsafe_allow_html=True)
        fig_low_scores, ax_low_scores = plt.subplots(figsize=(10, 5))
        ax_low_scores.imshow(wordcloud_low_scores, interpolation='bilinear')
        ax_low_scores.axis('off')
        st.pyplot(fig_low_scores)


############ SENTIMENT ANALYSIS FUNCTION ENDS ############

# Function for sentiment analysis dashboard

def sentiment_dashboard(data_series, title):
    # Sidebar for control
    st.sidebar.markdown("### Filter Options")
    show_wordcloud = st.sidebar.checkbox("Show Word Cloud", value=True)
    filter_negative = st.sidebar.checkbox("Show Negative Comments", value=False)
    filter_positive = st.sidebar.checkbox("Show Positive Comments", value=False)

    # Initialize sentiment results and comment lists
    sentiment_results = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
    negative_comments = []
    positive_comments = []

    # Analyze sentiment and collect results
    for sentence in data_series.dropna():
        sentiment_scores = sentiment_analyzer.polarity_scores(sentence)
        compound_score = sentiment_scores['compound']

        if compound_score <= -0.05:
            sentiment_results['Negative'] += 1
            negative_comments.append((sentence, compound_score))
        elif compound_score >= 0.05:
            sentiment_results['Positive'] += 1
            positive_comments.append((sentence, compound_score))
        else:
            sentiment_results['Neutral'] += 1

    # Display word cloud
    if show_wordcloud:
        wordcloud = WordCloud(width=400, height=200, background_color='white').generate(' '.join(data_series.dropna()))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        st.pyplot(plt)  # Display word cloud in Streamlit

    # Display top negative and positive comments
    if filter_negative:
        st.markdown("### Top 5 Negative Comments")
        for comment, score in sorted(negative_comments, key=lambda x: x[1], reverse=True)[:5]:
            st.write(f"{comment} (Score: {score:.4f})")

    if filter_positive:
        st.markdown("### Top 5 Positive Comments")
        for comment, score in sorted(positive_comments, key=lambda x: x[1], reverse=True)[:5]:
            st.write(f"{comment} (Score: {score:.4f})")

    # Create stacked bar chart for sentiment distribution
    total = sum(sentiment_results.values())
    proportions = {k: v / total for k, v in sentiment_results.items()}

    fig = go.Figure()
    cumulative_size = 0
    for sentiment, proportion in proportions.items():
        color = 'lightgreen' if sentiment == 'Positive' else 'lightcoral' if sentiment == 'Negative' else 'lightgrey'
        fig.add_trace(go.Bar(x=[proportion], y=['Sentiment'], orientation='h', name=sentiment, base=cumulative_size,
                             marker=dict(color=color)))
        cumulative_size += proportion

    # Update layout and display chart in Streamlit
    fig.update_layout(
        title="Sentiment Distribution",
        barmode='stack',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False),
    )

    st.plotly_chart(fig)  # Display the stacked bar chart


##### THIS SECTION FOR SIDEBAR AND SENTIMENT ANALYSIS CHARTS END END END END ####

############ SECTION 1 STARTS ############
if dashboard == "Section 1: Employee Experience":

    filtered_data = apply_filters(data, st.session_state['selected_role'], st.session_state['selected_function'],
                                  st.session_state['selected_location'])

    q6ValuesCount, q6MedianScore = score_distribution(data, 11)
    q11ValuesCount, q11MedianScore = score_distribution(data, 13)

    # Question 4: What HR processes do you interact with the most in your day-to-day work ?
    q4_data = pd.DataFrame({
        'ID': filtered_data['ID'],
        'HR_Process': filtered_data['What HR processes do you interact with the most in your day-to-day work ?']
    })
    # Remove the last semicolon from each HR_Process value
    q4_data['HR_Process'] = q4_data['HR_Process'].str.rstrip(';')
    # Splitting the HR_Process values into separate lists of processes
    q4_data['HR_Process'] = q4_data['HR_Process'].str.split(';')
    # Explode the lists into separate rows while maintaining the corresponding ID
    q4_processed = q4_data.explode('HR_Process')
    # Reset index to maintain the original ID
    q4_processed.reset_index(drop=True, inplace=True)
    q4_count = q4_processed.groupby('HR_Process').size().reset_index(name='Count')

    # Question 5: In what areas do you think HR could improve its capabilities to enhance how they deliver services and support you ?
    q5_data = pd.DataFrame({
        'ID': filtered_data['ID'],
        'Improve_Area': filtered_data[
            'In what areas do you think HR could improve its capabilities to enhance how they deliver services and support you ?']
    })
    # Remove the last semicolon from each value
    q5_data['Improve_Area'] = q5_data['Improve_Area'].str.rstrip(';')
    # Splitting the values into separate lists of processes
    q5_data['Improve_Area'] = q5_data['Improve_Area'].str.split(';')
    # Explode the lists into separate rows while maintaining the corresponding ID
    q5_processed = q5_data.explode('Improve_Area')
    # Reset index to maintain the original ID
    q5_processed.reset_index(drop=True, inplace=True)
    q5_count = q5_processed.groupby('Improve_Area').size().reset_index(name='Count')

    # Question 4 and 5 combined
    # Merge the two dataset on function
    # Merge datasets by matching HR_Process and Improve_Area
    q4_q5_count = pd.merge(q4_count, q5_count, left_on='HR_Process', right_on='Improve_Area', how='outer')
    # Drop unnecessary columns
    q4_q5_count.drop(['Improve_Area'], axis=1, inplace=True)
    q4_q5_count.rename(
        columns={'HR_Process': 'HR Function', 'Count_x': 'HR_Process_Interacted', 'Count_y': 'Improvement_Areas'},
        inplace=True)
    q4_q5_count.sort_values('HR_Process_Interacted', ascending=False, inplace=True)
    # Separate 'None' row from the DataFrame
    none_row = q4_q5_count[q4_q5_count['HR Function'] == 'None']
    q4_q5_count = q4_q5_count[q4_q5_count['HR Function'] != 'None']

    # Sort 'HR_Process_Interacted' in descending order
    q4_q5_count.sort_values(by='HR_Process_Interacted', ascending=True, inplace=True)

    # Append 'None' row at the end
    q4_q5_count = pd.concat([none_row, q4_q5_count])
    # Reshape data into tidy format
    df_tidy = q4_q5_count.melt(id_vars='HR Function', var_name='Type', value_name='Count')

    # Question 7: How do you access HR Information ?
    q7_data = pd.DataFrame({'device': filtered_data["How do you access HR Information ?"]})
    q7_data['device'] = q7_data['device'].str.rstrip(';').str.split(';')
    q7_data = q7_data.explode('device')
    q7_data.dropna(inplace=True)
    # Count the occurrences of each device
    device_counts = q7_data['device'].value_counts().reset_index()
    device_counts.columns = ['device', 'count']
    # Calculate percentage
    device_counts['percentage'] = device_counts['count'] / device_counts['count'].sum() * 100

    st.markdown(
        """
        <style>
        .top-bar {
            background-color: #f0f2f6;  /* Light grey background */
            text-align: left;
            display: flex;
            justify-content: flex-start;
            align-items: center;
            height: auto;
        }
        </style>
        """, unsafe_allow_html=True
    )

    # Question 10: Do you find the HR department responsive to your inquiries and concerns?
    q10_responsiveness_count = (data.iloc[:, 15] == 'Yes').sum()
    q10_responsiveness_pct = q10_responsiveness_count / len(data) * 100

    highest_hr_process_interacted = q4_q5_count[q4_q5_count['HR Function'] != 'None']['HR_Process_Interacted'].max()
    highest_improvement_areas = q4_q5_count[q4_q5_count['HR Function'] != 'None']['Improvement_Areas'].max()
    most_used_device = device_counts.iloc[0]['device']

    # Summary of all outputs in the bar container
    st.markdown(
        f"""
            <style>
            .top-bar {{
                font-weight: normal;
                font-size: 17px;
                padding: 10px 20px;
                color: #333333;
                display: block;
                width: 100%;
                box-sizing: border-box;
            }}
            .top-bar ul, .top-bar li {{
            font-size: 17px;
            padding-left: 20px;
            margin: 0;
            }}
            </style>
            <div class="top-bar">
            This survey section is answered by all the <strong>{len(data)}</strong> survey participants:
            <ul>
                <li>{q10_responsiveness_pct:.0f}% of the respondents, {q10_responsiveness_count} employee(s), find the HR department responsive to their inquiries and concerns.</li>
                <li>The median satisfaction rating on overall HR services and support is {q6MedianScore}.</li>
                <li>The median satisfaction rating on the HR communication channels is {q11MedianScore}.</li>
                <li> Highest Process interacted with {highest_hr_process_interacted}</li>
                <li> Highest Improvement Area: {highest_improvement_areas}</li>
                <li> Most Device used: {most_used_device}</li>
            </ul>
            </div>
            """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <style>
        .text-container {
            font-size: 15px;
            padding: 10px 0px;
            color: #333333;
        }
        </style>
        """, unsafe_allow_html=True
    )

    # A text container for filtering instructions
    st.markdown(
        f"""
        <div class="text-container" style="font-style: italic;">
        Filter the data by selecting tags from the sidebar. The charts below will be updated to reflect the&nbsp;
        <strong>{len(filtered_data)}</strong>&nbsp;filtered respondents.
        </div>
        """,
        unsafe_allow_html=True
    )

    satisfaction_ratio = 0.6
    barcharts_ratio = 1 - satisfaction_ratio
    satisfaction_col, barcharts_col = st.columns([satisfaction_ratio, barcharts_ratio])

    st.markdown("""
        <style>
        .chart-container {
            padding-top: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

    with satisfaction_col:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        categories = ['Very Dissatisfied', 'Dissatisfied', 'Neutral', 'Satisfied', 'Very Satisfied']
        q6ValuesCount, q6MedianScore = score_distribution(filtered_data, 11)

        ratings_df = pd.DataFrame({'Satisfaction Level': categories, 'Percentage': q6ValuesCount.values})

        # Display title and median score
        title_html = f"<h2 style='font-size: 17px; font-family: Arial; color: #333333;'>Overall Rating on HR Services and Support</h2>"
        caption_html = f"<div style='font-size: 15px; font-family: Arial; color: #707070;'>The median satisfaction score is {q6MedianScore:.1f}</div>"
        st.markdown(title_html, unsafe_allow_html=True)
        st.markdown(caption_html, unsafe_allow_html=True)

        # Create a horizontal bar chart with Plotly
        fig = px.bar(ratings_df, y='Satisfaction Level', x='Percentage', text='Percentage',
                     orientation='h',
                     color='Satisfaction Level', color_discrete_map={
                'Very Dissatisfied': '#440154',  # Dark purple
                'Dissatisfied': '#3b528b',  # Dark blue
                'Neutral': '#21918c',  # Cyan
                'Satisfied': '#5ec962',  # Light green
                'Very Satisfied': '#fde725'  # Bright yellow
            })

        # Remove legend and axes titles
        fig.update_layout(showlegend=False, xaxis_visible=False, xaxis_title=None, yaxis_title=None, autosize=True,
                          height=300, margin=dict(l=20, r=20, t=30, b=20))

        # Format text on bars
        fig.update_traces(texttemplate='%{x:.1f}%', textposition='outside')
        fig.update_xaxes(range=[0, max(ratings_df['Percentage']) * 1.1])

        # Improve layout aesthetics
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        # Use Streamlit to display the Plotly chart
        st.plotly_chart(fig, use_container_width=True, key="overall_rating_bar_chart")
        st.markdown('</div>', unsafe_allow_html=True)

    with barcharts_col:
        satisfaction_options = ['Select a satisfaction level', 'Very Dissatisfied', 'Dissatisfied', 'Neutral',
                                'Satisfied', 'Very Satisfied']
        satisfaction_dropdown1 = st.selectbox('', satisfaction_options,
                                              key='satisfaction_dropdown1')

        satisfaction_filtered_data1 = filter_by_satisfaction(filtered_data, satisfaction_dropdown1, 11)

        location_summary1, role_summary1, function_summary1 = prepare_summaries(satisfaction_filtered_data1)
        left_margin = 150
        total_height = 310
        role_chart_height = total_height * 0.45
        function_chart_height = total_height * 0.55

        fig_role1 = px.bar(role_summary1, y='Role', x='Count', orientation='h')
        fig_role1.update_layout(title="by Role", margin=dict(l=left_margin, r=0, t=50, b=0),
                                height=role_chart_height, showlegend=False)
        fig_role1.update_traces(marker_color='#336699', text=role_summary1['Count'], textposition='outside')
        fig_role1.update_yaxes(showticklabels=True, title='')
        fig_role1.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_role1, use_container_width=True, key="roles_bar_chart1")

        fig_function1 = px.bar(function_summary1, y='Function', x='Count', orientation='h')
        fig_function1.update_layout(title="by Function", margin=dict(l=left_margin, r=0, t=50, b=0),
                                    height=function_chart_height, showlegend=False)
        fig_function1.update_traces(marker_color='#336699', text=function_summary1['Count'], textposition='outside')
        fig_function1.update_yaxes(showticklabels=True, title='')
        fig_function1.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_function1, use_container_width=True, key="functions_bar_chart1")

    with satisfaction_col:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        categories = ['Very Dissatisfied', 'Dissatisfied', 'Neutral', 'Satisfied', 'Very Satisfied']
        q11ValuesCount, q11MedianScore = score_distribution(filtered_data, 13)

        ratings_df = pd.DataFrame({'Satisfaction Level': categories, 'Percentage': q11ValuesCount.values})

        # Display title and median score
        title_html = f"<h2 style='font-size: 17px; font-family: Arial; color: #333333;'>Rating on HR Communication Channels</h2>"
        caption_html = f"<div style='font-size: 15px; font-family: Arial; color: #707070;'>The median satisfaction score is {q11MedianScore:.1f}</div>"
        st.markdown(title_html, unsafe_allow_html=True)
        st.markdown(caption_html, unsafe_allow_html=True)

        # Create a horizontal bar chart with Plotly
        fig = px.bar(ratings_df, y='Satisfaction Level', x='Percentage', text='Percentage',
                     orientation='h',
                     color='Satisfaction Level', color_discrete_map={
                'Very Dissatisfied': '#440154',  # Dark purple
                'Dissatisfied': '#3b528b',  # Dark blue
                'Neutral': '#21918c',  # Cyan
                'Satisfied': '#5ec962',  # Light green
                'Very Satisfied': '#fde725'  # Bright yellow
            })

        # Remove legend and axes titles
        fig.update_layout(showlegend=False, xaxis_visible=False, xaxis_title=None, yaxis_title=None, autosize=True,
                          height=300, margin=dict(l=20, r=20, t=30, b=20))
        fig.update_xaxes(range=[0, max(ratings_df['Percentage']) * 1.1])

        # Format text on bars
        fig.update_traces(texttemplate='%{x:.1f}%', textposition='outside')

        # Improve layout aesthetics
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        # Use Streamlit to display the Plotly chart
        st.plotly_chart(fig, use_container_width=True, key="rating_hr_communication_channels_bar_chart")
        st.markdown('</div>', unsafe_allow_html=True)

    with barcharts_col:
        satisfaction_dropdown2 = st.selectbox('', satisfaction_options,
                                              key='satisfaction_dropdown2')

        satisfaction_filtered_data2 = filter_by_satisfaction(filtered_data, satisfaction_dropdown2, 13)

        location_summary2, role_summary2, function_summary2 = prepare_summaries(satisfaction_filtered_data2)
        left_margin = 150
        total_height = 310
        role_chart_height = total_height * 0.45
        function_chart_height = total_height * 0.55

        fig_role2 = px.bar(role_summary2, y='Role', x='Count', orientation='h')
        fig_role2.update_layout(title="by Role", margin=dict(l=left_margin, r=0, t=50, b=0),
                                height=role_chart_height, showlegend=False)
        fig_role2.update_traces(marker_color='#336699', text=role_summary2['Count'], textposition='outside')
        fig_role2.update_yaxes(showticklabels=True, title='')
        fig_role2.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_role2, use_container_width=True, key="roles_bar_chart2")

        fig_function2 = px.bar(function_summary2, y='Function', x='Count', orientation='h')
        fig_function2.update_layout(title="by Function", margin=dict(l=left_margin, r=0, t=50, b=0),
                                    height=function_chart_height, showlegend=False)
        fig_function2.update_traces(marker_color='#336699', text=function_summary2['Count'], textposition='outside')
        fig_function2.update_yaxes(showticklabels=True, title='')
        fig_function2.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_function2, use_container_width=True, key="functions_bar_chart2")


    # Define colors for each device
    colors = {'Computer': '#440154', 'Mobile': '#5ec962', 'Tablet': '#3b528b'}

    # Set up space for two visualizations
    fig_q4_ratio = 0.65
    fig_q7_ratio = 1 - fig_q4_ratio
    q4_col, q7_col = st.columns([fig_q4_ratio, fig_q7_ratio])

    with q4_col:
        # Plot for HR Processes in the first column
        fig_q4 = go.Figure(data=[
            go.Bar(
            name='Improvement Areas',
            y=df_tidy[df_tidy['Type'] == 'Improvement_Areas']['HR Function'],#make it horizontal bar chart to show texts completely
            x=df_tidy[df_tidy['Type'] == 'Improvement_Areas']['Count'], #make it horizontal bar chart to show texts completely
            marker_color='#3b528b',
            orientation='h' #make it horizontal bar chart to show texts completely
            ),
            go.Bar(
            name='Employee Interaction',
            y=df_tidy[df_tidy['Type'] == 'HR_Process_Interacted']['HR Function'],#make it horizontal bar chart to show texts completely
            x=df_tidy[df_tidy['Type'] == 'HR_Process_Interacted']['Count'], #make it horizontal bar chart to show texts completely
            marker_color='#5ec962',
            orientation='h' #make it horizontal bar chart to show texts completely
            )
        ])
        fig_q4.update_layout(
            title='HR Processes: Employee Interaction vs Improvement Areas',
            title_font=dict(size=17, family="Arial", color='#333333'),
            xaxis_title='HR Process',
            yaxis_title='Number of Respondents',
            barmode='group',
            annotations=[
                dict(
                    xref='paper', yref='paper', x=0, y=1.1,
                    xanchor='left', yanchor='top',
                    text="<i>Each respondent is able to select more than one HR process</i>",
                    font=dict(family='Arial', size=12, color='#707070'),
                    showarrow=False)
            ],
            legend=dict(
                orientation="h",
                x=0.5,
                xanchor="center",
                y=-0.2,
                yanchor="top"
            ),
            margin=dict(l=22, r=20, t=70, b=70)
        )
        st.plotly_chart(fig_q4, use_container_width=True)

    # Plot for Device Usage in the second column
    with q7_col:
        fig_q7 = px.bar(device_counts, x='percentage', y='device', text='percentage', orientation='h', color='device',
                        color_discrete_map=colors)
        fig_q7.update_layout(
            title='Devices Used to Access HR Information',
            title_font=dict(size=17, family="Arial", color='#333333'),
            xaxis={'visible': False, 'showticklabels': False},
            yaxis_title=None,
            showlegend=False
        )
        fig_q7.update_traces(texttemplate='%{text:.0f}%', textposition='outside')
        st.plotly_chart(fig_q7, use_container_width=True)
    
    # Question 9: Which reason(s) drive that score ?
    # Display the reasons for communication channel satisfaction
    st.markdown('<h1 style="font-size:17px;font-family:Arial;color:#333333;">The Reasons for Ratings on Communication Channels</h1>', unsafe_allow_html=True)

    # Example usage
    communication_stopwords = ["communication", "channels", "HR", "information", "important", "informed", "stay", "communicated", "employees", "company", "help", "communicates", "need", "everyone", "makes"]

    # Run this code in a Streamlit app
    if __name__ == "__main__":
        st.markdown("<h1 style='text-align: center; font-size: 24px; font-weight: normal;'>Word Cloud Visualization</h1>", unsafe_allow_html=True)
        generate_wordclouds(filtered_data, 13, 14, communication_stopwords)

    
    from transformers import pipeline

    @st.cache_resource(show_spinner=False)
    def load_model():
        try:
            model = pipeline("summarization", model="csebuetnlp/mT5_multilingual_XLSum")
            return model
        except Exception as e:
            st.error(f"Error loading the summarizer model: {e}")
            return None

    def main():
        st.title("Summarization with Transformers")
        
        # Display a message or spinner while the model is loading
        with st.spinner("Loading summarization model..."):
            summarizer = load_model()
        
        if summarizer:
            st.write("Successfully loaded the summarizer model.")
            # Add your Streamlit app content here
            user_input = st.text_area("Enter text for summarization")
            if st.button("Summarize"):
                with st.spinner("Summarizing..."):
                    summary = summarizer(user_input, max_length=100, min_length=25, do_sample=False)
                    st.write(summary[0]['summary_text'])
        else:
            st.error("Model could not be loaded. Please check the logs for more details.")

    if __name__ == "__main__":
        main()

    


    

############ SECTION 1 ENDS ############


############ SECTION 2 STARTS ############
if dashboard == 'Section 2: Recruiting & Onboarding':
    filtered_data = apply_filters(data, st.session_state['selected_role'], st.session_state['selected_function'],
                                  st.session_state['selected_location'])
    
    
    # A text container for filtering instructions
    st.markdown(
        f"""
        <div class="text-container" style="font-style: italic;">
        Filter the data by selecting tags from the sidebar. The charts below will be updated to reflect the&nbsp;
        <strong>{len(filtered_data)}</strong>&nbsp;filtered respondents.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    ### Question11: How long have you been part of the company ?
    q11_data_available_count = (filtered_data.iloc[:, 16] == 'Less than a year').sum()
    q11_data_available_pct = q11_data_available_count / len(filtered_data) * 100
   
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    How long have you been part of the company?
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"{q11_data_available_pct:.2f}% of the respondents, {q11_data_available_count} employee(s), have been part of the company LESS THAN a year.")
    
    
    ### Question12: How would rate the recruiting process ?
    satisfaction_ratio = 0.6
    barcharts_ratio = 1 - satisfaction_ratio
    satisfaction_col, barcharts_col = st.columns([satisfaction_ratio, barcharts_ratio])

    st.markdown("""
        <style>
        .chart-container {
            padding-top: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

    with satisfaction_col:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        categories = ['Very Dissatisfied', 'Dissatisfied', 'Neutral', 'Satisfied', 'Very Satisfied']
        q12ValuesCount, q12MedianScore = score_distribution(filtered_data, 17)

        ratings_df = pd.DataFrame({'Satisfaction Level': categories, 'Percentage': q12ValuesCount.values})

        # Display title and median score
        title_html = f"<h2 style='font-size: 17px; font-family: Arial; color: #333333;'>Rating on the Recruiting Process</h2>"
        caption_html = f"<div style='font-size: 15px; font-family: Arial; color: #707070;'>The median satisfaction score is {q12MedianScore:.1f}</div>"
        st.markdown(title_html, unsafe_allow_html=True)
        st.markdown(caption_html, unsafe_allow_html=True)

        # Create a horizontal bar chart with Plotly
        fig = px.bar(ratings_df, y='Satisfaction Level', x='Percentage', text='Percentage',
                     orientation='h',
                     color='Satisfaction Level', color_discrete_map={
                'Very Dissatisfied': '#440154',  # Dark purple
                'Dissatisfied': '#3b528b',  # Dark blue
                'Neutral': '#21918c',  # Cyan
                'Satisfied': '#5ec962',  # Light green
                'Very Satisfied': '#fde725'  # Bright yellow
            })

        # Remove legend and axes titles
        fig.update_layout(showlegend=False, xaxis_visible=False, xaxis_title=None, yaxis_title=None, autosize=True,
                          height=300, margin=dict(l=20, r=20, t=30, b=20))

        # Format text on bars
        fig.update_traces(texttemplate='%{x:.1f}%', textposition='outside')
        fig.update_xaxes(range=[0, max(ratings_df['Percentage']) * 1.1])

        # Improve layout aesthetics
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        # Use Streamlit to display the Plotly chart
        st.plotly_chart(fig, use_container_width=True, key="overall_rating_bar_chart")
        st.markdown('</div>', unsafe_allow_html=True)

    with barcharts_col:
        satisfaction_options = ['Select a satisfaction level', 'Very Dissatisfied', 'Dissatisfied', 'Neutral',
                                'Satisfied', 'Very Satisfied']
        satisfaction_dropdown1 = st.selectbox('', satisfaction_options,
                                              key='satisfaction_dropdown1')

        satisfaction_filtered_data1 = filter_by_satisfaction(filtered_data, satisfaction_dropdown1, 17)

        location_summary1, role_summary1, function_summary1 = prepare_summaries(satisfaction_filtered_data1)
        left_margin = 150
        total_height = 310
        role_chart_height = total_height * 0.45
        function_chart_height = total_height * 0.55

        fig_role1 = px.bar(role_summary1, y='Role', x='Count', orientation='h')
        fig_role1.update_layout(title="by Role", margin=dict(l=left_margin, r=0, t=50, b=0),
                                height=role_chart_height, showlegend=False)
        fig_role1.update_traces(marker_color='#336699', text=role_summary1['Count'], textposition='outside')
        fig_role1.update_yaxes(showticklabels=True, title='')
        fig_role1.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_role1, use_container_width=True, key="roles_bar_chart1")

        fig_function1 = px.bar(function_summary1, y='Function', x='Count', orientation='h')
        fig_function1.update_layout(title="by Function", margin=dict(l=left_margin, r=0, t=50, b=0),
                                    height=function_chart_height, showlegend=False)
        fig_function1.update_traces(marker_color='#336699', text=function_summary1['Count'], textposition='outside')
        fig_function1.update_yaxes(showticklabels=True, title='')
        fig_function1.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_function1, use_container_width=True, key="functions_bar_chart1")
        
        
    ### Question13: What reason(s) drive that score ?
    ### Part I: negative reasons for recruiting process
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Reasons that drive scores: 1 - Very Dissatisfied / 2 - Dissatisfied / 3 - Neutral 
    </h2>
    """,
    unsafe_allow_html=True
    )
    
    q13a_data = pd.DataFrame({'negative_reasons': filtered_data.iloc[:, 18]})
    q13a_data['negative_reasons'] = q13a_data['negative_reasons'].str.rstrip(';').str.split(';')
    q13a_data = q13a_data.explode('negative_reasons')
    q13a_data.dropna(inplace=True)

    # Count the occurrences of each negative reason
    negative_reason_recruiting_counts = q13a_data['negative_reasons'].value_counts().reset_index()
    negative_reason_recruiting_counts.columns = ['negative_reasons', 'count']

    # Calculate percentage
    negative_reason_recruiting_counts['percentage'] = negative_reason_recruiting_counts['count'] / len(
        filtered_data) * 100

    # Create a vertical bar chart
    fig6 = px.bar(negative_reason_recruiting_counts, x='negative_reasons', y='percentage', text='count',
                  color='negative_reasons', color_discrete_sequence=['#FFA500'])

    # make a tree map on the negative reasons
    fig10 = px.treemap(negative_reason_recruiting_counts, path=['negative_reasons'], values='count', color='count',
                       color_continuous_scale='RdBu')

    # Show the chart
    st.plotly_chart(fig6, use_container_width=False)
    st.plotly_chart(fig10, use_container_width=False)

    ### Part II:  positive reasons for recruiting process
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Reasons that drive scores: 4 - Satisfied / 5 - Very Satisfied
    </h2>
    """,
    unsafe_allow_html=True
    )
    
    
    q13b_data = pd.DataFrame({'positive_reasons': filtered_data.iloc[:, 19]})
    q13b_data['positive_reasons'] = q13b_data['positive_reasons'].str.rstrip(';').str.split(';')
    q13b_data = q13b_data.explode('positive_reasons')
    q13b_data.dropna(inplace=True)

    # Count the occurrences of each positive reason
    positive_reason_recruiting_counts = q13b_data['positive_reasons'].value_counts().reset_index()
    positive_reason_recruiting_counts.columns = ['positive_reasons', 'count']

    # Calculate percentage
    positive_reason_recruiting_counts['percentage'] = positive_reason_recruiting_counts['count'] / len(
        filtered_data) * 100

    # Create a vertical bar chart
    fig7 = px.bar(positive_reason_recruiting_counts, x='positive_reasons', y='percentage', text='count',
                  color='positive_reasons', color_discrete_sequence=['#519DE9'])

    # make a tree map on the positive reasons
    fig9 = px.treemap(positive_reason_recruiting_counts, path=['positive_reasons'], values='count', color='count',
                      color_continuous_scale='RdBu')

    # Show the chart
    st.plotly_chart(fig7, use_container_width=False)
    st.plotly_chart(fig9, use_container_width=False)
    
    
    
    ### Question14: What aspect of the recruiting process took the most time and requires improvements ?
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Aspects of the Recruiting Process that Require Improvements
    </h2>
    """,
    unsafe_allow_html=True
    )
    
   
    q14_data = pd.DataFrame({'recruting process that required improvement': filtered_data.iloc[:, 20]})

    q14_data['recruting process that required improvement'] = q14_data[
        'recruting process that required improvement'].str.rstrip(';').str.split(';')
    q14_data = q14_data.explode('recruting process that required improvement')
    q14_data.dropna(inplace=True)

    # Count the occurrences of each aspect that required improvement
    aspect_recruiting_counts = q14_data['recruting process that required improvement'].value_counts().reset_index()
    aspect_recruiting_counts.columns = ['recruting process that required improvement', 'count']

    # Calculate percentage
    aspect_recruiting_counts['percentage'] = aspect_recruiting_counts['count'] / len(filtered_data) * 100

    # Create a vertical bar chart
    fig8 = px.bar(aspect_recruiting_counts, x='recruting process that required improvement', y='percentage',
                  text='count', color='recruting process that required improvement',
                  color_discrete_sequence=['#FF7F7F'])

    # make a tree map on the aspect that required improvement
    fig11 = px.treemap(aspect_recruiting_counts, path=['recruting process that required improvement'], values='count',
                       color='count', color_continuous_scale='RdBu')

    # Show the chart
    st.plotly_chart(fig8, use_container_width=False)
    st.plotly_chart(fig11, use_container_width=False)
    
    
    ### Question15: From 1 to 5, how would you rate the onboarding process ?
    satisfaction_ratio = 0.6
    barcharts_ratio = 1 - satisfaction_ratio
    satisfaction_col, barcharts_col = st.columns([satisfaction_ratio, barcharts_ratio])

    st.markdown("""
        <style>
        .chart-container {
            padding-top: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

    with satisfaction_col:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        categories = ['Very Dissatisfied', 'Dissatisfied', 'Neutral', 'Satisfied', 'Very Satisfied']
        q15ValuesCount, q15MedianScore = score_distribution(filtered_data, 21)

        ratings_df = pd.DataFrame({'Satisfaction Level': categories, 'Percentage': q15ValuesCount.values})

        # Display title and median score
        title_html = f"<h2 style='font-size: 17px; font-family: Arial; color: #333333;'>Rating on the Onboarding Process</h2>"
        caption_html = f"<div style='font-size: 15px; font-family: Arial; color: #707070;'>The median satisfaction score is {q15MedianScore:.1f}</div>"
        st.markdown(title_html, unsafe_allow_html=True)
        st.markdown(caption_html, unsafe_allow_html=True)

        # Create a horizontal bar chart with Plotly
        fig = px.bar(ratings_df, y='Satisfaction Level', x='Percentage', text='Percentage',
                     orientation='h',
                     color='Satisfaction Level', color_discrete_map={
                'Very Dissatisfied': '#440154',  # Dark purple
                'Dissatisfied': '#3b528b',  # Dark blue
                'Neutral': '#21918c',  # Cyan
                'Satisfied': '#5ec962',  # Light green
                'Very Satisfied': '#fde725'  # Bright yellow
            })

        # Remove legend and axes titles
        fig.update_layout(showlegend=False, xaxis_visible=False, xaxis_title=None, yaxis_title=None, autosize=True,
                          height=300, margin=dict(l=20, r=20, t=30, b=20))

        # Format text on bars
        fig.update_traces(texttemplate='%{x:.1f}%', textposition='outside')
        fig.update_xaxes(range=[0, max(ratings_df['Percentage']) * 1.1])

        # Improve layout aesthetics
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        # Use Streamlit to display the Plotly chart
        st.plotly_chart(fig, use_container_width=True, key="overall_rating_bar_chart")
        st.markdown('</div>', unsafe_allow_html=True)

    with barcharts_col:
        satisfaction_options = ['Select a satisfaction level', 'Very Dissatisfied', 'Dissatisfied', 'Neutral',
                                'Satisfied', 'Very Satisfied']
        satisfaction_dropdown15 = st.selectbox('', satisfaction_options,
                                              key='satisfaction_dropdown15')

        satisfaction_filtered_data15 = filter_by_satisfaction(filtered_data, satisfaction_dropdown15, 21)

        location_summary1, role_summary1, function_summary1 = prepare_summaries(satisfaction_filtered_data15)
        left_margin = 150
        total_height = 310
        role_chart_height = total_height * 0.45
        function_chart_height = total_height * 0.55

        fig_role1 = px.bar(role_summary1, y='Role', x='Count', orientation='h')
        fig_role1.update_layout(title="by Role", margin=dict(l=left_margin, r=0, t=50, b=0),
                                height=role_chart_height, showlegend=False)
        fig_role1.update_traces(marker_color='#336699', text=role_summary1['Count'], textposition='outside')
        fig_role1.update_yaxes(showticklabels=True, title='')
        fig_role1.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_role1, use_container_width=True, key="roles_bar_chart1")

        fig_function1 = px.bar(function_summary1, y='Function', x='Count', orientation='h')
        fig_function1.update_layout(title="by Function", margin=dict(l=left_margin, r=0, t=50, b=0),
                                    height=function_chart_height, showlegend=False)
        fig_function1.update_traces(marker_color='#336699', text=function_summary1['Count'], textposition='outside')
        fig_function1.update_yaxes(showticklabels=True, title='')
        fig_function1.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_function1, use_container_width=True, key="functions_bar_chart1")
    
    
    ### Question16: What reason(s) drive that score ?
    ### Part I: negative reasons for onboarding process
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Reasons that drive scores: 1 - Very Dissatisfied / 2 - Dissatisfied / 3 - Neutral 
    </h2>
    """,
    unsafe_allow_html=True
    )
    
    
    q16a_data = pd.DataFrame({'negative_reasons': filtered_data.iloc[:, 22]})
    q16a_data['negative_reasons'] = q16a_data['negative_reasons'].str.rstrip(';').str.split(';')
    q16a_data = q16a_data.explode('negative_reasons')
    q16a_data.dropna(inplace=True)

    # Count the occurrences of each negative reason
    negative_reason_recruiting_counts = q16a_data['negative_reasons'].value_counts().reset_index()
    negative_reason_recruiting_counts.columns = ['negative_reasons', 'count']

    # Calculate percentage
    negative_reason_recruiting_counts['percentage'] = negative_reason_recruiting_counts['count'] / len(
        filtered_data) * 100

    # Create a vertical bar chart
    fig13 = px.bar(negative_reason_recruiting_counts, x='negative_reasons', y='percentage', text='count',
                   color='negative_reasons', color_discrete_sequence=['#FFA500'])

    # make a tree map on the negative reasons
    fig14 = px.treemap(negative_reason_recruiting_counts, path=['negative_reasons'], values='count', color='count',
                       color_continuous_scale='RdBu')

    # Show the chart
    st.plotly_chart(fig13, use_container_width=False)
    st.plotly_chart(fig14, use_container_width=False)
    
    
    ### Part II:  positive reasons for onboarding process
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Reasons that drive scores: 4 - Satisfied / 5 - Very Satisfied
    </h2>
    """,
    unsafe_allow_html=True
    )
    
    q16b_data = pd.DataFrame({'positive_reasons': filtered_data.iloc[:, 23]})
    q16b_data['positive_reasons'] = q16b_data['positive_reasons'].str.rstrip(';').str.split(';')
    q16b_data = q16b_data.explode('positive_reasons')
    q16b_data.dropna(inplace=True)

    # Count the occurrences of each positive reason
    positive_reason_recruiting_counts = q16b_data['positive_reasons'].value_counts().reset_index()
    positive_reason_recruiting_counts.columns = ['positive_reasons', 'count']

    # Calculate percentage
    positive_reason_recruiting_counts['percentage'] = positive_reason_recruiting_counts['count'] / len(
        filtered_data) * 100

    # Create a vertical bar chart
    fig15 = px.bar(positive_reason_recruiting_counts, x='positive_reasons', y='percentage', text='count',
                   color='positive_reasons', color_discrete_sequence=['#519DE9'])

    # make a tree map on the positive reasons
    fig16 = px.treemap(positive_reason_recruiting_counts, path=['positive_reasons'], values='count', color='count',
                       color_continuous_scale='RdBu')

    # Show the chart
    st.plotly_chart(fig15, use_container_width=False)
    st.plotly_chart(fig16, use_container_width=False)
    
    
    ### Question17: What part of the Onboarding process was particulary helpful ?
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Part of the Onboarding process that is Helpful
    </h2>
    """,
    unsafe_allow_html=True
    )
    
    q17_data = pd.DataFrame({'helpful_onboarding_process': filtered_data.iloc[:, 24]})
    q17_data['helpful_onboarding_process'] = q17_data['helpful_onboarding_process'].str.rstrip(';').str.split(';')
    q17_data = q17_data.explode('helpful_onboarding_process')
    q17_data.dropna(inplace=True)

    # Count the occurrences of each aspect that required improvement
    helpful_onboarding_counts = q17_data['helpful_onboarding_process'].value_counts().reset_index()
    helpful_onboarding_counts.columns = ['helpful_onboarding_process', 'count']

    # Calculate percentage
    helpful_onboarding_counts['percentage'] = helpful_onboarding_counts['count'] / len(filtered_data) * 100

    # Create a vertical bar chart
    fig17 = px.bar(helpful_onboarding_counts, x='helpful_onboarding_process', y='percentage', text='count',
                   color='helpful_onboarding_process', color_discrete_sequence=['#519DE9'])

    # make a tree map on the aspect that required improvement
    fig18 = px.treemap(helpful_onboarding_counts, path=['helpful_onboarding_process'], values='count', color='count',
                       color_continuous_scale='RdBu')

    # Show the chart
    st.plotly_chart(fig17, use_container_width=False)
    st.plotly_chart(fig18, use_container_width=False)
    
    
    ### Question 18: What part of the Onboarding process could be improved
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Part of the Onboarding Process Could Be Improved
    </h2>
    """,
    unsafe_allow_html=True
    )

    # onboarding process to improve
    q18_data = pd.DataFrame({'onboarding_process_to_improve': filtered_data.iloc[:, 25]})
    q18_data['onboarding_process_to_improve'] = q18_data['onboarding_process_to_improve'].str.rstrip(';').str.split(';')
    q18_data = q18_data.explode('onboarding_process_to_improve')
    q18_data.dropna(inplace=True)

    # Count the occurrences of each aspect that required improvement
    aspect_onboarding_counts = q18_data['onboarding_process_to_improve'].value_counts().reset_index()
    aspect_onboarding_counts.columns = ['onboarding_process_to_improve', 'count']

    # Calculate percentage
    aspect_onboarding_counts['percentage'] = aspect_onboarding_counts['count'] / len(filtered_data) * 100

    # Create a vertical bar chart
    fig19 = px.bar(aspect_onboarding_counts, x='onboarding_process_to_improve', y='percentage', text='count',
                   color='onboarding_process_to_improve', color_discrete_sequence=['#FF7F7F'])

    # make a tree map on the aspect that required improvement
    fig20 = px.treemap(aspect_onboarding_counts, path=['onboarding_process_to_improve'], values='count', color='count',
                       color_continuous_scale='RdBu')

    # Show the chart
    st.plotly_chart(fig19, use_container_width=False)
    st.plotly_chart(fig20, use_container_width=False)
    
############ SECTION 2 ENDS ############


############ SECTION 3 STARTS ############    
if dashboard == 'Section 3: Performance & Talent':
    filtered_data = apply_filters(data, st.session_state['selected_role'], st.session_state['selected_function'],
                                  st.session_state['selected_location'])
    
    
    # A text container for filtering instructions
    st.markdown(
        f"""
        <div class="text-container" style="font-style: italic;">
        Filter the data by selecting tags from the sidebar. The charts below will be updated to reflect the&nbsp;
        <strong>{len(filtered_data)}</strong>&nbsp;filtered respondents.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    ### Question19: From 1 to 5, how satisfied are you with the company's performance evaluation and feedback process ?
    satisfaction_ratio = 0.6
    barcharts_ratio = 1 - satisfaction_ratio
    satisfaction_col, barcharts_col = st.columns([satisfaction_ratio, barcharts_ratio])

    st.markdown("""
        <style>
        .chart-container {
            padding-top: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

    with satisfaction_col:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        categories = ['Very Dissatisfied', 'Dissatisfied', 'Neutral', 'Satisfied', 'Very Satisfied']
        q19ValuesCount, q19MedianScore = score_distribution(filtered_data, 26)

        ratings_df = pd.DataFrame({'Satisfaction Level': categories, 'Percentage': q19ValuesCount.values})

        # Display title and median score
        title_html = f"<h2 style='font-size: 17px; font-family: Arial; color: #333333;'>Rating on Company's Performance Evaluation and Feedback Process</h2>"
        caption_html = f"<div style='font-size: 15px; font-family: Arial; color: #707070;'>The median satisfaction score is {q19MedianScore:.1f}</div>"
        st.markdown(title_html, unsafe_allow_html=True)
        st.markdown(caption_html, unsafe_allow_html=True)

        # Create a horizontal bar chart with Plotly
        fig = px.bar(ratings_df, y='Satisfaction Level', x='Percentage', text='Percentage',
                     orientation='h',
                     color='Satisfaction Level', color_discrete_map={
                'Very Dissatisfied': '#440154',  # Dark purple
                'Dissatisfied': '#3b528b',  # Dark blue
                'Neutral': '#21918c',  # Cyan
                'Satisfied': '#5ec962',  # Light green
                'Very Satisfied': '#fde725'  # Bright yellow
            })

        # Remove legend and axes titles
        fig.update_layout(showlegend=False, xaxis_visible=False, xaxis_title=None, yaxis_title=None, autosize=True,
                          height=300, margin=dict(l=20, r=20, t=30, b=20))

        # Format text on bars
        fig.update_traces(texttemplate='%{x:.1f}%', textposition='outside')
        fig.update_xaxes(range=[0, max(ratings_df['Percentage']) * 1.1])

        # Improve layout aesthetics
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        # Use Streamlit to display the Plotly chart
        st.plotly_chart(fig, use_container_width=True, key="overall_rating_bar_chart")
        st.markdown('</div>', unsafe_allow_html=True)

    with barcharts_col:
        satisfaction_options = ['Select a satisfaction level', 'Very Dissatisfied', 'Dissatisfied', 'Neutral',
                                'Satisfied', 'Very Satisfied']
        satisfaction_dropdown1 = st.selectbox('', satisfaction_options,
                                              key='satisfaction_dropdown1')

        satisfaction_filtered_data1 = filter_by_satisfaction(filtered_data, satisfaction_dropdown1, 26)

        location_summary1, role_summary1, function_summary1 = prepare_summaries(satisfaction_filtered_data1)
        left_margin = 150
        total_height = 310
        role_chart_height = total_height * 0.45
        function_chart_height = total_height * 0.55

        fig_role1 = px.bar(role_summary1, y='Role', x='Count', orientation='h')
        fig_role1.update_layout(title="by Role", margin=dict(l=left_margin, r=0, t=50, b=0),
                                height=role_chart_height, showlegend=False)
        fig_role1.update_traces(marker_color='#336699', text=role_summary1['Count'], textposition='outside')
        fig_role1.update_yaxes(showticklabels=True, title='')
        fig_role1.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_role1, use_container_width=True, key="roles_bar_chart1")

        fig_function1 = px.bar(function_summary1, y='Function', x='Count', orientation='h')
        fig_function1.update_layout(title="by Function", margin=dict(l=left_margin, r=0, t=50, b=0),
                                    height=function_chart_height, showlegend=False)
        fig_function1.update_traces(marker_color='#336699', text=function_summary1['Count'], textposition='outside')
        fig_function1.update_yaxes(showticklabels=True, title='')
        fig_function1.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_function1, use_container_width=True, key="functions_bar_chart1")
    
    
    ### Question20: Which reason(s) drive that score ?
    ### Missing worcloud
    
    
    ### Question21: From 1 to 5, how comfortable do you feel discussing your career goals and development with your manager? 
    with satisfaction_col:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        categories = ['Very Uncomfortable', 'Uncomfortable', 'Hesitant', 'Comfortable', 'Very Comfortable']
        q21ValuesCount, q21MedianScore = score_distribution(filtered_data, 28)

        ratings_df = pd.DataFrame({'Comfort Level': categories, 'Percentage': q21ValuesCount.values})

        # Display title and median score
        title_html = f"<h2 style='font-size: 17px; font-family: Arial; color: #333333;'>Comfort Level in Discussing Career Goals         and Development with Manager</h2>"
        caption_html = f"<div style='font-size: 15px; font-family: Arial; color: #707070;'>The median comfort score is                   {q21MedianScore:.1f}</div>"
        st.markdown(title_html, unsafe_allow_html=True)
        st.markdown(caption_html, unsafe_allow_html=True)

        # Create a horizontal bar chart with Plotly
        fig = px.bar(ratings_df, y='Comfort Level', x='Percentage', text='Percentage',
                     orientation='h',
                     color='Comfort Level', color_discrete_map={
                'Very Uncomfortable': '#440154',  # Dark purple
                'Uncomfortable': '#3b528b',  # Dark blue
                'Hesitant': '#21918c',  # Cyan
                'Comfortable': '#5ec962',  # Light green
                'Very Comfortable': '#fde725'  # Bright yellow
            })

        # Remove legend and axes titles
        fig.update_layout(showlegend=False, xaxis_visible=False, xaxis_title=None, yaxis_title=None, autosize=True,
                          height=300, margin=dict(l=20, r=20, t=30, b=20))

        # Format text on bars
        fig.update_traces(texttemplate='%{x:.1f}%', textposition='outside')
        fig.update_xaxes(range=[0, max(ratings_df['Percentage']) * 1.1])

        # Improve layout aesthetics
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        # Use Streamlit to display the Plotly chart
        st.plotly_chart(fig, use_container_width=True, key="overall_rating_bar_chart")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with barcharts_col:
        comfort_options = ['Select a comfort level', 'Very Uncomfortable', 'Uncomfortable', 'Hesitant',
                                'Comfortable', 'Very Comfortable']
        comfort_dropdown1 = st.selectbox('', comfort_options,
                                              key='comfort_dropdown1')

        comfort_filtered_data1 = filter_by_comfort(filtered_data, comfort_dropdown1, 28)

        location_summary1, role_summary1, function_summary1 = prepare_summaries(comfort_filtered_data1)
        left_margin = 150
        total_height = 310
        role_chart_height = total_height * 0.45
        function_chart_height = total_height * 0.55

        fig_role1 = px.bar(role_summary1, y='Role', x='Count', orientation='h')
        fig_role1.update_layout(title="by Role", margin=dict(l=left_margin, r=0, t=50, b=0),
                                height=role_chart_height, showlegend=False)
        fig_role1.update_traces(marker_color='#336699', text=role_summary1['Count'], textposition='outside')
        fig_role1.update_yaxes(showticklabels=True, title='')
        fig_role1.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_role1, use_container_width=True, key="roles_bar_chart1")

        fig_function1 = px.bar(function_summary1, y='Function', x='Count', orientation='h')
        fig_function1.update_layout(title="by Function", margin=dict(l=left_margin, r=0, t=50, b=0),
                                    height=function_chart_height, showlegend=False)
        fig_function1.update_traces(marker_color='#336699', text=function_summary1['Count'], textposition='outside')
        fig_function1.update_yaxes(showticklabels=True, title='')
        fig_function1.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_function1, use_container_width=True, key="functions_bar_chart1")
    
    
    ### Question22: Which reason(s) drive that score ?
    ### Missing wordcloud
    
    
    ### Question23: Are you able to identify and tag your skills within your HRIS ?
    q23_data_available_count = (filtered_data.iloc[:, 30] == 'Yes').sum()
    q23_data_available_pct = q23_data_available_count / len(filtered_data) * 100

    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Identify and tag your skills within the HRIS
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"{q23_data_available_pct:.2f}% of the respondents, {q23_data_available_count} employee(s), are able to identify and tag         their skills within the HRIS.")
       
############ SECTION 3 ENDS ############


############ SECTION 4 STARTS ############      
if dashboard == 'Section 4: Learning':
    filtered_data = apply_filters(data, st.session_state['selected_role'], st.session_state['selected_function'],
                                  st.session_state['selected_location'])
        
    # A text container for filtering instructions
    st.markdown(
        f"""
        <div class="text-container" style="font-style: italic;">
        Filter the data by selecting tags from the sidebar. The charts below will be updated to reflect the&nbsp;
        <strong>{len(filtered_data)}</strong>&nbsp;filtered respondents.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    
    satisfaction_ratio = 0.6
    barcharts_ratio = 1 - satisfaction_ratio
    satisfaction_col, barcharts_col = st.columns([satisfaction_ratio, barcharts_ratio])

    st.markdown("""
        <style>
        .chart-container {
            padding-top: 20px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    
    ### Question24: From 1 to 5, how satisfied are you with your current learning management system ?
    with satisfaction_col:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        categories = ['Very Dissatisfied', 'Dissatisfied', 'Neutral', 'Satisfied', 'Very Satisfied']
        q24ValuesCount, q24MedianScore = score_distribution(filtered_data, 31)

        ratings_df = pd.DataFrame({'Satisfaction Level': categories, 'Percentage': q24ValuesCount.values})

        # Display title and median score
        title_html = f"<h2 style='font-size: 17px; font-family: Arial; color: #333333;'>Rating on Current Learning Management System</h2>"
        caption_html = f"<div style='font-size: 15px; font-family: Arial; color: #707070;'>The median satisfaction score is {q24MedianScore:.1f}</div>"
        st.markdown(title_html, unsafe_allow_html=True)
        st.markdown(caption_html, unsafe_allow_html=True)

        # Create a horizontal bar chart with Plotly
        fig = px.bar(ratings_df, y='Satisfaction Level', x='Percentage', text='Percentage',
                     orientation='h',
                     color='Satisfaction Level', color_discrete_map={
                'Very Dissatisfied': '#440154',  # Dark purple
                'Dissatisfied': '#3b528b',  # Dark blue
                'Neutral': '#21918c',  # Cyan
                'Satisfied': '#5ec962',  # Light green
                'Very Satisfied': '#fde725'  # Bright yellow
            })

        # Remove legend and axes titles
        fig.update_layout(showlegend=False, xaxis_visible=False, xaxis_title=None, yaxis_title=None, autosize=True,
                          height=300, margin=dict(l=20, r=20, t=30, b=20))

        # Format text on bars
        fig.update_traces(texttemplate='%{x:.1f}%', textposition='outside')
        fig.update_xaxes(range=[0, max(ratings_df['Percentage']) * 1.1])

        # Improve layout aesthetics
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        # Use Streamlit to display the Plotly chart
        st.plotly_chart(fig, use_container_width=True, key="overall_rating_bar_chart")
        st.markdown('</div>', unsafe_allow_html=True)

    with barcharts_col:
        satisfaction_options = ['Select a satisfaction level', 'Very Dissatisfied', 'Dissatisfied', 'Neutral',
                                'Satisfied', 'Very Satisfied']
        satisfaction_dropdown1 = st.selectbox('', satisfaction_options,
                                              key='satisfaction_dropdown1')

        satisfaction_filtered_data1 = filter_by_satisfaction(filtered_data, satisfaction_dropdown1, 31)

        location_summary1, role_summary1, function_summary1 = prepare_summaries(satisfaction_filtered_data1)
        left_margin = 150
        total_height = 310
        role_chart_height = total_height * 0.45
        function_chart_height = total_height * 0.55

        fig_role1 = px.bar(role_summary1, y='Role', x='Count', orientation='h')
        fig_role1.update_layout(title="by Role", margin=dict(l=left_margin, r=0, t=50, b=0),
                                height=role_chart_height, showlegend=False)
        fig_role1.update_traces(marker_color='#336699', text=role_summary1['Count'], textposition='outside')
        fig_role1.update_yaxes(showticklabels=True, title='')
        fig_role1.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_role1, use_container_width=True, key="roles_bar_chart1")

        fig_function1 = px.bar(function_summary1, y='Function', x='Count', orientation='h')
        fig_function1.update_layout(title="by Function", margin=dict(l=left_margin, r=0, t=50, b=0),
                                    height=function_chart_height, showlegend=False)
        fig_function1.update_traces(marker_color='#336699', text=function_summary1['Count'], textposition='outside')
        fig_function1.update_yaxes(showticklabels=True, title='')
        fig_function1.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_function1, use_container_width=True, key="functions_bar_chart1")
        
    
    ### Question25: What are the learning format that you prefer ?
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Preferred Learning Format
    </h2>
    """,
    unsafe_allow_html=True
    )

    # Create a DataFrame with the learning format data
    q25_data = pd.DataFrame({'learning_format': filtered_data.iloc[:, 32]})
    q25_data['learning_format'] = q25_data['learning_format'].str.rstrip(';')
    q25_data.dropna(inplace=True)

    # Count the occurrences of each learning format
    learning_format_counts = q25_data['learning_format'].value_counts().reset_index()
    learning_format_counts.columns = ['learning_format', 'count']

    # Calculate percentage
    learning_format_counts['percentage'] = learning_format_counts['count'] / learning_format_counts['count'].sum() * 100

    # Define the preferred order of learning formats
    preferred_order = ['E-Learning', 'On site', 'Micro-Learning', 'Coaching']

    # Ensure the DataFrame respects the preferred order
    learning_format_counts['learning_format'] = pd.Categorical(
        learning_format_counts['learning_format'],
        categories=preferred_order,
        ordered=True
    )
    learning_format_counts.sort_values('learning_format', inplace=True)

    # Create a horizontal bar chart
    fig25 = px.bar(learning_format_counts, x='percentage', y='learning_format', text='percentage', 
                   orientation='h',
                   color='learning_format', color_discrete_map={
                       'E-Learning': '#440154',  # Dark purple
                       'On site': '#3b528b',  # Dark blue
                       'Micro-Learning': '#21918c',  # Cyan
                       'Coaching': '#5ec962',  # Light green
                   })

    # Remove legend and axes titles
    fig25.update_layout(showlegend=False, xaxis_visible=False, xaxis_title=None, yaxis_title=None, autosize=True,
                        height=300, margin=dict(l=20, r=20, t=30, b=20))

    # Format text on bars
    fig25.update_traces(texttemplate='%{x:.1f}%', textposition='outside')
    fig25.update_xaxes(range=[0, max(learning_format_counts['percentage']) * 1.1])

    # Improve layout aesthetics
    fig25.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

    # Show the chart
    st.plotly_chart(fig25, use_container_width=False)

    
    ### Question26: Have you participated in any training or development programs provided by HR?
    q26_data_available_count = (filtered_data.iloc[:, 33] == 'Yes').sum()
    q26_data_available_pct = q26_data_available_count / len(filtered_data) * 100

    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Participation in any Training or Development Programs Provided by HR
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"{q26_data_available_pct:.2f}% of the respondents, {q26_data_available_count} employee(s), participated in training or        development programs provided by HR.")
    
    
    ### Question27: Have you received any recommendations on training (either by the HR team or directly on your Learning    System) ?
    q27_data_available_count = (filtered_data.iloc[:, 34] == 'Yes').sum()
    q27_data_available_pct = q27_data_available_count / len(filtered_data) * 100

    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Recommendations on Training (either by the HR team or directly on Learning System)
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"{q27_data_available_pct:.2f}% of the respondents, {q27_data_available_count} employee(s), received recommendations on         training.")
    
    
    ### Question28: What could be improved or what kind of format is missing today ?
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    What could be improved or what kind of format is missing today ?
    </h2>
    """,
    unsafe_allow_html=True
    )
    ### Missing wordcloud


############ SECTION 4 ENDS ############


############ SECTION 5 STARTS ############
if dashboard == 'Section 5: Compensation':
    filtered_data = apply_filters(data, st.session_state['selected_role'], st.session_state['selected_function'],
                                  st.session_state['selected_location'])
    
    # A text container for filtering instructions
    st.markdown(
        f"""
        <div class="text-container" style="font-style: italic;">
        Filter the data by selecting tags from the sidebar. The charts below will be updated to reflect the&nbsp;
        <strong>{len(filtered_data)}</strong>&nbsp;filtered respondents.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    ### Qustion29: Do you participate in the Compensation Campaign ?
    q29_data_available_count = (filtered_data.iloc[:, 36] == 'Yes').sum()
    q29_data_available_pct = q29_data_available_count / len(filtered_data) * 100
   
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Compensation Campaign Participation
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"{q29_data_available_pct:.2f}% of the respondents, {q29_data_available_count} employee(s), participated in the   compensation campaign.")
    
    ### Qustion30: Do you think that the data available in the Compensation form enables you to make a fair decision regarding a promotion, a bonus or a raise ? (e.g : compa-ratio, variation between years, historical data on salary and bonus, …) 
    q30_data_available_count = (filtered_data.iloc[:, 37] == 'Yes').sum()
    q30_data_available_pct = q30_data_available_count / q29_data_available_count * 100
    
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Data availability in the Compensation Form
    </h2>
    """,
    unsafe_allow_html=True
    )
    
    st.write(
        f"Among the people who participate the Compensation Campaign, {q30_data_available_pct:.2f}% of the respondents, {q30_data_available_count} employee(s), think that the data available in the Compensation form enables him/her to make a fair decision regarding a promotion, a bonus or a raise.")

    ### Qustion31: What data is missing according to you ?
    st.markdown(
        """
        <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
        What data is missing according to you ?
        </h2>
        """,
        unsafe_allow_html=True
    )

    q38_data_reliable = filtered_data['What data is missing according to you ?'].dropna()
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt

    # Replace spaces with underscores
    phrases = q38_data_reliable.str.replace(' ', '_')

    # Generate word cloud
    wordcloud = WordCloud(width=1000, height=500).generate(' '.join(phrases))

    plt.figure(figsize=(15, 8))
    plt.imshow(wordcloud)
    plt.axis("off")

    # Display the plot in Streamlit
    st.pyplot(plt)
    
    
    ### Question32: Do you manage/launch your compensation campaigns nationally or in another way?
    st.markdown(
        """
        <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
        Compensation Campaigns Management/Launch
        </h2>
        """,
        unsafe_allow_html=True
    )

    # Create a DataFrame with the compensation format data
    q32_data = pd.DataFrame({'compensation_manage': filtered_data.iloc[:, 39]})
    q32_data['compensation_manage'] = q32_data['compensation_manage'].str.rstrip(';')
    q32_data.dropna(inplace=True)

    # Count the occurrences of each compensation format
    compensation_manage_counts = q32_data['compensation_manage'].value_counts().reset_index()
    compensation_manage_counts.columns = ['compensation_manage', 'count']

    # Calculate percentage
    compensation_manage_counts['percentage'] = compensation_manage_counts['count'] / compensation_manage_counts['count'].sum() * 100

    # Create a horizontal bar chart
    fig32 = px.bar(compensation_manage_counts, x='percentage', y='compensation_manage', text='percentage', 
                   orientation='h',
                   color='compensation_manage', color_discrete_map={
                       'National Campaign': '#440154',  # Dark purple
                       'International Campaign': '#3b528b',  # Dark blue
                       'Regional Campaign': '#21918c',  # Cyan
                   })

    # Remove legend and axes titles
    fig32.update_layout(showlegend=False, xaxis_visible=False, xaxis_title=None, yaxis_title=None, autosize=True,
                        height=300, margin=dict(l=20, r=20, t=30, b=20))

    # Format text on bars
    fig32.update_traces(texttemplate='%{x:.1f}%', textposition='outside')
    fig32.update_xaxes(range=[0, max(compensation_manage_counts['percentage']) * 1.1])

    # Improve layout aesthetics
    fig32.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

    # Show the chart
    st.plotly_chart(fig32, use_container_width=False)

    
    ### Question33: How would you rate the overall satisfaction regarding the compensation campaign ?
    satisfaction_ratio = 0.6
    barcharts_ratio = 1 - satisfaction_ratio
    satisfaction_col, barcharts_col = st.columns([satisfaction_ratio, barcharts_ratio])

    st.markdown("""
        <style>
        .chart-container {
            padding-top: 20px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    with satisfaction_col:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        categories = ['Very Dissatisfied', 'Dissatisfied', 'Neutral', 'Satisfied', 'Very Satisfied']
        q33ValuesCount, q33MedianScore = score_distribution(filtered_data, 40)

        ratings_df = pd.DataFrame({'Satisfaction Level': categories, 'Percentage': q33ValuesCount.values})

        # Display title and median score
        title_html = f"<h2 style='font-size: 17px; font-family: Arial; color: #333333;'>Rating on Compensation Campaign</h2>"
        caption_html = f"<div style='font-size: 15px; font-family: Arial; color: #707070;'>The median satisfaction score is {q33MedianScore:.1f}</div>"
        st.markdown(title_html, unsafe_allow_html=True)
        st.markdown(caption_html, unsafe_allow_html=True)

        # Create a horizontal bar chart with Plotly
        fig = px.bar(ratings_df, y='Satisfaction Level', x='Percentage', text='Percentage',
                     orientation='h',
                     color='Satisfaction Level', color_discrete_map={
                'Very Dissatisfied': '#440154',  # Dark purple
                'Dissatisfied': '#3b528b',  # Dark blue
                'Neutral': '#21918c',  # Cyan
                'Satisfied': '#5ec962',  # Light green
                'Very Satisfied': '#fde725'  # Bright yellow
            })

        # Remove legend and axes titles
        fig.update_layout(showlegend=False, xaxis_visible=False, xaxis_title=None, yaxis_title=None, autosize=True,
                          height=300, margin=dict(l=20, r=20, t=30, b=20))

        # Format text on bars
        fig.update_traces(texttemplate='%{x:.1f}%', textposition='outside')
        fig.update_xaxes(range=[0, max(ratings_df['Percentage']) * 1.1])

        # Improve layout aesthetics
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        # Use Streamlit to display the Plotly chart
        st.plotly_chart(fig, use_container_width=True, key="overall_rating_bar_chart")
        st.markdown('</div>', unsafe_allow_html=True)

    with barcharts_col:
        satisfaction_options = ['Select a satisfaction level', 'Very Dissatisfied', 'Dissatisfied', 'Neutral',
                                'Satisfied', 'Very Satisfied']
        satisfaction_dropdown1 = st.selectbox('', satisfaction_options,
                                              key='satisfaction_dropdown1')

        satisfaction_filtered_data1 = filter_by_satisfaction(filtered_data, satisfaction_dropdown1, 40)

        location_summary1, role_summary1, function_summary1 = prepare_summaries(satisfaction_filtered_data1)
        left_margin = 150
        total_height = 310
        role_chart_height = total_height * 0.45
        function_chart_height = total_height * 0.55

        fig_role1 = px.bar(role_summary1, y='Role', x='Count', orientation='h')
        fig_role1.update_layout(title="by Role", margin=dict(l=left_margin, r=0, t=50, b=0),
                                height=role_chart_height, showlegend=False)
        fig_role1.update_traces(marker_color='#336699', text=role_summary1['Count'], textposition='outside')
        fig_role1.update_yaxes(showticklabels=True, title='')
        fig_role1.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_role1, use_container_width=True, key="roles_bar_chart1")

        fig_function1 = px.bar(function_summary1, y='Function', x='Count', orientation='h')
        fig_function1.update_layout(title="by Function", margin=dict(l=left_margin, r=0, t=50, b=0),
                                    height=function_chart_height, showlegend=False)
        fig_function1.update_traces(marker_color='#336699', text=function_summary1['Count'], textposition='outside')
        fig_function1.update_yaxes(showticklabels=True, title='')
        fig_function1.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_function1, use_container_width=True, key="functions_bar_chart1")
        
        
    ### Question36: Do you have retroactivity on salary payments ? (e.g. New salary announced in March but payed from January)
    q36_data_available_count = (filtered_data.iloc[:, 43] == 'Yes').sum()
    q36_data_available_pct = q36_data_available_count / q29_data_available_count * 100
    
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Retroactivity on Salary Payments
    </h2>
    """,
    unsafe_allow_html=True
    )
    
    st.write(
        f"Among the people who participate the Compensation Campaign, {q36_data_available_pct:.2f}% of the respondents, {q36_data_available_count} employee(s), have retroactivity on salary payments.")
    
    
    ### Question37: Do you participate in the variable pay/bonus campaign ?
    q37_data_available_count = (filtered_data.iloc[:, 44] == 'Yes').sum()
    q37_data_available_pct = q37_data_available_count / q29_data_available_count * 100
    
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Participation in Variable Pay/Bonus Campaign 
    </h2>
    """,
    unsafe_allow_html=True
    )
    
    st.write(
        f"Among the people who participate the Compensation Campaign, {q37_data_available_pct:.2f}% of the respondents, {q37_data_available_count} employee(s), participated in variable pay/bonus campaign.")
    
    
    ### Question38: How would you rate the overall satisfaction regarding the Variable Pay/Bonus campaign  ?
    satisfaction_ratio = 0.6
    barcharts_ratio = 1 - satisfaction_ratio
    satisfaction_col, barcharts_col = st.columns([satisfaction_ratio, barcharts_ratio])

    st.markdown("""
        <style>
        .chart-container {
            padding-top: 20px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    with satisfaction_col:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        categories = ['Very Dissatisfied', 'Dissatisfied', 'Neutral', 'Satisfied', 'Very Satisfied']
        q38ValuesCount, q38MedianScore = score_distribution(filtered_data, 45)

        ratings_df = pd.DataFrame({'Satisfaction Level': categories, 'Percentage': q38ValuesCount.values})

        # Display title and median score
        title_html = f"<h2 style='font-size: 17px; font-family: Arial; color: #333333;'>Rating on Variable Pay/Bonus Campaign </h2>"
        caption_html = f"<div style='font-size: 15px; font-family: Arial; color: #707070;'>The median satisfaction score is {q38MedianScore:.1f}</div>"
        st.markdown(title_html, unsafe_allow_html=True)
        st.markdown(caption_html, unsafe_allow_html=True)

        # Create a horizontal bar chart with Plotly
        fig = px.bar(ratings_df, y='Satisfaction Level', x='Percentage', text='Percentage',
                     orientation='h',
                     color='Satisfaction Level', color_discrete_map={
                'Very Dissatisfied': '#440154',  # Dark purple
                'Dissatisfied': '#3b528b',  # Dark blue
                'Neutral': '#21918c',  # Cyan
                'Satisfied': '#5ec962',  # Light green
                'Very Satisfied': '#fde725'  # Bright yellow
            })

        # Remove legend and axes titles
        fig.update_layout(showlegend=False, xaxis_visible=False, xaxis_title=None, yaxis_title=None, autosize=True,
                          height=300, margin=dict(l=20, r=20, t=30, b=20))

        # Format text on bars
        fig.update_traces(texttemplate='%{x:.1f}%', textposition='outside')
        fig.update_xaxes(range=[0, max(ratings_df['Percentage']) * 1.1])

        # Improve layout aesthetics
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        # Use Streamlit to display the Plotly chart
        st.plotly_chart(fig, use_container_width=True, key="overall_rating_bar_chart")
        st.markdown('</div>', unsafe_allow_html=True)

    with barcharts_col:
        satisfaction_options = ['Select a satisfaction level', 'Very Dissatisfied', 'Dissatisfied', 'Neutral',
                                'Satisfied', 'Very Satisfied']
        satisfaction_dropdown38 = st.selectbox('', satisfaction_options,
                                              key='satisfaction_dropdown38')

        satisfaction_filtered_data1 = filter_by_satisfaction(filtered_data, satisfaction_dropdown38, 45)

        location_summary1, role_summary1, function_summary1 = prepare_summaries(satisfaction_filtered_data1)
        left_margin = 150
        total_height = 310
        role_chart_height = total_height * 0.45
        function_chart_height = total_height * 0.55

        fig_role1 = px.bar(role_summary1, y='Role', x='Count', orientation='h')
        fig_role1.update_layout(title="by Role", margin=dict(l=left_margin, r=0, t=50, b=0),
                                height=role_chart_height, showlegend=False)
        fig_role1.update_traces(marker_color='#336699', text=role_summary1['Count'], textposition='outside')
        fig_role1.update_yaxes(showticklabels=True, title='')
        fig_role1.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_role1, use_container_width=True, key="roles_bar_chart1")

        fig_function1 = px.bar(function_summary1, y='Function', x='Count', orientation='h')
        fig_function1.update_layout(title="by Function", margin=dict(l=left_margin, r=0, t=50, b=0),
                                    height=function_chart_height, showlegend=False)
        fig_function1.update_traces(marker_color='#336699', text=function_summary1['Count'], textposition='outside')
        fig_function1.update_yaxes(showticklabels=True, title='')
        fig_function1.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_function1, use_container_width=True, key="functions_bar_chart1")
        
        
    ### Question39: Do you manage/launch your bonus/variable pay campaigns nationally or in another way?
    st.markdown(
        """
        <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
       Bonus/Variable Pay Campaigns Management/Launch
        </h2>
        """,
        unsafe_allow_html=True
    )

    # Create a DataFrame with the compensation format data
    q39_data = pd.DataFrame({'bonus_manage': filtered_data.iloc[:, 46]})
    q39_data['bonus_manage'] = q39_data['bonus_manage'].str.rstrip(';')
    q39_data.dropna(inplace=True)

    # Count the occurrences of each compensation format
    bonus_manage_counts = q39_data['bonus_manage'].value_counts().reset_index()
    bonus_manage_counts.columns = ['bonus_manage', 'count']

    # Calculate percentage
    bonus_manage_counts['percentage'] = bonus_manage_counts['count'] / bonus_manage_counts['count'].sum() * 100

    # Create a horizontal bar chart
    fig39 = px.bar(bonus_manage_counts, x='percentage', y='bonus_manage', text='percentage', 
                   orientation='h',
                   color='bonus_manage', color_discrete_map={
                       'National Campaign': '#440154',  # Dark purple
                       'International Campaign': '#3b528b',  # Dark blue
                       'Regional Campaign': '#21918c',  # Cyan
                   })

    # Remove legend and axes titles
    fig39.update_layout(showlegend=False, xaxis_visible=False, xaxis_title=None, yaxis_title=None, autosize=True,
                        height=300, margin=dict(l=20, r=20, t=30, b=20))

    # Format text on bars
    fig39.update_traces(texttemplate='%{x:.1f}%', textposition='outside')
    fig39.update_xaxes(range=[0, max(bonus_manage_counts['percentage']) * 1.1])

    # Improve layout aesthetics
    fig39.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

    # Show the chart
    st.plotly_chart(fig39, use_container_width=False)
    
    
    ### Question40: Are the dates of your Variable Pay campaign different from the one for the Compensation Campaign ?
    q40_data_available_count = (filtered_data.iloc[:, 47] == 'Yes').sum()
    q40_data_available_pct = q40_data_available_count / q29_data_available_count * 100
    
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Variable Pay Campaign Dates Different from Compensation Campaign Dates
    </h2>
    """,
    unsafe_allow_html=True
    )
    
    st.write(
        f"Among the people who participate the Compensation Campaign, {q40_data_available_pct:.2f}% of the respondents, {q40_data_available_count} employee(s), have different dates for the Variable Pay Campaign compared to the Compensation Campaign.")

    
############ SECTION 5 ENDS ############


############ SECTION 6 STARTS ############
if dashboard == 'Section 6: Payroll':
    filtered_data = apply_filters(data, st.session_state['selected_role'], st.session_state['selected_function'],
                                  st.session_state['selected_location'])
    
    
    # A text container for filtering instructions
    st.markdown(
        f"""
        <div class="text-container" style="font-style: italic;">
        Filter the data by selecting tags from the sidebar. The charts below will be updated to reflect the&nbsp;
        <strong>{len(filtered_data)}</strong>&nbsp;filtered respondents.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    
    ### Question41: Are you part of the payroll team ?
    q41_data_available_count = (filtered_data.iloc[:, 48] == 'Yes').sum()
    q41_data_available_pct = q41_data_available_count / len(filtered_data) * 100
   
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Payroll Team
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"{q41_data_available_pct:.2f}% of the respondents, {q41_data_available_count} employee(s), are part of the payroll team.")
    
    
    ### Question42: How satisfied are you with your current payroll system ?
    satisfaction_ratio = 0.6
    barcharts_ratio = 1 - satisfaction_ratio
    satisfaction_col, barcharts_col = st.columns([satisfaction_ratio, barcharts_ratio])

    st.markdown("""
        <style>
        .chart-container {
            padding-top: 20px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    with satisfaction_col:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        categories = ['Very Dissatisfied', 'Dissatisfied', 'Neutral', 'Satisfied', 'Very Satisfied']
        q42ValuesCount, q42MedianScore = score_distribution(filtered_data, 49)

        ratings_df = pd.DataFrame({'Satisfaction Level': categories, 'Percentage': q42ValuesCount.values})

        # Display title and median score
        title_html = f"<h2 style='font-size: 17px; font-family: Arial; color: #333333;'>Rating on Current Payroll System</h2>"
        caption_html = f"<div style='font-size: 15px; font-family: Arial; color: #707070;'>The median satisfaction score is {q42MedianScore:.1f}</div>"
        st.markdown(title_html, unsafe_allow_html=True)
        st.markdown(caption_html, unsafe_allow_html=True)

        # Create a horizontal bar chart with Plotly
        fig = px.bar(ratings_df, y='Satisfaction Level', x='Percentage', text='Percentage',
                     orientation='h',
                     color='Satisfaction Level', color_discrete_map={
                'Very Dissatisfied': '#440154',  # Dark purple
                'Dissatisfied': '#3b528b',  # Dark blue
                'Neutral': '#21918c',  # Cyan
                'Satisfied': '#5ec962',  # Light green
                'Very Satisfied': '#fde725'  # Bright yellow
            })

        # Remove legend and axes titles
        fig.update_layout(showlegend=False, xaxis_visible=False, xaxis_title=None, yaxis_title=None, autosize=True,
                          height=300, margin=dict(l=20, r=20, t=30, b=20))

        # Format text on bars
        fig.update_traces(texttemplate='%{x:.1f}%', textposition='outside')
        fig.update_xaxes(range=[0, max(ratings_df['Percentage']) * 1.1])

        # Improve layout aesthetics
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        # Use Streamlit to display the Plotly chart
        st.plotly_chart(fig, use_container_width=True, key="overall_rating_bar_chart")
        st.markdown('</div>', unsafe_allow_html=True)

    with barcharts_col:
        satisfaction_options = ['Select a satisfaction level', 'Very Dissatisfied', 'Dissatisfied', 'Neutral',
                                'Satisfied', 'Very Satisfied']
        satisfaction_dropdown38 = st.selectbox('', satisfaction_options,
                                              key='satisfaction_dropdown38')

        satisfaction_filtered_data1 = filter_by_satisfaction(filtered_data, satisfaction_dropdown38, 49)

        location_summary1, role_summary1, function_summary1 = prepare_summaries(satisfaction_filtered_data1)
        left_margin = 150
        total_height = 310
        role_chart_height = total_height * 0.45
        function_chart_height = total_height * 0.55

        fig_role1 = px.bar(role_summary1, y='Role', x='Count', orientation='h')
        fig_role1.update_layout(title="by Role", margin=dict(l=left_margin, r=0, t=50, b=0),
                                height=role_chart_height, showlegend=False)
        fig_role1.update_traces(marker_color='#336699', text=role_summary1['Count'], textposition='outside')
        fig_role1.update_yaxes(showticklabels=True, title='')
        fig_role1.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_role1, use_container_width=True, key="roles_bar_chart1")

        fig_function1 = px.bar(function_summary1, y='Function', x='Count', orientation='h')
        fig_function1.update_layout(title="by Function", margin=dict(l=left_margin, r=0, t=50, b=0),
                                    height=function_chart_height, showlegend=False)
        fig_function1.update_traces(marker_color='#336699', text=function_summary1['Count'], textposition='outside')
        fig_function1.update_yaxes(showticklabels=True, title='')
        fig_function1.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_function1, use_container_width=True, key="functions_bar_chart1")
        
        
    ### Question43: Do you realize your payroll activities internally or is it outsourced ?
    q43_data_available_count = (filtered_data.iloc[:, 50] == 'Internal').sum()
    q43_data_available_pct = q43_data_available_count / q41_data_available_count * 100
   
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Payroll Activities
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"Among the people who are part of the payroll team, {q43_data_available_pct:.2f}% of the respondents, {q43_data_available_count} employee(s), realize their payroll activities internally and others realize that it is outsourced.")
    
    
    ### Question44: Does your system cover legal updates ?
    q44_data_available_count = (filtered_data.iloc[:, 51] == 'Yes').sum()
    q44_data_available_pct = q44_data_available_count / q41_data_available_count * 100
   
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Legal Updates
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"Among the people who are part of the payroll team, {q44_data_available_pct:.2f}% of the respondents, {q44_data_available_count} employee(s), answer that their system covers legal updates.")
    
    
    ### Question45: Are you autonomous when it comes to updating simple data, or do you systematically rely on outside firms for updates?
    q45_data_available_count = (filtered_data.iloc[:, 52] == 'Autonomous').sum()
    q45_data_available_pct = q45_data_available_count / q41_data_available_count * 100
   
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Are you autonomous when it comes to updating simple data?
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"Among the people who are part of the payroll team, {q45_data_available_pct:.2f}% of the respondents, {q45_data_available_count} employee(s), answer that they are autonomous and others rely on outside firms for updates.")
    
    
    ### Question46: Can you share any specific features of your current system that you like/that made you choose it?
    st.markdown(
        """
        <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
        Can you share any specific features of your current system that you like/that made you choose it?
        </h2>
        """,
        unsafe_allow_html=True
    )
    ### Missing wordcloud
    
    
    ### Question47: If your payroll system is used in several countries, do you have a global platform for consolidating all your employees' country data?
    q47_data_available_count = (filtered_data.iloc[:, 54] == 'Yes').sum()
    q47_data_available_pct = q47_data_available_count / q41_data_available_count * 100
   
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Global Platform for Multiple Countries
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"Among the people who are part of the payroll team, {q47_data_available_pct:.2f}% of the respondents, {q47_data_available_count} employee(s), answer that they have a global platform for consolidating all employees' country data.")
    
    
    ### Question48: If so, does this platform automatically generate KPIs relating to your payroll (M/F headcount, salaries paid, contributions paid, etc.)?
    q48_data_available_count = (filtered_data.iloc[:, 55] == 'Yes').sum()
    q48_data_available_pct = q48_data_available_count / q47_data_available_count * 100
   
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Global Platform Function: Automatically Generate KPIs
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"Among the people who have a global platform, {q48_data_available_pct:.2f}% of the respondents, {q48_data_available_count} employee(s), answer that this platform automatically generate KPIs relating to the payroll (M/F headcount, salaries paid, contributions paid, etc.).")
    
    
    ### Question49: Can mass entries be made in the tool?
    q49_data_available_count = (filtered_data.iloc[:, 56] == 'Yes').sum()
    q49_data_available_pct = q49_data_available_count / q41_data_available_count * 100
   
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Mass Entries
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"Among the people who are part of the payroll team, {q49_data_available_pct:.2f}% of the respondents, {q49_data_available_count} employee(s), answer that they have a global platform for consolidating all employees' country data.")
    
    
    
    ### Question50: Is your payroll connected with your time management system ?
    q50_data_available_count = (filtered_data.iloc[:, 57] == 'Yes').sum()
    q50_data_available_pct = q50_data_available_count / q41_data_available_count * 100
   
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Payroll Connected with Time Management System
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"Among the people who are part of the payroll team, {q50_data_available_pct:.2f}% of the respondents, {q50_data_available_count} employee(s), answer that the payroll system is connected with time management system.")
    
    
    ### Question51: Is your payroll connected with a CORE HR/Administrative solution ?
    q51_data_available_count = (filtered_data.iloc[:, 58] == 'Yes').sum()
    q51_data_available_pct = q51_data_available_count / q41_data_available_count * 100
   
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Payroll Connected with a CORE HR/Administrative Solution
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"Among the people who are part of the payroll team, {q51_data_available_pct:.2f}% of the respondents, {q51_data_available_count} employee(s), answer that the payroll system is connected with a CORE HR/Administrative solution.")
    
############ SECTION 6 ENDS ############


############ SECTION 7 STARTS ############    
if dashboard == 'Section 7: Time Management':
    filtered_data = apply_filters(data, st.session_state['selected_role'], st.session_state['selected_function'],
                                  st.session_state['selected_location'])
    
    
    # A text container for filtering instructions
    st.markdown(
        f"""
        <div class="text-container" style="font-style: italic;">
        Filter the data by selecting tags from the sidebar. The charts below will be updated to reflect the&nbsp;
        <strong>{len(filtered_data)}</strong>&nbsp;filtered respondents.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    
    ### Question52: Are you part of the Time Management Team ?
    q52_data_available_count = (filtered_data.iloc[:, 59] == 'Yes').sum()
    q52_data_available_pct = q52_data_available_count / len(filtered_data) * 100
   
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Time Management Team
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"{q52_data_available_pct:.2f}% of the respondents, {q52_data_available_count} employee(s), are part of the time management team.")
    
    
    ### Question53: Do you currently have a time management system ?
    q53_data_available_count = (filtered_data.iloc[:, 60] == 'Yes').sum()
    q53_data_available_pct = q53_data_available_count / q52_data_available_count * 100
   
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Time Management System
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"Among the people who are part of the time management team, {q53_data_available_pct:.2f}% of the respondents,  {q53_data_available_count} employee(s),  answer that they currently have a time management system.")
    
    
    ### Question54: How satisfied are you with your current time management system ?
    satisfaction_ratio = 0.6
    barcharts_ratio = 1 - satisfaction_ratio
    satisfaction_col, barcharts_col = st.columns([satisfaction_ratio, barcharts_ratio])

    st.markdown("""
        <style>
        .chart-container {
            padding-top: 20px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    with satisfaction_col:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        categories = ['Very Dissatisfied', 'Dissatisfied', 'Neutral', 'Satisfied', 'Very Satisfied']
        q54ValuesCount, q54MedianScore = score_distribution(filtered_data, 61)

        ratings_df = pd.DataFrame({'Satisfaction Level': categories, 'Percentage': q54ValuesCount.values})

        # Display title and median score
        title_html = f"<h2 style='font-size: 17px; font-family: Arial; color: #333333;'>Rating on Current Time Management System</h2>"
        caption_html = f"<div style='font-size: 15px; font-family: Arial; color: #707070;'>The median satisfaction score is {q54MedianScore:.1f}</div>"
        st.markdown(title_html, unsafe_allow_html=True)
        st.markdown(caption_html, unsafe_allow_html=True)

        # Create a horizontal bar chart with Plotly
        fig = px.bar(ratings_df, y='Satisfaction Level', x='Percentage', text='Percentage',
                     orientation='h',
                     color='Satisfaction Level', color_discrete_map={
                'Very Dissatisfied': '#440154',  # Dark purple
                'Dissatisfied': '#3b528b',  # Dark blue
                'Neutral': '#21918c',  # Cyan
                'Satisfied': '#5ec962',  # Light green
                'Very Satisfied': '#fde725'  # Bright yellow
            })

        # Remove legend and axes titles
        fig.update_layout(showlegend=False, xaxis_visible=False, xaxis_title=None, yaxis_title=None, autosize=True,
                          height=300, margin=dict(l=20, r=20, t=30, b=20))

        # Format text on bars
        fig.update_traces(texttemplate='%{x:.1f}%', textposition='outside')
        fig.update_xaxes(range=[0, max(ratings_df['Percentage']) * 1.1])

        # Improve layout aesthetics
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        # Use Streamlit to display the Plotly chart
        st.plotly_chart(fig, use_container_width=True, key="overall_rating_bar_chart")
        st.markdown('</div>', unsafe_allow_html=True)

    with barcharts_col:
        satisfaction_options = ['Select a satisfaction level', 'Very Dissatisfied', 'Dissatisfied', 'Neutral',
                                'Satisfied', 'Very Satisfied']
        satisfaction_dropdown38 = st.selectbox('', satisfaction_options,
                                              key='satisfaction_dropdown38')

        satisfaction_filtered_data1 = filter_by_satisfaction(filtered_data, satisfaction_dropdown38, 61)

        location_summary1, role_summary1, function_summary1 = prepare_summaries(satisfaction_filtered_data1)
        left_margin = 150
        total_height = 310
        role_chart_height = total_height * 0.45
        function_chart_height = total_height * 0.55

        fig_role1 = px.bar(role_summary1, y='Role', x='Count', orientation='h')
        fig_role1.update_layout(title="by Role", margin=dict(l=left_margin, r=0, t=50, b=0),
                                height=role_chart_height, showlegend=False)
        fig_role1.update_traces(marker_color='#336699', text=role_summary1['Count'], textposition='outside')
        fig_role1.update_yaxes(showticklabels=True, title='')
        fig_role1.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_role1, use_container_width=True, key="roles_bar_chart1")

        fig_function1 = px.bar(function_summary1, y='Function', x='Count', orientation='h')
        fig_function1.update_layout(title="by Function", margin=dict(l=left_margin, r=0, t=50, b=0),
                                    height=function_chart_height, showlegend=False)
        fig_function1.update_traces(marker_color='#336699', text=function_summary1['Count'], textposition='outside')
        fig_function1.update_yaxes(showticklabels=True, title='')
        fig_function1.update_xaxes(showticklabels=False, title='')
        st.plotly_chart(fig_function1, use_container_width=True, key="functions_bar_chart1")
    
    
    
    ### Question55: Do you have a self-service for your employees ?
    q55_data_available_count = (filtered_data.iloc[:, 62] == 'Yes').sum()
    q55_data_available_pct = q55_data_available_count / q52_data_available_count * 100
   
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Self-service for the Employees
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"Among the people who are part of the time management team, {q55_data_available_pct:.2f}% of the respondents,  {q55_data_available_count} employee(s),  answer that they have a self-service for their employees.")
    
    
    ### Question56: Does the system allow employees to view their vacation counters (entitlement / taken / balance)
    q56_data_available_count = (filtered_data.iloc[:, 63] == 'Yes').sum()
    q56_data_available_pct = q56_data_available_count / q52_data_available_count * 100
   
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    System Function: View Vacation Counters
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"Among the people who are part of the time management team, {q56_data_available_pct:.2f}% of the respondents,  {q56_data_available_count} employee(s),  answer that the system allow employess to view their vacation counters (entitlement / taken / balance).")
    
    
    ### Question57: Does your system cover all the shift scheduling functions you need?
    q57_data_available_count = (filtered_data.iloc[:, 64] == 'Yes').sum()
    q57_data_available_pct = q57_data_available_count / q52_data_available_count * 100
   
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    System Function: Cover the Shift Scheduling
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"Among the people who are part of the time management team, {q57_data_available_pct:.2f}% of the respondents,  {q57_data_available_count} employee(s),  answer that the system cover all the shift scheduling functions needed.")
    
    
    
    ### Question58: Do you have the capability to run all the report needed ?
    q58_data_available_count = (filtered_data.iloc[:, 65] == 'Yes').sum()
    q58_data_available_pct = q58_data_available_count / q52_data_available_count * 100
   
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Capability: Run all the reports
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"Among the people who are part of the time management team, {q58_data_available_pct:.2f}% of the respondents,  {q58_data_available_count} employee(s),  answer that they have the capability to run all the reports needed.")
    
    
    ### Question59: According to you, what functionalities are missing from your current system ?
    st.markdown(
        """
        <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
        According to you, what functionalities are missing from your current system ?
        </h2>
        """,
        unsafe_allow_html=True
    )
    ### Missing wordcloud
    
    
    ### Question60: Does the system allow employees to take their own leave, with workflow validation by their manager or HR?
    q60_data_available_count = (filtered_data.iloc[:, 67] == 'Yes').sum()
    q60_data_available_pct = q60_data_available_count / q52_data_available_count * 100
   
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    System Function: Allow Employess to Take Their Own Leave
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"Among the people who are part of the time management team, {q60_data_available_pct:.2f}% of the respondents,  {q60_data_available_count} employee(s),  answer that the system allows employees to take their own leave, with workflow validation by their manager or HR.")
    
    
    ### Question61: Does your system automatically take retroactive items into account (e.g. application to April payroll of a salary increase with an effective date of January 1)?
    q61_data_available_count = (filtered_data.iloc[:, 68] == 'Yes').sum()
    q61_data_available_pct = q61_data_available_count / q52_data_available_count * 100
   
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    System Function: Automatically Take Retroactive Items Into Account
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"Among the people who are part of the time management team, {q61_data_available_pct:.2f}% of the respondents,  {q61_data_available_count} employee(s),  answer that the system automatically take retroactive items into account (e.g. application to April payroll of a salary increase with an effective date of January 1).")
    
############ SECTION 7 ENDS ############


############ SECTION 8 STARTS ############ 
if dashboard == 'Section 8: User Experience':
    filtered_data = apply_filters(data, st.session_state['selected_role'], st.session_state['selected_function'],
                                  st.session_state['selected_location'])
    
    
    # A text container for filtering instructions
    st.markdown(
        f"""
        <div class="text-container" style="font-style: italic;">
        Filter the data by selecting tags from the sidebar. The charts below will be updated to reflect the&nbsp;
        <strong>{len(filtered_data)}</strong>&nbsp;filtered respondents.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    
    ### Question62: In the context of your job, what are the most valuable activities your current HRIS enable you to do?
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    In the context of your job, what are the most valuable activities your current HRIS enable you to do?
    </h2>
    """,
    unsafe_allow_html=True
    )
    ### Missing wordcloud,emotion analysis
    
    
    ### Question63: In the context of your job, what do your current HRIS fail to address?
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    In the context of your job, what do your current HRIS fail to address?
    </h2>
    """,
    unsafe_allow_html=True
    )
    ### Missing wordcloud,emotion analysis
    
    
    ### Question64: Do you consider the time you spend on your HRIS to be time well spent?
    q64_data_available_count = (filtered_data.iloc[:, 71] == 'Yes').sum()
    q64_data_available_pct = q64_data_available_count / len(filtered_data) * 100
   
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    Time Spend on HRIS
    </h2>
    """,
    unsafe_allow_html=True
    )

    st.write(
        f"{q64_data_available_pct:.2f}% of the respondents, {q64_data_available_count} employee(s), consider the time you spend on your HRIS to be time well spent.")
    
    
    ### Question65: In 3 words, how would you describe your current user-experience with the HRIS ?
    st.markdown(
    """
    <h2 style='font-size: 17px; font-family: Arial; color: #333333;'>
    In 3 words, how would you describe your current user-experience with the HRIS ?
    </h2>
    """,
    unsafe_allow_html=True
    )
    ### Missing wordcloud,emotion analysis
    
    

    import pandas as pd
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM
    import torch
    import numpy as np


    def load_models():
        # Load the tokenizers and models
        tokenizer_1 = AutoTokenizer.from_pretrained("j-hartmann/emotion-english-distilroberta-base")
        model_1 = AutoModelForSequenceClassification.from_pretrained("j-hartmann/emotion-english-distilroberta-base")

        tokenizer_2 = AutoTokenizer.from_pretrained("mrm8488/t5-base-finetuned-emotion")
        model_2 = AutoModelForSeq2SeqLM.from_pretrained("mrm8488/t5-base-finetuned-emotion")

        return tokenizer_1, model_1, tokenizer_2, model_2


    def predict_emotions_hybrid(df, text_columns):
        tokenizer_1, model_1, tokenizer_2, model_2 = load_models()

        emotion_labels_1 = ["anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise"]
        emotion_labels_2 = ["anger", "joy", "optimism", "sadness"]

        for column in text_columns:
            if column not in df.columns:
                raise ValueError(f"Column '{column}' does not exist in DataFrame")
            df[column] = df[column].fillna("")

        for column in text_columns:
            # Predictions from the first model
            encoded_texts_1 = tokenizer_1(df[column].tolist(), padding=True, truncation=True, return_tensors='pt')
            with torch.no_grad():
                outputs_1 = model_1(**encoded_texts_1)
                probabilities_1 = torch.nn.functional.softmax(outputs_1.logits, dim=-1)

            # Predictions from the second model
            encoded_texts_2 = tokenizer_2(df[column].tolist(), padding=True, truncation=True, return_tensors='pt')
            with torch.no_grad():
                outputs_2 = model_2.generate(input_ids=encoded_texts_2['input_ids'],
                                             attention_mask=encoded_texts_2['attention_mask'])
                predicted_labels_2 = [tokenizer_2.decode(output, skip_special_tokens=True) for output in outputs_2]
                probabilities_2 = torch.tensor(
                    [[1 if label == emotion else 0 for emotion in emotion_labels_2] for label in predicted_labels_2])

            # Adjust probabilities_2 to match the length of emotion_labels_1 by filling missing labels with zero probabilities
            adjusted_probabilities_2 = torch.zeros(probabilities_2.size(0), len(emotion_labels_1))
            for i, emotion in enumerate(emotion_labels_2):
                if emotion in emotion_labels_1:
                    adjusted_probabilities_2[:, emotion_labels_1.index(emotion)] = probabilities_2[:, i]

            # Average the probabilities
            averaged_probabilities = (probabilities_1 + adjusted_probabilities_2) / 2
            predicted_emotions = [emotion_labels_1[probability.argmax()] for probability in averaged_probabilities]

            df[f'{column}_predicted_emotion'] = predicted_emotions

        return df


    # Load the DataFrame from the Excel file
    df = pd.read_excel('/content/data.xlsx')

    # Specify the columns to analyze
    columns_to_analyze = [
        'What could be improved or what kind of format is missing today ?',
        'In the context of your job, what are the most valuable activities your current HRIS enable you to do?',
        'In the context of your job, what do your current HRIS fail to address?',
        'In 3 words, how would you describe your current user-experience with the HRIS ?'
    ]

    # Run the function
    df_with_emotions = predict_emotions_hybrid(df, columns_to_analyze)

    # Display the DataFrame with predicted emotions
    df_with_emotions.head()

    
############ SECTION 8 ENDS ############
