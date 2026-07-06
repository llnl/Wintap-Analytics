import sys
from pathlib import Path
from mdutils.mdutils import MdUtils
import networkx as nx
import matplotlib.pyplot as plt

from caldera_report_common import (
    load_report,
    decode_if_base64,
    iter_hosts,
    iter_links,
    iter_steps,
    sanitize_operation_name,
)

# Modified from: https://github.com/marksowell/caldera-report-generator
# Enhanced with unified step rendering, ATT&CK links, and NetworkX graph

def beachhead(host):
    return f"""
        node beachhead {{
            type Process {{
                att_type ProcessKey {{
                    hostName equals {host['host']};
                    pid equals {host['pid']};
                }}
            }}
        }}
    """

def c2_server(server):
    # Server should be: http://172.31.10.226:8888
    if '//' in server:
        ip_port = server.split('//')[1]
    else:
        ip_port = server
    if ':' in ip_port:
        ip, port = ip_port.split(':')
    else:
        ip = ip_port
        port = 'N/A'
    return f'''
        node c2_server {{
            type IpV4Addr {{
                att_type IpV4Addr {{
                    ip equals {ip};
                }}
            }}
        }}
        link c2_server to beachhead {{
            type RemoteHasIpV4 {{
                att_type IpV4Addr {{
                    ip equals {ip};
                }}
            }}
        }}
    '''

def hosts(data, markdown):
    markdown.new_header(level=1, title="Hosts Attacked")
    
    columns = ["Host", "User", "Beachhead Cmd", "PID", "Parent PID", "IPs", "C2 Server"]
    rows = [columns]  # header row
    
    hostmap = {}
    c2_servers_seen = set()

    for host in iter_hosts(data):
        paw = host.get('paw')
        hostmap[paw] = host.get('host')
        
        row = [
            host.get('host', 'N/A'),
            host.get('username', 'N/A'),
            host.get('exe_name', 'N/A'),
            str(host.get('pid', 'N/A')),
            str(host.get('ppid', 'N/A')),
            ', '.join(host.get('host_ip_addrs', [])) if host.get('host_ip_addrs') else "N/A",
            host.get('server', 'N/A')
        ]
        rows.append(row)
        
        # Collect unique C2 for later graph
        c2_servers_seen.add(host.get('server', 'N/A'))

    if len(rows) > 1:
        flat_text = [item for sublist in rows for item in sublist]
        markdown.new_table(columns=len(columns), rows=len(rows), text=flat_text)
    else:
        markdown.new_paragraph("No hosts found in report.")
        
    return hostmap, c2_servers_seen

def render_step(step, hostmap, markdown, source="legacy_links"):
    paw = step.get('paw') or step.get('host', 'N/A')
    hostname = hostmap.get(paw, paw)
    
    cmd = decode_if_base64(step.get('plaintext_command') or step.get('command'))
    
    attack_id = step.get('ability', {}).get('technique_id') or step.get('attack', {}).get('technique_id', 'N/A')
    technique_name = step.get('ability', {}).get('technique_name') or step.get('attack', {}).get('technique_name', 'N/A')
    
    markdown.new_paragraph(f"**[{source.upper()}] {hostname} ({paw})**")
    if cmd:
        markdown.new_paragraph(f"**Command:** `{cmd}`")
    markdown.new_paragraph(f"**Description:** {step.get('description', 'N/A')}")
    markdown.new_paragraph(f"**Technique:** {technique_name}")
    if attack_id != 'N/A':
        url = f"https://attack.mitre.org/techniques/{attack_id.replace('.', '/')}"
        markdown.new_paragraph(f"**ATT&CK:** [{attack_id}]({url})")
    markdown.new_paragraph(f"**Status:** `{'Success' if step.get('status') == 0 else 'Failed'}`")
    markdown.new_paragraph(f"**PID:** {step.get('pid', 'N/A')}")
    markdown.new_paragraph(f"**Time:** {step.get('collect') or step.get('run', 'N/A')} → {step.get('finish', 'N/A')}")
    markdown.new_line()

def generate_graph(data, hostmap, png_path: Path):
    G = nx.DiGraph()
    G.add_node("C2 Server", shape="box", color="red")
    
    for host in iter_hosts(data):
        hostname = host.get('host', 'N/A')
        paw = host.get('paw', 'N/A')
        G.add_node(hostname, paw=paw, shape="ellipse", color="lightblue")
        G.add_edge("C2 Server", hostname, label="beacon")
        
        # Add beachhead process
        proc = f"{hostname}#{host.get('pid', 'N/A')}"
        G.add_node(proc, shape="rectangle", color="orange")
        G.add_edge(hostname, proc, label="spawned")
    
    plt.figure(figsize=(12,8))
    pos = nx.spring_layout(G, k=1, iterations=50)
    nx.draw(G, pos, with_labels=True, node_color="lightgray", node_size=2000, font_size=9)
    plt.title(f"CALDERA Operation: {data.get('name', 'Unnamed')}")
    plt.savefig(png_path, dpi=150, bbox_inches='tight')
    plt.close()

def main():
    # Check if a file path is provided as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python convert_caldera.py <path_to_json_file>")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    try:
        data = load_report(json_file_path)
    except Exception as e:
        print(f"Failed to load JSON file: {e}")
        sys.exit(1)
    
    operation_name = sanitize_operation_name(data.get('name'))

    out_dir = Path(__file__).resolve().parent / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)

    md_path = out_dir / f"{operation_name}_caldera_report.md"
    png_path = out_dir / f"{operation_name}_graph.png"

    markdown = MdUtils(file_name=str(md_path), title=data.get('name', 'Unnamed Operation'))
    
    markdown.new_header(1, "CALDERA Operation Report")
    markdown.new_paragraph(f"**Operation:** {data.get('name', 'N/A')}<br>**Start:** {data.get('start', 'N/A')}<br>**Adversary:** {data.get('adversary', {}).get('name', 'N/A')}")
    
    hostmap, _ = hosts(data, markdown)
    
    markdown.new_header(1, "Execution Timeline")
    # Unified rendering for links
    for link in iter_links(data):
        render_step(link, hostmap, markdown, source="link")
    
    for step in iter_steps(data):
        render_step(step, hostmap, markdown, source="step")
    
    generate_graph(data, hostmap, png_path)
    markdown.new_paragraph(f"![Operation Graph]({png_path.name})")
    
    markdown.create_md_file()
    print(f"Generated: {operation_name}_caldera_report.md and {operation_name}_graph.png")

if __name__ == "__main__":
    main()
