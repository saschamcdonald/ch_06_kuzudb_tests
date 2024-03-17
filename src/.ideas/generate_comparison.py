import json
import datetime
import os
import shutil
import hashlib
import glob

def generate_color(filename):
    hash_value = hashlib.md5(filename.encode()).hexdigest()
    r = int(hash_value[:2], 16)
    g = int(hash_value[2:4], 16)
    b = int(hash_value[4:6], 16)
    return f'rgba({r}, {g}, {b}, 0.3)'

def generate_chart_js(chart_id, chart_type, labels, datasets):
    datasets_js = [
        {
            'label': dataset['label'],
            'data': dataset['data'],
            'backgroundColor': dataset['backgroundColor'],
            'borderColor': dataset['borderColor'],
            'borderWidth': 1
        } for dataset in datasets
    ]
    chart_js = f"""
    <script>
        var ctx = document.getElementById('{chart_id}').getContext('2d');
        var myChart = new Chart(ctx, {{
            type: '{chart_type}',
            data: {{
                labels: {json.dumps(labels)},
                datasets: {json.dumps(datasets_js)}
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }},
                plugins: {{
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                var label = context.dataset.label || '';
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

class DashboardCreator:
    def __init__(self, data_directory='.'):
        self.data_directory = data_directory
        self.aggregated_data = self.aggregate_data()

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

    def prepare_all_comparison_data(self):
        categories = ['Person', 'Company', 'WorksAt']
        labels = sorted(self.aggregated_data.keys())
        datasets = [
            {"label": category, "data": [], "backgroundColor": generate_color(category + "BG"), "borderColor": generate_color(category + "Border")}
            for category in categories
        ]

        for version in labels:
            for dataset in datasets:
                category = dataset['label']
                load_time = next((item["Load Time (Seconds)"] for item in self.aggregated_data[version]['load_times'] if item["Table Name"] == category), 0)
                dataset['data'].append(load_time)

        return labels, datasets

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

        labels, datasets = self.prepare_all_comparison_data()
        comparison_chart_html = generate_chart_js("comparisonChart", "bar", labels, datasets)

        for version, data in self.aggregated_data.items():
            dashboard_filename = f'{version.replace(".", "_")}_dashboard.html'
            with open(dashboard_filename, 'w') as f:
                f.write(f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>{version} Dashboard</title>
                    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                </head>
                <body>
                    <h1>{version} Dashboard</h1>
                    <div style="width:80%; height:400px;">
                        <canvas id="comparisonChart"></canvas>
                    </div>
                    {comparison_chart_html}
                </body>
                </html>
                """)
            index_content += f'<li><a href="{dashboard_filename}">{version} Dashboard</a></li>\n'

        index_content += "</ul></body></html>"
        with open('index.html', 'w') as f:
            f.write(index_content)

if __name__ == "__main__":
    dashboard_creator = DashboardCreator('.')
    dashboard_creator.generate_dashboard()
