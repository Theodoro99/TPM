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
        self.tooltip = None  # Will hold the active tooltip

    def get_chart_data(self):
        """Get real data from the database for this chart"""
        try:
            from app.db.database import SessionLocal
            from app.db.models import LogbookEntry, StatusEnum, Category
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
                    "colors": [ft.colors.BLUE_400, ft.colors.GREEN_400, ft.colors.AMBER_400, ft.colors.RED_400,
                               ft.colors.PURPLE_400]
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

                elif self.title == "Monthly Trends" or self.title == "Resolution Time Trends" or self.title == "Issue Categories Over Time" or self.title == "Seasonal Patterns":
                    # Get data based on actual database entries
                    # First, find the date range from the database
                    earliest_entry = session.query(func.min(LogbookEntry.created_at)).scalar()
                    latest_entry = session.query(func.max(LogbookEntry.created_at)).scalar()

                    # Use actual data range or fallback to current date if no entries
                    end_date = latest_entry if latest_entry else datetime.now()
                    # Use 6 months before end_date or earliest entry, whichever is later
                    default_start = end_date - timedelta(days=180)  # ~6 months
                    start_date = earliest_entry if earliest_entry and earliest_entry > default_start else default_start

                    print(f"Using date range: {start_date} to {end_date}")

                    # Get month names for the date range
                    months = []
                    month_dates = []
                    current = start_date

                    # Make sure we include the full month of the end date
                    end_month_date = end_date.replace(day=28)  # Use day 28 to ensure we're still in the same month
                    if end_month_date.month != end_date.month:
                        end_month_date = end_date.replace(month=end_date.month + 1, day=1) - timedelta(days=1)

                    while current <= end_month_date:
                        # Include year in the label if it spans multiple years
                        if start_date.year != end_date.year:
                            months.append(current.strftime("%b %Y"))
                        else:
                            months.append(current.strftime("%b"))

                        month_dates.append(current)

                        # Move to next month
                        if current.month == 12:
                            current = current.replace(year=current.year + 1, month=1)
                        else:
                            current = current.replace(month=current.month + 1)

                    print(f"Using months: {months}")

                    # Get counts by status and month
                    datasets = []
                    for status, color in [
                        (StatusEnum.OPEN, ft.colors.AMBER_500),
                        (StatusEnum.COMPLETED, ft.colors.GREEN_500),
                        (StatusEnum.ESCALATION, ft.colors.RED_500)
                    ]:
                        monthly_counts = []
                        # Use the month_dates list we created earlier
                        for i, month_start in enumerate(month_dates):
                            # Calculate the end of this month
                            if i < len(month_dates) - 1:
                                month_end = month_dates[i + 1]
                            else:
                                # For the last month, go to the end of the month
                                if month_start.month == 12:
                                    month_end = month_start.replace(year=month_start.year + 1, month=1)
                                else:
                                    month_end = month_start.replace(month=month_start.month + 1)

                            # Query for this month
                            count = session.query(func.count(LogbookEntry.id)).filter(
                                LogbookEntry.status == status,
                                LogbookEntry.created_at >= month_start,
                                LogbookEntry.created_at < month_end,
                                or_(LogbookEntry.is_deleted == False, LogbookEntry.is_deleted == None)
                            ).scalar() or 0

                            # We'll keep the actual count, even if it's zero
                            # The chart rendering will handle zero values appropriately

                            monthly_counts.append(count)
                            print(f"Month: {months[i]}, Status: {status.value}, Count: {count}")

                        datasets.append({
                            "name": status.value.capitalize(),
                            "values": monthly_counts,
                            "color": color
                        })

                    # Print the final dataset for debugging
                    print(f"Final datasets: {datasets}")
                    return {"labels": months, "datasets": datasets}

                elif "Resolution Time" in self.title:
                    # For resolution time charts
                    if "by Category" in self.title:
                        # Get average resolution time by category
                        # For SQLite compatibility, we need to handle datetime calculations differently
                        # First, get all completed entries with their category and resolution times
                        entries = session.query(
                            LogbookEntry,
                            Category
                        ).join(
                            Category,
                            LogbookEntry.category_id == Category.id,
                            isouter=True
                        ).filter(
                            LogbookEntry.status == StatusEnum.COMPLETED,
                            or_(LogbookEntry.is_deleted == False, LogbookEntry.is_deleted == None)
                        ).all()

                        # Process the entries to calculate resolution times
                        category_hours = {}
                        category_counts = {}

                        for entry_tuple in entries:
                            entry = entry_tuple[0]
                            category = entry_tuple[1]

                            # Use category name if available, otherwise use "Uncategorized"
                            category_name = category.name if category else "Uncategorized"

                            if category_name not in category_hours:
                                category_hours[category_name] = 0
                                category_counts[category_name] = 0

                            # Calculate hours using Python datetime objects
                            if entry.resolution_time and entry.created_at:
                                # Use resolution_time if available
                                # For entries with future resolution times, use a more meaningful calculation
                                # Extract just the time part (hours and minutes) from the resolution_time
                                resolution_hours = entry.resolution_time.hour
                                resolution_minutes = entry.resolution_time.minute

                                # Calculate total hours as a simple value (e.g., 3:30 = 3.5 hours)
                                hours = resolution_hours + (resolution_minutes / 60)
                                print(f"Using time-only calculation: {hours:.2f} hours for category {category_name}")
                            elif entry.updated_at:
                                # Fall back to updated_at time component
                                updated_hours = entry.updated_at.hour
                                updated_minutes = entry.updated_at.minute

                                # Calculate total hours as a simple value (e.g., 3:30 = 3.5 hours)
                                hours = updated_hours + (updated_minutes / 60)
                                print(
                                    f"Using updated_at time-only calculation: {hours:.2f} hours for category {category_name}")
                            else:
                                continue  # Skip entries without valid timestamps

                            category_hours[category_name] += hours
                            category_counts[category_name] += 1

                        # Calculate averages and create result tuples
                        query_result = [
                            (category_name,
                             category_hours[category_name] / category_counts[category_name] if category_counts[
                                                                                                   category_name] > 0 else 0)
                            for category_name in category_hours.keys()
                        ]

                        if query_result:
                            labels = [r[0] for r in query_result]
                            values = [float(r[1] or 0) for r in query_result]

                            # Use predefined colors for better visualization
                            predefined_colors = [
                                ft.colors.BLUE_400, ft.colors.GREEN_400, ft.colors.AMBER_400,
                                ft.colors.RED_400, ft.colors.PURPLE_400, ft.colors.CYAN_400,
                                ft.colors.DEEP_ORANGE_400, ft.colors.INDIGO_400, ft.colors.TEAL_400
                            ]
                            colors = [predefined_colors[i % len(predefined_colors)] for i, _ in enumerate(labels)]
                            return {"labels": labels, "values": values, "colors": colors}

                    elif "by Technician" in self.title:
                        # Get average resolution time by responsible person
                        # For SQLite compatibility, we need to handle datetime calculations differently
                        # First, get all completed entries with their responsible person and resolution times
                        entries = session.query(
                            LogbookEntry.responsible_person,
                            LogbookEntry.resolution_time,
                            LogbookEntry.created_at,
                            LogbookEntry.updated_at
                        ).filter(
                            LogbookEntry.status == StatusEnum.COMPLETED,
                            or_(LogbookEntry.is_deleted == False, LogbookEntry.is_deleted == None)
                        ).all()

                        # Process the entries to calculate resolution times
                        person_hours = {}
                        person_counts = {}

                        for entry in entries:
                            person = entry.responsible_person or "Unknown"
                            if person not in person_hours:
                                person_hours[person] = 0
                                person_counts[person] = 0

                            # Calculate hours using Python datetime objects
                            if entry.resolution_time and entry.created_at:
                                # Use resolution_time if available
                                # For entries with future resolution times, use a more meaningful calculation
                                # Extract just the time part (hours and minutes) from the resolution_time
                                resolution_hours = entry.resolution_time.hour
                                resolution_minutes = entry.resolution_time.minute

                                # Calculate total hours as a simple value (e.g., 3:30 = 3.5 hours)
                                hours = resolution_hours + (resolution_minutes / 60)
                                print(f"Using time-only calculation: {hours:.2f} hours for tech {person}")
                            elif entry.updated_at:
                                # Fall back to updated_at time component
                                updated_hours = entry.updated_at.hour
                                updated_minutes = entry.updated_at.minute

                                # Calculate total hours as a simple value (e.g., 3:30 = 3.5 hours)
                                hours = updated_hours + (updated_minutes / 60)
                                print(f"Using updated_at time-only calculation: {hours:.2f} hours for tech {person}")
                            else:
                                continue  # Skip entries without valid timestamps

                            print(f"Adding {hours:.2f} hours for technician {person}")
                            person_hours[person] += hours
                            person_counts[person] += 1

                        # Calculate averages and create result tuples
                        query_result = [
                            (person, person_hours[person] / person_counts[person] if person_counts[person] > 0 else 0)
                            for person in person_hours.keys()
                        ]

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
                    "colors": [ft.colors.BLUE_400, ft.colors.GREEN_400, ft.colors.AMBER_400, ft.colors.RED_400,
                               ft.colors.PURPLE_400]
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

                            # For zero values, position at the bottom but still show the point
                            if value == 0:
                                y_pos = 1.0  # Bottom of the chart
                            else:
                                y_pos = 1 - (value / max_value if max_value > 0 else 0)

                            # Create the data point with hover effect
                            data_point = ft.Container(
                                content=ft.Container(
                                    content=ft.Container(
                                        bgcolor=dataset["color"],
                                        width=10,
                                        height=10,
                                        border_radius=ft.border_radius.all(5),
                                        border=ft.border.all(1.5, ft.colors.WHITE),
                                        shadow=ft.BoxShadow(
                                            spread_radius=1,
                                            blur_radius=2,
                                            color=ft.colors.with_opacity(0.3, ft.colors.BLACK),
                                        ),
                                    ),
                                    padding=ft.padding.all(1),
                                ),
                                alignment=ft.alignment.center,
                                # Adjust positioning to ensure full width distribution
                                left=f"{x_pos * 100}%",  # Use percentage string format
                                top=f"{y_pos * 100}%",  # Use percentage string format
                                right=None,
                                bottom=None,
                                width=14,
                                height=14,
                                animate=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT),
                                # Store the data for hover tooltip
                                data={"dataset": dataset["name"], "value": value, "color": dataset["color"]},
                                # Add hover effect for better interaction
                                on_hover=self.handle_point_hover
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

                                # Handle zero values for line positioning
                                if dataset["values"][i] == 0:
                                    y1 = 1.0  # Bottom of chart
                                else:
                                    y1 = 1 - (dataset["values"][i] / max_value if max_value > 0 else 0)

                                x2 = (i + 1) / (num_points - 1) if num_points > 1 else 0.5

                                # Handle zero values for line positioning
                                if dataset["values"][i + 1] == 0:
                                    y2 = 1.0  # Bottom of chart
                                else:
                                    y2 = 1 - (dataset["values"][i + 1] / max_value if max_value > 0 else 0)

                                # Create a line segment with improved positioning
                                # Calculate the angle of the line for proper positioning
                                dx = x2 - x1
                                dy = y2 - y1
                                angle = math.atan2(dy, dx) * 180 / math.pi

                                # Create a line segment that connects the points properly with enhanced styling
                                line = ft.Container(
                                    bgcolor=dataset["color"],
                                    height=3,  # Increased line thickness for better visibility
                                    left=f"{x1 * 100}%",  # Use percentage string format
                                    top=f"{y1 * 100}%",  # Position at first point
                                    width=f"{(x2 - x1) * 100}%",  # Width as percentage of container
                                    rotate=ft.Rotate(angle, alignment=ft.alignment.center_left),
                                    opacity=0.8,  # Slight transparency for a more modern look
                                    animate=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT),
                                    shadow=ft.BoxShadow(
                                        spread_radius=0.5,
                                        blur_radius=1,
                                        color=ft.colors.with_opacity(0.2, ft.colors.BLACK),
                                    ),
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

    def handle_point_hover(self, e):
        """Handle hover events for data points in the line chart"""
        # Only process hover enter events
        if e.data == "true":  # hover enter
            # Get the data point that triggered the event
            point = e.control
            # Extract the data from the data point
            dataset_name = point.data["dataset"]
            value = point.data["value"]
            color = point.data["color"]

            # Create or update tooltip
            if self.tooltip:
                # Remove existing tooltip if it exists
                if self.tooltip in self.page.overlay:
                    self.page.overlay.remove(self.tooltip)

            # Create new tooltip
            self.tooltip = ft.Tooltip(
                message=f"{dataset_name}: {value}",
                bgcolor=ft.colors.with_opacity(0.9, ft.colors.BLACK),
                text_style=ft.TextStyle(
                    color=ft.colors.WHITE,
                    size=14,
                    weight=ft.FontWeight.BOLD
                ),
                border_radius=ft.border_radius.all(5),
                padding=ft.padding.all(8),
                visible=True,
            )

            # Position tooltip near the data point
            # Add the tooltip to the page overlay
            if self.page and self.tooltip not in self.page.overlay:
                self.page.overlay.append(self.tooltip)
                self.page.update()

            # Highlight the data point
            point.content.border = ft.border.all(2, color)
            point.width = 18
            point.height = 18
            point.update()
        else:  # hover exit
            # Reset the data point size
            point = e.control
            point.content.border = None
            point.width = 14
            point.height = 14
            point.update()

            # Hide tooltip
            if self.tooltip and self.page and self.tooltip in self.page.overlay:
                self.page.overlay.remove(self.tooltip)
                self.page.update()

    def create_placeholder(self, message="No data available"):
        """Create a placeholder when chart data is not available"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        name=ft.icons.BAR_CHART_OUTLINED,
                        size=50,
                        color=ft.colors.BLUE_GREY_400,
                    ),
                    ft.Text(
                        message,
                        size=16,
                        color=ft.colors.BLUE_GREY_400,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            alignment=ft.alignment.center,
            expand=True,
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
        self.avg_resolution_open = "0 hours"
        self.avg_resolution_ongoing = "0 hours"
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
                # For SQLite compatibility, we need to handle datetime calculations in Python
                completed_entries_data = session.query(
                    LogbookEntry.resolution_time,
                    LogbookEntry.created_at,
                    LogbookEntry.updated_at
                ).filter(
                    LogbookEntry.status == StatusEnum.COMPLETED,
                    or_(LogbookEntry.is_deleted == False, LogbookEntry.is_deleted == None)
                ).all()

                # Calculate average resolution time using Python datetime objects
                total_hours = 0
                entry_count = 0

                for entry in completed_entries_data:
                    # Calculate hours using Python datetime objects
                    if entry.resolution_time:
                        # Use resolution_time if available
                        # For entries with future resolution times, use a more meaningful calculation
                        # Extract just the time part (hours and minutes) from the resolution_time
                        resolution_hours = entry.resolution_time.hour
                        resolution_minutes = entry.resolution_time.minute

                        # Calculate total hours as a simple value (e.g., 3:30 = 3.5 hours)
                        hours = resolution_hours + (resolution_minutes / 60)
                        total_hours += hours
                        entry_count += 1
                        print(f"Using time-only calculation: {hours:.2f} hours for summary stats")

                avg_resolution_hours = total_hours / entry_count if entry_count > 0 else 0

                # Average resolution time for OPEN entries
                open_entries_data = session.query(
                    LogbookEntry.resolution_time,
                    LogbookEntry.created_at,
                    LogbookEntry.updated_at
                ).filter(
                    LogbookEntry.status == StatusEnum.OPEN,
                    or_(LogbookEntry.is_deleted == False, LogbookEntry.is_deleted == None)
                ).all()

                # Calculate average resolution time for OPEN entries
                total_open_hours = 0
                open_entry_count = 0

                for entry in open_entries_data:
                    if entry.resolution_time:
                        resolution_hours = entry.resolution_time.hour
                        resolution_minutes = entry.resolution_time.minute
                        hours = resolution_hours + (resolution_minutes / 60)
                        total_open_hours += hours
                        open_entry_count += 1
                        print(f"Open entry resolution time: {hours:.2f} hours")

                avg_resolution_open_hours = total_open_hours / open_entry_count if open_entry_count > 0 else 0

                # Average resolution time for ONGOING entries
                ongoing_entries_data = session.query(
                    LogbookEntry.resolution_time,
                    LogbookEntry.created_at,
                    LogbookEntry.updated_at
                ).filter(
                    LogbookEntry.status == StatusEnum.ONGOING,
                    or_(LogbookEntry.is_deleted == False, LogbookEntry.is_deleted == None)
                ).all()

                # Calculate average resolution time for ONGOING entries
                total_ongoing_hours = 0
                ongoing_entry_count = 0

                for entry in ongoing_entries_data:
                    if entry.resolution_time:
                        resolution_hours = entry.resolution_time.hour
                        resolution_minutes = entry.resolution_time.minute
                        hours = resolution_hours + (resolution_minutes / 60)
                        total_ongoing_hours += hours
                        ongoing_entry_count += 1
                        print(f"Ongoing entry resolution time: {hours:.2f} hours")

                avg_resolution_ongoing_hours = total_ongoing_hours / ongoing_entry_count if ongoing_entry_count > 0 else 0

            # Update values
            self.total_entries = str(total_entries)

            # Format average resolution time for completed entries
            if avg_resolution_hours < 1:
                avg_resolution_formatted = f"{int(avg_resolution_hours * 60)} mins"
            else:
                avg_resolution_formatted = f"{avg_resolution_hours:.1f} hours"
            self.avg_resolution_time = avg_resolution_formatted

            # Format average resolution time for open entries
            if avg_resolution_open_hours < 1:
                avg_resolution_open_formatted = f"{int(avg_resolution_open_hours * 60)} mins"
            else:
                avg_resolution_open_formatted = f"{avg_resolution_open_hours:.1f} hours"
            self.avg_resolution_open = avg_resolution_open_formatted

            # Format average resolution time for ongoing entries
            if avg_resolution_ongoing_hours < 1:
                avg_resolution_ongoing_formatted = f"{int(avg_resolution_ongoing_hours * 60)} mins"
            else:
                avg_resolution_ongoing_formatted = f"{avg_resolution_ongoing_hours:.1f} hours"
            self.avg_resolution_ongoing = avg_resolution_ongoing_formatted

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
        # Optimize card dimensions for better fit
        card_width = 170
        card_height = 110
        padding_size = 12
        title_size = 13
        value_size = 18

        # Create a function to generate a stat card with consistent styling
        def create_stat_card(title, value, color):
            return ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                title,
                                size=title_size,
                                color=ft.colors.BLUE_GREY_700,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=5),
                            ft.Text(
                                value,
                                size=value_size,
                                weight=ft.FontWeight.BOLD,
                                color=color,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.all(padding_size),
                    width=card_width,
                    height=card_height,
                ),
                elevation=2,
            )

        # Create all stat cards
        total_entries_card = create_stat_card("Total Entries", self.total_entries, ft.colors.BLUE_700)
        avg_resolution_card = create_stat_card("Avg. Resolution Time", self.avg_resolution_time, ft.colors.ORANGE_700)
        avg_open_card = create_stat_card("Avg. Open Resolution", self.avg_resolution_open, ft.colors.AMBER_700)
        avg_ongoing_card = create_stat_card("Avg. Ongoing Resolution", self.avg_resolution_ongoing,
                                            ft.colors.PURPLE_700)
        completion_rate_card = create_stat_card("Completion Rate", self.completion_rate, ft.colors.GREEN_700)
        escalation_rate_card = create_stat_card("Escalation Rate", self.escalation_rate, ft.colors.RED_700)

        # Organize cards into two rows for better layout
        row1 = ft.Row(
            [total_entries_card, avg_resolution_card, completion_rate_card],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )

        row2 = ft.Row(
            [avg_open_card, avg_ongoing_card, escalation_rate_card],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )

        # Return a column containing both rows
        return ft.Column(
            [row1, ft.Container(height=10), row2],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )


class ReportsView(ft.Container):
    def __init__(self):
        super().__init__()

        # Initialize components
        self.report_filters = ReportFilters(on_apply=self.update_reports)
        self.summary_stats = SummaryStats()

        # Initialize file pickers for exports
        self.pdf_picker = ft.FilePicker(on_result=self.save_pdf_result)
        self.excel_picker = ft.FilePicker(on_result=self.save_excel_result)
        self.csv_picker = ft.FilePicker(on_result=self.save_csv_result)

        # Create chart instances and store references to them
        self.chart_issues_by_category = ChartCard("Issues by Category", chart_type="pie")
        self.chart_issues_by_location = ChartCard("Issues by Location", chart_type="pie")
        self.chart_monthly_trends = ChartCard("Monthly Trends", chart_type="line", height=400)
        self.chart_resolution_by_category = ChartCard("Resolution Time by Category", chart_type="bar")
        self.chart_resolution_by_technician = ChartCard("Resolution Time by Technician", chart_type="bar")

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
                                            content=self.chart_issues_by_category,
                                            margin=ft.margin.all(10),
                                            padding=ft.padding.all(20),
                                            bgcolor=ft.colors.with_opacity(0.03, ft.colors.BLACK),
                                            border_radius=ft.border_radius.all(8),
                                            height=380,
                                        ),
                                        ft.Container(
                                            content=self.chart_issues_by_location,
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
                                    content=self.chart_monthly_trends,
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
                                            content=self.chart_resolution_by_category,
                                            margin=ft.margin.all(10),
                                            padding=ft.padding.all(20),
                                            bgcolor=ft.colors.with_opacity(0.03, ft.colors.BLACK),
                                            border_radius=ft.border_radius.all(8),
                                            height=450,
                                        ),
                                        ft.Container(
                                            content=self.chart_resolution_by_technician,
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
                                            width=180,
                                            height=45,
                                        ),
                                        ft.ElevatedButton(
                                            "Export to Excel",
                                            icon=ft.icons.TABLE_CHART,
                                            on_click=self.export_to_excel,
                                            bgcolor=ft.colors.BLACK,
                                            color=ft.colors.ORANGE,
                                            width=180,
                                            height=45,
                                        ),
                                        ft.ElevatedButton(
                                            "Export to CSV",
                                            icon=ft.icons.DOWNLOAD,
                                            on_click=self.export_to_csv,
                                            bgcolor=ft.colors.BLACK,
                                            color=ft.colors.ORANGE,
                                            width=180,
                                            height=45,
                                        ),
                                    ],
                                    spacing=20,
                                    alignment=ft.MainAxisAlignment.CENTER,
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
        print(f"ReportsView mounted, page reference: {self.page}")

        # Add file pickers to page overlay
        if self.page and not hasattr(self, "_pickers_added"):
            self.page.overlay.extend([self.pdf_picker, self.excel_picker, self.csv_picker])
            self._pickers_added = True
            print("File pickers added to page overlay")

        # Rebuild the export buttons to ensure they have the correct page reference
        self.rebuild_export_tab()

    def rebuild_export_tab(self):
        """Rebuild the export tab with new buttons to ensure they have the correct page reference"""
        try:
            # Find the Export tab
            for i, tab in enumerate(self.tabs.tabs):
                if tab.text == "Export":
                    # Create new export buttons
                    export_tab_content = ft.Container(
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
                                            on_click=self.export_to_pdf_direct,
                                            bgcolor=ft.colors.BLACK,
                                            color=ft.colors.ORANGE,
                                            width=180,
                                            height=45,
                                        ),
                                        ft.ElevatedButton(
                                            "Export to Excel",
                                            icon=ft.icons.TABLE_CHART,
                                            on_click=self.export_to_excel_direct,
                                            bgcolor=ft.colors.BLACK,
                                            color=ft.colors.ORANGE,
                                            width=180,
                                            height=45,
                                        ),
                                        ft.ElevatedButton(
                                            "Export to CSV",
                                            icon=ft.icons.DOWNLOAD,
                                            on_click=self.export_to_csv_direct,
                                            bgcolor=ft.colors.BLACK,
                                            color=ft.colors.ORANGE,
                                            width=180,
                                            height=45,
                                        ),
                                    ],
                                    spacing=20,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                                # Rest of the tab content remains the same
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
                    )

                    # Replace the tab content
                    self.tabs.tabs[i].content = export_tab_content

                    # Update the UI
                    if self.page:
                        self.page.update()
                    break

            print("Export tab rebuilt with new buttons")
        except Exception as ex:
            print(f"Error rebuilding export tab: {ex}")

    def save_pdf_result(self, e: ft.FilePickerResultEvent):
        """Handle the result of the PDF file picker dialog"""
        try:
            if e.path:
                print(f"PDF file path selected: {e.path}")
                # Generate and save the PDF file
                self.generate_pdf_report(e.path)

                # Show success message
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"PDF report saved to: {e.path}"),
                        action="OK",
                        bgcolor=ft.colors.BLACK,
                        action_color=ft.colors.ORANGE,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            else:
                print("PDF export cancelled")
        except Exception as ex:
            print(f"Error in PDF file picker result: {ex}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error saving PDF: {ex}"),
                    action="OK",
                    bgcolor=ft.colors.RED_500,
                    action_color=ft.colors.WHITE,
                )
                self.page.snack_bar.open = True
                self.page.update()

    def generate_pdf_report(self, file_path):
        """Generate a PDF report and save it to the specified path"""
        try:
            # Import required libraries for PDF generation
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from app.db.database import SessionLocal
            from app.db.models import LogbookEntry
            from datetime import datetime

            # Create a PDF document
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []

            # Add title
            title_style = styles['Heading1']
            title = Paragraph("LogBook Report", title_style)
            elements.append(title)
            elements.append(Spacer(1, 12))

            # Add date
            date_style = styles['Normal']
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            date_text = Paragraph(f"Generated on: {current_date}", date_style)
            elements.append(date_text)
            elements.append(Spacer(1, 12))

            # Get data from database
            with SessionLocal() as session:
                entries = session.query(LogbookEntry).filter(
                    LogbookEntry.is_deleted.is_(False)
                ).all()

                # Create table data
                data = [
                    ["ID", "Task", "Call Description", "Solution", "Status", "Location", "Created At"]
                ]

                for entry in entries:
                    data.append([
                        str(entry.id),
                        entry.task or "",
                        entry.call_description or "",
                        entry.solution_description or "",
                        entry.status.value if entry.status else "",
                        entry.device or "",
                        entry.created_at.strftime("%Y-%m-%d") if entry.created_at else ""
                    ])

                # Process data to truncate long text and ensure text fits in cells
                processed_data = [data[0]]  # Keep the header row
                for row in data[1:]:
                    processed_row = []

                    # Process each cell in the row
                    for i, cell in enumerate(row):
                        # Column-specific processing
                        if i == 0:  # ID column
                            # Truncate ID to first 8 characters + '...' if too long
                            if len(cell) > 10:
                                processed_row.append(cell[:8] + '...')
                            else:
                                processed_row.append(cell)
                        elif i == 2 or i == 3:  # Call Description and Solution columns
                            # Truncate long text to 30 characters + '...' if too long
                            if len(cell) > 30:
                                processed_row.append(cell[:30] + '...')
                            else:
                                processed_row.append(cell)
                        else:  # Other columns
                            processed_row.append(cell)

                    processed_data.append(processed_row)

                # Set up the page size and margins
                page_width = letter[0]  # Width of letter page in points
                margin = 40  # Margin in points
                usable_width = page_width - (2 * margin)  # Usable width for the table

                # Calculate proportional column widths that fit within the page
                # Allocate more space to text columns (Call Description and Solution)
                proportions = [0.12, 0.12, 0.20, 0.20, 0.12, 0.12, 0.12]  # Must sum to 1.0
                col_widths = [usable_width * p for p in proportions]

                # Create table with calculated column widths
                table = Table(processed_data, colWidths=col_widths, repeatRows=1)

                # Apply styles to ensure text stays within cells
                table.setStyle(TableStyle([
                    # Basic styling
                    ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

                    # Font sizes - make them smaller to fit more text
                    ('FONTSIZE', (0, 0), (-1, 0), 8),  # Headers
                    ('FONTSIZE', (0, 1), (-1, -1), 6),  # Data rows

                    # Cell padding - minimize to maximize text space
                    ('TOPPADDING', (0, 0), (-1, -1), 1),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),  # Header bottom padding
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 1),  # Data rows bottom padding
                    ('LEFTPADDING', (0, 0), (-1, -1), 2),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2),

                    # Background and borders
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),

                    # Critical for text containment
                    ('WORDWRAP', (0, 0), (-1, -1), True),
                    ('SHRINK', (0, 0), (-1, -1), 1.0),  # Allow text to shrink if needed
                ]))

                # Set a reasonable row height to accommodate wrapped text
                for i in range(len(processed_data)):
                    if i == 0:  # Header row
                        table._rowHeights[i] = 20
                    else:  # Data rows
                        table._rowHeights[i] = 30  # Fixed height for all data rows

                elements.append(table)

                # Add summary statistics
                elements.append(Spacer(1, 20))
                summary_style = styles['Heading2']
                summary_title = Paragraph("Summary Statistics", summary_style)
                elements.append(summary_title)
                elements.append(Spacer(1, 12))

                # Count by status
                status_counts = {}
                for entry in entries:
                    status = entry.status.value if entry.status else "Unknown"
                    status_counts[status] = status_counts.get(status, 0) + 1

                # Create status summary table
                status_data = [["Status", "Count"]]
                for status, count in status_counts.items():
                    status_data.append([status, str(count)])

                # Use fixed column widths for summary table
                summary_col_widths = [100, 60]  # Status column wider than Count column
                status_table = Table(status_data, colWidths=summary_col_widths)
                status_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),  # Slightly larger font for summary headers
                    ('FONTSIZE', (0, 1), (-1, -1), 9),  # Normal font for summary data
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))

                elements.append(status_table)

            # Build the PDF document
            doc.build(elements)
            print(f"PDF report successfully generated at {file_path}")

        except ImportError as ie:
            print(f"Missing required library for PDF generation: {ie}")
            # Install reportlab if not available
            import subprocess
            subprocess.run(["pip", "install", "reportlab"])
            # Try again after installation
            self.generate_pdf_report(file_path)
        except Exception as ex:
            print(f"Error generating PDF report: {ex}")
            raise

    def save_excel_result(self, e: ft.FilePickerResultEvent):
        """Handle the result of the Excel file picker dialog"""
        try:
            if e.path:
                print(f"Excel file path selected: {e.path}")
                # Generate and save the Excel file
                self.generate_excel_report(e.path)

                # Show success message
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Excel report saved to: {e.path}"),
                        action="OK",
                        bgcolor=ft.colors.BLACK,
                        action_color=ft.colors.ORANGE,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            else:
                print("Excel export cancelled")
        except Exception as ex:
            print(f"Error in Excel file picker result: {ex}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error saving Excel: {ex}"),
                    action="OK",
                    bgcolor=ft.colors.RED_500,
                    action_color=ft.colors.WHITE,
                )
                self.page.snack_bar.open = True
                self.page.update()

    def generate_excel_report(self, file_path):
        """Generate an Excel report and save it to the specified path"""
        try:
            # Import required libraries for Excel generation
            import pandas as pd
            from app.db.database import SessionLocal
            from app.db.models import LogbookEntry
            from datetime import datetime

            # Get data from database
            with SessionLocal() as session:
                entries = session.query(LogbookEntry).filter(
                    LogbookEntry.is_deleted.is_(False)
                ).all()

                # Create dataframe
                data = []
                for entry in entries:
                    data.append({
                        "ID": entry.id,
                        "Task": entry.task or "",
                        "Call Description": entry.call_description or "",
                        "Solution": entry.solution_description or "",
                        "Status": entry.status.value if entry.status else "",
                        "Location": entry.device or "",
                        "Created At": entry.created_at.strftime("%Y-%m-%d") if entry.created_at else ""
                    })

                df = pd.DataFrame(data)

                # Create Excel writer
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    # Write main data sheet
                    df.to_excel(writer, sheet_name='Logbook Entries', index=False)

                    # Create summary sheet
                    if not df.empty:
                        # Count by status
                        status_counts = df['Status'].value_counts().reset_index()
                        status_counts.columns = ['Status', 'Count']

                        # Write summary sheet
                        status_counts.to_excel(writer, sheet_name='Summary', index=False)

                        # Get workbook and summary worksheet
                        workbook = writer.book
                        summary_sheet = workbook['Summary']

                        # Add title to summary sheet
                        summary_sheet['A1'].font = workbook.create_font(size=14, bold=True)
                        summary_sheet.merge_cells('A1:B1')
                        summary_sheet['A1'] = 'Status Summary'

                        # Add headers in row 2
                        summary_sheet['A2'] = 'Status'
                        summary_sheet['B2'] = 'Count'

                        # Style headers
                        for cell in summary_sheet[2]:
                            cell.font = workbook.create_font(bold=True)

                        # Adjust column widths
                        for column in summary_sheet.columns:
                            max_length = 0
                            column_letter = column[0].column_letter
                            for cell in column:
                                if cell.value:
                                    max_length = max(max_length, len(str(cell.value)))
                            adjusted_width = (max_length + 2)
                            summary_sheet.column_dimensions[column_letter].width = adjusted_width

            print(f"Excel report successfully generated at {file_path}")

        except ImportError as ie:
            print(f"Missing required library for Excel generation: {ie}")
            # Install required libraries if not available
            import subprocess
            subprocess.run(["pip", "install", "pandas", "openpyxl"])
            # Try again after installation
            self.generate_excel_report(file_path)
        except Exception as ex:
            print(f"Error generating Excel report: {ex}")
            raise

    def save_csv_result(self, e: ft.FilePickerResultEvent):
        """Handle the result of the CSV file picker dialog"""
        try:
            if e.path:
                print(f"CSV file path selected: {e.path}")
                # Generate and save the CSV file
                self.generate_csv_report(e.path)

                # Show success message
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"CSV report saved to: {e.path}"),
                        action="OK",
                        bgcolor=ft.colors.BLACK,
                        action_color=ft.colors.ORANGE,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            else:
                print("CSV export cancelled")
        except Exception as ex:
            print(f"Error in CSV file picker result: {ex}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error saving CSV: {ex}"),
                    action="OK",
                    bgcolor=ft.colors.RED_500,
                    action_color=ft.colors.WHITE,
                )
                self.page.snack_bar.open = True
                self.page.update()

    def generate_csv_report(self, file_path):
        """Generate a CSV report and save it to the specified path"""
        try:
            # Import required libraries for CSV generation
            import csv
            from app.db.database import SessionLocal
            from app.db.models import LogbookEntry

            # Get data from database
            with SessionLocal() as session:
                entries = session.query(LogbookEntry).filter(
                    LogbookEntry.is_deleted.is_(False)
                ).all()

                # Write to CSV file
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    # Define CSV writer and headers
                    fieldnames = ['ID', 'Task', 'Call Description', 'Solution', 'Status', 'Location', 'Created At']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    # Write header
                    writer.writeheader()

                    # Write data rows
                    for entry in entries:
                        writer.writerow({
                            'ID': entry.id,
                            'Task': entry.task or "",
                            'Call Description': entry.call_description or "",
                            'Solution': entry.solution_description or "",
                            'Status': entry.status.value if entry.status else "",
                            'Location': entry.device or "",
                            'Created At': entry.created_at.strftime("%Y-%m-%d") if entry.created_at else ""
                        })

            print(f"CSV report successfully generated at {file_path}")

        except Exception as ex:
            print(f"Error generating CSV report: {ex}")
            raise

    def export_to_pdf_direct(self, e):
        """Direct export to PDF handler that doesn't use optional parameters"""
        print(f"PDF export clicked, event: {e}, page: {self.page}")
        try:
            # Open the save file dialog
            if self.page:
                self.pdf_picker.save_file(
                    dialog_title="Save PDF Report",
                    file_name="logbook_report.pdf",
                    allowed_extensions=["pdf"],
                )
            else:
                print("Page reference is not available for PDF export")
        except Exception as ex:
            print(f"Error exporting to PDF: {ex}")

    def export_to_pdf(self, e=None):
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

    def export_to_excel_direct(self, e):
        """Direct export to Excel handler that doesn't use optional parameters"""
        print(f"Excel export clicked, event: {e}, page: {self.page}")
        try:
            # Open the save file dialog
            if self.page:
                self.excel_picker.save_file(
                    dialog_title="Save Excel Report",
                    file_name="logbook_report.xlsx",
                    allowed_extensions=["xlsx"],
                )
            else:
                print("Page reference is not available for Excel export")
        except Exception as ex:
            print(f"Error exporting to Excel: {ex}")

    def export_to_excel(self, e=None):
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

    def export_to_csv_direct(self, e):
        """Direct export to CSV handler that doesn't use optional parameters"""
        print(f"CSV export clicked, event: {e}, page: {self.page}")
        try:
            # Open the save file dialog
            if self.page:
                self.csv_picker.save_file(
                    dialog_title="Save CSV Report",
                    file_name="logbook_report.csv",
                    allowed_extensions=["csv"],
                )
            else:
                print("Page reference is not available for CSV export")
        except Exception as ex:
            print(f"Error exporting to CSV: {ex}")

    def export_to_csv(self, e=None):
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
            print("Configure scheduled reports button clicked")
            # Create a dialog for scheduled reports configuration
            if not hasattr(self, 'page') or not self.page:
                print("Error: Page reference not available")
                return

            # Create a custom dialog using Container and Card instead of AlertDialog
            # This approach works better in some Flet views

            # Create the dialog content
            email_field = ft.TextField(
                label="Email Address",
                hint_text="Enter email to receive reports",
                hint_style=ft.TextStyle(color=ft.colors.with_opacity(0.7, ft.colors.WHITE)),
                border_color=ft.colors.WHITE,
                focused_border_color=ft.colors.ORANGE,
                color=ft.colors.WHITE,
                label_style=ft.TextStyle(color=ft.colors.WHITE),
                bgcolor=ft.colors.with_opacity(0.3, ft.colors.BLACK),
                width=400,
            )

            # Create custom dropdown-like controls for better visibility
            # For frequency selection
            self.frequency_value = "weekly"
            frequency_label = ft.Text("Frequency", color=ft.colors.WHITE, size=14)

            # Create a container to show the selected value
            frequency_display = ft.Container(
                content=ft.Row(
                    [
                        ft.Text("Weekly", color=ft.colors.WHITE, size=16),
                        ft.Icon(ft.icons.ARROW_DROP_DOWN, color=ft.colors.WHITE),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                width=400,
                height=50,
                border=ft.border.all(1, ft.colors.WHITE),
                border_radius=5,
                padding=10,
                bgcolor=ft.colors.with_opacity(0.3, ft.colors.BLACK),
                on_click=lambda _: self.toggle_frequency_menu(),
            )

            # Create the frequency options
            frequency_options = ft.Column(
                [
                    ft.Container(
                        content=ft.Text("Daily", color=ft.colors.BLACK),
                        padding=10,
                        bgcolor=ft.colors.WHITE,
                        on_click=lambda _: self.select_frequency("daily", "Daily"),
                        width=400,
                    ),
                    ft.Container(
                        content=ft.Text("Weekly", color=ft.colors.BLACK),
                        padding=10,
                        bgcolor=ft.colors.WHITE,
                        on_click=lambda _: self.select_frequency("weekly", "Weekly"),
                        width=400,
                    ),
                    ft.Container(
                        content=ft.Text("Monthly", color=ft.colors.BLACK),
                        padding=10,
                        bgcolor=ft.colors.WHITE,
                        on_click=lambda _: self.select_frequency("monthly", "Monthly"),
                        width=400,
                    ),
                ],
                visible=False,  # Initially hidden
            )

            # Combine into a frequency selector
            frequency_selector = ft.Column(
                [
                    frequency_label,
                    frequency_display,
                    frequency_options,
                ],
                spacing=5,
            )

            # For report type selection
            self.report_type_value = "summary"
            report_type_label = ft.Text("Report Type", color=ft.colors.WHITE, size=14)

            # Create a container to show the selected value
            report_type_display = ft.Container(
                content=ft.Row(
                    [
                        ft.Text("Summary Report", color=ft.colors.WHITE, size=16),
                        ft.Icon(ft.icons.ARROW_DROP_DOWN, color=ft.colors.WHITE),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                width=400,
                height=50,
                border=ft.border.all(1, ft.colors.WHITE),
                border_radius=5,
                padding=10,
                bgcolor=ft.colors.with_opacity(0.3, ft.colors.BLACK),
                on_click=lambda _: self.toggle_report_type_menu(),
            )

            # Create the report type options
            report_type_options = ft.Column(
                [
                    ft.Container(
                        content=ft.Text("Summary Report", color=ft.colors.BLACK),
                        padding=10,
                        bgcolor=ft.colors.WHITE,
                        on_click=lambda _: self.select_report_type("summary", "Summary Report"),
                        width=400,
                    ),
                    ft.Container(
                        content=ft.Text("Detailed Report", color=ft.colors.BLACK),
                        padding=10,
                        bgcolor=ft.colors.WHITE,
                        on_click=lambda _: self.select_report_type("detailed", "Detailed Report"),
                        width=400,
                    ),
                    ft.Container(
                        content=ft.Text("Custom Report", color=ft.colors.BLACK),
                        padding=10,
                        bgcolor=ft.colors.WHITE,
                        on_click=lambda _: self.select_report_type("custom", "Custom Report"),
                        width=400,
                    ),
                ],
                visible=False,  # Initially hidden
            )

            # Combine into a report type selector
            report_type_selector = ft.Column(
                [
                    report_type_label,
                    report_type_display,
                    report_type_options,
                ],
                spacing=5,
            )

            # Store references to the components for later use
            self.frequency_display = frequency_display
            self.frequency_options = frequency_options
            self.report_type_display = report_type_display
            self.report_type_options = report_type_options

            # Create a reference to store the dialog container
            self.dialog_ref = ft.Ref[ft.Container]()

            # Create the dialog content
            dialog_content = ft.Card(
                color=ft.colors.with_opacity(0.9, ft.colors.BLACK),
                content=ft.Container(
                    content=ft.Column([
                        ft.Row(
                            [ft.Text("Configure Scheduled Reports", size=20, weight=ft.FontWeight.BOLD,
                                     color=ft.colors.WHITE)],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Divider(),
                        ft.Text("Set up automated reports to be delivered to your email.", color=ft.colors.WHITE),
                        ft.Container(height=20),
                        email_field,
                        ft.Container(height=10),
                        frequency_selector,
                        ft.Container(height=10),
                        report_type_selector,
                        ft.Container(height=20),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Save Configuration",
                                    on_click=lambda _: self.save_report_config(email_field.value, self.frequency_value,
                                                                               self.report_type_value,
                                                                               self.dialog_ref.current),
                                    bgcolor=ft.colors.BLACK,
                                    color=ft.colors.ORANGE,
                                ),
                                ft.ElevatedButton(
                                    "Cancel",
                                    on_click=lambda _: self.close_custom_dialog(self.dialog_ref.current),
                                    bgcolor=ft.colors.ORANGE,
                                    color=ft.colors.WHITE,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=10,
                        ),
                    ], tight=True, spacing=10),
                    padding=20,
                    width=500,
                ),
                elevation=10,
            )

            # Create the modal overlay
            dialog_container = ft.Container(
                ref=self.dialog_ref,
                content=ft.Stack([
                    # Semi-transparent background
                    ft.Container(
                        bgcolor=ft.colors.with_opacity(0.5, ft.colors.BLACK),
                        width=float('inf'),
                        height=float('inf'),
                        on_click=lambda _: self.close_custom_dialog(self.dialog_ref.current),
                    ),
                    # Center the dialog
                    ft.Container(
                        content=dialog_content,
                        alignment=ft.alignment.center,
                    )
                ]),
                width=float('inf'),
                height=float('inf'),
                bgcolor=ft.colors.TRANSPARENT,
            )

            # Add the dialog to the page
            self.page.overlay.append(dialog_container)
            self.page.update()
            print("Custom dialog opened successfully")

        except Exception as ex:
            print(f"Error configuring scheduled reports: {ex}")
            # Show error in snackbar if possible
            if hasattr(self, 'page') and self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error opening scheduled reports dialog: {ex}"),
                    bgcolor=ft.colors.RED_500,
                )
                self.page.snack_bar.open = True
                self.page.update()

    def save_report_config(self, email, frequency, report_type, dialog_container):
        """Save the scheduled report configuration"""
        try:
            # Validate email input
            if not email or '@' not in email or '.' not in email:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Please enter a valid email address."),
                        bgcolor=ft.colors.RED_500,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                return

            # Here you would save the configuration to the database
            # For now, just show a success message

            # Close the custom dialog
            self.close_custom_dialog(dialog_container)

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
                print(f"Report configuration saved for {email}")
        except Exception as ex:
            print(f"Error saving report configuration: {ex}")

    def close_dialog(self, dialog):
        """Close the dialog"""
        dialog.open = False
        self.page.update()

    def toggle_frequency_menu(self):
        """Toggle the visibility of the frequency dropdown menu"""
        self.frequency_options.visible = not self.frequency_options.visible
        # Hide the other dropdown menu
        self.report_type_options.visible = False
        self.page.update()

    def select_frequency(self, value, display_text):
        """Select a frequency option"""
        self.frequency_value = value
        self.frequency_display.content.controls[0].value = display_text
        self.frequency_options.visible = False
        self.page.update()

    def toggle_report_type_menu(self):
        """Toggle the visibility of the report type dropdown menu"""
        self.report_type_options.visible = not self.report_type_options.visible
        # Hide the other dropdown menu
        self.frequency_options.visible = False
        self.page.update()

    def select_report_type(self, value, display_text):
        """Select a report type option"""
        self.report_type_value = value
        self.report_type_display.content.controls[0].value = display_text
        self.report_type_options.visible = False
        self.page.update()

    def close_custom_dialog(self, dialog_container):
        """Close the custom dialog by removing it from the page overlay"""
        try:
            if dialog_container in self.page.overlay:
                self.page.overlay.remove(dialog_container)
                self.page.update()
                print("Custom dialog closed successfully")
        except Exception as ex:
            print(f"Error closing custom dialog: {ex}")

    def refresh_charts(self, filter_data):
        """Refresh all charts with new data based on the filter data"""
        # Create new chart instances with fresh data
        self.chart_issues_by_category = ChartCard("Issues by Category", chart_type="pie")
        self.chart_issues_by_location = ChartCard("Issues by Location", chart_type="pie")
        self.chart_monthly_trends = ChartCard("Monthly Trends", chart_type="line", height=400)
        self.chart_resolution_by_category = ChartCard("Resolution Time by Category", chart_type="bar")
        self.chart_resolution_by_technician = ChartCard("Resolution Time by Technician", chart_type="bar")

        # Update the UI components with the new chart instances
        # Overview tab
        overview_tab = self.tabs.tabs[0].content.content.controls
        overview_tab[0].controls[0].content = self.chart_issues_by_category
        overview_tab[0].controls[1].content = self.chart_issues_by_location
        overview_tab[2].content = self.chart_monthly_trends

        # Performance tab
        performance_tab = self.tabs.tabs[1].content.content.controls
        performance_tab[0].controls[0].content = self.chart_resolution_by_category
        performance_tab[0].controls[1].content = self.chart_resolution_by_technician

        print("Charts refreshed with new data")

    def update_reports(self, filter_data):
        """Update reports based on filter data."""
        from app.db.database import SessionLocal
        from app.db.models import LogbookEntry, StatusEnum, Category
        from sqlalchemy import not_, or_

        print(f"Update reports with filters: {filter_data}")

        # Extract filter data
        start_date = datetime.strptime(filter_data.get('start_date', '2020-01-01'), '%Y-%m-%d').date()
        end_date = datetime.strptime(filter_data.get('end_date', datetime.now().strftime('%Y-%m-%d')),
                                     '%Y-%m-%d').date()

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

            # Get entries with resolution_time field
            entries = session.query(LogbookEntry).filter(
                LogbookEntry.created_at.between(start_date, end_date + timedelta(days=1)),
                LogbookEntry.status == StatusEnum.COMPLETED,
                LogbookEntry.resolution_time is not None,  # Only entries with resolution_time
                or_(not LogbookEntry.is_deleted, LogbookEntry.is_deleted is None)
            ).all()

            # Calculate average resolution time
            total_hours = 0
            entry_count = 0

            for entry in entries:
                if entry.resolution_time and entry.created_at:
                    # Calculate the difference in hours between created_at and resolution_time
                    time_diff = (entry.resolution_time - entry.created_at).total_seconds() / 3600

                    # Only count reasonable resolution times (less than 48 hours)
                    # This prevents outliers from skewing the average
                    if 0 <= time_diff <= 48:
                        total_hours += time_diff
                        entry_count += 1
                        print(f"Entry {entry.id}: Resolution time: {time_diff:.2f} hours")

            # Calculate average in hours
            avg_resolution_hours = total_hours / entry_count if entry_count > 0 else 0
            print(f"Total hours: {total_hours}, Entry count: {entry_count}, Average: {avg_resolution_hours:.2f} hours")

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

        # Refresh all charts with new data based on the date filters
        self.refresh_charts(filter_data)

        # Update the UI
        self.update()


