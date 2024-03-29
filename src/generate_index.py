import json
import datetime
import os
import shutil
import hashlib
from comparisons import ComparisonWidget



# Function to generate chart.js script
def generate_chart_js(chart_id, chart_type, labels, data, dataset_label):
    backgroundColors = [
        'rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)',
        'rgba(255, 206, 86, 0.2)', 'rgba(75, 192, 192, 0.2)',
        'rgba(153, 102, 255, 0.2)', 'rgba(255, 159, 64, 0.2)'
    ]
    borderColors = [
        'rgba(255,99,132,1)', 'rgba(54, 162, 235, 1)',
        'rgba(255, 206, 86, 1)', 'rgba(75, 192, 192, 1)',
        'rgba(153, 102, 255, 1)', 'rgba(255, 159, 64, 1)'
    ]

    chart_js = f"""
    <script>
        var ctx = document.getElementById('{chart_id}').getContext('2d');
        var myChart = new Chart(ctx, {{
            type: '{chart_type}',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{{
                    label: '{dataset_label}',
                    data: {json.dumps(data)},
                    backgroundColor: {json.dumps(backgroundColors)},
                    borderColor: {json.dumps(borderColors)},
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                var label = context.label || '';
                                if (label) {{
                                    label += ': ';
                                }}
                                label += context.raw.toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",");
                                return label;
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
    """
    return chart_js


# Function to find all the JSON files in the directory
def get_json_files():
    return [f for f in os.listdir('.') if f.endswith('.json')]


class DashboardCreator:
    def __init__(self, data_files):
        self.data_files = data_files

    def generate_color(self, filename):
        hash_value = hashlib.md5(filename.encode()).hexdigest()
        r = int(hash_value[:2], 16)
        g = int(hash_value[2:4], 16)
        b = int(hash_value[4:6], 16)
        return f'rgba({r}, {g}, {b}, 0.3)'

    def generate_dashboard(self):
        data_directory='.'
        comparison_widget = ComparisonWidget(data_directory)
        widget_html = comparison_widget.generate_widget()
        index_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dashboard Index</title>
</head>
<body>
    <h1>Dashboard Index</h1>
    <ul>
"""

        last_dashboard_file = None

        for data_file in self.data_files:
            with open(data_file, 'r') as f:
                self.data = json.load(f)

            dashboard_filename = f'{data_file.replace(".json", ".html")}'

            execution_date = self.data.get("execution_date", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            summary_dict = {}
            load_time_data = []

            sidebar_links_html = """
<div class="sidebar">
<a href="#" onclick="openTab(event, 'config')">Config</a>
    <div class="other-dashboards">
        <p>Other Dashboards</p>
"""
            for file in self.data_files:
                friendly_name = file.replace(".json", "").replace("_", " ").capitalize()
                sidebar_links_html += f'        <a href="{file.replace(".json", ".html")}">{friendly_name}</a>\n'
                sidebar_links_html += """ <ul>
                   <li> <a href="#" onclick="openTab(event, 'database_summary')">Database Summary</a> </li>
                    <li> <a href="#" onclick="openTab(event, 'load_times')">Load Times</a> </li>
                    </ul>"""

            sidebar_links_html += "    </div>\n</div>"

            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{dashboard_filename.replace(".html", "").replace("_", " ").capitalize()}</title>
    <link rel="stylesheet" href="style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>

<!-- Sidebar -->
{ sidebar_links_html }

<!-- Main content -->
<div class="tab">
"""

            kuzu_version = self.data["kuzu"]
            # Summary Tab Content
            html_content += f"""
    <div id="summary" class="tabcontent">
        <h2>Summary Kuzu - {kuzu_version}</h2>
        <table style="background-color: {self.generate_color(dashboard_filename)};">
            <tr><th>Kuzu Version</th><td>{kuzu_version}</td></tr>
            <tr><th>Date of Execution</th><td>{execution_date}</td></tr>
        </table>
        <h3>Database Summary</h3>
        <table style="background-color: #f8f8f8;">
            <tr><th>Entity</th><th>Table Count</th></tr>
"""

            if "database_summary" in self.data:
                for item in self.data["database_summary"]:
                    entity = item["Entity"]
                    node_count = int(item["Table Count"].replace(",", ""))
                    summary_dict[entity] = node_count
                    html_content += f'<tr><td>{entity}</td><td>{node_count:,}</td></tr>'

            html_content += f"""
        </table>
        <h3>Load Times: Kuzu - {kuzu_version}</h3>
        <table style="background-color: #f8f8f8;">
            <tr><th>Table Name</th><th>Load Time (Seconds)</th></tr>
"""

            if "load_times" in self.data:
                load_time_data = self.data["load_times"]
                for item in load_time_data:
                    html_content += f'<tr><td>{item["Table Name"]}</td><td>{item["Load Time (Seconds)"]}</td></tr>'

            html_content += f"""
        </table>
        <h2> Kuzu versons - Table Load Times</h2>
        <p> {widget_html}</p>
    </div>

"""

            if "database_summary" in self.data:
                for item in self.data["database_summary"]:
                    entity = item["Entity"]
                    node_count = int(item["Table Count"].replace(",", ""))
                    summary_dict[entity] = node_count

                summary_labels = list(summary_dict.keys())
                summary_data = list(summary_dict.values())

                # Database Summary Tab Content
                html_content += f"""
    <div id="database_summary" class="tabcontent">
        <h2>Database Summary: Kuzu - {kuzu_version}</h2>
        <div class="chart-container"><canvas id="summaryChart"></canvas></div><br>
        <table style="background-color: #f8f8f8;">
            <tr><th>Entity</th><th>Table Count</th></tr>
        """
                for entity, count in summary_dict.items():
                    html_content += f'<tr><td>{entity}</td><td>{count:,}</td></tr>'
                html_content += '</table></div>'

                html_content += generate_chart_js("summaryChart", "pie", summary_labels, summary_data, "Database Summary")

            if "load_times" in self.data:
                load_time_data = self.data["load_times"]

                load_time_labels = [item["Table Name"] for item in load_time_data]
                load_time_values = [round(float(item["Load Time (Seconds)"]), 2) for item in load_time_data]

                # Load Times Tab Content
                html_content += f"""
    <div id="load_times" class="tabcontent">
        <h2>Load Times: Kuzu Version - {kuzu_version}</h2>
        <div class="chart-container"><canvas id="loadTimeChart"></canvas></div><br>
        <table style="background-color: #f8f8f8;">
            <tr><th>Table Name</th><th>Load Time (Seconds)</th></tr>
        """
                for item in load_time_data:
                    html_content += f'<tr><td>{item["Table Name"]}</td><td>{item["Load Time (Seconds)"]}</td></tr>'
                html_content += '</table></div>'

                html_content += generate_chart_js("loadTimeChart", "bar", load_time_labels, load_time_values, "Load Times")

            # Config Tab Content
            html_content += f"""
    <div id="config" class="tabcontent">
        <h2>Config: Kuzu  - {kuzu_version}</h2>
        <form id="configForm">
            <label for="open_tabs">Open Dashboards:</label><br>
            <input type="radio" id="same_tab" name="open_tabs" value="same_tab" checked>
            <label for="same_tab">Same Tab</label><br>
            <input type="radio" id="separate_tabs" name="open_tabs" value="separate_tabs">
            <label for="separate_tabs">Separate Tabs</label><br><br>
        </form>
    </div>
"""

            html_content += """
</div>

<script>
    // Open the default tab when the page loads
    document.getElementById("summary").style.display = "block";

    // Function to switch between tabs
    function openTab(evt, tabName) {
        var i, tabcontent, tablinks;
        tabcontent = document.getElementsByClassName("tabcontent");
        for (i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
        }
        tablinks = document.getElementsByClassName("sidebar")[0].getElementsByTagName("a");
        for (i = 0; i < tablinks.length; i++) {
            tablinks[i].classList.remove("active");
        }
        document.getElementById(tabName).style.display = "block";
        evt.currentTarget.classList.add("active");
    }

    // Function to handle configuration changes
    document.getElementById("configForm").addEventListener("change", function() {
        var tabsOption = document.querySelector('input[name="open_tabs"]:checked').value;
        var sidebarLinks = document.getElementsByClassName("sidebar")[0].getElementsByTagName("a");
        for (var i = 0; i < sidebarLinks.length; i++) {
            var link = sidebarLinks[i];
            if (tabsOption === "same_tab") {
                link.removeAttribute("target");
            } else {
                link.setAttribute("target", "_blank");
            }
        }
    });
</script>

</body>
</html>
        """

            with open(dashboard_filename, 'w') as f:
                f.write(html_content)

            last_dashboard_file = dashboard_filename

            index_content += f'        <li><a href="{dashboard_filename}">{dashboard_filename.replace(".html", "").replace("_", " ").capitalize()}</a></li>\n'

        index_content += """
    </ul>
</body>
</html>
"""
        with open('index.html', 'w') as f:
            f.write(index_content)

        if last_dashboard_file:
            shutil.copyfile(last_dashboard_file, 'index.html')


if __name__ == "__main__":
    
    data_files = get_json_files()
    dashboard_creator = DashboardCreator(data_files)
    dashboard_creator.generate_dashboard()
