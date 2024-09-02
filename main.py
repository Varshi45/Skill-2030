import streamlit as st
from page.home import home_page
from page.interviews import interviews_page
from page.categorical_analysis import categorical_analysis_page
from page.test_analysis import test_analysis_page

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a page", ["Home", "Interviews", "Overall Analysis", "Test Analysis"])

    if page == "Home":
        home_page()
    elif page == "Interviews":
        interviews_page()
    elif page == "Overall Analysis":
        categorical_analysis_page()
    elif page == "Test Analysis":
        test_analysis_page()

if __name__ == "__main__":
    main()
