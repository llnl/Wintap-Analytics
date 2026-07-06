import common.page_frags as pf
from pages._base_page import BasePageLayout
from pages.pages import app_pages
from common.utils import sidebar_config
from utils.config import settings
import streamlit as st

import altair as alt

import common.dqautil as du
import wintappy.datautils.stdview_duckdb as svd
import os


class LandingPage(BasePageLayout):
    def __init__(self):
        super().__init__()

    def page_content(self):
        st.set_page_config(page_title="DLL Inspection", layout="wide")
        sidebar_config(app_pages())
        st.header("DDL Inspection")
        pf.summary()

        self.dll_gap_chart()

    def dll_gap_chart(self):
        dll_gaps_sql = du.getsqlstmt("pages/dll-queries.sql", "dll_gaps_sql")
        print(dll_gaps_sql)
        dll_gaps = du.getdata(du.getcon(), dll_gaps_sql.sql)

        st.metric(label="Rows", value=dll_gaps.shape[0])

        dll = dll_gaps.drop("diff", axis=1)

        chart_width = None
        chart_height = None

        # Note: Including width in chart spec causes poor/unusable display in streamlit.
        # Define selection thingy
        brush = alt.selection_interval(encodings=["x"])

        dll_chart = (
            alt.Chart(dll)
            .mark_bar(size=20)
            .encode(x="eventts", x2="prevts", y="hostname", color=alt.Color("hostname"))
            .properties(
                title="Gaps in DLL activity"
                # ).add_params(brush
            )
        )

        upper = dll_chart.add_params(brush)
        lower = dll_chart.encode(alt.X("eventts:T").scale(domain=brush))

        with st.container(border=True):
            # Selection linking works, but width doesn't
            #    st.altair_chart(upper & lower, use_container_width=True)

            # Selection linking works, but width doesn't
            upper.properties(width=1200, height=200, title="DLL Gaps")
            st.altair_chart(upper & lower, use_container_width=True)

    # Width works, on upper, but lower fails with "Unrecognized signal param_N"


#    st.altair_chart(upper, use_container_width=True)
#    st.altair_chart(lower, use_container_width=True)


# This function is really just here to hold onto this broken, unused code until I can fix it...
def combo():
    canaries = du.getdata(du.dqasql.canaries_sql)

    canaries_chart = (
        alt.Chart(canaries)
        .mark_circle()
        .encode(
            x="process_started",
            y="hostname",
            color="dll_num_uniq_files:N",
            tooltip=["process_name:N", "process_started:T", "dll_num_uniq_files:Q"],
        )
        .properties(title="Canary processes")
    )

    brush = alt.selection_interval(encodings=["x"])

    dll_chart = (
        alt.Chart(dll)
        .mark_bar(size=20)
        .encode(x="eventts", x2="prevts", y="hostname", color=alt.Color("hostname"))
        .properties(
            title="Gaps in DLL activity"
            # ).add_params(brush
        )
    )
    combo_chart = dll_chart.add_params(brush) + canaries_chart

    detail_chart = (
        dll_chart.encode(alt.X("process_started:T").scale(domain=brush))
        + canaries_chart
    )

    with st.container(border=True):
        st.altair_chart(combo_chart, use_container_width=True, theme="streamlit")
        st.altair_chart(detail_chart, use_container_width=True, theme="streamlit")
        st.markdown(
            """
            * Horizontal bars gaps when no DLL activity was seen.
            * Points are canary proceses, run every 5 seconds.
            * There *should* be DLL events for every process.
    """
        )


def main():
    page = LandingPage()
    page.page_content()


if __name__ == "__main__":
    main()
