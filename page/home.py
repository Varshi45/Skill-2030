#page/home.py

import streamlit as st
import pandas as pd
from app import get_student_counts, render_pie_chart

def home_page():
    st.title("Skill-2030 Dashboard - Home")

    # Fetch and render student count data categorized by batch
    batch_counts = get_student_counts()
    render_pie_chart(batch_counts)
