import streamlit as st
import pandas as pd
import plotly.express as px

from app import get_interview_data, get_interview_sessions, get_performance_data

def render_sub_category_metrics(performance_data, pool_names):
    df = pd.DataFrame(performance_data)
    df['Pool Name'] = df['Pool ID'].map(pool_names)

    if df.empty:
        st.write("No performance data available.")
        return

    st.write("Sub-Category Performance Metrics")

    # Render sub-category average scores if available
    if 'Sub-Category Averages' in df.columns and df['Sub-Category Averages'].apply(bool).any():
        for sub_category in df['Sub-Category Averages'].iloc[0].keys():
            sub_category_scores = []
            for index, row in df.iterrows():
                # Check if the sub-category's average score is greater than zero
                if row['Sub-Category Averages'][sub_category]['Average Score'] > 0:
                    sub_category_scores.append({
                        'Pool Name': row['Pool Name'],
                        'Sub-Category': sub_category,
                        'Average Score': row['Sub-Category Averages'][sub_category]['Average Score']
                    })

            # Only render the sub-category chart if there are scores greater than zero
            if sub_category_scores:
                sub_category_df = pd.DataFrame(sub_category_scores)

                fig_sub_category = px.bar(
                    sub_category_df,
                    x='Pool Name',
                    y='Average Score',
                    color='Pool Name',
                    title=f'Average {sub_category.title()} Score by Interview Pool',
                    labels={'Pool Name': 'Interview Pool', 'Average Score': f'{sub_category.title()} Average Score'},
                    height=500
                )
                st.plotly_chart(fig_sub_category, use_container_width=True)

def categorical_analysis_page():
    st.title("Skill-2030 Dashboard - Categorical Analysis")

    # Fetch the interview data
    interview_data = get_interview_data()
    columns = ["ID", "Name", "Description", "Created On", "Candidates", "Start Time", "End Time"]
    interview_df = pd.DataFrame(interview_data, columns=columns)
    interview_df['Created On'] = pd.to_datetime(interview_df['Created On']).dt.date
    interview_df['Start Time'] = pd.to_datetime(interview_df['Start Time']).dt.tz_localize(None).dt.strftime('%Y-%m-%d %H:%M:%S')
    interview_df['End Time'] = pd.to_datetime(interview_df['End Time']).dt.tz_localize(None).dt.strftime('%Y-%m-%d %H:%M:%S')

    # Prepare pool names mapping
    pool_names = {row['ID']: row['Name'] for _, row in interview_df.iterrows()}

    # Fetch interview sessions and performance data
    pool_ids = interview_df['ID'].tolist()
    interview_sessions = get_interview_sessions(pool_ids)
    performance_data = get_performance_data(interview_sessions)

    # Render sub-category metrics
    render_sub_category_metrics(performance_data, pool_names)
