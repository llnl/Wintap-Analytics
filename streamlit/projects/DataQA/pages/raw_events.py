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
            page_icon="common/Wintap.png", page_title="Raw Events", layout="wide"
        )
        sidebar_config(app_pages())
        st.header("Investigating Raw Events")
        pf.summary()

        with st.expander("Event Summary", expanded=False):
            # Events over time. Produces a variable vertical size based on the number of hosts. Problematic for larger data sets.
            # To do: Dynamically adjust the bucket size based on the dataset duration for the best resolution/performance.
            # Move this into stdview_duckdb and make behavior the default...

            (min, max) = du.get(du.getcon(), "data_range")
            svd.init_db(du.getcon(), min, max, bucket_size="0:00:30")
            eventdf = svd.fetch_summary_data(du.getcon())
            st.altair_chart(svd.create_event_chart(eventdf), use_container_width=True)


def main():
    page = LandingPage()
    page.page_content()


if __name__ == "__main__":
    main()
