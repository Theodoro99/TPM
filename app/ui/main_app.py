import flet as ft
from flet.control import Control
from flet.app_bar import AppBar
from flet.column import Column
from flet.container import Container
from flet.icon import Icon
from flet.icon_button import IconButton
from flet.page import Page
from flet.text import Text
from flet.tabs import Tabs, Tab
from flet import colors, icons
from app.ui.views.login_view import LoginView
from app.ui.views.dashboard_view_new import DashboardView
from app.ui.views.logbook_view import LogbookView
from app.ui.views.reports_view import ReportsView
from app.ui.views.settings_view import SettingsView
from app.ui.views.profile_view import ProfileView
from app.ui.views.recent_activity_view import RecentActivityView


class MainApp(Control):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.page.title = "PreventPlus"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_min_width = 800
        self.page.window_min_height = 600
        
        # Set up route handling
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop
        
        # Set theme colors
        self.page.theme = ft.Theme(
            color_scheme_seed=colors.BLUE,
            color_scheme=ft.ColorScheme(
                primary=colors.BLUE_700,
                secondary=colors.TEAL_700,
            )
        )
        
        # Initialize state
        self.is_authenticated = False
        self.current_user = None
        self.current_view = "dashboard"
        
        # Initialize views
        self.login_view = LoginView(on_login=self.handle_login)
        self.dashboard_view = DashboardView()
        self.logbook_view = LogbookView()
        self.recent_activity_view = RecentActivityView()
        self.reports_view = ReportsView()
        self.settings_view = SettingsView()
        self.profile_view = ProfileView(on_logout=self.handle_logout)
        
        # Initialize navigation tabs
        self.navigation_tabs = Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                Tab(
                    text="Dashboard",
                    icon=icons.DASHBOARD_OUTLINED,
                    content=Container(),  # Empty container as content is managed separately
                ),
                Tab(
                    text="Logbook",
                    icon=icons.BOOK_OUTLINED,
                    content=Container(),
                ),
                Tab(
                    text="Recent Activity",
                    icon=icons.HISTORY_OUTLINED,
                    content=Container(),
                ),
                Tab(
                    text="Reports",
                    icon=icons.BAR_CHART_OUTLINED,
                    content=Container(),
                ),
                Tab(
                    text="Settings",
                    icon=icons.SETTINGS_OUTLINED,
                    content=Container(),
                ),
                Tab(
                    text="Profile",
                    icon=icons.PERSON_OUTLINED,
                    content=Container(),
                ),
            ],
            on_change=self.handle_navigation_change,
        )
        
        # Initialize app bar
        self.app_bar = AppBar(
            leading=Icon(icons.ENGINEERING),
            leading_width=40,
            title=Text("PreventPlus"),
            center_title=False,
            bgcolor=colors.BLUE_700,
            actions=[
                IconButton(
                    icon=icons.BRIGHTNESS_4_OUTLINED,
                    tooltip="Toggle brightness",
                    on_click=self.toggle_theme_mode,
                ),
                IconButton(
                    icon=icons.LOGOUT,
                    tooltip="Logout",
                    on_click=self.handle_logout,
                ),
            ],
        )
    
    def build(self):
        # If not authenticated, show login view
        if not self.is_authenticated:
            return self.login_view
        
        # Main content based on current view
        content = Container(
            content=self.get_current_view(),
            expand=True,
            padding=20,
        )
        
        # Main layout with horizontal navigation tabs and content
        return Column(
            [
                self.app_bar,
                self.navigation_tabs,
                content,
            ],
            expand=True,
        )
    
    def get_current_view(self):
        """Return the current view based on self.current_view."""
        if self.current_view == "dashboard":
            return self.dashboard_view
        elif self.current_view == "logbook":
            return self.logbook_view
        elif self.current_view == "recent_activity":
            return self.recent_activity_view
        elif self.current_view == "reports":
            return self.reports_view
        elif self.current_view == "settings":
            return self.settings_view
        elif self.current_view == "profile":
            return self.profile_view
        else:
            # Default to dashboard view
            return self.dashboard_view
    
    def handle_navigation_change(self, e):
        """Handle navigation tabs selection change."""
        index = e.control.selected_index
        
        if index == 0:
            self.current_view = "dashboard"
        elif index == 1:
            self.current_view = "logbook"
        elif index == 2:
            self.current_view = "recent_activity"
        elif index == 3:
            self.current_view = "reports"
        elif index == 4:
            self.current_view = "settings"
        elif index == 5:
            self.current_view = "profile"
        
        self.update()
    
    def handle_login(self, user):
        """Handle successful login."""
        self.is_authenticated = True
        self.current_user = user
        self.update()
    
    def handle_logout(self, e=None):
        """Handle logout."""
        self.is_authenticated = False
        self.current_user = None
        self.update()
    
    def toggle_theme_mode(self, e):
        """Toggle between light and dark theme."""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.update()
    
    def route_change(self, route):
        """Handle route changes for navigation."""
        route_path = route.route
        
        if route_path == "/":
            self.current_view = "dashboard"
            self.navigation_tabs.selected_index = 0
        elif route_path == "/logbook":
            self.current_view = "logbook"
            self.navigation_tabs.selected_index = 1
        elif route_path == "/recent_activity":
            self.current_view = "recent_activity"
            self.navigation_tabs.selected_index = 2
        elif route_path == "/reports":
            self.current_view = "reports"
            self.navigation_tabs.selected_index = 3
        elif route_path == "/settings":
            self.current_view = "settings"
            self.navigation_tabs.selected_index = 4
        elif route_path == "/profile":
            self.current_view = "profile"
            self.navigation_tabs.selected_index = 5
            
        self.update()
    
    def view_pop(self, view):
        """Handle view pop for navigation."""
        self.page.go("/")
        self.update()


def main(page: Page):
    """Main entry point for the Flet application."""
    # Initialize the page with routing
    page.views.clear()
    page.go('/')
    
    # Create and add the main app
    app = MainApp(page)
    page.add(app)
