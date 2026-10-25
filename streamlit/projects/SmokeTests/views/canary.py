import streamlit as st
from page_views import test_page

test_page(st.session_state['_smoke_context'], True)
