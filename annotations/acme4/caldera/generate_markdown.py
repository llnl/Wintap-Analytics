import sys
from pathlib import Path
from mdutils.mdutils import MdUtils

from caldera_report_common import (
    decode_if_base64,
    iter_hosts,
    load_report,
    sanitize_operation_name,
)


# Modified from: https://github.com/marksowell/caldera-report-generator

# Generate a simple markdown file for each report.

def hosts(data, markdown):
    # Iterate through host groups
    # Things get from here:
    # the C2 IP Node
    # the C2 5-tuples, with date range(?)
    # the beachhead PID/parent PID
    # Map of "paw" to hostname. paw is a Caldera unique host id and is used in other parts of the report.
    hostmap = {}
    hosts = ["Host","User","Beachhead Command","PID","Parent PID","IP","C2 Server"]
    num_hosts = 0
    markdown.new_header(level=1, title="Hosts Attacked")
    for host in iter_hosts(data):
        # There *should* only be 1 c2 server, so save values in a map and dump out after iterating over hosts.
        # Build a table of host info
        hosts.extend([
            host.get('host', 'N/A'),
            host.get('username', 'N/A'),
            host.get('exe_name', 'N/A'),
            host.get('pid', 'N/A'),
            host.get('ppid', 'N/A'),
            ', '.join(host.get('host_ip_addrs', [])) if host.get('host_ip_addrs') else 'N/A',
            host.get('server', 'N/A'),
        ])
        if host.get('paw'):
            hostmap[host.get('paw')] = host.get('host')
        num_hosts += 1
    # Output the table now so its at the top.
    markdown.new_table(columns=7, rows=num_hosts+1, text=hosts)

    # Now iterate thru the links for each host.
    # Links executed
    markdown.new_header(level=1, title="Links")
    markdown.new_line("(what exactly is a link? seems to be a command executed when initializing the beachhead?)")
    for host in iter_hosts(data):
        links(host, hostmap, markdown)

    return hostmap

def links(host, hostmap, markdown):
    markdown.new_header(level=2, title=f"Host: {host.get('host', 'N/A')}")
    for link in host.get('links', []):
        cmd = decode_if_base64(link.get('plaintext_command'))
        markdown.new_paragraph(f"  Technique: {link['ability']['technique_name']}")
        markdown.new_paragraph(f"  PID: {link['pid']}")
        markdown.new_paragraph(f"  Status: {'Success' if link['status'] == 0 else 'Failed'}")
        markdown.new_paragraph(f"  Start: {link['collect']}")
        markdown.new_paragraph(f"  Finish: {link['finish']}")
        markdown.new_paragraph(f"  Command: \n```powershell\n{cmd}\n```")
        markdown.new_paragraph("")

def steps(data, hostmap, markdown):
    markdown.new_header(level=1, title="Steps")
    for host_key, host_steps in data.get("steps", {}).items():
        markdown.new_header(level=2, title=f"Host: {hostmap[host_key]} (paw: {host_key})")
        for step in host_steps.get("steps", []):
            cmd = decode_if_base64(step.get('plaintext_command'))
            markdown.new_header(level=3, title=f"  Description: {step.get('description')}")
            markdown.new_paragraph(f"  Attack: {step.get('attack')}")
            markdown.new_paragraph(f"  Status: {'Success' if step.get('status') == 0 else 'Failed'}")
            markdown.new_paragraph(f"  PID: {step.get('pid')}")
            markdown.new_paragraph(f"  Start: {step.get('run')}")
            markdown.new_paragraph(f"  Command: \n```powershell\n{cmd}\n```")
            markdown.new_paragraph("")

def main():
    # Check if a file path is provided as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python generate_markdown.py <path_to_json_file>")
        sys.exit(1)

    json_file_path = sys.argv[1]

    try:
        data = load_report(json_file_path)
    except Exception as e:
        print(f"Failed to load JSON file: {e}")
        sys.exit(1)

    # Get the operation name, sanitize it, and convert to lowercase
    operation_name = sanitize_operation_name(data.get('name'))

    # Write reports next to this script so callers can run from any cwd.
    out_dir = Path(__file__).resolve().parent / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    markdown = MdUtils(
        file_name=str(out_dir / f"{operation_name}_caldera_report.md"),
        title=data.get("name", "Unnamed Operation"),
    )
    hostmap = hosts(data, markdown)
    steps(data, hostmap, markdown)
    markdown.new_table_of_contents(table_title='Contents', depth=3)
    markdown.create_md_file()


if __name__ == "__main__":
    main()

