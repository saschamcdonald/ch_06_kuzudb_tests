import json

class DashboardCreator:
    def __init__(self, data_file='dashboard_data.json'):
        with open(data_file, 'r') as f:
            self.data = json.load(f)

    def generate_dashboard(self):
        # Prepare data for the load times chart
        labels_load_times = [item['Table Name'] for item in self.data["load_times"]]
        data_load_times = [item['Load Time (Seconds)'] for item in self.data["load_times"]]

        # Prepare data for the database summary chart
        labels_summary = [item['Entity'] for item in self.data["database_summary"]]
        data_summary = [item['Node Count'] for item in self.data["database_summary"]]

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dashboard</title>
    <link rel="stylesheet" href="style.css">  <!-- Ensure you have a CSS file for styling -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Dashboard</h1>
    <div>
        <h2>Load Times</h2>
        <canvas id="loadTimeChart"></canvas>
    </div>
    <div>
        <h2>Database Summary</h2>
        <canvas id="summaryChart"></canvas>
    </div>
    <script>
        var loadTimeCtx = document.getElementById('loadTimeChart').getContext('2d');
        new Chart(loadTimeCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(labels_load_times)},
                datasets: [{{
                    label: 'Load Times (Seconds)',
                    data: {json.dumps(data_load_times)},
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                scales: {{
                    yAxes: [{{
                        ticks: {{
                            beginAtZero: true
                        }}
                    }}]
                }}
            }}
        }});

        var summaryCtx = document.getElementById('summaryChart').getContext('2d');
        new Chart(summaryCtx, {{
            type: 'pie',
            data: {{
                labels: {json.dumps(labels_summary)},
                datasets: [{{
                    label: 'Node Counts',
                    data: {json.dumps(data_summary)},
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 159, 64, 0.2)'
                    ],
                    borderColor: [
                        'rgba(255,99,132,1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'top',
                    }},
                    title: {{
                        display: true,
                        text: 'Database Entity Counts'
                    }}
                }}
            }},
        }});
    </script>
</body>
</html>
        """
        with open('dashboard.html', 'w') as f:
            f.write(html_content)

if __name__ == "__main__":
    dashboard_creator = DashboardCreator()
    dashboard_creator.generate_dashboard()
