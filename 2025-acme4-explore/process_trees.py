import igraph as ig
import numpy as np
import pandas as pd
from collections import Counter

## compute bag of features
def subtree_features(sg):
    root = np.where(np.array(sg.degree(mode='in'))==0)[0][0]
    V, L, _ = sg.bfs(root)
    F = []
    for i in range(len(L)-1):
        P = []
        for j in np.arange(L[i],L[i+1]):
            P.append(sg.vs[V[j]]['process'])
        C = Counter(P)
        keys = list(C.keys())
        vals = list(C.values())
        for j in range(len(keys)):
            for k in range(vals[j]):
                F.append(str(i)+'::'+keys[j]+'::'+str(k)) 
    return set(F)

## overlap coefficient (aka Szymkiewicz-Simpson)
def szym_sim(a,b):
    return len(a.intersection(b))/min(len(a),len(b))

def get_parent(Trees, tree, node):
    sg = Trees.subgraph(tree)
    if sg.degree(node, mode='in')==1:
        return sg.es.select(_target=node)[0].source
    else:
        return -1

## utility function - extract subgraph from VertexClustering object
def get_bfs_subtree(Trees, tree_id, root_id):
    
    ## get subtree
    g = Trees.subgraph(tree_id)

    ## bfs ordering
    nodes, _ , parent = g.bfs(root_id)
    
    ## save vertices in new graph
    G = ig.Graph(directed=True)
    names = [str(g.vs['name'][i]) for i in nodes] ## in BFS order
    G.add_vertices(names)
    
    ## save attributes in same order    
    for att in g.vs.attribute_names():
        if att != 'name':
            G.vs[att] = [g.vs[att][i] for i in nodes]
    
    ## add edges
    E = [(str(g.vs['name'][parent[i]]),str(g.vs['name'][i])) for i in nodes if parent[i]>=0]
    G.add_edges(E)    
    
    ## tree layout for plotting
    G["ly"] = G.layout_reingold_tilford() 

    return G

def build_process_trees(process, min_tree_size=3, max_tree_size=1000000):
    ## keep required columns
    cols = ['pid_hash', 'parent_pid_hash', 'process_name', 'user_name', 'process_started', 'file_md5']
    df = process[cols]    
    df = df.drop_duplicates(cols)
    ## parents and children
    child = set(df.pid_hash)
    parent = set(df.parent_pid_hash) ## Can be 'None', we'll delete later
    ## node dictionaries
    nodes = parent.union(child)
    nodes_dict = {v:k for k,v in enumerate(nodes)}
    inv_nodes_dict = {k:v for k,v in enumerate(nodes)}

    ## build directed graph from edgelist
    child = [nodes_dict[x] for x in df.pid_hash]
    parent = [nodes_dict[x] for x in df.parent_pid_hash]
    edges = np.array([parent,child]).T
    G = ig.Graph.TupleList(edges, directed=True)
    G = G.simplify() ## there are 53 self-edges
    G.vs['pid'] = [inv_nodes_dict[int(x)] for x in G.vs['name']]

    ## add some node features
    user_dict = dict(zip(df.pid_hash,df.user_name))
    G.vs['username'] = [user_dict.get(x, None) for x in G.vs['pid']]
    process_dict = dict(zip(df.pid_hash, df.process_name))
    G.vs['process'] = [process_dict.get(x, "") for x in G.vs['pid']]
    # merge None and ''
    x = np.where(np.array(G.vs['process'])==None)[0]
    G.vs[x]['process'] = ''
    ## file md5
    _dict = dict(zip(df.pid_hash, df.file_md5))
    G.vs['filemd5'] = [_dict.get(x, "") for x in G.vs['pid']]
    ## timestamps
    T = []
    for x in df['process_started']:
        if pd.isna(x):
            T.append('')
        else: 
            T.append(int(x.timestamp()))
    time_dict = dict(zip(df.pid_hash, T))
    G.vs['time'] = [time_dict.get(x, "") for x in G.vs['pid']]

    ## short names for plotting and to anonymize
    shortname_dict = {'ACME-HH-BKQ\\ssm-user':'ssmBKQ',
     'ACME-HH-WHS\\ssm-user':'ssmWHS',
     'ACME-HH-YVU\\ssm-user':'ssmYVU',
     'ACME-WS-PLU\\ssm-user':'ssmPLU',
     'ACME\\SUPERDA':'user99',
     'ACME\\baduser25':'bad25',
     'ACME\\baduser3':'bad3',
     'ACME\\baduser9':'bad9',
     'ACME\\davidf':'user77',
     'ACME\\ghostuser1':'ghost1',
     'ACME\\ghostuser2':'ghost2',
     'ACME\\grantj':'user88',
     'ACME\\user1':'user1',
     'ACME\\user10':'user10',
     'ACME\\user11':'user11',
     'ACME\\user2':'user2',
     'ACME\\user20':'user20',
     'ACME\\user3':'user3',
     'ACME\\user4':'user4',
     'ACME\\user6':'user6',
     'ACME\\user8':'user8',
     'ACME\\user9':'user9',
     'EC2AMAZ-R9HHULK\\Administrator':'admin',
     'Font Driver Host\\UMFD-0':'umfd0',
     'Font Driver Host\\UMFD-1':'umfd1',
     'Font Driver Host\\UMFD-2':'umfd2',
     'Font Driver Host\\UMFD-3':'umfd3',
     'Font Driver Host\\UMFD-4':'umfd4',
     'Font Driver Host\\UMFD-5':'umfd5',
     'Font Driver Host\\UMFD-6':'umfd6',
     'Font Driver Host\\UMFD-7':'umfd7',
     'NT AUTHORITY\\LOCAL SERVICE':'LOCAL',
     'NT AUTHORITY\\NETWORK SERVICE':'NET',
     'NT AUTHORITY\\SYSTEM':'SYS',
      None:'',
     'ROOT':'ROOT',
     'Window Manager\\DWM-1':'dwm1',
     'Window Manager\\DWM-2':'dwm2',
     'Window Manager\\DWM-3':'dwm3',
     'Window Manager\\DWM-4':'dwm4',
     'Window Manager\\DWM-5':'dwm5',
     'Window Manager\\DWM-6':'dwm6',
     'Window Manager\\DWM-7':'dwm7'}

    ## node labels
    G.vs['label'] = [shortname_dict[v['username']]+'::'+v['process'] for v in G.vs]
    G.vs['shortlabel'] = [shortname_dict[v['username']] for v in G.vs]
    
    ## use red for badusers
    G.vs['label_color'] = 'black'
    G.vs['color'] = 'black'
    G.vs[np.where(['bad' in x for x in G.vs['shortlabel']])[0]]['label_color'] = 'red'
    G.vs[np.where(['bad' in x for x in G.vs['shortlabel']])[0]]['color'] = 'red'

    idx = np.where(np.array(G.vs['pid']) == None)[0]
    if len(idx)>0:
        G.delete_vertices(idx)
    
    ## find all connected components a.k.a. process trees (with one exception)
    Trees = G.connected_components(mode="weak")
    G.vs['tree'] = Trees.membership

    ## drop trees of size < min_tree_size and non-tree(s)
    _dct = dict(enumerate(Trees.sizes()))
    G.vs['tree_size'] = [_dct[i] for i in G.vs['tree']]
    roots = np.where(np.array(G.degree(mode='in'))==0)
    non_tree = set(np.array(G.vs['tree'])).difference(set(np.array(G.vs['tree'])[roots]))
    G.delete_vertices([v for v in G.vs if (v['tree_size']<min_tree_size or v['tree'] in non_tree)])

    ## re-compute 
    Trees = G.connected_components(mode="weak")
    G.vs['tree'] = Trees.membership

    ## build dataframe with (sub)process trees 
    ## keep only trees with some non-empty root process name
    L = []
    for tree in range(len(Trees)):
        if len(Trees[tree])<=max_tree_size:
            sg = Trees.subgraph(tree)
            for v in sg.vs:
                if v['process'] != '' and v['process'] != 'unknown' and sg.degree(v, mode='out')>0: ## pick non-leaf nodes with some process name
                    V, l, p = sg.bfs(v.index)
                    nodes = len(V)
                    splits = sum([x>1 for x in list(Counter(np.array(p)[np.array(p)>=0]).values())])
                    if nodes<=2: ## subtrees of size 3+ only
                        continue
                    leaves = nodes - len(set(np.array(p)[np.array(p)>=0]))
                    layers = len(l)-1
                    b3 = len([x for x in sg.vs[V]['username'] if x is not None and 'baduser3' in x])
                    b9 = len([x for x in sg.vs[V]['username'] if x is not None and 'baduser9' in x])
                    b25 = len([x for x in sg.vs[V]['username'] if x is not None and 'baduser25' in x])
                    x = [tree, v.index,v['process'], nodes, layers, leaves, b3,b9,b25,splits,np.diff(l)]
                    L.append(x)

    ## dataframe
    df_trees = pd.DataFrame(L, columns=['tree','root','process','nodes','layers','leaves','bad3','bad9','bad25','splits','distribution'])
    df_trees['badusers'] = df_trees.bad3 + df_trees.bad9 + df_trees.bad25

    return Trees, df_trees