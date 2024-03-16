import json
import datetime
import os
import shutil
import hashlib
import glob

from importlib.metadata import version  # Check Python version compatibility

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
def get_json_files(directory='.'):
    return [f for f in glob.glob(os.path.join(directory, '*.json'))]


class DashboardCreator:
    def __init__(self, data_directory='.'):
        self.data_directory = data_directory
        self.aggregated_data = self.aggregate_data()
        self.person_data = self.prepare_comparison_data('Person')
        self.company_data = self.prepare_comparison_data('Company')
        self.works_at_data = self.prepare_comparison_data('WorksAt')



    def aggregate_data(self):
        aggregated_data = {}
        json_files = glob.glob(os.path.join(self.data_directory, '*.json'))
        for json_file in json_files:
            with open(json_file, 'r') as f:
                data = json.load(f)
            kuzu_version = data.get('kuzu')
            if kuzu_version not in aggregated_data:
                aggregated_data[kuzu_version] = {'load_times': [], 'database_summary': []}
            aggregated_data[kuzu_version]['load_times'].extend(data.get('load_times', []))
            aggregated_data[kuzu_version]['database_summary'].extend(data.get('database_summary', []))
        return aggregated_data

    def prepare_comparison_data(self, table_name='Person'):
        labels = sorted(self.aggregated_data.keys())  # Kuzu versions
        data = []
        for version in labels:
            # Find the load time for the specified table in each version, or use 0 if not found
            load_time = next((lt["Load Time (Seconds)"] for lt in self.aggregated_data[version]["load_times"] if lt["Table Name"] == table_name), 0)
            data.append(load_time)
        return labels, data

    def generate_color(self, filename):
        hash_value = hashlib.md5(filename.encode()).hexdigest()
        r = int(hash_value[:2], 16)
        g = int(hash_value[2:4], 16)
        b = int(hash_value[4:6], 16)
        return f'rgba({r}, {g}, {b}, 0.3)'

    def generate_dashboard(self):
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

        for version in self.aggregated_data:
            data = self.aggregated_data[version]
            dashboard_filename = f'{version.replace(".", "_")}_dashboard.html'

            execution_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            summary_dict = {}
            load_time_data = []

            sidebar_links_html = """
    <div class="sidebar">
        <a href="#" onclick="openTab(event, 'summary')">Summary</a>
        <a href="comparison.html">Compare Results</a>
        <a href="#" onclick="openTab(event, 'database_summary')">Database Summary</a>
        <a href="#" onclick="openTab(event, 'load_times')">Load Times</a>
        <a href="#" onclick="openTab(event, 'config')">Config</a>
        <div class="other-dashboards">
            <p>Other Dashboards</p>
    """
            for version in self.aggregated_data:
                friendly_name = version.replace(".", " ").capitalize()
                sidebar_links_html += f'        <a href="{version.replace(".", "_")}_dashboard.html">{friendly_name}</a>\n'

            sidebar_links_html += "    </div>\n</div>"

            html_content = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{version.replace(".", "_").replace("_", " ").capitalize()} Dashboard</title>
        <link rel="stylesheet" href="style.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            /* Define sidebar styles */
            .sidebar {{
                height: 100%;
                width: 250px;
                position: fixed;
                z-index: 1;
                top: 0;
                left: 0;
                background-color: #111;
                overflow-x: hidden;
                padding-top: 20px;
            }}
            
            /* Define sidebar links styles */
            .sidebar a {{
                padding: 10px 8px;
                text-decoration: none;
                font-size: 20px;
                color: #818181;
                display: block;
                transition: background-color 0.3s;
            }}
            
            /* Define sidebar links on hover styles */
            .sidebar a:hover {{
                background-color: #333;
                color: #f1f1f1;
            }}

            /* Define active tab styles */
            .sidebar a.active, .sidebar a.active:hover {{
                background-color: {self.generate_color(version)};
                color: white;
            }}

            /* Define tab styles */
            .tab {{
                margin-left: 250px; /* Same width as the sidebar */
            }}

            /* Define tab content styles */
            .tabcontent {{
                display: none;
                padding: 6px 12px;
                border: 1px solid #ccc;
                border-top: none;
            }}
            
            /* Define table styles */
            table {{
                border-collapse: collapse;
                width: 100%;
                border: 1px solid #ddd;
                font-family: Arial, sans-serif;
            }}
            
            th, td {{
                padding: 8px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            
            tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            
            th {{
                color: #111; /* Text color for title columns */
            }}
        </style>
    </head>
    <body>

    <!-- Sidebar -->
    { sidebar_links_html }

    <!-- Main content -->
    <div class="tab">
    """

            # Summary Tab Content
            html_content += f"""
        <div id="summary" class="tabcontent">
            <h2>Summary Kuzu - {version}</h2>
            <table style="background-color: {self.generate_color(version)};">
                <tr><th>Kuzu Version</th><td>{version}</td></tr>
                <tr><th>Date of Execution</th><td>{execution_date}</td></tr>
            </table>
            <h3>Database Summary</h3>
            <table style="background-color: #f8f8f8;">
                <tr><th>Entity</th><th>Table Count</th></tr>
    """

            if "database_summary" in data:
                for item in data["database_summary"]:
                    entity = item["Entity"]
                    node_count = int(item["Table Count"].replace(",", ""))
                    summary_dict[entity] = node_count
                    html_content += f'<tr><td>{entity}</td><td>{node_count:,}</td></tr>'

            html_content += f"""
            </table>
            <h3>Load Times: Kuzu - {version}</h3>
            <table style="background-color: #f8f8f8;">
                <tr><th>Table Name</th><th>Load Time (Seconds)</th></tr>
    """

            if "load_times" in data:
                load_time_data = data["load_times"]
                for item in load_time_data:
                    html_content += f'<tr><td>{item["Table Name"]}</td><td>{item["Load Time (Seconds)"]}</td></tr>'

            html_content += """
            </table>
        </div>
    """

            # Database Summary Tab Content
            summary_labels = list(summary_dict.keys())
            summary_data = list(summary_dict.values())
            html_content += f"""
        <div id="database_summary" class="tabcontent">
            <h2>Database Summary: Kuzu - {version}</h2>
            <div class="chart-container"><canvas id="summaryChart_{version.replace(".", "_")}"></canvas></div><br>
            <table style="background-color: #f8f8f8;">
                <tr><th>Entity</th><th>Table Count</th></tr>
            """
            for entity, count in summary_dict.items():
                html_content += f'<tr><td>{entity}</td><td>{count:,}</td></tr>'
            html_content += '</table></div>'

            # Generate pie chart for database summary
            chart_id = f"summaryChart_{version.replace('.', '_')}"
            chart_type = "pie"
            chart_dataset_label = "Database Summary"
            chart_html = generate_chart_js(chart_id, chart_type, summary_labels, summary_data, chart_dataset_label)
            html_content += chart_html

            # Load Times Tab Content
            html_content += f"""
        <div id="load_times" class="tabcontent">
            <h2>Load Times: Kuzu Version - {version}</h2>
            <div class="chart-container"><canvas id="loadTimeChart_{version.replace(".", "_")}"></canvas></div><br>
            <table style="background-color: #f8f8f8;">
                <tr><th>Table Name</th><th>Load Time (Seconds)</th></tr>
            """
            for item in load_time_data:
                html_content += f'<tr><td>{item["Table Name"]}</td><td>{item["Load Time (Seconds)"]}</td></tr>'
            html_content += '</table></div>'

            # Config Tab Content
            html_content += f"""
        <div id="config" class="tabcontent">
            <h2>Config: Kuzu  - {version}</h2>
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

            index_content += f'        <li><a href="{dashboard_filename}">{dashboard_filename.replace("_", " ").capitalize()}</a></li>\n'

            # Generate load time chart for the current dashboard
            load_times_labels = [item["Table Name"] for item in load_time_data]
            load_times_values = [float(item["Load Time (Seconds)"]) for item in load_time_data]
            load_time_chart_html = generate_chart_js(f"loadTimeChart_{version.replace('.', '_')}", "bar", load_times_labels, load_times_values, "Load Times")

            # Write load time chart HTML to the current dashboard
            with open(dashboard_filename, 'a') as f:
                f.write(load_time_chart_html)

        # Create comparison dashboard
        person_labels, person_data = self.person_data
        person_chart_html = generate_chart_js("loadTimeComparisonChart", "bar", person_labels, person_data, "Load Times for Person")
        company_labels, company_data = self.company_data
        company_chart_html = generate_chart_js("loadTimeComparisonChart", "bar", company_labels, company_data, "Load Times for Company")
        works_at_labels, works_at_data = self.works_at_data
        works_at_chart_html = generate_chart_js("loadTimeComparisonChart", "bar", works_at_labels, works_at_data, "Load Times for WorksAt")
        
        comparison_html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Comparison Dashboard</title>
        <link rel="stylesheet" href="style.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            /* Define sidebar styles */
            .sidebar {{
                height: 100%;
                width: 250px;
                position: fixed;
                z-index: 1;
                top: 0;
                left: 0;
                background-color: #111;
                overflow-x: hidden;
                padding-top: 20px;
            }}
            
            /* Define sidebar links styles */
            .sidebar a {{
                padding: 10px 8px;
                text-decoration: none;
                font-size: 20px;
                color: #818181;
                display: block;
                transition: background-color 0.3s;
            }}
            
            /* Define sidebar links on hover styles */
            .sidebar a:hover {{
                background-color: #333;
                color: #f1f1f1;
            }}

            /* Define active tab styles */
            .sidebar a.active, .sidebar a.active:hover {{
                background-color: #333;
                color: #f1f1f1;
            }}

            /* Define tab styles */
            .tab {{
                margin-left: 250px; /* Same width as the sidebar */
            }}

            /* Define tab content styles */
            .tabcontent {{
                display: none;
                padding: 6px 12px;
                border: 1px solid #ccc;
                border-top: none;
            }}
            
            /* Define table styles */
            table {{
                border-collapse: collapse;
                width: 100%;
                border: 1px solid #ddd;
                font-family: Arial, sans-serif;
            }}
            
            th, td {{
                padding: 8px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            
            tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            
            th {{
                color: #111; /* Text color for title columns */
            }}
        </style>
    </head>
    <body>

    <!-- Sidebar -->
    { sidebar_links_html }

    <!-- Main content -->
    <div class="tab">
    """

        # Append comparison chart HTML to the comparison dashboard content
        comparison_html_content += """
        <div id="summary" class="tabcontent">
            <h2>Load Time Comparison</h2>
            <div class="chart-container"><canvas id="loadTimeComparisonChart"></canvas></div>
        </div>
        """

        # Append Person chart HTML
        comparison_html_content += person_chart_html

        # Append Company chart HTML
        comparison_html_content += company_chart_html

        # Append WorksAt chart HTML
        comparison_html_content += works_at_chart_html

        comparison_html_content += """
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
        </script>

        </body>
        </html>
        """

        with open('comparison.html', 'w') as f:
            f.write(comparison_html_content)

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
    data_directory = '.'  # Change this to the directory where your JSON files are located
    dashboard_creator = DashboardCreator(data_directory)
    dashboard_creator.generate_dashboard()
