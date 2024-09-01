#db_logic.py
import json
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Function to connect to the PostgreSQL database
def connect_to_db():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    return conn

# Function to fetch student count categorized by batch, discarding students from 2016 or earlier
def fetch_student_count_by_batch(conn):
    cur = conn.cursor()
    query = """
    SELECT email 
    FROM users_user 
    WHERE email LIKE '%@vishnu.edu.in';
    """
    cur.execute(query)
    results = cur.fetchall()
    cur.close()
    batch_counts = {}

    for (email,) in results:
        if len(email) >= 2 and email[:2].isdigit():
            year = int(email[:2])
            if "pa5a" in email:
                year -= 1
            full_year = 2000 + year

            if full_year >= 2017:
                if full_year in batch_counts:
                    batch_counts[full_year] += 1
                else:
                    batch_counts[full_year] = 1

    return batch_counts

def fetch_current_year_interview_ids(conn):
    cur = conn.cursor()
    current_year = datetime.now().year
    query = """
    SELECT id 
    FROM interviews_interview
    WHERE org_id = 1 AND EXTRACT(YEAR FROM timestamp) = %s;
    """
    cur.execute(query, (current_year,))
    results = cur.fetchall()
    cur.close()
    return [row[0] for row in results]

def fetch_pool_ids(conn, interview_ids):
    cur = conn.cursor()
    query = """
    SELECT pool_id 
    FROM interviews_interviewsession
    WHERE interview_id = ANY(%s)
    ORDER BY id ASC;
    """
    cur.execute(query, (interview_ids,))
    results = cur.fetchall()
    cur.close()
    return [row[0] for row in results]

def fetch_interview_data(conn):
    interview_ids = fetch_current_year_interview_ids(conn)
    
    if not interview_ids:
        return []

    pool_ids = fetch_pool_ids(conn, interview_ids)
    
    if not pool_ids:
        return []

    cur = conn.cursor()
    query = """
    SELECT id, name, invitation, created_on, 
           num_candidates, end_time, start_time
    FROM interviews_assignmentpool
    WHERE id = ANY(%s) AND num_candidates > 9;
    """
    cur.execute(query, (pool_ids,))
    results = cur.fetchall()
    cur.close()
    return results

def process_performance_data(interview_sessions):
    pool_scores = {}
    
    # Iterate through each session to process the data
    for session in interview_sessions:
        session_id, pool_id, performance, is_completed, details = session
        
        if isinstance(details, str):
            details = json.loads(details)
        
        if pool_id not in pool_scores:
            pool_scores[pool_id] = {
                'scores': [],
                'num_failed': 0,
                'not_completed': 0,
                'sub_categories': {}
            }
        
        pool_scores[pool_id]['scores'].append(performance)
        
        if performance < 70:
            pool_scores[pool_id]['num_failed'] += 1
        
        if not is_completed:
            pool_scores[pool_id]['not_completed'] += 1
        
        # Process sub-category details
        for sub_category, sub_data in details.items():
            if isinstance(sub_data, dict) and 'score' in sub_data:
                sub_performance = sub_data['score']
                
                if sub_category not in pool_scores[pool_id]['sub_categories']:
                    pool_scores[pool_id]['sub_categories'][sub_category] = {
                        'scores': [],
                        'num_failed': 0,
                        'not_completed': 0
                    }
                
                pool_scores[pool_id]['sub_categories'][sub_category]['scores'].append(sub_performance)
                
                if sub_performance < 70:
                    pool_scores[pool_id]['sub_categories'][sub_category]['num_failed'] += 1
                
                if not is_completed:
                    pool_scores[pool_id]['sub_categories'][sub_category]['not_completed'] += 1

    # Aggregate the data
    performance_data = []
    for pool_id, data in pool_scores.items():
        avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else None

        # Pool level data
        performance_data.append({
            'Pool ID': pool_id,
            'Average Score': avg_score,
            'Number of Students Failed': data['num_failed'],
            'Number of Students Not Completed': data['not_completed'],
            'Sub-Category Averages': {}
        })
        
        # Sub-category level data
        for sub_category, sub_data in data['sub_categories'].items():
            avg_sub_score = sum(sub_data['scores']) / len(sub_data['scores']) if sub_data['scores'] else None
            performance_data[-1]['Sub-Category Averages'][sub_category] = {
                'Average Score': avg_sub_score,
                'Number of Students Failed': sub_data['num_failed'],
                'Number of Students Not Completed': sub_data['not_completed']
            }
    
    return performance_data


def fetch_interview_sessions(conn, pool_ids):
    cur = conn.cursor()
    query = """
    SELECT id, pool_id, performance, is_completed, details
    FROM interviews_interviewsession
    WHERE pool_id = ANY(%s);
    """
    cur.execute(query, (pool_ids,))
    results = cur.fetchall()
    cur.close()
    return results
