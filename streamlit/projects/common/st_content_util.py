import streamlit as st
from pandas import DataFrame
import pandas as pd

import common.dqautil as du


def simple(dbrows):
    """
    Build a custom row layout use streamlit objects
    """
    dspcols = ["pid_hash", "process_name", "os_pid", "process_started"]
    for row in dbrows.fetchall():
        for col in dspcols:
            st.write(f"{col}: {row[dbrows.index(col)]}")


def singlerow(rowsDF: DataFrame):
    """
    Rotate the dataframe 90 degrees, making column names, column 1 values and row values columns 2-N.
    """
    form = rowsDF.df().transpose()
    form.columns = ["Value"]
    pd.set_option("display.max_columns", None)
    st.dataframe(form)


def display_node(pid_hash):
    node = du.getcon().sql(f"select * from process_summary where pid_hash='{pid_hash}'")
    # TODO: support multiple nodes with something like this:
    # pid_hashes=sel["nodes"]
    # node = con.executemany("select * from process_summary where pid_hash in (?)", [[pid_hashes]])
    cols = node.columns

    singlerow(node)
