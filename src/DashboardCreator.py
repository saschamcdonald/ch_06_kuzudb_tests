import json

import json

class Widget:
    def generate_html(self):
        raise NotImplementedError("Subclasses should implement this method.")
    
    def generate_js(self):
        raise NotImplementedError("Subclasses should implement this method.")


class ChartWidget(Widget):
    def __init__(self, chart_id, chart_type, labels, data, dataset_label):
        self.chart_id = chart_id
        self.chart_type = chart_type
        self.labels = labels
        self.data = data
        self.dataset_label = dataset_label

    def generate_html(self):
        return f'<div class="resizable-chart"><canvas id="{self.chart_id}"></canvas><div class="resize-handle"></div></div>\n'

    def generate_js(self):
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
            new Chart(document.getElementById('{self.chart_id}').getContext('2d'), {{
                type: '{self.chart_type}',
                data: {{
                    labels: {json.dumps(self.labels)},
                    datasets: [{{
                        label: '{self.dataset_label}',
                        data: {json.dumps(self.data)},
                        backgroundColor: {json.dumps(backgroundColors)},
                        borderColor: {json.dumps(borderColors)},
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                }}
            }});
        '''

class Tab:
    def __init__(self, name):
        self.name = name
        self.widgets = []

    def add_widget(self, widget):
        self.widgets.append(widget)


class DashboardCreator:
    def __init__(self, data_file='dashboard_data.json'):
        with open(data_file, 'r') as f:
            self.data = json.load(f)
        self.tabs = []

    def add_tab(self, tab):
        self.tabs.append(tab)

class DashboardCreator:
    def __init__(self, data_file='dashboard_data.json'):
        with open(data_file, 'r') as f:
            self.data = json.load(f)
        self.tabs = []

    def add_tab(self, tab):
        self.tabs.append(tab)

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
                        const minWidth = 1200; // Minimum width in pixels
                        const maxWidth = 1200; // Maximum width in pixels
                        const minHeight = 1200; // Minimum height in pixels
                        const maxHeight = 1200; // Maximum height in pixels
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
        <div class="tab-container">
    """

        # Dynamically create tabs based on available data categories
        if "load_times" in self.data:
            load_times_tab = Tab("Load Times")
            load_time_labels = [item["Table Name"] for item in self.data["load_times"]]
            load_time_data = [item["Load Time (Seconds)"] for item in self.data["load_times"]]
            load_times_chart = ChartWidget("loadTimeChart", "bar", load_time_labels, load_time_data, "Load Times")
            load_times_tab.add_widget(load_times_chart)
            self.add_tab(load_times_tab)

        if "database_summary" in self.data:
            database_summary_tab = Tab("Database Summary")
            summary_labels = [item["Entity"] for item in self.data["database_summary"]]
            summary_data = [int(item["Node Count"].replace(",", "")) if item["Node Count"].replace(",", "").isdigit() else 0 for item in self.data["database_summary"]]
            database_summary_chart = ChartWidget("summaryChart", "pie", summary_labels, summary_data, "Database Entities")
            database_summary_tab.add_widget(database_summary_chart)
            self.add_tab(database_summary_tab)

        # Generate HTML for tabs and their widgets
        for tab in self.tabs:
            html_content += f'<div class="tab" id="{tab.name.replace(" ", "")}Tab">\n'
            html_content += f'<h2>{tab.name}</h2>\n'
            for widget in tab.widgets:
                html_content += widget.generate_html()
            html_content += '</div>\n'

        # Closing div for tab-container
        html_content += '</div>'

        # Generate JS for widgets
        html_content += '<script>'
        for tab in self.tabs:
            for widget in tab.widgets:
                html_content += widget.generate_js()
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
    load_time_tab = Tab("Load Times")
    # Assuming you've extracted `load_time_labels` and `load_time_data` from your data
    load_time_widget = ChartWidget("loadTimeChart", "bar", load_time_labels, load_time_data, "Load Times")
    load_time_tab.add_widget(load_time_widget)

    dashboard_creator.add_tab(load_time_tab)
    dashboard_creator.generate_dashboard()