import streamlit as st

def main():
    st.title("Watchdog Streamlit App")
    st.write("This is a simple Streamlit application that monitors FastAPI and Streamlit services.")
    
    st.header("Service Status")
    st.write("The watchdog script is responsible for monitoring the health of the services.")
    
    # Placeholder for displaying service health status
    st.write("FastAPI Status: **Running**")
    st.write("Streamlit Status: **Running**")

if __name__ == "__main__":
    main()