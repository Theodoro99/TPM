import flet as ft
from flet import icons

"""Login View Module.

This module contains the LoginView class which provides
a complete authentication interface for the PreventPlus application.
"""


class LoginView(ft.Container):
    """A modern login interface with dark theme and professional styling.

    Args:
        on_login: Callback function that receives user data upon successful authentication

    Features:
        - Clean, professional UI with dark theme
        - Form validation
        - Database authentication
        - Responsive layout
        - Error handling
    """

    def __init__(self, on_login=None):
        """Initialize the login view components and layout."""
        super().__init__()
        self.on_login = on_login
        self.expand = True

        # Initialize UI components first
        self._init_ui_components()

        # Then build the login UI
        self.content = self._build_login_ui()

    def _init_ui_components(self):
        """Initialize all UI components with their styling and properties.

        Creates:
            - Username/password fields with custom styling
            - Error message display
            - Login button with enhanced visibility
        """
        # Text fields with improved styling for dark theme
        self.username_field = ft.TextField(
            label="Username",
            icon=icons.PERSON_OUTLINED,
            autofocus=True,
            width=320,  # Increased width to match larger card
            border_color=ft.colors.ORANGE_400,
            focused_border_color=ft.colors.ORANGE_500,
            cursor_color=ft.colors.ORANGE_500,
            text_style=ft.TextStyle(color=ft.colors.WHITE),
            label_style=ft.TextStyle(color=ft.colors.ORANGE_200),
            bgcolor="#3A3A3A",  # Slightly lighter than the card background
        )

        self.password_field = ft.TextField(
            label="Password",
            icon=icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True,
            width=320,  # Increased width to match larger card
            border_color=ft.colors.ORANGE_400,
            focused_border_color=ft.colors.ORANGE_500,
            cursor_color=ft.colors.ORANGE_500,
            text_style=ft.TextStyle(color=ft.colors.WHITE),
            label_style=ft.TextStyle(color=ft.colors.ORANGE_200),
            bgcolor="#3A3A3A",  # Slightly lighter than the card background
        )

        self.error_text = ft.Text(
            color=ft.colors.RED_400,  # Brighter red for better visibility on dark background
            size=13,
            visible=False,
            weight=ft.FontWeight.W_500,
        )

        # Login button with larger text
        self.login_button = ft.TextButton(
            content=ft.Text(
                "Login",
                color=ft.colors.ORANGE_300,
                size=28,  # Increased text size even more
                weight=ft.FontWeight.BOLD,  # Make text bold for better visibility
            ),
            width=200,
            on_click=self.login_clicked,
        )

        # Removed forgot password button as requested

    def _build_login_ui(self):
        """Construct the complete login interface layout.

        Returns:
            Row: The main layout containing:
                - Decorative left panel with branding
                - Right panel with login form
        """
        # Create a modern, professional login page with black and orange theme
        return ft.Row(
            [
                # Left side - decorative panel with gradient
                ft.Container(
                    width=400,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_center,
                        end=ft.alignment.bottom_center,
                        colors=[
                            ft.colors.BLACK,
                            "#1A1A1A",
                            "#262626",
                        ],
                    ),
                    content=ft.Column(
                        [
                            ft.Container(height=80),
                            ft.Container(
                                content=ft.Image(
                                    src="/static/logo.png",
                                    width=180,
                                    height=180,
                                    fit=ft.ImageFit.CONTAIN,
                                    color=ft.colors.ORANGE_500,
                                ),
                                alignment=ft.alignment.center,
                            ),
                            ft.Container(height=20),
                            ft.Text(
                                "PreventPlus",
                                size=38,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.WHITE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=5),
                            ft.Text(
                                "Maintenance Management",
                                size=18,
                                color=ft.colors.ORANGE_300,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=40),
                            ft.Container(
                                content=ft.Text(
                                    "© 2025 PreventPlus - Maintenance Management",
                                    size=12,
                                    color=ft.colors.WHITE70,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                alignment=ft.alignment.center,
                                margin=ft.margin.only(bottom=30),
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        expand=True,
                    ),
                ),

                # Right side - login form with white background
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        [
                            ft.Container(height=80),  # Top spacing

                            # Login form card
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Container(
                                                content=ft.Text(
                                                    "Log In to Your Account",
                                                    size=24,
                                                    weight=ft.FontWeight.W_600,
                                                    color=ft.colors.WHITE,
                                                ),
                                                padding=ft.padding.only(top=25, bottom=10),
                                            ),
                                            ft.Container(
                                                content=ft.Text(
                                                    "Enter your credentials to access your dashboard",
                                                    size=14,
                                                    color=ft.colors.ORANGE_200,
                                                ),
                                                padding=ft.padding.only(bottom=25),
                                            ),
                                            self.username_field,
                                            ft.Container(height=15),
                                            self.password_field,
                                            ft.Container(height=8),
                                            self.error_text,
                                            ft.Container(height=20),
                                            self.login_button,
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        width=400,  # Increased from 350 to 400
                                    ),
                                    padding=ft.padding.symmetric(horizontal=40, vertical=30),  # Increased padding
                                    border_radius=15,  # Slightly larger border radius
                                    bgcolor="#2A2A2A",  # Dark gray background for better contrast
                                ),
                                elevation=4,
                                color=ft.colors.BLACK,
                                surface_tint_color=ft.colors.BLACK,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    bgcolor="#FFF3E0",  # Light orange background for the right side
                ),
            ],
            expand=True,
        )

    def login_clicked(self, e):
        """Handle the login button click event.

        Performs:
            - Field validation
            - Database authentication
            - Error handling
            - Success callback

        Args:
            e: The click event object
        """
        username = self.username_field.value
        password = self.password_field.value

        if not username or not password:
            self.error_text.value = "Please enter both username and password"
            self.error_text.visible = True
            self.update()
            return

        # Use the actual authentication system
        from sqlalchemy.orm import Session
        from app.db.database import SessionLocal
        from app.core.security import authenticate_user

        # Create a database session
        db = SessionLocal()
        try:
            # Authenticate the user
            user_obj = authenticate_user(db, username, password)

            if user_obj:
                # Convert user object to dictionary for the callback
                user = {
                    "id": str(user_obj.id),
                    "username": user_obj.username,
                    "full_name": user_obj.full_name,
                    "role": user_obj.role,
                }
                if self.on_login:
                    self.on_login(user)
            else:
                self.error_text.value = "Invalid username or password"
                self.error_text.visible = True
                self.update()
        finally:
            db.close()

