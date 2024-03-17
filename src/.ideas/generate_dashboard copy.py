# generate_dashboard.py
from comparisons import ComparisonWidget

def generate_full_dashboard(data_directory='.'):
    comparison_widget = ComparisonWidget(data_directory)
    widget_html = comparison_widget.generate_widget()
    
    dashboard_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Dashboard</title>
    </head>
    <body>
        <h1>Dashboard</h1>
        {widget_html}
    </body>
    </html>
    """
    
    with open('dashboard.html', 'w') as file:
        file.write(dashboard_html)
    print("Dashboard generated successfully.")

if __name__ == "__main__":
    generate_full_dashboard('.')
