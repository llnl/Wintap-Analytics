import common.page_frags as pf
from pages._base_page import BasePageLayout
from pages.pages import app_pages
from common.utils import sidebar_config
from utils.config import settings
import streamlit as st

import common.dqautil as du
import wintappy.datautils.stdview_duckdb as svd
import os


class LandingPage(BasePageLayout):
    def __init__(self):
        super().__init__()

    def page_content(self):
        st.set_page_config(
            page_icon=settings.app.logo, page_title="Debug", layout="wide"
        )
        sidebar_config(app_pages())
        st.header("Streamlit Debugging Tools")
        pf.summary()

        with st.expander("Session State"):
            st.json(st.session_state)

        # Widgets update session_state using the "key" attribute. Awesome.
        # But, in multipage apps, they also clear out session_state when leaving the page!
        # Suggested hack is to persist the value in a shadow variable.
        # Ref: https://discuss.streamlit.io/t/text-input-behavior-for-updating-a-session-state-value-is-not-intuitive-for-my-use-case/38814

        # Initialize shadow for first execution
        if "_debug_sql" not in st.session_state:
            st.session_state._debug_sql = "summarize process"

        def change_sql():
            st.session_state._debug_sql = st.session_state.debug_sql

        st.text_input(
            "SQL",
            value=st.session_state._debug_sql,
            key="debug_sql",
            on_change=change_sql,
        )
        try:
            st.dataframe(du.getcon().sql(st.session_state.debug_sql).df())
        except Exception as e:
            st.error(e)


def main():
    page = LandingPage()
    page.page_content()


if __name__ == "__main__":
    main()
