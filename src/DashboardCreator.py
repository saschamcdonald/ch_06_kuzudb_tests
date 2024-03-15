import json
import subprocess
import datetime


class DashboardCreator:
    def __init__(self, data_file='dashboard_data.json'):
        with open(data_file, 'r') as f:
            self.data = json.load(f)

    def generate_chart_js(self, chart_id, chart_type, labels, data, dataset_label, summaries=None):
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

    def get_kuzu_version(self):
        try:
            # Run the "pip show" command and capture its output
            result = subprocess.run(['pip', 'show', 'kuzu'], capture_output=True, text=True)
            if result.returncode == 0:
                # Process the output to find the version line
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        return line.split(' ')[1]
                return 'Version not found'
            else:
                return 'Error executing pip command'
        except Exception as e:
            return f'Error: {e}'

    def generate_dashboard(self):
        kuzu_version = self.get_kuzu_version()
        execution_date = self.data.get("execution_date", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        summary_dict = {}
        load_time_data = []

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dashboard</title>
    <link rel="stylesheet" href="style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
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
            background-color: #4CAF50;
            color: white;
        }}
    </style>
</head>
<body>
    <h1>Dashboard</h1>
    <table>
        <tr><th>Kuzu Database Version</th><td>{kuzu_version}</td></tr>
        <tr><th>Date of Execution</th><td>{execution_date}</td></tr>
    </table><br>
"""

        if "database_summary" in self.data:
            for item in self.data["database_summary"]:
                entity = item["Entity"]
                node_count = int(item["Table Count"].replace(",", ""))
                summary_dict[entity] = node_count

            summary_labels = list(summary_dict.keys())
            summary_data = list(summary_dict.values())

            html_content += f'<div class="chart-container"><canvas id="summaryChart"></canvas></div><br>'
            html_content += self.generate_chart_js("summaryChart", "pie", summary_labels, summary_data, "Database Summary")

            html_content += """
            <h2>Database Summary</h2>
            <table>
                <tr><th>Entity</th><th>Table Count</th></tr>
            """
            for entity, count in summary_dict.items():
                html_content += f'<tr><td>{entity}</td><td>{count:,}</td></tr>'
            html_content += '</table><br>'

        if "load_times" in self.data:
            load_time_data = self.data["load_times"]

            load_time_labels = [item["Table Name"] for item in load_time_data]
            load_time_values = [round(float(item["Load Time (Seconds)"]), 2) for item in load_time_data]

            html_content += f'<div class="chart-container"><canvas id="loadTimeChart"></canvas></div><br>'
            html_content += self.generate_chart_js("loadTimeChart", "bar", load_time_labels, load_time_values, "Load Times")

            html_content += """
            <h2>Load Times</h2>
            <table>
                <tr><th>Table Name</th><th>Load Time (Seconds)</th></tr>
            """
            for item in load_time_data:
                html_content += f'<tr><td>{item["Table Name"]}</td><td>{item["Load Time (Seconds)"]}</td></tr>'
            html_content += '</table><br>'

        html_content += """
</body>
</html>
        """

        with open('dashboard.html', 'w') as f:
            f.write(html_content)


if __name__ == "__main__":
    dashboard_creator = DashboardCreator()
    dashboard_creator.generate_dashboard()
