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
            page_icon=settings.app.logo, page_title="DQA", layout="wide"
        )
        sidebar_config(app_pages())
        st.header("Wintap Summary Info!")
        pf.summary()

        with st.expander("Data Summary", expanded=True):
            # Hosts, labels, etc over time. Produces a constant vertical size, so its a good default for any size data set
            sqlstmt = du.getsqlstmt("common/process-queries.sql", "data_summary")
            dsdf = du.getdata(du.getcon(), sqlstmt.sql)
            if type(dsdf) != type(None):
                st.altair_chart(svd.create_data_summary(dsdf), use_container_width=True)
            else:
                st.error(f"Summary not availabe due to missing Process_Uber_Summary!")

        # Data size using stdview_duckdb.table_summary()
        # Note: This relies on parquet for rolling to be available. Handle gracefully when there is no parquet.
        try:
            parquet_size_df = svd.table_summary(
                du.getcon(),
                dataset=os.path.join(
                    settings.datasets.dataset_path, st.session_state.curds
                ),
            )
            with st.expander("Rolling Data Details"):
                st.dataframe(parquet_size_df)
        except FileNotFoundError as e:
            st.error("No rolling data")

        st.header("Process Life Cycle", divider=True)
        st.dataframe(
            du.getplsdf(du.getcon()),
            hide_index=True,
            column_config={
                "process_life_cd": "Start/Term",
                "uniq_process_name": "Uniq Process",
                "num_processes": "Processes",
                "pct": st.column_config.NumberColumn("Percent", format="%.2f %%"),
            },
        )

        # Proof-of-life debug info
        pf.debug_info()


def main():
    page = LandingPage()
    page.page_content()


if __name__ == "__main__":
    main()
