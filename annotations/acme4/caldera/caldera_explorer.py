import streamlit as st
import duckdb
import json
import pandas as pd
from collections import defaultdict

st.set_page_config(layout="wide", page_title="Caldera Report Explorer")

# Initialize session state for selections
if 'selections' not in st.session_state:
    st.session_state.selections = {}

# Load schema
@st.cache_data
def load_schema(schema_path='caldera_report_schema.json'):
    with open(schema_path, 'r') as f:
        return json.load(f)

# Build tree structure from schema
@st.cache_data
def build_table_tree(schema):
    """Build hierarchical tree: parent -> [children]"""
    tree = defaultdict(list)
    for table_name, table_info in schema['tables'].items():
        parent = table_info.get('parent')
        if parent:
            tree[parent].append(table_name)
        elif not table_name.startswith('_dlt'):  # Root tables (excluding DLT internal)
            tree[None].append(table_name)
    return tree

# Get table depth
def get_table_depth(table_name, tree, depth=0):
    """Calculate depth of table in hierarchy"""
    for parent, children in tree.items():
        if table_name in children:
            if parent is None:
                return 0
            return get_table_depth(parent, tree, depth) + 1
    return depth

def build_tree_text(tree, schema, parent=None, prefix="", is_last=True):
    """Build ASCII tree representation"""
    lines = []
    
    if parent is None:
        # Start with root tables
        root_tables = [t for t in tree[None] if not t.startswith('_dlt')]
        for i, table in enumerate(sorted(root_tables)):
            is_last_root = (i == len(root_tables) - 1)
            lines.append(f"📄 {table}")
            lines.extend(build_tree_text(tree, schema, table, "", is_last_root))
    else:
        # Add children
        children = sorted(tree.get(parent, []))
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            
            # Determine the tree characters
            if is_last:
                connector = "└── " if is_last_child else "├── "
                extension = "    " if is_last_child else "│   "
            else:
                connector = "├── " if not is_last_child else "└── "
                extension = "│   " if not is_last_child else "    "
            
            # Check if selected
            icon = "📍" if child in st.session_state.selections else "📁"
            lines.append(f"{prefix}{connector}{icon} {child}")
            
            # Recursively add children
            lines.extend(build_tree_text(tree, schema, child, prefix + extension, is_last_child))
    
    return lines

def render_interactive_tree(tree, schema):
    """Render an interactive tree with expandable nodes"""
    st.subheader("🌳 Interactive Table Tree")
    
    root_tables = [t for t in tree[None] if not t.startswith('_dlt')]
    
    for root in sorted(root_tables):
        render_tree_node(tree, schema, root, level=0)

def render_tree_node(tree, schema, table_name, level=0):
    """Recursively render tree node with expander"""
    children = sorted(tree.get(table_name, []))
    
    # Determine icon
    is_selected = table_name in st.session_state.selections
    icon = "📍" if is_selected else ("📄" if level == 0 else "📁")
    
    # Get row count if available
    indent = "　" * level  # Using full-width space for indentation
    
    if children:
        with st.expander(f"{indent}{icon} **{table_name}** ({len(children)} children)", expanded=(level < 2)):
            if is_selected:
                st.caption(f"Selected ID: {st.session_state.selections[table_name][:16]}...")
            
            for child in children:
                render_tree_node(tree, schema, child, level + 1)
    else:
        st.markdown(f"{indent}{icon} **{table_name}**")
        if is_selected:
            st.caption(f"{indent}　Selected ID: {st.session_state.selections[table_name][:16]}...")

# Connect to DuckDB with schema selection
@st.cache_resource
def get_connection(db_path='caldera.duckdb', cur_schema='dlt'):
    conn = duckdb.connect(db_path, read_only=True)
    conn.sql(f"USE {cur_schema}")
    return conn

def get_available_schemas(conn):
    """Get list of schemas in the database"""
    schemas = conn.execute("SELECT schema_name FROM information_schema.schemata ORDER BY schema_name").fetchall()
    return [s[0] for s in schemas]

def query_table(conn, table_name, parent_id=None, limit=1000):
    """Query table with optional parent filter"""
    try:
        if parent_id is not None:
            query = f"SELECT * FROM {table_name} WHERE _dlt_parent_id = ? LIMIT {limit}"
            df = conn.execute(query, [parent_id]).df()
            count_query = f"SELECT COUNT(*) as cnt FROM {table_name} WHERE _dlt_parent_id = ?"
            count = conn.execute(count_query, [parent_id]).fetchone()[0]
        else:
            df = conn.execute(f"SELECT * FROM {table_name} LIMIT {limit}").df()
            count = conn.execute(f"SELECT COUNT(*) as cnt FROM {table_name}").fetchone()[0]
        return df, count
    except Exception as e:
        st.error(f"Error querying {table_name}: {e}")
        return None, 0

def display_table_with_selection(conn, table_name, parent_id=None, level=0):
    """Display table with row selection capability"""
    df, count = query_table(conn, table_name, parent_id)
    
    if df is None or df.empty:
        st.warning(f"No data in {table_name}")
        return None
    
    # Show filter status
    if parent_id:
        st.info(f"📌 Filtered by parent ID: `{parent_id}`")
    
    st.write(f"**Rows:** {count:,} (showing up to 1000)")
    
    # Display dataframe with selection
    event = st.dataframe(
        df,
        width=True,
        on_select="rerun",
        selection_mode="single-row"
    )
    
    # Get selected row
    selected_rows = event.selection.rows if hasattr(event, 'selection') else []
    
    if selected_rows:
        selected_idx = selected_rows[0]
        if '_dlt_id' in df.columns:
            selected_id = df.iloc[selected_idx]['_dlt_id']
            
            # Show selected row details
            with st.expander("🔍 Selected Row Details"):
                st.json(df.iloc[selected_idx].to_dict())
            
            return selected_id
    
    # If nothing selected but we have a previous selection, keep it
    if table_name in st.session_state.selections:
        st.caption(f"📍 Using previous selection: `{st.session_state.selections[table_name]}`")
        return st.session_state.selections[table_name]
    
    return None

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    schema_path = st.text_input("Schema JSON", value="caldera_report_schema.json")
    db_path = st.text_input("DuckDB file", value="caldera.duckdb")

    # Create a short-lived connection just to list schemas.
    _tmp_conn = duckdb.connect(db_path, read_only=True)
    available_schemas = get_available_schemas(_tmp_conn)
    _tmp_conn.close()

    selected_schema = st.selectbox(
        "Select Schema",
        available_schemas,
        index=available_schemas.index('dlt') if 'dlt' in available_schemas else 0,
    )

    st.divider()

# Load schema and build tree
schema = load_schema(schema_path=schema_path)
tree = build_table_tree(schema)
conn = get_connection(db_path=db_path, cur_schema=selected_schema)

# Main app
st.title("Caldera Report Explorer")
st.caption("Select rows to filter child tables. Selections cascade down the hierarchy.")

# Add tree visualization tab
tab_data, tab_tree = st.tabs(["📊 Data Explorer", "🌳 Table Structure"])

with tab_tree:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📋 ASCII Tree View")
        tree_lines = build_tree_text(tree, schema)
        tree_text = "\n".join(tree_lines)
        st.code(tree_text, language=None)
    
    with col2:
        render_interactive_tree(tree, schema)

with tab_data:
    # Organize tables by depth
    tables_by_depth = defaultdict(list)
    for table_name in schema['tables'].keys():
        if not table_name.startswith('_dlt'):
            depth = get_table_depth(table_name, tree)
            tables_by_depth[depth].append(table_name)

    # Display root table (depth 0)
    st.header("📄 Level 0: Root Table")

    root_table = 'raw_report'
    selected_root_id = display_table_with_selection(conn, root_table, level=0)

    if selected_root_id:
        st.session_state.selections[root_table] = selected_root_id

    # Display Level 1 children
    if 1 in tables_by_depth and selected_root_id:
        st.header("📁 Level 1: Child Tables")
        
        level1_tabs = st.tabs(tables_by_depth[1])
        
        for tab, table_name in zip(level1_tabs, tables_by_depth[1]):
            with tab:
                parent = schema['tables'][table_name].get('parent')
                st.caption(f"Parent: `{parent}`")
                
                # Use selected parent ID for filtering
                parent_id = st.session_state.selections.get(parent)
                selected_id = display_table_with_selection(conn, table_name, parent_id, level=1)
                
                if selected_id:
                    st.session_state.selections[table_name] = selected_id

    # Display Level 2 children
    if 2 in tables_by_depth:
        st.header("📂 Level 2: Grandchild Tables")
        
        level2_tabs = st.tabs(tables_by_depth[2])
        
        for tab, table_name in zip(level2_tabs, tables_by_depth[2]):
            with tab:
                parent = schema['tables'][table_name].get('parent')
                st.caption(f"Parent: `{parent}`")
                
                # Use selected parent ID for filtering
                parent_id = st.session_state.selections.get(parent)
                
                if parent_id:
                    selected_id = display_table_with_selection(conn, table_name, parent_id, level=2)
                    
                    if selected_id:
                        st.session_state.selections[table_name] = selected_id
                else:
                    st.info("⬆️ Select a row in the parent table to view this data")

    # Display Level 3+ children
    max_depth = max(tables_by_depth.keys()) if tables_by_depth else 0
    for depth in range(3, max_depth + 1):
        if depth in tables_by_depth:
            st.header(f"📂 Level {depth} Tables")
            
            level_tabs = st.tabs(tables_by_depth[depth])
            
            for tab, table_name in zip(level_tabs, tables_by_depth[depth]):
                with tab:
                    parent = schema['tables'][table_name].get('parent')
                    st.caption(f"Parent: `{parent}`")
                    
                    # Use selected parent ID for filtering
                    parent_id = st.session_state.selections.get(parent)
                    
                    if parent_id:
                        selected_id = display_table_with_selection(conn, table_name, parent_id, level=depth)
                        
                        if selected_id:
                            st.session_state.selections[table_name] = selected_id
                    else:
                        st.info("⬆️ Select a row in the parent table to view this data")

# Sidebar with schema overview and selection state (continued)
with st.sidebar:
    st.header("Schema Overview")
    st.write(f"**Active Schema:** `{selected_schema}`")
    st.write(f"**Total Tables:** {len([t for t in schema['tables'].keys() if not t.startswith('_dlt')])}")
    st.write(f"**Max Depth:** {max_depth}")
    
    st.divider()
    
    st.subheader("Current Selections")
    if st.session_state.selections:
        for table, dlt_id in st.session_state.selections.items():
            st.text(f"📍 {table}")
            st.caption(f"   ID: {dlt_id[:16]}...")
    else:
        st.caption("No selections yet")
    
    if st.button("🔄 Clear All Selections"):
        st.session_state.selections = {}
        st.rerun()
    
    st.divider()
    
    st.subheader("Quick Tree View")
    tree_lines = build_tree_text(tree, schema)
    st.code("\n".join(tree_lines[:20]) + "\n..." if len(tree_lines) > 20 else "\n".join(tree_lines), language=None)
