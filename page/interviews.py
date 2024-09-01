import streamlit as st
import pandas as pd
import plotly.express as px

from app import render_performance_metrics, get_interview_data, get_students, categorize_students, display_categorized_students, plot_candidate_distribution, get_interview_sessions, get_performance_data

def interviews_page():
    st.title("Skill-2030 Dashboard - Interviews")

    # Fetch the interview data
    interview_data = get_interview_data()
    columns = ["ID", "Name", "Description", "Created On", "Candidates", "Start Time", "End Time"]
    interview_df = pd.DataFrame(interview_data, columns=columns)
    interview_df['Created On'] = pd.to_datetime(interview_df['Created On']).dt.date
    interview_df['Start Time'] = pd.to_datetime(interview_df['Start Time']).dt.tz_localize(None).dt.strftime('%Y-%m-%d %H:%M:%S')
    interview_df['End Time'] = pd.to_datetime(interview_df['End Time']).dt.tz_localize(None).dt.strftime('%Y-%m-%d %H:%M:%S')

    st.dataframe(interview_df)

    # Fetch student data and categorize
    students_df = get_students()
    categorized_students_df = categorize_students(students_df)
    all_categorized_students_df = display_categorized_students(categorized_students_df, interview_df)

    # Plot candidate distribution
    plot_candidate_distribution(interview_df, all_categorized_students_df)

    # Plot the categorized student distribution with Pool ID as separate bars
    fig_students = px.bar(
        all_categorized_students_df,
        x='Category',
        y='Count',
        color='Pool ID',
        title='Branch Distribution for Each Assignment Pool',
        labels={'Category': 'Category', 'Count': 'Number of Students', 'Pool ID': 'Interview Pool'},
        height=500,
        barmode='group'
    )
    st.plotly_chart(fig_students, use_container_width=True)

    # Prepare pool names mapping
    pool_names = {row['ID']: row['Name'] for _, row in interview_df.iterrows()}

    # Display performance metrics
    pool_ids = interview_df['ID'].tolist()
    interview_sessions = get_interview_sessions(pool_ids)
    performance_data = get_performance_data(interview_sessions)
    render_performance_metrics(performance_data, pool_names)
