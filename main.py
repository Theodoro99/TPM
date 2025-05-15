import os
import flet as ft
from dotenv import load_dotenv

# Import database models for querying data
from app.db.database import engine, SessionLocal
from app.db.models import Base, LogbookEntry, StatusEnum
from sqlalchemy import func

# Import views
from app.ui.views.dashboard_view_new import DashboardView
from app.ui.views.recent_activity_view import RecentActivityView
from app.ui.views.reports_view import ReportsView
from app.ui.views.settings_view import SettingsView

# Load environment variables
load_dotenv()

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

# Database is now persistent - entries will be saved between application restarts

# Define a modern Flet app with professional design
# Global view instances
dashboard_view = None
recent_activity_view = None
reports_view = None


def main(page: ft.Page):
    page.title = "PreventPlus"
    # Use a light theme with orange accent color
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.colors.ORANGE_600,
            primary_container=ft.colors.ORANGE_100,
            secondary=ft.colors.DEEP_ORANGE_400,
            background=ft.colors.ORANGE_50,
            surface=ft.colors.WHITE,
            on_primary=ft.colors.WHITE,
            on_secondary=ft.colors.WHITE,
            on_background=ft.colors.GREY_900,
            on_surface=ft.colors.GREY_900,
        ),
        font_family="Roboto"
    )
    page.padding = 0
    page.bgcolor = ft.Colors.GREY_50
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window_bgcolor = ft.Colors.TRANSPARENT
    page.window_title_bar_hidden = True
    page.window_title_bar_buttons_hidden = True

    # Set up routing
    page.on_route_change = lambda e: route_change(e, page)
    page.on_view_pop = lambda e: page.go("/")

    # Function to toggle between light and dark theme
    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            # Set dark theme
            page.theme_mode = ft.ThemeMode.DARK
            page.theme = ft.Theme(
                color_scheme=ft.ColorScheme(
                    primary=ft.colors.ORANGE_900,
                    primary_container=ft.colors.ORANGE_800,
                    secondary=ft.colors.DEEP_ORANGE_700,
                    background=ft.colors.GREY_900,
                    surface=ft.colors.GREY_800,
                    on_primary=ft.colors.WHITE,
                    on_secondary=ft.colors.WHITE,
                    on_background=ft.colors.GREY_300,
                    on_surface=ft.colors.GREY_300,
                ),
                font_family="Roboto"
            )
        else:
            # Set light theme with orange accent
            page.theme_mode = ft.ThemeMode.LIGHT
            page.theme = ft.Theme(
                color_scheme=ft.ColorScheme(
                    primary=ft.colors.ORANGE_600,
                    primary_container=ft.colors.ORANGE_100,
                    secondary=ft.colors.DEEP_ORANGE_400,
                    background=ft.colors.ORANGE_50,
                    surface=ft.colors.WHITE,
                    on_primary=ft.colors.WHITE,
                    on_secondary=ft.colors.WHITE,
                    on_background=ft.colors.GREY_900,
                    on_surface=ft.colors.GREY_900,
                ),
                font_family="Roboto"
            )
        page.update()

    # Create modern login form elements
    username_field = ft.TextField(
        label="Username",
        prefix_icon=ft.Icons.PERSON,
        border_radius=8,
        focused_border_color=ft.Colors.BLUE_600,
        autofocus=True,
        text_size=14,
        height=50,
        content_padding=ft.padding.only(left=12, right=12),
        color=ft.Colors.BLACK,
        label_style=ft.TextStyle(color=ft.Colors.BLACK),
    )

    password_field = ft.TextField(
        label="Password",
        prefix_icon=ft.Icons.LOCK,
        password=True,
        border_radius=8,
        focused_border_color=ft.Colors.BLUE_600,
        text_size=14,
        height=50,
        content_padding=ft.padding.only(left=12, right=12),
        color=ft.Colors.BLACK,
        label_style=ft.TextStyle(color=ft.Colors.BLACK),
    )

    error_text = ft.Text(
        "",
        color=ft.Colors.RED_500,
        size=12,
        visible=False,
        weight=ft.FontWeight.W_500,
    )

    def validate_login(e):
        # Simple validation for demo purposes
        if username_field.value == "admin" and password_field.value == "admin":
            # Initialize views
            initialize_views(page)
            # Navigate to dashboard
            page.go("/dashboard")
        else:
            error_text.value = "Invalid username or password"
            error_text.visible = True
            page.update()

    login_button = ft.ElevatedButton(
        "Login",
        icon=ft.Icons.LOGIN,
        on_click=validate_login,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.colors.ORANGE_600,
            elevation=0,
            padding=ft.padding.only(top=15, bottom=15, left=25, right=25),
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        height=50,
        width=320,
    )

    # Function to create a modern stat card
    def create_stat_card(title, value, icon, color):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(icon, color=ft.Colors.WHITE, size=24),
                        bgcolor=color,
                        border_radius=12,
                        padding=10,
                    ),
                    ft.Text(
                        value,
                        size=42,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_900,
                    ),
                    ft.Text(
                        title,
                        size=14,
                        color=ft.Colors.GREY_700,
                        weight=ft.FontWeight.W_500,
                    ),
                ],
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            width=220,
            height=160,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            padding=20,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=5,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )

    # Function to initialize all views
    def initialize_views(page):
        global dashboard_view, recent_activity_view, reports_view, settings_view
        from datetime import datetime

        # Create dashboard view
        dashboard_view = DashboardView()
        dashboard_view.page = page

        # Create recent activity view
        recent_activity_view = RecentActivityView()
        recent_activity_view.page = page

        # Create reports view
        reports_view = ReportsView()
        reports_view.page = page

        # Create settings view
        settings_view = SettingsView()
        settings_view.page = page

        # Update dashboard view with actual data
        # Get counts and recent activities from database
        with SessionLocal() as session:
            # Get counts
            total_count = session.query(func.count(LogbookEntry.id)).scalar() or 0
            open_count = session.query(func.count(LogbookEntry.id)).filter(
                LogbookEntry.status == StatusEnum.OPEN).scalar() or 0
            completed_count = session.query(func.count(LogbookEntry.id)).filter(
                LogbookEntry.status == StatusEnum.COMPLETED).scalar() or 0
            escalated_count = session.query(func.count(LogbookEntry.id)).filter(
                LogbookEntry.status == StatusEnum.ESCALATION).scalar() or 0

            # Get recent activities (5 most recent entries)
            recent_entries = (
                session.query(LogbookEntry)
                .order_by(LogbookEntry.created_at.desc())
                .limit(5)
                .all()
            )

            # Format recent activities for the dashboard
            recent_activities = []
            for entry in recent_entries:
                # Format the date/time
                if entry.created_at:
                    from datetime import datetime
                    now = datetime.now()
                    delta = now - entry.created_at
                    if delta.days > 0:
                        time_str = f"{delta.days} days ago"
                    elif delta.seconds // 3600 > 0:
                        time_str = f"{delta.seconds // 3600} hours ago"
                    else:
                        time_str = f"{delta.seconds // 60} minutes ago"
                else:
                    time_str = "Unknown time"

        # Create app bar with navigation buttons
        app_bar = ft.AppBar(
            leading=ft.Icon(ft.Icons.ENGINEERING),
            leading_width=40,
            title=ft.Text("PreventPlus"),
            center_title=False,
            bgcolor=ft.colors.ORANGE_600,
            color=ft.Colors.WHITE,
            actions=[
                # Navigation buttons
                ft.IconButton(
                    icon=ft.Icons.DASHBOARD_OUTLINED,
                    tooltip="Dashboard",
                    icon_color=ft.Colors.WHITE,
                    on_click=lambda _: page.go("/dashboard"),
                ),
                ft.IconButton(
                    icon=ft.Icons.HISTORY_OUTLINED,
                    tooltip="Recent Activity",
                    icon_color=ft.Colors.WHITE,
                    on_click=lambda _: page.go("/recent_activity"),
                ),
                ft.IconButton(
                    icon=ft.Icons.BAR_CHART_OUTLINED,
                    tooltip="Reports",
                    icon_color=ft.Colors.WHITE,
                    on_click=lambda _: page.go("/reports"),
                ),
                ft.IconButton(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    tooltip="Settings",
                    icon_color=ft.Colors.WHITE,
                    on_click=lambda _: page.go("/settings"),
                ),
                # Theme and logout buttons
                ft.IconButton(
                    icon=ft.Icons.BRIGHTNESS_4_OUTLINED,
                    tooltip="Toggle brightness",
                    icon_color=ft.Colors.WHITE,
                    on_click=toggle_theme,
                ),
                ft.IconButton(
                    icon=ft.Icons.LOGOUT,
                    tooltip="Logout",
                    icon_color=ft.Colors.WHITE,
                    on_click=lambda _: show_login(page),
                ),
            ],
        )

        # Add app bar and dashboard view to page by default
        page.add(app_bar, dashboard_view)
        page.update()

    # Function to show login screen
    def show_login(page):
        page.clean()

        # Create a modern login form
        login_card = ft.Container(
            content=ft.Column(
                [
                    # Logo and app name
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=ft.Icon(
                                        ft.Icons.ENGINEERING_ROUNDED,
                                        color=ft.Colors.BLUE_600,
                                        size=32,
                                    ),
                                    margin=ft.margin.only(right=10),
                                ),
                                ft.Text(
                                    "PreventPlus",
                                    weight=ft.FontWeight.BOLD,
                                    size=24,
                                    color=ft.Colors.GREY_900,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        margin=ft.margin.only(bottom=30),
                    ),

                    # Login title
                    ft.Container(
                        content=ft.Text(
                            "Log In to Your Account",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_900,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        margin=ft.margin.only(bottom=24),
                    ),

                    # Form fields
                    ft.Container(
                        content=ft.Column(
                            [
                                username_field,
                                ft.Container(height=16),
                                password_field,
                                ft.Container(height=8),
                                error_text,
                                ft.Container(height=24),
                                login_button,
                            ],
                            spacing=0,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ),

                    # Footer
                    ft.Container(
                        content=ft.Text(
                            "© 2025 PreventPlus - Maintenance Management",
                            size=12,
                            color=ft.Colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        margin=ft.margin.only(top=40),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=420,
            height=500,
            padding=40,
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
        )

        # Add login card to page
        page.add(
            ft.Container(
                content=login_card,
                alignment=ft.alignment.center,
                expand=True,
            )
        )
        page.update()

    # Function to handle route changes
    def route_change(e, page):
        route_path = e.route

        # If not initialized, initialize views
        if dashboard_view is None:
            initialize_views(page)

        # Clear the page
        page.clean()

        # Create app bar with navigation buttons
        app_bar = ft.AppBar(
            leading=ft.Icon(ft.Icons.ENGINEERING),
            leading_width=40,
            title=ft.Text("PreventPlus"),
            center_title=False,
            bgcolor=ft.colors.ORANGE_600,
            color=ft.Colors.WHITE,
            actions=[
                # Navigation buttons
                ft.IconButton(
                    icon=ft.Icons.DASHBOARD_OUTLINED,
                    tooltip="Dashboard",
                    icon_color=ft.Colors.WHITE,
                    on_click=lambda _: page.go("/dashboard"),
                ),
                ft.IconButton(
                    icon=ft.Icons.HISTORY_OUTLINED,
                    tooltip="Recent Activity",
                    icon_color=ft.Colors.WHITE,
                    on_click=lambda _: page.go("/recent_activity"),
                ),
                ft.IconButton(
                    icon=ft.Icons.BAR_CHART_OUTLINED,
                    tooltip="Reports",
                    icon_color=ft.Colors.WHITE,
                    on_click=lambda _: page.go("/reports"),
                ),
                ft.IconButton(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    tooltip="Settings",
                    icon_color=ft.Colors.WHITE,
                    on_click=lambda _: page.go("/settings"),
                ),
                # Theme and logout buttons
                ft.IconButton(
                    icon=ft.Icons.BRIGHTNESS_4_OUTLINED,
                    tooltip="Toggle brightness",
                    icon_color=ft.Colors.WHITE,
                    on_click=toggle_theme,
                ),
                ft.IconButton(
                    icon=ft.Icons.LOGOUT,
                    tooltip="Logout",
                    icon_color=ft.Colors.WHITE,
                    on_click=lambda _: show_login(page),
                ),
            ],
        )

        # Determine which view to show based on route
        current_view = None
        if route_path == "/" or route_path == "/dashboard":
            current_view = dashboard_view
        elif route_path == "/recent_activity":
            current_view = recent_activity_view
        elif route_path == "/reports":
            current_view = reports_view
        elif route_path == "/settings":
            current_view = settings_view
        else:
            # Default to dashboard
            current_view = dashboard_view

        # Add app bar and current view to page
        page.add(app_bar, current_view)
        page.update()

    # Show login screen initially
    show_login(page)


# Define port for the application
# Default port with environment variable override
PORT = int(os.getenv("PORT", "8558"))  # Default port is 8558

if __name__ == "__main__":
    import argparse

    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Run the LogBook application')
    parser.add_argument('--port', type=int, default=PORT, help='Port to run the application on')
    args = parser.parse_args()

    # Run Flet app with the specified port
    print(f"Starting LogBook application on port {args.port}")
    ft.app(target=main, port=args.port)
