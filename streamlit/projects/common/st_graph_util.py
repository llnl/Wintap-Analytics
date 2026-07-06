from st_cytoscape import cytoscape
import common.st_content_util as scu
import common.wintapgraph as wg
import networkx as nx
import streamlit as st
import common.dqautil as du
import json


def networkx_to_stcyto(G):
    """
    Use networkx.cytoscape_data to export to JSON, then reshape that to stcyto
    This works, but...
    """

    # Start with networkx export
    cytojson = nx.cytoscape_data(G)

    # Convert to format expected by stcyto:
    #  elements/nodes/data -> data
    #  elements/edges/data -> data
    # Yup, nodes and edges get merged into the same level.
    stcyto = cytojson["elements"]["nodes"]
    stcyto.extend(cytojson["elements"]["edges"])
    return stcyto


def nx_to_stcyto(G):
    """
    Convert directly from networkx graph to stcyto json.
    Provides more control and allows labels
    """
    elements = []
    for i in G.nodes(data="label"):
        label = "Missing" if i[1] == None else i[1]
        elements.append({"data": {"id": i[0], "label": label}})

    for i in G.edges:
        elements.append({"data": {"source": i[0], "target": i[1]}})
    return elements


def export_graph(netg, name="Sample"):
    print(f"Writing graph to files: {name}")
    nx.write_graphml_lxml(netg, f"{name}.graphml")
    cytodict = nx.cytoscape_data(netg, name)
    with open(f"{name}.json", "w") as f:
        json.dump(cytodict, f)

def display_comp(netg):
    # Try splitting the graph into its connected components and plot them seperately
#    for comp in nx.connected_component_subgraphs(netg):
    for comp in nx.connected_components(netg.to_undirected()):
        st.write(type(comp))
        st.write(comp)
        display_graph(comp)

def display_graph(netg, process_name_txt="(should be the filter value)"):
    if "netg" in locals():
        with st.container(border=True):
            st.header("Wintap Data")
            sel_layout = st.selectbox(
                "Layout", ["breadthfirst", "cose", "concentric", "circle", "grid"]
            )

            # Use 0 in-degree, which is effectively the children.
            leaf_nodes = [n for n, d in netg.in_degree() if d == 0]
            # A variety of experiments that haven't worked out well for better layout.
#            root_nodes = [n for n, d in netg.out_degree() if d == 0]
#            edgelist = [e for e in netg.edges if e not in nx.selfloop_edges(netg)]
#            krnl_nodes = [s for (s,d) in edgelist]
#            with st.expander("Node IDs"):
#                st.write(krnl_nodes)
#                st.write(root_nodes)

            sel = cytoscape(
                nx_to_stcyto(netg),
                get_stylesheet(),
                layout={
                    "name": sel_layout,
#                    "roots": leaf_nodes,
                    "directed": False,
#                    "grid": True,
                },
                height="800px",
                min_zoom=0.5,
                max_zoom=3,
                key="_netg",
            )

        st.markdown("**Selected nodes**: %s" % (", ".join(sel["nodes"])))
        st.markdown("**Selected edges**: %s" % (", ".join(sel["edges"])))

        # Display selected nodes in a table.
        # Note: cheating for now and just displaying the first one.
        if len(sel["nodes"]) > 0:
            scu.display_node(sel["nodes"][0])

        st.button(
            "Export (cytoscape and graphml)",
            on_click=export_graph,
            args=[
                netg,
                f"Wintap-{st.session_state.curds}-{st.session_state.curdb}-{process_name_txt}",
            ],
        )


def get_stylesheet():
    """
    Stylesheets don't seem, to work completely, Need more effort to figure out what does/doesn't work in Streamlit
    """
    stylesheet = [
        {
            "selector": "node",
            "style": {
                "label": "data(label)",
                "width": 40,
                "height": 40,
                "font-size": 32,
                "text-valign": "center",
                "line-height": "2",
                "text-wrap": "wrap",
                "text-justification": "left",
            },
        },
        {
            "selector": "edge",
            "style": {
                "width": 3,
                "curve-style": "bezier",
                "target-arrow-shape": "triangle",
            },
        },
    ]
    return stylesheet
