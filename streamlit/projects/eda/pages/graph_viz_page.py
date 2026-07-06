import common.page_frags as pf
from pages._base_page import BasePageLayout
from pages.pages import app_pages
from common.utils import sidebar_config
import common.utils as utils
from utils.config import settings
import streamlit as st

from st_cytoscape import cytoscape
import common.wintapgraph as wg
import common.st_content_util as scu
import common.st_graph_util as sgu
import networkx as nx
import common.dqautil as du
import pandas as pd

# Search form keys
PROCESS_NAME = "process_name"
PID_HASH = "pid_hash"


class LandingPage(BasePageLayout):
    def __init__(self):
        super().__init__()

    def page_content(self):
        utils.load_keys([PROCESS_NAME, PID_HASH])
        st.set_page_config(
            page_icon=settings.app.logo, page_title="GraphViz", layout="wide"
        )
        sidebar_config(app_pages())
        st.header("Graph-based Exploration")
        pf.summary()

        netg, seed_processes = self.search_form()

        if netg:
            sgu.display_graph(netg)
            # , "roots": roots
            with st.expander("Graph JSON"):
                st.write(sgu.nx_to_stcyto(netg))

    def search_form(self):
        form_col, data_col = st.columns([1, 4])

        with form_col:
            netg = seed_processes = None
            st.markdown("### Search Criteria")
            with st.form("seed_form"):
                st.text_input("Process Name", key=f"_{PROCESS_NAME}")
                st.text_input("Pid Hash", key=f"_{PID_HASH}")
                ip_addr_txt = st.text_input("IP Address")
                port_txt = st.text_input("Port")
                num_seeds = st.slider("Max Seeds to Use",1,10)
                st.form_submit_button(
                    "Submit Query", on_click=utils.store_keys, args=[[PROCESS_NAME, PID_HASH]]
                )

        with data_col:
            if PROCESS_NAME in st.session_state and len(st.session_state[PROCESS_NAME])>0:
                # Find a more generic way to determine form was submitted
                netg, seed_processes = wg.build_graph(du.getcon(), process_name=[st.session_state[PROCESS_NAME]])
            elif PID_HASH in st.session_state and len(st.session_state[PID_HASH])>0:
                netg, seed_processes = wg.build_graph(du.getcon(), pid_hash=st.session_state[PID_HASH])
            
            if seed_processes != None:
                st.markdown("### Seed Processes")
                st.dataframe(seed_processes.df())
            else:
                st.info("No data")
        return netg, seed_processes


def main():
    page = LandingPage()
    page.page_content()


if __name__ == "__main__":
    main()
