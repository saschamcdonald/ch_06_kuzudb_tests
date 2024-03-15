import os
import re

def find_dashboard_files(directory_path='.'):
    """
    Scan the directory for dashboard HTML files matching the pattern 'dashboard_{string}.html'.
    """
    pattern = re.compile(r'^dashboard_.*\.html$')
    return [filename for filename in os.listdir(directory_path) if pattern.match(filename)]

def generate_index_html(dashboard_files, output_file='index.html', title='Dashboard Index'):
    """
    Generate an index.html file that links to each dashboard HTML file.
    """
    links_html = '\n'.join([f'    <li><a href="{filename}">{filename.replace("dashboard_", "").replace(".html", "").capitalize()}</a></li>' for filename in dashboard_files])
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        ul {{ list-style-type: none; padding: 0; }}
        li {{ margin: 5px 0; }}
        a {{ color: #007bff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h2>Dashboard Links</h2>
    <ul>
{links_html}
    </ul>
</body>
</html>"""

    with open(output_file, 'w') as file:
        file.write(html_content)

if __name__ == "__main__":
    directory_path = '.'  # Directory where your dashboard HTML files are stored
    dashboard_files = find_dashboard_files(directory_path)
    generate_index_html(dashboard_files)
