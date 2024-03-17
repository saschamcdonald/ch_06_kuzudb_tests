import json
import datetime
import os
import hashlib
import glob

# Function to generate a unique color based on the category
def generate_color(category):
    hash_value = hashlib.md5(category.encode()).hexdigest()
    r = int(hash_value[:2], 16)
    g = int(hash_value[2:4], 16)
    b = int(hash_value[4:6], 16)
    return f'rgba({r}, {g}, {b}, 0.6)'

# Function to generate Chart.js JavaScript code
def generate_chart_js(chart_id, chart_type, labels, datasets):
    datasets_js = [{
        'label': dataset['label'],
        'data': dataset['data'],
        'backgroundColor': dataset['backgroundColor'],
        'borderColor': dataset['borderColor'],
        'borderWidth': 1
    } for dataset in datasets]

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

# DashboardCreator class for handling data aggregation and dashboard generation
class DashboardCreator:
    def __init__(self, data_directory='.'):
        self.data_directory = data_directory
        self.aggregated_data = self.aggregate_data()

    # Aggregate data from all JSON files
    def aggregate_data(self):
        aggregated_data = {}
        json_files = glob.glob(os.path.join(self.data_directory, '*.json'))
        for json_file in json_files:
            with open(json_file, 'r') as f:
                data = json.load(f)
            version = data.get('kuzu')
            if version not in aggregated_data:
                aggregated_data[version] = {'load_times': [], 'database_summary': []}
            aggregated_data[version]['load_times'].extend(data.get('load_times', []))
            aggregated_data[version]['database_summary'].extend(data.get('database_summary', []))
        return aggregated_data

    # Prepare comparative data for the dashboard
    def prepare_all_comparison_data(self):
        labels = sorted(self.aggregated_data.keys())
        categories = ['Person', 'Company', 'WorksAt']
        datasets = [{
            'label': category,
            'data': [sum(item["Load Time (Seconds)"] for item in self.aggregated_data[version]['load_times'] if item["Table Name"] == category) for version in labels],
            'backgroundColor': generate_color(category),
            'borderColor': generate_color(category)
        } for category in categories]
        return labels, datasets

    # Generate the comparison dashboard HTML file
    def generate_dashboard(self):
        labels, datasets = self.prepare_all_comparison_data()
        comparison_chart_js = generate_chart_js("comparisonChart", "bar", labels, datasets)

        dashboard_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Comparison Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
            <h1>Comparison Dashboard</h1>
            <div style="width:80%; height:400px;">
                <canvas id="comparisonChart"></canvas>
            </div>
            {comparison_chart_js}
        </body>
        </html>
        """

        # Write the HTML content to the comparison_dashboard.html file
        with open('comparison_dashboard.html', 'w') as f:
            f.write(dashboard_html)

        print("Comparison dashboard generated successfully.")

# Main execution
if __name__ == "__main__":
    dashboard_creator = DashboardCreator('.')
    dashboard_creator.generate_dashboard()
