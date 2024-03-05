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
                    tooltips: {{
                        callbacks: {{
                            label: function(tooltipItem, data) {{
                                return data.datasets[tooltipItem.datasetIndex].label + ': ' + tooltipItem.yLabel + ' seconds';
                            }},
                            afterLabel: function(tooltipItem, data) {{
                                return {additional_info_js_array}[tooltipItem.index];
                            }}
                        }}
                    }}
                }}
            }});
        '''