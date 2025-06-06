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
from app.ui.views.login_view import LoginView

"""PreventPlus - Maintenance Management Application.

This module contains the main Flet application for the PreventPlus system,
including UI setup, routing, and view management.
"""

# Load environment variables
load_dotenv()
"""Loads configuration from .env file."""

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)
"""Initializes database schema on startup."""

# Database is now persistent - entries will be saved between application restarts

# Define a modern Flet app with professional design
# Global view instances
dashboard_view = None
recent_activity_view = None
reports_view = None


def main(page: ft.Page):
    """Main Flet application entry point.

    Args:
        page: The Flet Page instance representing the application window

    Configures:
        - Application theme and styling
        - View routing and navigation
        - Database initialization
        - User authentication flow
    """

    page.title = "PreventPlus"
    # Use a light theme with orange accent color
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.ORANGE_600,
            primary_container=ft.Colors.ORANGE_100,
            secondary=ft.Colors.DEEP_ORANGE_400,
            background=ft.Colors.ORANGE_50,
            surface=ft.Colors.WHITE,
            on_primary=ft.Colors.WHITE,
            on_secondary=ft.Colors.WHITE,
            on_background=ft.Colors.GREY_900,
            on_surface=ft.Colors.GREY_900,
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
        """Toggle between light and dark color themes.

        Args:
            e: Event object from Flet control
        """

        if page.theme_mode == ft.ThemeMode.LIGHT:
            # Set dark theme
            page.theme_mode = ft.ThemeMode.DARK
            page.theme = ft.Theme(
                color_scheme=ft.ColorScheme(
                    primary=ft.Colors.ORANGE_900,
                    primary_container=ft.Colors.ORANGE_800,
                    secondary=ft.Colors.DEEP_ORANGE_700,
                    background=ft.Colors.GREY_900,
                    surface=ft.Colors.GREY_800,
                    on_primary=ft.Colors.WHITE,
                    on_secondary=ft.Colors.WHITE,
                    on_background=ft.Colors.GREY_300,
                    on_surface=ft.Colors.GREY_300,
                ),
                font_family="Roboto"
            )
        else:
            # Set light theme with orange accent
            page.theme_mode = ft.ThemeMode.LIGHT
            page.theme = ft.Theme(
                color_scheme=ft.ColorScheme(
                    primary=ft.Colors.ORANGE_600,
                    primary_container=ft.Colors.ORANGE_100,
                    secondary=ft.Colors.DEEP_ORANGE_400,
                    background=ft.Colors.ORANGE_50,
                    surface=ft.Colors.WHITE,
                    on_primary=ft.Colors.WHITE,
                    on_secondary=ft.Colors.WHITE,
                    on_background=ft.Colors.GREY_900,
                    on_surface=ft.Colors.GREY_900,
                ),
                font_family="Roboto"
            )
        page.update()

    # Function to initialize all views
    def initialize_views(page):
        """Initialize all application views and load initial data.

        Args:
            page: Flet Page instance for view initialization

        Initializes:
            - Dashboard view with statistics
            - Recent activity view
            - Reports view
            - Settings view
        """
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
            bgcolor=ft.Colors.ORANGE_600,
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
        """Display login screen and handle authentication flow.

        Args:
            page: Flet Page instance for UI updates
        """

        page.clean()

        # Use the custom LoginView instead of hardcoded login form
        login_view = LoginView(on_login=lambda user: handle_successful_login(page, user))

        # Add login view to page
        page.add(
            ft.Container(
                content=login_view,
                alignment=ft.alignment.center,
                expand=True,
            )
        )
        page.update()

    # Function to handle successful login
    def handle_successful_login(page, user):
        """Handle post-login initialization and routing.

        Args:
            page: Flet Page instance for UI updates
            user: Authenticated user object
        """
        initialize_views(page)
        page.go("/dashboard")

    # Function to handle route changes
    def route_change(e, page):
        """Handle application route changes and view switching.

        Args:
            e: Route change event object
            page: Flet Page instance for UI updates
        """

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
            bgcolor=ft.Colors.ORANGE_600,
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
"""Default application port with environment variable override."""

if __name__ == "__main__":
    """Main entry point when run as a script.

    Handles:
        - Command line argument parsing
        - Application startup
    """
    import argparse

    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Run the LogBook application')
    parser.add_argument('--port', type=int, default=PORT, help='Port to run the application on')
    args = parser.parse_args()

    # Run Flet app with the specified port
    print(f"Starting LogBook application on port {args.port}")
    ft.app(target=main, port=args.port)