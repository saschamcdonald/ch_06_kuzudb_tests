import json

class DashboardCreator:
    def __init__(self, data_file='dashboard_data.json'):
        with open(data_file, 'r') as f:
            self.data = json.load(f)

    def generate_dashboard(self):
        # Simplified example to include a Chart.js visualization
        # Extend this method to include more complex logic as needed
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Dashboard</h1>
    <canvas id="loadTimeChart" width="400" height="400"></canvas>
    <script>
        var ctx = document.getElementById('loadTimeChart').getContext('2d');
        var chart = new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps([lt[0] for lt in self.data["load_times"]])},
                datasets: [{{
                    label: 'Load Times',
                    data: {json.dumps([lt[1] for lt in self.data["load_times"]])},
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
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
    </script>
</body>
</html>
        """
        with open('dashboard.html', 'w') as f:
            f.write(html_content)

if __name__ == "__main__":
    dashboard_creator = DashboardCreator()
    dashboard_creator.generate_dashboard()
