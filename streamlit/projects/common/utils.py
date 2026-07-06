import common.dqautil as du
import streamlit as st
from utils.config import settings
import pages.pages as pages


def get_allds():
    if "allds" not in st.session_state:
        st.session_state.allds = du.finddatasets(settings.datasets.dataset_path)
    return st.session_state.allds


def app_base_config():
    st.set_page_config(
        # Page_title actually sets the tab name
        page_title=settings.app.page_title,
        initial_sidebar_state="expanded",
    )
    st.markdown("Virtual Main Page: Select a page from the sidebar!!")
    st.json(st.session_state)


def sidebar_config(pages,logo=settings.app.logo, logo_width=120):
    st.sidebar.image(logo, width=logo_width)
    st.sidebar.title(settings.app.page_title)
    st.sidebar.header("Menu")
    # Add all pages to the sidebar. They'll be listed in the order added.
    for page in pages:
        st.sidebar.page_link(page.filename, label=page.label)
    sidebar_db_chooser()


def change_cur_ds():
    # Streamlit scopes widget bound keys to a page and we want the state maintained across the session, so sync here.
    st.session_state.curds = st.session_state._curds
    st.session_state._curdb = None
    st.session_state.curdb = None


def change_cur_db():
    # Streamlit scopes widget bound keys to a page and we want the state maintained across the session, so sync here.
    st.session_state.curdb = st.session_state._curdb
    if st.session_state.curdb != None:
        print(f"on_change: opening db: {st.session_state.curdb}")
        du.opendb(get_allds()[st.session_state.curds].getdb(st.session_state.curdb))


def sidebar_db_chooser():
    with st.sidebar:
        # Index into options list. Default to None forces user to select one.
        curds_idx = None
        if "curds" in st.session_state:
            # Get index to set as default selections
            curds_idx = list(get_allds()).index(st.session_state.curds)

        st.selectbox(
            "Dataset: ",
            get_allds().keys(),
            index=curds_idx,
            key="_curds",
            on_change=change_cur_ds,
        )
        if "curds" in st.session_state:
            # With only 1 database, don't bother with the selectbox, just use it. And display as text.
            if len(get_allds()[st.session_state.curds].databases) == 1:
                st.session_state._curdb = get_allds()[st.session_state.curds].databases[
                    0
                ]
                change_cur_db()
                st.markdown(f"*{st.session_state.curdb}*")
            else:
                curdb_idx = None
                if "curdb" in st.session_state and st.session_state.curdb != None:
                    curdb_idx = list(
                        get_allds()[st.session_state.curds].databases
                    ).index(st.session_state.curdb)
                st.selectbox(
                    "Database: ",
                    get_allds()[st.session_state.curds].databases,
                    index=curdb_idx,
                    key="_curdb",
                    on_change=change_cur_db,
                )


# Widget state utilities
def store_keys(keys: list):
    for key in keys:
        st.session_state[key] = st.session_state["_" + key]


def load_keys(keys: list):
    for key in keys:
        if key in st.session_state:
            st.session_state["_" + key] = st.session_state[key]
