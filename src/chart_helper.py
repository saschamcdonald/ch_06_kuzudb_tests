import json

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
            maintainAspectRatio: true
        }}
    }});
</script>
"""
    return chart_js
