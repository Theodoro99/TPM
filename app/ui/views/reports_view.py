import flet as ft
import calendar
import math
from datetime import datetime, timedelta
from sqlalchemy import not_, or_


class ChartCard(ft.Card):
    def __init__(self, title, chart_type="bar", height=300):
        super().__init__()
        self.title = title
        self.chart_type = chart_type
        self.height = height
        self.data = self.get_chart_data()
        self.content = self.build_content()
        self.elevation = 3
    
    def get_chart_data(self):
        """Get real data from the database for this chart"""
        try:
            from app.db.database import SessionLocal
            from app.db.models import LogbookEntry, StatusEnum
            from sqlalchemy import func, not_, or_, desc, extract
            from datetime import datetime, timedelta
            import random  # For generating demo data if needed
            
            # Default data in case of errors
            default_data = {
                "pie": {
                    "labels": ["Open", "Ongoing", "Completed", "Escalated"],
                    "values": [25, 25, 25, 25],
                    "colors": [ft.colors.AMBER_500, ft.colors.PURPLE_500, ft.colors.GREEN_500, ft.colors.RED_500]
                },
                "bar": {
                    "labels": ["Category 1", "Category 2", "Category 3", "Category 4", "Category 5"],
                    "values": [10, 20, 15, 25, 30],
                    "colors": [ft.colors.BLUE_400, ft.colors.GREEN_400, ft.colors.AMBER_400, ft.colors.RED_400, ft.colors.PURPLE_400]
                },
                "line": {
                    "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                    "datasets": [
                        {
                            "name": "Open",
                            "values": [5, 8, 12, 10, 7, 9],
                            "color": ft.colors.AMBER_500
                        },
                        {
                            "name": "Completed",
                            "values": [3, 5, 8, 10, 12, 15],
                            "color": ft.colors.GREEN_500
                        },
                        {
                            "name": "Escalated",
                            "values": [2, 3, 1, 4, 2, 3],
                            "color": ft.colors.RED_500
                        }
                    ]
                }
            }
            
            with SessionLocal() as session:
                # Get data based on chart title and type
                if self.title == "Issues by Category":
                    # Group entries by task/category
                    query_result = session.query(
                        LogbookEntry.task, 
                        func.count(LogbookEntry.id)
                    ).filter(
                        or_(LogbookEntry.is_deleted == False, LogbookEntry.is_deleted == None)
                    ).group_by(LogbookEntry.task).all()
                    
                    if query_result:
                        labels = [r[0] or "Uncategorized" for r in query_result]
                        values = [r[1] for r in query_result]
                        # Generate colors for each category - using predefined colors instead of from_rgb
                        predefined_colors = [
                            ft.colors.BLUE_400, ft.colors.GREEN_400, ft.colors.AMBER_400, 
                            ft.colors.RED_400, ft.colors.PURPLE_400, ft.colors.CYAN_400,
                            ft.colors.DEEP_ORANGE_400, ft.colors.INDIGO_400, ft.colors.TEAL_400
                        ]
                        colors = [predefined_colors[i % len(predefined_colors)] for i, _ in enumerate(labels)]
                        return {"labels": labels, "values": values, "colors": colors}
                
                elif self.title == "Issues by Location":
                    # Group entries by location/device
                    query_result = session.query(
                        LogbookEntry.device, 
                        func.count(LogbookEntry.id)
                    ).filter(
                        or_(LogbookEntry.is_deleted == False, LogbookEntry.is_deleted == None)
                    ).group_by(LogbookEntry.device).all()
                    
                    if query_result:
                        labels = [r[0] or "Unknown" for r in query_result]
                        values = [r[1] for r in query_result]
                        predefined_colors = [
                            ft.colors.BLUE_400, ft.colors.GREEN_400, ft.colors.AMBER_400, 
                            ft.colors.RED_400, ft.colors.PURPLE_400, ft.colors.CYAN_400,
                            ft.colors.DEEP_ORANGE_400, ft.colors.INDIGO_400, ft.colors.TEAL_400
                        ]
                        colors = [predefined_colors[i % len(predefined_colors)] for i, _ in enumerate(labels)]
                        return {"labels": labels, "values": values, "colors": colors}
                
                elif self.title == "Monthly Trends" or self.title == "Resolution Time Trends":
                    # Get data for the last 6 months
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=180)  # ~6 months
                    
                    # Get month names for the last 6 months
                    months = []
                    current = start_date
                    while current <= end_date:
                        months.append(current.strftime("%b"))
                        # Move to next month
                        if current.month == 12:
                            current = current.replace(year=current.year + 1, month=1)
                        else:
                            current = current.replace(month=current.month + 1)
                    
                    # Get counts by status and month
                    datasets = []
                    for status, color in [
                        (StatusEnum.OPEN, ft.colors.AMBER_500),
                        (StatusEnum.COMPLETED, ft.colors.GREEN_500),
                        (StatusEnum.ESCALATION, ft.colors.RED_500)
                    ]:
                        monthly_counts = []
                        current = start_date
                        while current <= end_date:
                            next_month = current.replace(month=current.month + 1) if current.month < 12 else current.replace(year=current.year + 1, month=1)
                            count = session.query(func.count(LogbookEntry.id)).filter(
                                LogbookEntry.status == status,
                                LogbookEntry.created_at >= current,
                                LogbookEntry.created_at < next_month,
                                or_(LogbookEntry.is_deleted == False, LogbookEntry.is_deleted == None)
                            ).scalar() or 0
                            monthly_counts.append(count)
                            current = next_month
                        
                        datasets.append({
                            "name": status.value.capitalize(),
                            "values": monthly_counts,
                            "color": color
                        })
                    
                    return {"labels": months, "datasets": datasets}
                
                elif "Resolution Time" in self.title:
                    # For resolution time charts
                    if "by Category" in self.title:
                        # Get average resolution time by task/category
                        query_result = session.query(
                            LogbookEntry.task,
                            func.avg(
                                func.coalesce(
                                    # Use resolution_time if available, otherwise fall back to updated_at
                                    func.extract('epoch', LogbookEntry.resolution_time - LogbookEntry.created_at),
                                    func.extract('epoch', LogbookEntry.updated_at - LogbookEntry.created_at)
                                ) / 3600
                            )
                        ).filter(
                            LogbookEntry.status == StatusEnum.COMPLETED,
                            or_(LogbookEntry.is_deleted == False, LogbookEntry.is_deleted == None)
                        ).group_by(LogbookEntry.task).all()
                        
                        if query_result:
                            labels = [r[0] or "Uncategorized" for r in query_result]
                            values = [float(r[1] or 0) for r in query_result]
                            colors = [ft.colors.BLUE_400 for _ in labels]
                            return {"labels": labels, "values": values, "colors": colors}
                    
                    elif "by Technician" in self.title:
                        # Get average resolution time by responsible person
                        query_result = session.query(
                            LogbookEntry.responsible_person,
                            func.avg(
                                func.coalesce(
                                    # Use resolution_time if available, otherwise fall back to updated_at
                                    func.extract('epoch', LogbookEntry.resolution_time - LogbookEntry.created_at),
                                    func.extract('epoch', LogbookEntry.updated_at - LogbookEntry.created_at)
                                ) / 3600
                            )
                        ).filter(
                            LogbookEntry.status == StatusEnum.COMPLETED,
                            or_(LogbookEntry.is_deleted == False, LogbookEntry.is_deleted == None)
                        ).group_by(LogbookEntry.responsible_person).all()
                        
                        if query_result:
                            labels = [r[0] or "Unknown" for r in query_result]
                            values = [float(r[1] or 0) for r in query_result]
                            colors = [ft.colors.GREEN_400 for _ in labels]
                            return {"labels": labels, "values": values, "colors": colors}
                
                elif self.title == "Common Issues":
                    # Get most common issues by description
                    query_result = session.query(
                        LogbookEntry.call_description,
                        func.count(LogbookEntry.id)
                    ).filter(
                        or_(LogbookEntry.is_deleted == False, LogbookEntry.is_deleted == None)
                    ).group_by(LogbookEntry.call_description).order_by(desc(func.count(LogbookEntry.id))).limit(5).all()
                    
                    if query_result:
                        # Truncate descriptions if they're too long
                        labels = [r[0][:30] + "..." if len(r[0]) > 30 else r[0] for r in query_result]
                        values = [r[1] for r in query_result]
                        colors = [ft.colors.PURPLE_400 for _ in labels]
                        return {"labels": labels, "values": values, "colors": colors}
            
            # Return default data if no specific data was generated
            return default_data[self.chart_type]
            
        except Exception as e:
            print(f"Error getting chart data for {self.title}: {e}")
            import traceback
            traceback.print_exc()
            # Return default data for this chart type
            return {
                "pie": {
                    "labels": ["Open", "Ongoing", "Completed", "Escalated"],
                    "values": [25, 25, 25, 25],
                    "colors": [ft.colors.AMBER_500, ft.colors.PURPLE_500, ft.colors.GREEN_500, ft.colors.RED_500]
                },
                "bar": {
                    "labels": ["Category 1", "Category 2", "Category 3", "Category 4", "Category 5"],
                    "values": [10, 20, 15, 25, 30],
                    "colors": [ft.colors.BLUE_400, ft.colors.GREEN_400, ft.colors.AMBER_400, ft.colors.RED_400, ft.colors.PURPLE_400]
                },
                "line": {
                    "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                    "datasets": [
                        {
                            "name": "Open",
                            "values": [5, 8, 12, 10, 7, 9],
                            "color": ft.colors.AMBER_500
                        },
                        {
                            "name": "Completed",
                            "values": [3, 5, 8, 10, 12, 15],
                            "color": ft.colors.GREEN_500
                        },
                        {
                            "name": "Escalated",
                            "values": [2, 3, 1, 4, 2, 3],
                            "color": ft.colors.RED_500
                        }
                    ]
                }
            }[self.chart_type]
    
    def build_content(self):
        # Create actual chart based on chart type and data
        if self.chart_type == "pie":
            chart = self.create_pie_chart()
        elif self.chart_type == "bar":
            chart = self.create_bar_chart()
        elif self.chart_type == "line":
            chart = self.create_line_chart()
        else:
            # Fallback to placeholder
            chart = self.create_placeholder()
        
        chart_content = ft.Container(
            content=chart,
            bgcolor=ft.colors.BLUE_50,
            border_radius=10,
            height=self.height,
            alignment=ft.alignment.center,
            padding=ft.padding.all(10),
        )
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        self.title,
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(height=10),
                    chart_content,
                ],
            ),
            padding=ft.padding.all(20),
        )
    
    def create_pie_chart(self):
        """Create a pie chart with the data"""
        try:
            # Check if we have data
            if not self.data or not self.data.get("labels") or not self.data.get("values"):
                return self.create_placeholder("No data available")
            
            # Sort data by value in descending order for better visualization
            combined_data = sorted(
                zip(self.data["labels"], self.data["values"]), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            # Limit to top 5 categories for better readability
            if len(combined_data) > 5:
                # Extract top 4 and combine the rest as "Other"
                top_items = combined_data[:4]
                other_value = sum(value for _, value in combined_data[4:])
                combined_data = top_items + [("Other", other_value)]
            
            # Create pie chart sections
            sections = []
            total = sum(self.data["values"])
            
            if total == 0:
                # No data, show placeholder
                return self.create_placeholder("No entries found")
            
            # Define styles for normal and hover states
            normal_radius = 50
            hover_radius = 60
            normal_title_style = ft.TextStyle(
                size=12, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD
            )
            hover_title_style = ft.TextStyle(
                size=16,
                color=ft.colors.WHITE,
                weight=ft.FontWeight.BOLD,
                shadow=ft.BoxShadow(blur_radius=2, color=ft.colors.BLACK54),
            )
            
            # Define colors with better contrast for pie chart
            predefined_colors = [
                ft.colors.BLUE_500, ft.colors.GREEN_500, ft.colors.AMBER_500, 
                ft.colors.RED_500, ft.colors.PURPLE_500, ft.colors.CYAN_500,
                ft.colors.DEEP_ORANGE_500, ft.colors.INDIGO_500
            ]
            
            for i, (label, value) in enumerate(combined_data):
                # Truncate long labels
                display_label = label if len(str(label)) < 15 else str(label)[:12] + "..."
                
                # Calculate percentage
                percentage = (value / total) * 100
                
                # Skip very small slices (less than 1%)
                if percentage < 1:
                    continue
                
                # Create a section with label and percentage
                section = ft.PieChartSection(
                    value,
                    title=f"{display_label}\n{percentage:.1f}%",
                    title_style=normal_title_style,
                    color=predefined_colors[i % len(predefined_colors)],
                    radius=normal_radius,
                )
                
                sections.append(section)
            
            # If no sections (all were too small), show at least one
            if not sections and combined_data:
                label, value = combined_data[0]
                display_label = label if len(str(label)) < 15 else str(label)[:12] + "..."
                sections.append(
                    ft.PieChartSection(
                        value=value,
                        title=f"{display_label}\n100.0%",
                        title_style=normal_title_style,
                        color=predefined_colors[0],
                        radius=normal_radius,
                    )
                )
            
            # Create an event handler for hover effects
            def on_chart_event(e):
                for idx, section in enumerate(chart.sections):
                    if idx == e.section_index:
                        section.radius = hover_radius
                        section.title_style = hover_title_style
                    else:
                        section.radius = normal_radius
                        section.title_style = normal_title_style
                chart.update()
            
            # Create the pie chart with proper parameters
            chart = ft.PieChart(
                sections=sections,
                sections_space=1,
                center_space_radius=40,
                on_chart_event=on_chart_event,
                expand=True
            )
            
            return chart
        except Exception as e:
            print(f"Error creating pie chart: {e}")
            return self.create_placeholder(f"Error: {str(e)[:50]}...")
    
    def create_bar_chart(self):
        """Create a bar chart with the data"""
        try:
            # Check if we have data
            if not self.data or not self.data.get("labels") or not self.data.get("values"):
                return self.create_placeholder("No data available")
            
            # Sort data by value in descending order for better visualization
            combined_data = sorted(
                zip(self.data["labels"], self.data["values"]), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            # Limit to top 8 items for better readability
            if len(combined_data) > 8:
                combined_data = combined_data[:8]
            
            # Unpack the sorted data
            labels, values = zip(*combined_data) if combined_data else ([], [])
            
            # Use consistent colors with better contrast
            colors = [
                ft.colors.BLUE_500, ft.colors.GREEN_500, ft.colors.AMBER_500, 
                ft.colors.RED_500, ft.colors.PURPLE_500, ft.colors.CYAN_500,
                ft.colors.DEEP_ORANGE_500, ft.colors.INDIGO_500
            ]
            
            # Find the maximum value for scaling
            max_value = max(values) if values else 0
            
            # Create a container for the bar chart
            chart_container = ft.Column(spacing=10, expand=True)
            
            # Add a title for the chart
            chart_container.controls.append(
                ft.Container(
                    content=ft.Text(
                        self.title,
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLACK,
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(bottom=15),
                )
            )
            
            # Track the currently highlighted bar
            highlighted_index = [-1]  # Using list to allow modification in inner function
            
            # Create a row for each bar
            bar_rows = []
            for i, (label, value) in enumerate(zip(labels, values)):
                # Truncate long labels
                display_label = label if len(str(label)) < 15 else str(label)[:12] + "..."
                
                # Calculate percentage width based on max value
                percentage = (value / max_value) * 100 if max_value > 0 else 0
                
                # Create the bar container with hover effect
                bar_container = ft.Container(
                    content=ft.Container(
                        bgcolor=colors[i % len(colors)],
                        border_radius=ft.border_radius.all(4),
                        padding=ft.padding.all(0),
                        shadow=None,  # Will be set on hover
                    ),
                    expand=True,
                    height=30,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
                )
                
                # Value label that will appear inside or outside the bar
                value_label = ft.Text(
                    str(value),
                    size=14,
                    color=ft.colors.WHITE,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.RIGHT,
                )
                
                # Create a bar with label and value
                bar_row = ft.Row(
                    [
                        # Label (left-aligned)
                        ft.Container(
                            content=ft.Text(
                                display_label,
                                size=14,
                                color=ft.colors.BLACK,
                                text_align=ft.TextAlign.RIGHT,
                            ),
                            width=120,
                            alignment=ft.alignment.center_right,
                            padding=ft.padding.only(right=10),
                        ),
                        
                        # Bar with value label inside
                        ft.Stack(
                            [
                                bar_container,
                                ft.Container(
                                    content=value_label,
                                    alignment=ft.alignment.center_right,
                                    padding=ft.padding.only(right=10),
                                    expand=True,
                                )
                            ],
                            expand=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                )
                
                # Set the width of the bar based on percentage
                bar_container.content.width = f"{percentage}%"
                
                # Store the row index for hover effect
                row_index = i
                
                # Add hover effect
                def create_hover_handler(index):
                    def on_hover(e):
                        # Reset previous highlight if any
                        if highlighted_index[0] >= 0 and highlighted_index[0] < len(bar_rows):
                            prev_bar = bar_rows[highlighted_index[0]].controls[1].controls[0].content
                            prev_bar.shadow = None
                            prev_bar.border = None
                        
                        # Highlight current bar
                        if e.data == "true":  # Mouse entered
                            bar_rows[index].controls[1].controls[0].content.shadow = ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=8,
                                color=ft.colors.with_opacity(0.3, colors[index % len(colors)]),
                            )
                            bar_rows[index].controls[1].controls[0].content.border = ft.border.all(
                                2, ft.colors.with_opacity(0.7, colors[index % len(colors)])
                            )
                            highlighted_index[0] = index
                        else:  # Mouse exited
                            highlighted_index[0] = -1
                        
                        chart_container.update()
                    
                    return on_hover
                
                # Attach hover handler
                bar_row.on_hover = create_hover_handler(row_index)
                
                bar_rows.append(bar_row)
                chart_container.controls.append(bar_row)
            
            # If no data, show placeholder
            if len(chart_container.controls) <= 1:  # Only title, no bars
                return self.create_placeholder("No data to display")
            
            # Add a container for better padding
            return ft.Container(
                content=chart_container,
                padding=ft.padding.all(15),
                border_radius=ft.border_radius.all(8),
                bgcolor=ft.colors.WHITE,
                shadow=ft.BoxShadow(
                    spread_radius=0.5,
                    blur_radius=5,
                    color=ft.colors.with_opacity(0.1, ft.colors.BLACK),
                ),
            )
        except Exception as e:
            print(f"Error creating bar chart: {e}")
            import traceback
            traceback.print_exc()
            return self.create_placeholder(f"Error: {str(e)[:50]}...")
    
    def create_line_chart(self):
        """Create a line chart with the data"""
        try:
            # Check if we have data
            if not self.data or not self.data.get("labels") or not self.data.get("datasets"):
                return self.create_placeholder("No data available")
            
            # Create a container for the line chart
            chart_container = ft.Column(spacing=10, expand=True)
            
            # Add the chart title and legend with improved styling
            legend = ft.Row(spacing=15, alignment=ft.MainAxisAlignment.CENTER)
            
            # Create legend items for each dataset with better styling
            for dataset in self.data["datasets"]:
                legend.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    width=15, 
                                    height=15, 
                                    bgcolor=dataset["color"], 
                                    border_radius=ft.border_radius.all(2),
                                    border=ft.border.all(0.5, ft.colors.BLACK26),
                                ),
                                ft.Text(
                                    dataset["name"], 
                                    size=13, 
                                    color=ft.colors.BLACK,
                                    weight=ft.FontWeight.W_500,
                                ),
                            ],
                            spacing=8,
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.only(left=8, right=8, top=5, bottom=5),
                        border_radius=ft.border_radius.all(15),
                        bgcolor=ft.colors.with_opacity(0.1, dataset["color"]),
                    )
                )
            
            chart_container.controls.append(legend)
            
            # Find max value across all datasets for scaling
            max_value = 0
            for dataset in self.data["datasets"]:
                if dataset["values"]:
                    max_value = max(max_value, max(dataset["values"]))
            
            # If no data, show placeholder
            if max_value == 0:
                return self.create_placeholder("No data to display")
            
            # Create a simulated line chart using stacked bars
            chart_content = ft.Column(spacing=0, expand=True)
            
            # Create Y-axis scale
            y_axis_labels = ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Text(f"{max_value}", size=10, color=ft.colors.BLACK54),
                            alignment=ft.alignment.center_right,
                            padding=ft.padding.only(right=5),
                        ),
                        ft.Container(
                            content=ft.Text(f"{int(max_value * 0.75)}", size=10, color=ft.colors.BLACK54),
                            alignment=ft.alignment.center_right,
                            padding=ft.padding.only(right=5),
                        ),
                        ft.Container(
                            content=ft.Text(f"{int(max_value * 0.5)}", size=10, color=ft.colors.BLACK54),
                            alignment=ft.alignment.center_right,
                            padding=ft.padding.only(right=5),
                        ),
                        ft.Container(
                            content=ft.Text(f"{int(max_value * 0.25)}", size=10, color=ft.colors.BLACK54),
                            alignment=ft.alignment.center_right,
                            padding=ft.padding.only(right=5),
                        ),
                        ft.Container(
                            content=ft.Text("0", size=10, color=ft.colors.BLACK54),
                            alignment=ft.alignment.center_right,
                            padding=ft.padding.only(right=5),
                        ),
                    ],
                    spacing=0,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    expand=True,
                ),
                width=30,
            )
            
            # Create the chart grid with data points
            chart_grid = ft.Container(
                content=self.create_enhanced_chart_grid(max_value),
                expand=True,
                border=ft.border.all(1, ft.colors.BLACK12),
                border_radius=ft.border_radius.all(4),
                padding=ft.padding.all(10),
            )
            
            # Combine Y-axis and chart grid
            chart_row = ft.Row(
                [y_axis_labels, chart_grid],
                spacing=0,
                expand=True,
            )
            
            chart_content.controls.append(chart_row)
            
            # Add X-axis labels
            x_axis = self.create_enhanced_x_axis_labels()
            chart_content.controls.append(x_axis)
            
            # Add the chart content to the container with extra bottom padding
            chart_container.controls.append(
                ft.Container(
                    content=chart_content,
                    expand=True,
                    margin=ft.margin.only(top=15, bottom=30),
                    padding=ft.padding.only(bottom=20),
                )
            )
            
            # Wrap the chart container in another container with extra padding
            return ft.Container(
                content=chart_container,
                padding=ft.padding.only(bottom=40),
                height=self.height + 80  # Add extra height to accommodate labels
            )
        except Exception as e:
            print(f"Error creating line chart: {e}")
            import traceback
            traceback.print_exc()
            return self.create_placeholder(f"Error: {str(e)[:50]}...")
    
    def create_enhanced_chart_grid(self, max_value):
        """Create an enhanced chart grid with data visualizations"""
        # Create a stack with grid lines and data points
        grid_stack = ft.Stack(expand=True)
        
        # Add horizontal grid lines
        grid_lines = ft.Column(expand=True)
        for i in range(5):
            grid_lines.controls.append(
                ft.Container(
                    content=ft.Container(
                        bgcolor=ft.colors.BLACK12,
                        height=1,
                    ),
                    alignment=ft.alignment.center,
                    expand=True,
                )
            )
        grid_stack.controls.append(grid_lines)
        
        # Add data points and trend lines for each dataset
        if self.data and self.data.get("datasets") and self.data.get("labels"):
            num_points = len(self.data["labels"])
            if num_points > 0:
                # For each dataset, create a series of data points
                for dataset in self.data["datasets"]:
                    data_points = []
                    for i, value in enumerate(dataset["values"]):
                        if i < num_points:
                            # Calculate position (x from 0 to 1, y from 0 to 1 inverted)
                            x_pos = i / (num_points - 1) if num_points > 1 else 0.5
                            y_pos = 1 - (value / max_value if max_value > 0 else 0)
                            
                            # Create a data point with improved positioning
                            data_point = ft.Container(
                                content=ft.Container(
                                    bgcolor=dataset["color"],
                                    width=8,
                                    height=8,
                                    border_radius=ft.border_radius.all(4),
                                    border=ft.border.all(1, ft.colors.WHITE),
                                ),
                                alignment=ft.alignment.center,
                                # Adjust positioning to ensure full width distribution
                                left=f"{x_pos * 100}%",  # Use percentage string format
                                top=f"{y_pos * 100}%",   # Use percentage string format
                                right=None,
                                bottom=None,
                                width=10,
                                height=10,
                                animate=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT),
                            )
                            data_points.append(data_point)
                    
                    # Add all data points to the stack
                    for point in data_points:
                        grid_stack.controls.append(point)
                    
                    # Create a simulated line using a series of small containers
                    if len(dataset["values"]) > 1:
                        for i in range(len(dataset["values"]) - 1):
                            if i < num_points - 1:
                                # Calculate positions for start and end points
                                x1 = i / (num_points - 1) if num_points > 1 else 0.5
                                y1 = 1 - (dataset["values"][i] / max_value if max_value > 0 else 0)
                                x2 = (i + 1) / (num_points - 1) if num_points > 1 else 0.5
                                y2 = 1 - (dataset["values"][i + 1] / max_value if max_value > 0 else 0)
                                
                                # Create a line segment with improved positioning
                                # Calculate the angle of the line for proper positioning
                                dx = x2 - x1
                                dy = y2 - y1
                                angle = math.atan2(dy, dx) * 180 / math.pi
                                
                                # Create a line segment that connects the points properly
                                line = ft.Container(
                                    bgcolor=dataset["color"],
                                    height=2,
                                    left=f"{x1 * 100}%",  # Use percentage string format
                                    top=f"{y1 * 100}%",   # Position at first point
                                    width=f"{(x2 - x1) * 100}%",  # Width as percentage of container
                                    rotate=ft.Rotate(angle, alignment=ft.alignment.center_left),
                                    animate=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT),
                                )
                                grid_stack.controls.append(line)
        
        return grid_stack
    
    def create_enhanced_x_axis_labels(self):
        """Create enhanced X-axis labels for the line chart"""
        # Create a container for the X-axis with increased height
        x_axis_container = ft.Container(
            content=ft.Row(
                [ft.Container(width=30)],  # Spacer for Y-axis alignment
                spacing=0,
            ),
            margin=ft.margin.only(top=5, bottom=10),
            height=40,
        )
        
        # Get the labels row
        labels_row = x_axis_container.content
        
        # Add a container for the labels with improved distribution
        labels_container = ft.Container(
            content=ft.Row(
                # Create actual label containers instead of placeholders
                [ft.Container(
                    content=ft.Text(
                        str(label)[:8] + "..." if len(str(label)) > 8 else str(label),
                        size=10,
                        color=ft.colors.BLACK54,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    width=None,  # Allow flexible width
                    alignment=ft.alignment.center,
                ) for label in self.data["labels"]],
                spacing=0,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                expand=True,
            ),
            expand=True,
        )
        
        labels_row.controls.append(labels_container)
        
        return x_axis_container
    
    def create_placeholder(self, message="No data available"):
        """Create a placeholder when chart data is not available"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        ft.icons.BAR_CHART if self.chart_type == "bar" else 
                        ft.icons.PIE_CHART if self.chart_type == "pie" else
                        ft.icons.SHOW_CHART,
                        size=50,
                        color=ft.colors.BLUE_GREY_300,
                    ),
                    ft.Text(
                        message,
                        size=16,
                        color=ft.colors.BLUE_GREY_500,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            alignment=ft.alignment.center,
            height=self.height,
            border=ft.border.all(1, ft.colors.BLUE_GREY_200),
            border_radius=5,
            padding=ft.padding.all(20),
        )


class ReportFilters(ft.Column):
    def __init__(self, on_apply=None):
        super().__init__()
        self.on_apply = on_apply
        
        # Initialize date-related variables
        today = datetime.now()
        self.selected_date = today
        self.initial_date = today.strftime("%Y-%m-%d")
        self.is_end_date_selection = False  # Flag to track which date field we're updating
        
        # Date range filters with improved styling
        self.start_date_field = ft.Container(
            content=ft.Column([
                ft.Text("Start Date", color=ft.colors.WHITE, size=14),
                ft.TextField(
                    value=self.initial_date,
                    read_only=True,
                    on_click=lambda e: self.show_date_picker(e, is_end_date=False),
                    border=ft.InputBorder.OUTLINE,
                    filled=True,
                    bgcolor=ft.colors.WHITE,
                    color=ft.colors.BLACK,
                    height=40,
                    width=150,
                )
            ], spacing=5),
            width=170,
        )
        
        self.end_date_field = ft.Container(
            content=ft.Column([
                ft.Text("End Date", color=ft.colors.WHITE, size=14),
                ft.TextField(
                    value=self.initial_date,
                    read_only=True,
                    on_click=lambda e: self.show_date_picker(e, is_end_date=True),
                    border=ft.InputBorder.OUTLINE,
                    filled=True,
                    bgcolor=ft.colors.WHITE,
                    color=ft.colors.BLACK,
                    height=40,
                    width=150,
                )
            ], spacing=5),
            width=170,
        )
        
        # Create a custom date picker dialog with improved styling
        self.date_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Select a date",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.ORANGE
            ),
            content=ft.Column([
                ft.Text(
                    "Click on a date to select it:",
                    size=16,
                    color=ft.colors.WHITE
                ),
                ft.Container(height=10),  # Spacer
                ft.Row([
                    ft.ElevatedButton(
                        text="Today",
                        style=ft.ButtonStyle(
                            color=ft.colors.BLACK,
                            bgcolor=ft.colors.ORANGE,
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        on_click=lambda e: self.set_date(datetime.now())
                    ),
                    ft.ElevatedButton(
                        text="Tomorrow",
                        style=ft.ButtonStyle(
                            color=ft.colors.BLACK,
                            bgcolor=ft.colors.ORANGE,
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        on_click=lambda e: self.set_date(datetime.now() + timedelta(days=1))
                    ),
                    ft.ElevatedButton(
                        text="Next Week",
                        style=ft.ButtonStyle(
                            color=ft.colors.BLACK,
                            bgcolor=ft.colors.ORANGE,
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        on_click=lambda e: self.set_date(datetime.now() + timedelta(days=7))
                    ),
                ]),
                ft.Container(height=10),  # Spacer
                # Month and year selection with improved styling
                ft.Row([
                    ft.Dropdown(
                        label="Month",
                        label_style=ft.TextStyle(
                            color=ft.colors.ORANGE,
                            weight=ft.FontWeight.BOLD,
                            size=14
                        ),
                        width=150,
                        options=[ft.dropdown.Option(str(i), f"{calendar.month_name[i]}") for i in range(1, 13)],
                        value=str(today.month),
                        on_change=self.update_calendar,
                        bgcolor=ft.colors.WHITE,
                        color=ft.colors.BLACK,
                        border_color=ft.colors.ORANGE,
                        focused_border_color=ft.colors.ORANGE,
                        focused_bgcolor=ft.colors.with_opacity(0.1, ft.colors.ORANGE),
                        expand=1
                    ),
                    ft.Dropdown(
                        label="Year",
                        label_style=ft.TextStyle(
                            color=ft.colors.ORANGE,
                            weight=ft.FontWeight.BOLD,
                            size=14
                        ),
                        width=120,
                        options=[ft.dropdown.Option(str(i), str(i)) for i in range(2020, 2031)],
                        value=str(today.year),
                        on_change=self.update_calendar,
                        bgcolor=ft.colors.WHITE,
                        color=ft.colors.BLACK,
                        border_color=ft.colors.ORANGE,
                        focused_border_color=ft.colors.ORANGE,
                        focused_bgcolor=ft.colors.with_opacity(0.1, ft.colors.ORANGE),
                        expand=1
                    ),
                ]),
                ft.Container(height=10),  # Spacer
                # Calendar grid will be added dynamically
                ft.Column([]),
            ]),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=self.close_date_dialog,
                    style=ft.ButtonStyle(
                        color=ft.colors.ORANGE,
                        bgcolor=ft.colors.with_opacity(0.1, ft.colors.BLACK),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=ft.colors.with_opacity(0.95, ft.colors.BLACK),
        )
        
        # Location filter removed as requested
        
        # Task filter (replacing Category filter)
        self.task_dropdown = ft.Dropdown(
            label="Task",
            width=200,
            bgcolor=ft.colors.WHITE,
            color=ft.colors.BLACK,
            text_style=ft.TextStyle(color=ft.colors.WHITE),
            label_style=ft.TextStyle(color=ft.colors.WHITE),
            options=[
                ft.dropdown.Option("all", "All Tasks"),
                ft.dropdown.Option("Interventie", "Interventie"),
                ft.dropdown.Option("Onderhoud", "Onderhoud"),
                ft.dropdown.Option("Facilities", "Facilities"),
                ft.dropdown.Option("NVT", "NVT"),
            ],
            value="all",
        )
        
        # Technician filter
        self.technician_dropdown = ft.Dropdown(
            label="Technician",
            width=200,
            bgcolor=ft.colors.WHITE,
            color=ft.colors.BLACK,
            text_style=ft.TextStyle(color=ft.colors.WHITE),
            label_style=ft.TextStyle(color=ft.colors.WHITE),
            options=[
                ft.dropdown.Option("all", "All Technicians"),
                ft.dropdown.Option("1", "John Smith"),
                ft.dropdown.Option("2", "Jane Doe"),
                ft.dropdown.Option("3", "Mike Johnson"),
                ft.dropdown.Option("4", "Sarah Williams"),
            ],
            value="all",
        )
        
        # Status filter
        self.status_dropdown = ft.Dropdown(
            label="Status",
            width=200,
            bgcolor=ft.colors.WHITE,
            color=ft.colors.BLACK,
            text_style=ft.TextStyle(color=ft.colors.WHITE),
            label_style=ft.TextStyle(color=ft.colors.WHITE),
            options=[
                ft.dropdown.Option("all", "All Statuses"),
                ft.dropdown.Option("open", "Open"),
                ft.dropdown.Option("ongoing", "Ongoing"),
                ft.dropdown.Option("completed", "Completed"),
                ft.dropdown.Option("escalation", "Escalated"),
            ],
            value="all",
        )
        
        # Apply button
        self.apply_button = ft.ElevatedButton(
            text="Apply Filters",
            icon=ft.icons.FILTER_ALT,
            on_click=self.apply_filters,
        )
        
        # Set up the controls
        self.controls = [self.build_content()]
    
    def build_content(self):
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Filter Reports",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(height=10),
                        ft.Row(
                            [
                                self.start_date_field,
                                self.end_date_field,
                            ],
                            wrap=True,
                            spacing=20,
                        ),
                        ft.Container(height=10),
                        ft.Row(
                            [
                                self.task_dropdown,
                                self.technician_dropdown,
                                self.status_dropdown,
                            ],
                            wrap=True,
                            spacing=20,
                        ),
                        ft.Container(height=20),
                        ft.Row(
                            [
                                self.apply_button,
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ],
                ),
                padding=ft.padding.all(20),
            ),
            elevation=2,
        )
    
    def show_date_picker(self, e, is_end_date=False):
        if self.page:
            # Set the flag to track which date field we're updating
            self.is_end_date_selection = is_end_date
            
            # Update the dialog title based on which date we're selecting
            self.date_dialog.title = ft.Text("Select End Date" if is_end_date else "Select Start Date")
            
            # Add date dialog to page overlay if not already added
            if self.date_dialog not in self.page.overlay:
                self.page.overlay.append(self.date_dialog)
            
            # Update the calendar grid before showing the dialog
            self.update_calendar_grid()
            
            # Show the date dialog
            self.date_dialog.open = True
            self.page.update()
    
    def update_calendar(self, e):
        # Update the calendar grid when month or year changes
        self.update_calendar_grid()
        self.page.update()
    
    def update_calendar_grid(self):
        # Get the dialog content column
        content_column = self.date_dialog.content
        
        # Get the row containing month and year dropdowns (index 4)
        month_year_row = content_column.controls[4]
        month_dropdown = month_year_row.controls[0]
        year_dropdown = month_year_row.controls[1]
        
        # Get the selected month and year
        selected_month = int(month_dropdown.value)
        selected_year = int(year_dropdown.value)
        
        # Get the calendar column (index 6)
        if len(content_column.controls) > 6:
            calendar_column = content_column.controls[6]
            calendar_column.controls.clear()
        else:
            calendar_column = ft.Column([])
            content_column.controls.append(calendar_column)
        
        # Get the calendar for the selected month and year
        cal = calendar.monthcalendar(selected_year, selected_month)
        
        # Add day headers with better visibility
        day_headers = ft.Row(
            [
                ft.Container(
                    content=ft.Text(
                        day, 
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ORANGE,
                        size=16
                    ),
                    alignment=ft.alignment.center,
                    width=40,
                    height=40,
                )
                for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        calendar_column.controls.append(day_headers)
        
        # Add calendar days
        for week in cal:
            week_row_controls = []
            for day in week:
                if day != 0:
                    # Create a container for each valid day with better contrast
                    day_container = ft.Container(
                        content=ft.Text(
                            str(day),
                            color=ft.colors.BLACK,
                            weight=ft.FontWeight.BOLD,
                            size=16
                        ),
                        alignment=ft.alignment.center,
                        width=40,
                        height=40,
                        bgcolor=ft.colors.WHITE,
                        border_radius=ft.border_radius.all(20),
                        data=f"{selected_year}-{selected_month:02d}-{day:02d}"
                    )
                    # Add click handler
                    day_container.on_click = lambda e, container=day_container: self.day_clicked(e)
                else:
                    # Empty container for padding with subtle background
                    day_container = ft.Container(
                        content=ft.Text(""),
                        alignment=ft.alignment.center,
                        width=40,
                        height=40,
                        bgcolor=ft.colors.with_opacity(0.1, ft.colors.GREY),
                        border_radius=ft.border_radius.all(20),
                    )
                week_row_controls.append(day_container)
            
            # Create row with all days
            week_row = ft.Row(
                controls=week_row_controls,
                alignment=ft.MainAxisAlignment.CENTER,
            )
            calendar_column.controls.append(week_row)
    
    def day_clicked(self, e):
        # Get the selected date from the container's data attribute
        date_str = e.control.data
        if date_str:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Set the selected date
            self.set_date(selected_date)
    
    def set_date(self, date):
        # Set the selected date and update the appropriate text field
        self.selected_date = date
        formatted_date = date.strftime("%Y-%m-%d")
        
        if self.is_end_date_selection:
            # Update end date field (now a TextField inside a Column inside a Container)
            text_field = self.end_date_field.content.controls[1]
            text_field.value = formatted_date
        else:
            # Update start date field (now a TextField inside a Column inside a Container)
            text_field = self.start_date_field.content.controls[1]
            text_field.value = formatted_date
        
        # Close the dialog
        self.close_date_dialog(None)
        
        # Update the page
        self.page.update()
    
    def close_date_dialog(self, e):
        # Close the date dialog
        self.date_dialog.open = False
        self.page.update()
    
    def apply_filters(self, e):
        """Apply filters and trigger callback."""
        # Get date values from the text fields inside the containers
        start_date_field = self.start_date_field.content.controls[1]
        end_date_field = self.end_date_field.content.controls[1]
        
        # Get filter values
        filter_data = {
            "start_date": start_date_field.value,
            "end_date": end_date_field.value,
            "task": self.task_dropdown.value,
            "technician": self.technician_dropdown.value,
            "status": self.status_dropdown.value,
        }
        
        # Call the callback function with the filter data
        if self.on_apply:
            self.on_apply(filter_data)


class SummaryStats(ft.Row):
    def __init__(self):
        super().__init__()
        
        # Initialize with empty values, will be updated with real data
        self.total_entries = "0"
        self.avg_resolution_time = "0 hours"
        self.completion_rate = "0%"
        self.escalation_rate = "0%"
        
        # Set up the controls
        self.controls = [self.build_content()]
        self.alignment = ft.MainAxisAlignment.SPACE_BETWEEN
        self.wrap = True
        
        # Load initial data
        self.load_data()
    
    def load_data(self):
        """Load real data from the database"""
        try:
            from app.db.database import SessionLocal
            from app.db.models import LogbookEntry, StatusEnum
            from sqlalchemy import func, not_, or_
            
            with SessionLocal() as session:
                # Total entries (excluding deleted or where is_deleted is None)
                total_entries = session.query(LogbookEntry).filter(
                    or_(LogbookEntry.is_deleted == False, LogbookEntry.is_deleted == None)
                ).count()
                
                # Completed entries for completion rate
                completed_entries = session.query(LogbookEntry).filter(
                    LogbookEntry.status == StatusEnum.COMPLETED,
                    or_(LogbookEntry.is_deleted == False, LogbookEntry.is_deleted == None)
                ).count()
                
                # Escalated entries for escalation rate
                escalated_entries = session.query(LogbookEntry).filter(
                    LogbookEntry.status == StatusEnum.ESCALATION,  # Note: ESCALATION not ESCALATED
                    or_(LogbookEntry.is_deleted == False, LogbookEntry.is_deleted == None)
                ).count()
                
                # Average resolution time (for completed entries)
                # Use resolution_time field if available, otherwise fall back to updated_at - created_at
                avg_resolution_query = session.query(
                    func.avg(
                        func.coalesce(
                            # Use resolution_time if available
                            func.extract('epoch', LogbookEntry.resolution_time - LogbookEntry.created_at),
                            # Fall back to updated_at - created_at
                            func.extract('epoch', LogbookEntry.updated_at - LogbookEntry.created_at)
                        ) / 3600
                    )
                ).filter(
                    LogbookEntry.status == StatusEnum.COMPLETED,
                    or_(LogbookEntry.is_deleted == False, LogbookEntry.is_deleted == None)
                )
                
                avg_resolution_hours = avg_resolution_query.scalar()
                # Handle None or negative values
                if avg_resolution_hours is None or avg_resolution_hours < 0:
                    avg_resolution_hours = 0
            
            # Update values
            self.total_entries = str(total_entries)
            
            # Format average resolution time
            if avg_resolution_hours < 1:
                avg_resolution_formatted = f"{int(avg_resolution_hours * 60)} mins"
            else:
                avg_resolution_formatted = f"{avg_resolution_hours:.1f} hours"
            self.avg_resolution_time = avg_resolution_formatted
            
            # Calculate rates
            completion_rate = (completed_entries / total_entries * 100) if total_entries > 0 else 0
            escalation_rate = (escalated_entries / total_entries * 100) if total_entries > 0 else 0
            
            self.completion_rate = f"{int(completion_rate)}%"
            self.escalation_rate = f"{int(escalation_rate)}%"
            
            # Rebuild the content
            self.controls = [self.build_content()]
            
        except Exception as e:
            print(f"Error loading summary stats data: {e}")
            # Keep default values if there's an error
    
    def build_content(self):
        stat_cards = [
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Total Entries",
                                size=16,
                                color=ft.colors.BLUE_GREY_700,
                            ),
                            ft.Container(height=5),
                            ft.Text(
                                self.total_entries,
                                size=30,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.BLUE_700,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.all(20),
                    width=220,
                    height=120,
                ),
                elevation=2,
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Avg. Resolution Time",
                                size=16,
                                color=ft.colors.BLUE_GREY_700,
                            ),
                            ft.Container(height=5),
                            ft.Text(
                                self.avg_resolution_time,
                                size=30,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.ORANGE_700,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.all(20),
                    width=220,
                    height=120,
                ),
                elevation=2,
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Completion Rate",
                                size=16,
                                color=ft.colors.BLUE_GREY_700,
                            ),
                            ft.Container(height=5),
                            ft.Text(
                                self.completion_rate,
                                size=30,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.GREEN_700,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.all(20),
                    width=220,
                    height=120,
                ),
                elevation=2,
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Escalation Rate",
                                size=16,
                                color=ft.colors.BLUE_GREY_700,
                            ),
                            ft.Container(height=5),
                            ft.Text(
                                self.escalation_rate,
                                size=30,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.RED_700,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.all(20),
                    width=220,
                    height=120,
                ),
                elevation=2,
            ),
        ]
        
        return ft.Row(
            stat_cards,
            wrap=True,
            spacing=20,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )


class ReportsView(ft.Container):
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.report_filters = ReportFilters(on_apply=self.update_reports)
        self.summary_stats = SummaryStats()
        
        # Initialize tabs
        self.tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(
                    text="Overview",
                    content=ft.Container(
                        content=ft.Column(
                            [
                                # First row of charts with more spacing
                                ft.Row(
                                    [
                                        ft.Container(
                                            content=ChartCard("Issues by Category", chart_type="pie"),
                                            margin=ft.margin.all(10),
                                            padding=ft.padding.all(20),
                                            bgcolor=ft.colors.with_opacity(0.03, ft.colors.BLACK),
                                            border_radius=ft.border_radius.all(8),
                                            height=380,
                                        ),
                                        ft.Container(
                                            content=ChartCard("Issues by Location", chart_type="pie"),
                                            margin=ft.margin.all(10),
                                            padding=ft.padding.all(20),
                                            bgcolor=ft.colors.with_opacity(0.03, ft.colors.BLACK),
                                            border_radius=ft.border_radius.all(8),
                                            height=380,
                                        ),
                                    ],
                                    wrap=True,
                                    spacing=30,
                                ),
                                # Divider between chart rows
                                ft.Container(
                                    content=ft.Divider(height=1, color=ft.colors.with_opacity(0.1, ft.colors.BLACK)),
                                    margin=ft.margin.only(top=20, bottom=20),
                                ),
                                # Second row with line chart
                                ft.Container(
                                    content=ChartCard("Monthly Trends", chart_type="line", height=400),
                                    margin=ft.margin.all(10),
                                    padding=ft.padding.all(10),
                                    bgcolor=ft.colors.with_opacity(0.03, ft.colors.BLACK),
                                    border_radius=ft.border_radius.all(8),
                                ),
                            ],
                            spacing=20,
                        ),
                        padding=ft.padding.only(top=20),
                    ),
                ),
                ft.Tab(
                    text="Performance",
                    content=ft.Container(
                        content=ft.Column(
                            [
                                # First row of charts with more spacing
                                ft.Row(
                                    [
                                        ft.Container(
                                            content=ChartCard("Resolution Time by Category", chart_type="bar"),
                                            margin=ft.margin.all(10),
                                            padding=ft.padding.all(20),
                                            bgcolor=ft.colors.with_opacity(0.03, ft.colors.BLACK),
                                            border_radius=ft.border_radius.all(8),
                                            height=450,
                                        ),
                                        ft.Container(
                                            content=ChartCard("Resolution Time by Technician", chart_type="bar"),
                                            margin=ft.margin.all(10),
                                            padding=ft.padding.all(20),
                                            bgcolor=ft.colors.with_opacity(0.03, ft.colors.BLACK),
                                            border_radius=ft.border_radius.all(8),
                                            height=450,
                                        ),
                                    ],
                                    wrap=True,
                                    spacing=30,
                                ),
                                # Divider between chart rows
                                ft.Container(
                                    content=ft.Divider(height=1, color=ft.colors.with_opacity(0.1, ft.colors.BLACK)),
                                    margin=ft.margin.only(top=20, bottom=20),
                                ),
                                # Second row with line chart
                                ft.Container(
                                    content=ChartCard("Resolution Time Trends", chart_type="line", height=500),
                                    margin=ft.margin.all(10),
                                    padding=ft.padding.all(10),
                                    bgcolor=ft.colors.with_opacity(0.03, ft.colors.BLACK),
                                    border_radius=ft.border_radius.all(8),
                                    height=550,
                                ),
                            ],
                            spacing=20,
                        ),
                        padding=ft.padding.only(top=20),
                    ),
                ),
                ft.Tab(
                    text="Issues",
                    content=ft.Container(
                        content=ft.Column(
                            [
                                # First row of charts with more spacing
                                ft.Row(
                                    [
                                        ft.Container(
                                            content=ChartCard("Common Issues", chart_type="bar"),
                                            margin=ft.margin.all(10),
                                            padding=ft.padding.all(20),
                                            bgcolor=ft.colors.with_opacity(0.03, ft.colors.BLACK),
                                            border_radius=ft.border_radius.all(8),
                                            height=450,
                                        ),
                                        ft.Container(
                                            content=ChartCard("Issue Categories Over Time", chart_type="line"),
                                            margin=ft.margin.all(10),
                                            padding=ft.padding.all(20),
                                            bgcolor=ft.colors.with_opacity(0.03, ft.colors.BLACK),
                                            border_radius=ft.border_radius.all(8),
                                            height=380,
                                        ),
                                    ],
                                    wrap=True,
                                    spacing=30,
                                ),
                                # Divider between chart rows
                                ft.Container(
                                    content=ft.Divider(height=1, color=ft.colors.with_opacity(0.1, ft.colors.BLACK)),
                                    margin=ft.margin.only(top=20, bottom=20),
                                ),
                                # Second row with line chart
                                ft.Container(
                                    content=ChartCard("Seasonal Patterns", chart_type="line", height=400),
                                    margin=ft.margin.all(10),
                                    padding=ft.padding.all(10),
                                    bgcolor=ft.colors.with_opacity(0.03, ft.colors.BLACK),
                                    border_radius=ft.border_radius.all(8),
                                ),
                            ],
                            spacing=20,
                        ),
                        padding=ft.padding.only(top=20),
                    ),
                ),
                ft.Tab(
                    text="Export",
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Export Reports",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.BLACK,
                                ),
                                ft.Container(height=20),
                                ft.Row(
                                    [
                                        ft.ElevatedButton(
                                            "Export to PDF",
                                            icon=ft.icons.PICTURE_AS_PDF,
                                            on_click=self.export_to_pdf,
                                            bgcolor=ft.colors.BLACK,
                                            color=ft.colors.ORANGE,
                                        ),
                                        ft.ElevatedButton(
                                            "Export to Excel",
                                            icon=ft.icons.TABLE_CHART,
                                            on_click=self.export_to_excel,
                                            bgcolor=ft.colors.BLACK,
                                            color=ft.colors.ORANGE,
                                        ),
                                        ft.ElevatedButton(
                                            "Export to CSV",
                                            icon=ft.icons.DOWNLOAD,
                                            on_click=self.export_to_csv,
                                            bgcolor=ft.colors.BLACK,
                                            color=ft.colors.ORANGE,
                                        ),
                                    ],
                                    spacing=10,
                                ),
                                ft.Container(height=20),
                                ft.Text(
                                    "Scheduled Reports",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.BLACK,
                                ),
                                ft.Container(height=20),
                                ft.Text(
                                    "Set up automated reports to be delivered to your email on a schedule.",
                                    size=16,
                                    color=ft.colors.BLACK,
                                ),
                                ft.Container(height=20),
                                ft.ElevatedButton(
                                    "Configure Scheduled Reports",
                                    icon=ft.icons.SCHEDULE,
                                    on_click=self.configure_scheduled_reports,
                                    bgcolor=ft.colors.BLACK,
                                    color=ft.colors.ORANGE,
                                ),
                            ],
                        ),
                        padding=ft.padding.only(top=20),
                    ),
                ),
            ],
            expand=1,
        )
        
        # Set up the container
        self.content = self.build_content()
        self.expand = True
        self.bgcolor = ft.colors.with_opacity(0.01, ft.colors.BLACK)
    
    def build_content(self):
        return ft.Column(
            [
                ft.Text(
                    "Reports & Analytics",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLACK,
                ),
                ft.Container(height=20),
                self.report_filters,
                ft.Container(height=20),
                self.summary_stats,
                ft.Container(height=20),
                self.tabs,
            ],
            scroll=ft.ScrollMode.AUTO,
        )
    
    def did_mount(self):
        """Called when the view is mounted in the page"""
        # The page reference is automatically set by Flet when the view is mounted
        # We don't need to do anything here, just use self.page directly
        print("ReportsView mounted")
    
    def export_to_pdf(self, e):
        """Export reports data to PDF format"""
        try:
            # Show a snackbar notification
            if hasattr(self, 'page') and self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Exporting to PDF... This feature will be fully implemented soon."),
                    action="OK",
                    bgcolor=ft.colors.BLACK,
                    action_color=ft.colors.ORANGE,
                )
                self.page.snack_bar.open = True
                self.page.update()
            else:
                print("Page reference is not available")
        except Exception as ex:
            print(f"Error exporting to PDF: {ex}")
    
    def export_to_excel(self, e):
        """Export reports data to Excel format"""
        try:
            # Show a snackbar notification
            if hasattr(self, 'page') and self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Exporting to Excel... This feature will be fully implemented soon."),
                    action="OK",
                    bgcolor=ft.colors.BLACK,
                    action_color=ft.colors.ORANGE,
                )
                self.page.snack_bar.open = True
                self.page.update()
            else:
                print("Page reference is not available")
        except Exception as ex:
            print(f"Error exporting to Excel: {ex}")
    
    def export_to_csv(self, e):
        """Export reports data to CSV format"""
        try:
            # Show a snackbar notification
            if hasattr(self, 'page') and self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Exporting to CSV... This feature will be fully implemented soon."),
                    action="OK",
                    bgcolor=ft.colors.BLACK,
                    action_color=ft.colors.ORANGE,
                )
                self.page.snack_bar.open = True
                self.page.update()
            else:
                print("Page reference is not available")
        except Exception as ex:
            print(f"Error exporting to CSV: {ex}")
    
    def configure_scheduled_reports(self, e):
        """Open the scheduled reports configuration dialog"""
        try:
            # Create a dialog for scheduled reports configuration
            if hasattr(self, 'page') and self.page:
                # Create the dialog content
                email_field = ft.TextField(
                    label="Email Address",
                    hint_text="Enter email to receive reports",
                    border_color=ft.colors.GREY,
                    focused_border_color=ft.colors.ORANGE,
                    color=ft.colors.BLACK,
                )
                
                frequency_dropdown = ft.Dropdown(
                    label="Frequency",
                    options=[
                        ft.dropdown.Option("daily", "Daily"),
                        ft.dropdown.Option("weekly", "Weekly"),
                        ft.dropdown.Option("monthly", "Monthly"),
                    ],
                    value="weekly",
                    color=ft.colors.BLACK,
                )
                
                report_type_dropdown = ft.Dropdown(
                    label="Report Type",
                    options=[
                        ft.dropdown.Option("summary", "Summary Report"),
                        ft.dropdown.Option("detailed", "Detailed Report"),
                        ft.dropdown.Option("custom", "Custom Report"),
                    ],
                    value="summary",
                    color=ft.colors.BLACK,
                )
                
                # Create the dialog
                dialog = ft.AlertDialog(
                    title=ft.Text("Configure Scheduled Reports", color=ft.colors.BLACK),
                    content=ft.Column([
                        ft.Text("Set up automated reports to be delivered to your email.", color=ft.colors.BLACK),
                        ft.Container(height=20),
                        email_field,
                        ft.Container(height=10),
                        frequency_dropdown,
                        ft.Container(height=10),
                        report_type_dropdown,
                    ], tight=True, spacing=10),
                    actions=[
                        ft.ElevatedButton(
                            "Save Configuration",
                            on_click=lambda _: self.save_report_config(email_field.value, frequency_dropdown.value, report_type_dropdown.value, dialog),
                            bgcolor=ft.colors.BLACK,
                            color=ft.colors.ORANGE,
                        ),
                        ft.ElevatedButton(
                            "Cancel",
                            on_click=lambda _: self.close_dialog(dialog),
                            bgcolor=ft.colors.with_opacity(0.1, ft.colors.BLACK),
                            color=ft.colors.BLACK,
                        ),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                
                # Show the dialog
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
        except Exception as ex:
            print(f"Error configuring scheduled reports: {ex}")
    
    def save_report_config(self, email, frequency, report_type, dialog):
        """Save the scheduled report configuration"""
        try:
            # Here you would save the configuration to the database
            # For now, just show a success message
            dialog.open = False
            self.page.update()
            
            # Show a success message
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Scheduled report configured for {email} with {frequency} frequency."),
                    action="OK",
                    bgcolor=ft.colors.BLACK,
                    action_color=ft.colors.ORANGE,
                )
                self.page.snack_bar.open = True
                self.page.update()
        except Exception as ex:
            print(f"Error saving report configuration: {ex}")
    
    def close_dialog(self, dialog):
        """Close the dialog"""
        dialog.open = False
        self.page.update()
    
    def update_reports(self, filter_data):
        """Update reports based on filter data."""
        from app.db.database import SessionLocal
        from app.db.models import LogbookEntry, StatusEnum
        from sqlalchemy import func, not_, or_
        
        print(f"Update reports with filters: {filter_data}")
        
        # Extract filter data
        start_date = datetime.strptime(filter_data.get('start_date', '2020-01-01'), '%Y-%m-%d').date()
        end_date = datetime.strptime(filter_data.get('end_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
        
        # Update summary stats with filtered data
        with SessionLocal() as session:
            # Base query with date filters and excluding deleted entries
            base_query = session.query(LogbookEntry).filter(
                LogbookEntry.created_at.between(start_date, end_date + timedelta(days=1)),
                or_(LogbookEntry.is_deleted == False, LogbookEntry.is_deleted == None)
            )
            
            # Total entries
            total_entries = base_query.count()
            
            # Completed entries for completion rate
            completed_entries = base_query.filter(LogbookEntry.status == StatusEnum.COMPLETED).count()
            
            # Escalated entries for escalation rate
            escalated_entries = base_query.filter(LogbookEntry.status == StatusEnum.ESCALATION).count()
            
            # Average resolution time (for completed entries)
            avg_resolution_query = session.query(
                func.avg(
                    func.extract('epoch', LogbookEntry.updated_at - LogbookEntry.created_at) / 3600
                )
            ).filter(
                LogbookEntry.created_at.between(start_date, end_date + timedelta(days=1)),
                LogbookEntry.status == StatusEnum.COMPLETED,
                or_(LogbookEntry.is_deleted == False, LogbookEntry.is_deleted == None)
            )
            
            avg_resolution_hours = avg_resolution_query.scalar() or 0
        
        # Update summary stats
        self.summary_stats.total_entries = str(total_entries)
        
        # Format average resolution time
        if avg_resolution_hours < 1:
            avg_resolution_formatted = f"{int(avg_resolution_hours * 60)} mins"
        else:
            avg_resolution_formatted = f"{avg_resolution_hours:.1f} hours"
        self.summary_stats.avg_resolution_time = avg_resolution_formatted
        
        # Calculate rates
        completion_rate = (completed_entries / total_entries * 100) if total_entries > 0 else 0
        escalation_rate = (escalated_entries / total_entries * 100) if total_entries > 0 else 0
        
        self.summary_stats.completion_rate = f"{int(completion_rate)}%"
        self.summary_stats.escalation_rate = f"{int(escalation_rate)}%"
        
        # Rebuild the summary stats content
        self.summary_stats.controls = [self.summary_stats.build_content()]
        
        # Update the UI
        self.update()
