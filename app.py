#app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from db_logic import connect_to_db, fetch_student_count_by_batch, fetch_interview_data, fetch_interview_sessions, process_performance_data

# Define cached functions
@st.cache_data
def get_student_counts():
    conn = connect_to_db()
    batch_counts = fetch_student_count_by_batch(conn)
    conn.close()
    return batch_counts

@st.cache_data
def get_interview_data():
    conn = connect_to_db()
    interview_data = fetch_interview_data(conn)
    conn.close()
    return interview_data

@st.cache_data
def get_students():
    conn = connect_to_db()
    cur = conn.cursor()
    query = """
    SELECT id, name, email, invited, pool_id, session_id, selected
    FROM interviews_candidate;
    """
    cur.execute(query)
    results = cur.fetchall()
    cur.close()
    conn.close()
    columns = ["ID", "Name", "Email", "Invited", "Pool ID", "Session ID", "Selected"]
    return pd.DataFrame(results, columns=columns)

@st.cache_data
def get_interview_sessions(pool_ids):
    conn = connect_to_db()
    sessions = fetch_interview_sessions(conn, pool_ids)
    conn.close()
    return sessions

@st.cache_data
def get_performance_data(interview_sessions):
    return process_performance_data(interview_sessions)

def render_pie_chart(batch_counts):
    labels = list(batch_counts.keys())
    values = list(batch_counts.values())

    fig = px.pie(
        values=values,
        names=labels,
        title="Student Distribution by Batch",
        hover_name=labels,
        hover_data={'values': values},
        labels={'values': 'Number of Students', 'names': 'Batch Year'},
    )

    fig.update_traces(textinfo='percent+label', hoverinfo='label+percent+value')
    fig.update_layout(
        showlegend=True,
        legend_title_text='Batch Year',
        annotations=[{
            'text': '',
            'showarrow': False,
            'font_size': 18,
        }]
    )

    st.plotly_chart(fig)

def plot_candidate_distribution(interview_df, categorized_students_df):
    categorized_students_df = categorized_students_df.merge(
        interview_df[['ID', 'Name']],
        left_on='Pool ID',
        right_on='ID',
        how='left'
    ).drop(columns='ID')

    categorized_students_df = categorized_students_df.rename(columns={'Name': 'Pool Name'})

    # Group by Pool Name and Category to get the total count for each pool and category
    pool_category_counts = categorized_students_df.groupby(['Pool Name', 'Category']).agg({'Count': 'sum'}).reset_index()

    # Calculate total count for each pool to display on top of the bars
    total_pool_counts = pool_category_counts.groupby('Pool Name')['Count'].sum().reset_index()

    # Create a bar plot without displaying total count for each category
    fig_candidates = px.bar(
        pool_category_counts,
        x='Pool Name',
        y='Count',
        color='Category',
        title='Student Distribution by Category for Each Interview Pool',
        labels={'Pool Name': 'Interview Pool', 'Count': 'Number of Students', 'Category': 'Student Category'},
        height=500,
        barmode='stack'
    )

    # Customize the hover information and text position
    fig_candidates.update_traces(textposition='outside')

    # Add annotations for the total count of each pool, placed above the bars
    for i, row in total_pool_counts.iterrows():
        fig_candidates.add_annotation(
            x=row['Pool Name'],
            y=row['Count'],
            text=f'Total: {row["Count"]}',
            showarrow=False,
            font=dict(size=12, color='black'),
            xanchor='center',
            yanchor='bottom'
        )

    # Display the plot
    st.plotly_chart(fig_candidates, use_container_width=True)


def display_categorized_students(students_df, interview_df):
    pool_ids = interview_df['ID'].tolist()

    categorized_students_list = []

    for pool_id in pool_ids:
        filtered_students = students_df[students_df['Pool ID'] == pool_id]
        categorized_students = filtered_students.groupby('Category').size().reset_index(name='Count')
        categorized_students['Pool ID'] = pool_id
        categorized_students_list.append(categorized_students)
    
    all_categorized_students_df = pd.concat(categorized_students_list, ignore_index=True)

    return all_categorized_students_df

def categorize_students(students_df):
    def get_category(email_suffix):
        if email_suffix.startswith('05'):
            return 'CSE'
        elif email_suffix.startswith('54'):
            return 'AI-DS'
        elif email_suffix.startswith('04'):
            return 'ECE'
        elif email_suffix.startswith('12'):
            return 'IT'
        elif email_suffix.startswith('01'):
            return 'CIVIL'
        elif email_suffix.startswith('02'):
            return 'EEE'
        elif email_suffix.startswith('03'):
            return 'ME'
        elif email_suffix.startswith('61'):
            return 'AI-ML'
        elif email_suffix.startswith('57'):
            return 'CS&BS'
        else:
            return 'Other'

    def extract_year(email):
        try:
            year_prefix = email[:2]
            return int(year_prefix)
        except ValueError:
            return None

    students_df['Year'] = students_df['Email'].apply(lambda x: extract_year(x))
    students_df['Category'] = students_df['Email'].apply(lambda x: get_category(x.split('@')[0][-4:]))
    students_df = students_df[students_df['Year'] == 21]

    return students_df

def render_performance_metrics(performance_data, pool_names):
    df = pd.DataFrame(performance_data)
    df['Pool Name'] = df['Pool ID'].map(pool_names)
    
    if df.empty:
        st.write("No performance data available.")
        return
    
    st.write(f"**Performance Metrics**")

    # Plot overall average score by pool
    fig_avg_score = px.bar(
        df,
        x='Pool Name',
        y='Average Score',
        color='Pool Name',
        title='Average Score by Interview Pool',
        labels={'Pool Name': 'Interview Pool', 'Average Score': 'Average Score'},
        height=500
    )

    # Add annotations for average score
    for i, row in df.iterrows():
        fig_avg_score.add_annotation(
            x=row['Pool Name'],
            y=row['Average Score'],
            text=f'{row["Average Score"]:.2f}',
            showarrow=False,
            font=dict(size=12, color='black'),
            xanchor='center',
            yanchor='bottom'
        )

    st.plotly_chart(fig_avg_score, use_container_width=True)

    # Plot number of students who failed by pool
    fig_failed = px.bar(
        df,
        x='Pool Name',
        y='Number of Students Failed',
        color='Pool Name',
        title='Number of Students Failed by Interview Pool',
        labels={'Pool Name': 'Interview Pool', 'Number of Students Failed': 'Number of Students Failed'},
        height=500
    )

    # Add annotations for students failed
    for i, row in df.iterrows():
        fig_failed.add_annotation(
            x=row['Pool Name'],
            y=row['Number of Students Failed'],
            text=f'{row["Number of Students Failed"]}',
            showarrow=False,
            font=dict(size=12, color='black'),
            xanchor='center',
            yanchor='bottom'
        )

    st.plotly_chart(fig_failed, use_container_width=True)

    # Plot number of students who haven't completed the interview by pool
    fig_not_completed = px.bar(
        df,
        x='Pool Name',
        y='Number of Students Not Completed',
        color='Pool Name',
        title='Number of Students Not Completed by Interview Pool',
        labels={'Pool Name': 'Interview Pool', 'Number of Students Not Completed': 'Number of Students Not Completed'},
        height=500
    )

    # Add annotations for students not completed
    for i, row in df.iterrows():
        fig_not_completed.add_annotation(
            x=row['Pool Name'],
            y=row['Number of Students Not Completed'],
            text=f'{row["Number of Students Not Completed"]}',
            showarrow=False,
            font=dict(size=12, color='black'),
            xanchor='center',
            yanchor='bottom'
        )

    st.plotly_chart(fig_not_completed, use_container_width=True)


