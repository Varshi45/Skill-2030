import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from db_logic import connect_to_db, fetch_interview_sessions, fetch_interview_data, fetch_student_count_by_batch
from app import render_performance_metrics, get_interview_data, get_interview_sessions, get_student_counts, get_students, get_performance_data, render_pie_chart, categorize_students

def get_branch_performance_data(interview_sessions, categorized_students_df):
    # Prepare data structure to hold branch performance data
    branch_scores = {}
    
    # Iterate through each session to process the data
    for session in interview_sessions:
        session_id, pool_id, performance, is_completed, details = session
        
        if isinstance(details, str):
            details = json.loads(details)
        
        # Get category from categorized students dataframe
        student_category = categorized_students_df[categorized_students_df['Session ID'] == session_id]['Category'].values
        
        if not student_category:
            continue
        
        student_category = student_category[0]
        
        if student_category not in branch_scores:
            branch_scores[student_category] = {
                'scores': [],
                'num_failed': 0,
                'not_completed': 0
            }
        
        branch_scores[student_category]['scores'].append(performance)
        
        if performance < 70:
            branch_scores[student_category]['num_failed'] += 1
        
        if not is_completed:
            branch_scores[student_category]['not_completed'] += 1

    # Aggregate the data
    performance_data = []
    for category, data in branch_scores.items():
        avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else None
        avg_score = round(avg_score, 1)  # Round to nearest decimal place
        
        performance_data.append({
            'Category': category,
            'Average Score': avg_score,
            'Number of Students Failed': data['num_failed'],
            'Number of Students Not Completed': data['not_completed']
        })
    
    return performance_data


def test_analysis_page():
    st.title("Skill-2030 Dashboard - Test Analysis")

    # Fetch interview data
    interview_data = get_interview_data()
    interview_df = pd.DataFrame(interview_data, columns=["ID", "Name", "Invitation", "Created On", "Num Candidates", "End Time", "Start Time"])

    if interview_df.empty:
        st.write("No interview data available.")
        return

    # Select an interview pool
    selected_test = st.selectbox("Select an Interview Pool", interview_df["Name"].tolist())
    selected_test_id = interview_df[interview_df["Name"] == selected_test]["ID"].iloc[0]

    # Fetch interview sessions
    pool_ids = interview_df["ID"].tolist()
    interview_sessions = get_interview_sessions(pool_ids)

    # Filter by selected interview pool
    filtered_sessions = [session for session in interview_sessions if session[1] == selected_test_id]

    if not filtered_sessions:
        st.write(f"No Data available for {selected_test}.")
        return

    # Fetch student data
    students_df = get_students()
    
    if students_df.empty:
        st.write("No student data available.")
        return

    # Categorize students and filter by interview pool
    categorized_students_df = categorize_students(students_df)
    categorized_students_df = categorized_students_df[categorized_students_df['Pool ID'] == selected_test_id]

    # Display branch-wise student distribution
    st.write(f"**Branch-wise student distribution for {selected_test}:**")

    branch_distribution = categorized_students_df.groupby('Category').size().reset_index(name='Count')
    st.dataframe(branch_distribution)

    # Display branch-wise score distribution as bar chart with labels on top of each bar
    st.write(f"Branch-wise score distribution for {selected_test}:")
    
    bar_fig = px.bar(branch_distribution, 
                     x='Category', 
                     y='Count', 
                     text='Count',
                     labels={"Category": "Branch", "Count": "Number of Students"},
                     title=f"Branch-wise Score Distribution for {selected_test}")

    bar_fig.update_traces(texttemplate='%{text}', textposition='outside')
    bar_fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide')

    st.plotly_chart(bar_fig)

    # Category Analysis using interactive Pie/Donut chart with Plotly
    fig = go.Figure(data=[go.Pie(labels=branch_distribution['Category'], 
                                 values=branch_distribution['Count'], 
                                 hole=.5, 
                                 hoverinfo="label+percent+value",
                                 textinfo="label+percent")])
    fig.update_layout(title_text=f"Category Analysis for {selected_test}",
                      annotations=[dict(text='Donut', x=0.5, y=0.5, font_size=20, showarrow=False)])
    st.plotly_chart(fig)

    # Scatter plot showing scores for each session using Plotly
    score_df = pd.DataFrame(filtered_sessions, columns=["ID", "Pool ID", "Performance", "Is Completed", "Details"])
    
    scatter_fig = px.scatter(score_df, 
                             x=score_df.index, 
                             y="Performance", 
                             color="Performance", 
                             hover_data={"ID": True, "Performance": True, "Pool ID": True},
                             labels={"Performance": "Performance Score", "index": "Session Index"})
    
    scatter_fig.update_layout(title=f"Scatter Plot of Scores for {selected_test}",
                              xaxis_title="Session Index",
                              yaxis_title="Performance Score")
    st.plotly_chart(scatter_fig)

    # Get branch performance data
    branch_performance_data = get_branch_performance_data(filtered_sessions, categorized_students_df)
    if branch_performance_data:
        branch_performance_df = pd.DataFrame(branch_performance_data)
        st.dataframe(branch_performance_df)

        performance_bar_fig = px.bar(branch_performance_df, 
                                    x='Category', 
                                    y='Average Score', 
                                    text='Average Score',
                                    color='Category',
                                    labels={"Category": "Branch", "Average Score": "Average Performance Score"},
                                    title=f"Branch-wise Average Performance for {selected_test}")

        performance_bar_fig.update_traces(texttemplate='%{text}', textposition='outside')
        performance_bar_fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide', margin=dict(t=50, b=50, l=50, r=50))

        st.plotly_chart(performance_bar_fig)

        # Melt the DataFrame to long format for easier plotting with Plotly
        branch_performance_melted = branch_performance_df.melt(id_vars='Category', 
                                                                value_vars=['Number of Students Failed', 'Number of Students Not Completed'],
                                                                var_name='Metric', 
                                                                value_name='Value')

        # Line chart for branch performance metrics
        line_fig = px.line(branch_performance_melted, 
                           x='Category', 
                           y='Value', 
                           color='Metric',
                           markers=True,
                           labels={"Category": "Branch", "Value": "Value", "Metric": "Metric"},
                           title=f"Branch-wise Performance Metrics for {selected_test}")

        line_fig.update_layout(xaxis_title='Branch', 
                               yaxis_title='Value',
                               legend_title='Metric',
                               margin=dict(t=50, b=50, l=50, r=50))

        st.plotly_chart(line_fig)

    else:
        st.write("No branch performance data available.")