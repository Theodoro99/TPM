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

# Load environment variables
load_dotenv()

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

def main(page: ft.Page):
    page.title = "PreventPlus"
    # Use a light theme with blue accent color
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE_600,
            primary_container=ft.Colors.BLUE_100,
            secondary=ft.Colors.TEAL_600,
            background=ft.Colors.GREY_50,
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
    
    # Initialize views
    dashboard_view = DashboardView()
    recent_activity_view = RecentActivityView()
    reports_view = ReportsView()
    
    # Store current view
    current_view = None
    
    # Set up routing
    def route_change(e):
        nonlocal current_view
        
        # Clear the page
        page.controls.clear()
        
        # Create app bar
        app_bar = ft.AppBar(
            leading=ft.Icon(ft.Icons.ENGINEERING),
            leading_width=40,
            title=ft.Text("PreventPlus"),
            center_title=False,
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.BRIGHTNESS_4_OUTLINED,
                    tooltip="Toggle brightness",
                    icon_color=ft.Colors.WHITE,
                ),
                ft.IconButton(
                    icon=ft.Icons.LOGOUT,
                    tooltip="Logout",
                    icon_color=ft.Colors.WHITE,
                    on_click=lambda _: show_login(page),
                ),
            ],
        )
        
        # Handle different routes
        if page.route == "/" or page.route == "/dashboard":
            current_view = dashboard_view
        elif page.route == "/recent_activity":
            current_view = recent_activity_view
        elif page.route == "/reports":
            current_view = reports_view
        else:
            # Default to dashboard
            current_view = dashboard_view
        
        # Add app bar and current view to page
        page.add(app_bar, current_view)
        page.update()
    
    # Set up view pop handler
    def view_pop(e):
        page.go("/")
    
    # Configure page for routing
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
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
            bgcolor=ft.Colors.BLUE_600,
            elevation=0,
            padding=ft.padding.only(top=15, bottom=15, left=25, right=25),
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        height=50,
        width=320,
    )
    
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
    
    # Show login screen initially
    show_login(page)


# Define port for the application
PORT = int(os.getenv("PORT", "8555"))  # Changed to 8555 to avoid port conflicts

if __name__ == "__main__":
    # Run Flet app
    ft.app(target=main, port=PORT)
