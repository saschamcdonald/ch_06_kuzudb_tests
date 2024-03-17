# comparisons.py
import json
import hashlib
import glob

def generate_color(category):
    hash_value = hashlib.md5(category.encode()).hexdigest()
    r, g, b = int(hash_value[:2], 16), int(hash_value[2:4], 16), int(hash_value[4:6], 16)
    return f'rgba({r}, {g}, {b}, 0.6)'

class ComparisonWidget:
    def __init__(self, data_directory='.'):
        self.data_directory = data_directory
        self.aggregated_data = self.aggregate_data()

    def aggregate_data(self):
        aggregated_data = {}
        json_files = glob.glob(f'{self.data_directory}/*.json')
        for json_file in json_files:
            with open(json_file, 'r') as file:
                data = json.load(file)
            version = data.get('kuzu', 'unknown')
            if version not in aggregated_data:
                aggregated_data[version] = {'load_times': [], 'database_summary': []}
            aggregated_data[version]['load_times'].extend(data.get('load_times', []))
            aggregated_data[version]['database_summary'].extend(data.get('database_summary', []))
        return aggregated_data

    def generate_widget(self):
        labels, datasets = self.prepare_all_comparison_data()
        return self.generate_chart_js("comparisonChart", "bar", labels, datasets)

    def prepare_all_comparison_data(self):
        labels = sorted(self.aggregated_data.keys())
        categories = ['Person', 'Company', 'WorksAt']
        datasets = [{
            'label': category,
            'data': [sum(item["Load Time (Seconds)"] for item in self.aggregated_data[version]['load_times'] if item["Table Name"] == category) for version in labels],
            'backgroundColor': generate_color(category + "_bg"),
            'borderColor': generate_color(category + "_border")
        } for category in categories]
        return labels, datasets

    @staticmethod
    def generate_chart_js(chart_id, chart_type, labels, datasets):
        datasets_js = [{
            'label': dataset['label'],
            'data': dataset['data'],
            'backgroundColor': dataset['backgroundColor'],
            'borderColor': dataset['borderColor'],
            'borderWidth': 1
        } for dataset in datasets]

        chart_js = f"""
        <div style="width:60%; height:400px; resize: both; overflow: auto;">
            <canvas id="{chart_id}"></canvas>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            var ctx = document.getElementById('{chart_id}').getContext('2d');
            var myChart = new Chart(ctx, {{
                type: '{chart_type}',
                data: {{
                    labels: {json.dumps(labels)},
                    datasets: {json.dumps(datasets_js)}
                }},
                options: {{ responsive: true, maintainAspectRatio: false }}
            }});
        </script>
        """
        return chart_js
