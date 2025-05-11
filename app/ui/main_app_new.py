import flet as ft

# Import views
from app.ui.views.login_view import LoginView
from app.ui.views.dashboard_view import DashboardView
from app.ui.views.logbook_view import LogbookView
from app.ui.views.reports_view import ReportsView
from app.ui.views.settings_view import SettingsView
from app.ui.views.profile_view import ProfileView


def main(page: ft.Page):
    """Main entry point for the Flet application."""
    # Set page properties
    page.title = "PreventPlus"
    page.theme = ft.Theme(color_scheme_seed=ft.colors.BLUE)
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Authentication state
    is_authenticated = False
    current_user = None
    current_view = "dashboard"
    
    # Create navigation buttons
    def create_nav_button(label, icon, selected_icon, view_name):
        selected = view_name == current_view
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        selected_icon if selected else icon,
                        size=24,
                        color=ft.colors.PRIMARY if selected else ft.colors.GREY_600,
                    ),
                    ft.Text(
                        label,
                        size=12,
                        color=ft.colors.PRIMARY if selected else ft.colors.GREY_600,
                        weight=ft.FontWeight.BOLD if selected else ft.FontWeight.NORMAL,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.all(10),
            border_radius=ft.border_radius.all(10),
            bgcolor=ft.colors.PRIMARY_CONTAINER if selected else ft.colors.TRANSPARENT,
            on_click=lambda e, view=view_name: change_view(e, view),
        )
    
    # Create views
    login_view = LoginView(on_login=lambda user: handle_login(user))
    dashboard_view = DashboardView()
    logbook_view = LogbookView()
    reports_view = ReportsView()
    settings_view = SettingsView()
    profile_view = ProfileView(on_logout=lambda e: handle_logout())
    
    # Create app bar
    app_bar = ft.AppBar(
        leading=ft.Icon(ft.icons.HEALTH_AND_SAFETY),
        leading_width=40,
        title=ft.Text("PreventPlus"),
        center_title=False,
        bgcolor=ft.colors.SURFACE_VARIANT,
        actions=[
            ft.IconButton(
                icon=ft.icons.WB_SUNNY_OUTLINED,
                tooltip="Toggle theme",
                on_click=lambda e: toggle_theme_mode()
            ),
            ft.IconButton(
                icon=ft.icons.LOGOUT,
                tooltip="Logout",
                on_click=lambda e: handle_logout()
            ),
        ],
    )
    
    # Function to handle view changes
    def change_view(e, view_name):
        nonlocal current_view
        current_view = view_name
        update_ui()
    
    # Function to handle login
    def handle_login(user):
        nonlocal is_authenticated, current_user
        is_authenticated = True
        current_user = user
        update_ui()
    
    # Function to handle logout
    def handle_logout():
        nonlocal is_authenticated, current_user
        is_authenticated = False
        current_user = None
        update_ui()
    
    # Function to toggle theme mode
    def toggle_theme_mode():
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
        page.update()
    
    # Function to get the current view content
    def get_current_view():
        if current_view == "dashboard":
            return dashboard_view
        elif current_view == "logbook":
            return logbook_view
        elif current_view == "reports":
            return reports_view
        elif current_view == "settings":
            return settings_view
        elif current_view == "profile":
            return profile_view
        else:
            return dashboard_view
    
    # Function to update the UI
    def update_ui():
        # Clear the page
        page.controls.clear()
        
        if not is_authenticated:
            # Show login view
            page.appbar = None
            page.add(login_view)
        else:
            # Set app bar
            page.appbar = app_bar
            
            # Create navigation buttons
            nav_buttons = [
                create_nav_button("Dashboard", ft.icons.DASHBOARD_OUTLINED, ft.icons.DASHBOARD, "dashboard"),
                create_nav_button("Logbook", ft.icons.BOOK_OUTLINED, ft.icons.BOOK, "logbook"),
                create_nav_button("Reports", ft.icons.BAR_CHART_OUTLINED, ft.icons.BAR_CHART, "reports"),
                create_nav_button("Settings", ft.icons.SETTINGS_OUTLINED, ft.icons.SETTINGS, "settings"),
                create_nav_button("Profile", ft.icons.PERSON_OUTLINED, ft.icons.PERSON, "profile"),
            ]
            
            # Create horizontal navigation bar
            nav_bar = ft.Container(
                content=ft.Row(
                    nav_buttons,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                padding=10,
                border=ft.border.only(bottom=ft.BorderSide(1, ft.colors.GREY_300)),
                bgcolor=ft.colors.WHITE,
            )
            
            # Main content based on current view
            content = ft.Container(
                content=get_current_view(),
                expand=True,
                padding=20,
            )
            
            # Add the nav bar and content to the page
            page.add(nav_bar, content)
        
        # Update the page
        page.update()
    
    # Initial UI setup
    update_ui()
