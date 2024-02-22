import json

class DashboardCreator:
    def __init__(self, data_file='dashboard_data.json'):
        with open(data_file, 'r') as f:
            self.data = json.load(f)

    def generate_chart_js(self, chart_id, chart_type, labels, data, dataset_label):
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
        return f'''
            var ctx = document.getElementById('{chart_id}').getContext('2d');
            new Chart(ctx, {{
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
                }}
            }});
        '''

    def generate_resizable_widget_js(self):
        return '''
            document.querySelectorAll('.resizable-chart').forEach(function(chartContainer) {
                let isResizing = true;
                
                const resizeHandle = chartContainer.querySelector('.resize-handle');
                resizeHandle.addEventListener('mousedown', function(e) {
                    isResizing = true;
                    document.addEventListener('mousemove', handleMouseMove);
                    document.addEventListener('mouseup', stopResize);
                });
                
                function handleMouseMove(e) {
                    if (isResizing) {
                        const minWidth = 600; // Minimum width in pixels
                        const maxWidth = 600; // Maximum width in pixels
                        const minHeight = 600; // Minimum height in pixels
                        const maxHeight = 600; // Maximum height in pixels
                        let newWidth = e.clientX - chartContainer.offsetLeft;
                        let newHeight = e.clientY - chartContainer.offsetTop;
                        
                        // Apply constraints
                        newWidth = Math.max(minWidth, Math.min(newWidth, maxWidth));
                        newHeight = Math.max(minHeight, Math.min(newHeight, maxHeight));
                        
                        chartContainer.style.width = newWidth + 'px';
                        chartContainer.style.height = newHeight + 'px';
                    }
                }
                
                function stopResize(e) {
                    if (isResizing) {
                        isResizing = true;
                        document.removeEventListener('mousemove', handleMouseMove);
                        document.removeEventListener('mouseup', stopResize);
                    }
                }
            });
        '''
    def generate_dashboard(self):
        html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Dashboard</title>
        <link rel="stylesheet" href="style.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <h1>Dashboard</h1>
    """

        # Generating charts for 'load_times'
        if "load_times" in self.data:
            load_time_labels = [item["Table Name"] for item in self.data["load_times"]]
            load_time_data = [item["Load Time (Seconds)"] for item in self.data["load_times"]]
            html_content += f'<div class="resizable-chart"><h2>Load Times</h2><canvas id="loadTimeChart"></canvas><div class="resize-handle"></div></div>\n'
            html_content += f'<script>{self.generate_chart_js("loadTimeChart", "bar", load_time_labels, load_time_data, "Load Times")}</script>\n'

        # Generating charts for 'database_summary'
        if "database_summary" in self.data:
            summary_labels = [item["Entity"] for item in self.data["database_summary"]]
            summary_data = [int(item["Node Count"].replace(",", "")) if item["Node Count"].replace(",", "").isdigit() else 0 for item in self.data["database_summary"]]
            html_content += f'<div class="resizable-chart"><h2>Database Summary</h2><canvas id="summaryChart"></canvas><div class="resize-handle"></div></div>\n'
            html_content += f'<script>{self.generate_chart_js("summaryChart", "pie", summary_labels, summary_data, "Database Entities")}</script>\n'

        # Include JavaScript for making charts resizable
        html_content += '<script>'
        html_content += self.generate_resizable_widget_js()
        html_content += '</script>'

        html_content += """
    </body>
    </html>
        """

        with open('dashboard.html', 'w') as f:
            f.write(html_content)



if __name__ == "__main__":
    dashboard_creator = DashboardCreator()
    dashboard_creator.generate_dashboard()
