import flet as ft
from flet.control import Control
from flet.alert_dialog import AlertDialog
from flet.card import Card
from flet.column import Column
from flet.container import Container
from flet.elevated_button import ElevatedButton
from flet.image import Image
from flet.outlined_button import OutlinedButton
from flet.padding import Padding
from flet.row import Row
from flet.text import Text
from flet.text_field import TextField
from flet import colors, icons


class LoginView(Control):
    def __init__(self, on_login=None):
        super().__init__()
        self.on_login = on_login
        self.username_field = TextField(
            label="Username",
            icon=icons.PERSON,
            autofocus=True,
            width=300,
        )
        self.password_field = TextField(
            label="Password",
            icon=icons.LOCK,
            password=True,
            can_reveal_password=True,
            width=300,
        )
        self.error_text = Text(
            color=colors.RED_500,
            size=12,
            visible=False,
        )
        self.login_button = ElevatedButton(
            text="Login",
            icon=icons.LOGIN,
            width=300,
            on_click=self.login_clicked,
        )
        self.forgot_password_button = OutlinedButton(
            text="Forgot Password?",
            width=300,
        )
    
    def build(self):
        return Container(
            content=Column(
                [
                    Container(
                        content=Image(
                            src="/static/logo.png",
                            width=150,
                            height=150,
                            fit=ft.ImageFit.CONTAIN,
                        ),
                        alignment=ft.alignment.center,
                    ),
                    Text(
                        "PreventPlus",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=colors.BLUE_700,
                    ),
                    Text(
                        "Technical Intervention Logbook",
                        size=16,
                        color=colors.BLUE_GREY_700,
                    ),
                    Container(height=30),
                    Card(
                        content=Container(
                            content=Column(
                                [
                                    Container(
                                        content=Text(
                                            "Login to your account",
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        padding=Padding(20, 20, 20, 0),
                                    ),
                                    Container(
                                        content=Column(
                                            [
                                                self.username_field,
                                                Container(height=10),
                                                self.password_field,
                                                Container(height=5),
                                                self.error_text,
                                                Container(height=10),
                                                self.login_button,
                                                Container(height=10),
                                                self.forgot_password_button,
                                            ],
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                        padding=20,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            width=350,
                        ),
                        elevation=5,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            alignment=ft.alignment.center,
            expand=True,
            bgcolor=colors.BLUE_50,
        )
    
    def login_clicked(self, e):
        """Handle login button click."""
        username = self.username_field.value
        password = self.password_field.value
        
        if not username or not password:
            self.error_text.value = "Please enter both username and password"
            self.error_text.visible = True
            self.update()
            return
        
        # TODO: Implement actual authentication with API
        # For now, just simulate a successful login for demo purposes
        if username == "admin" and password == "admin":
            # Simulate user data
            user = {
                "id": "1",
                "username": username,
                "full_name": "Admin User",
                "role": "admin",
            }
            if self.on_login:
                self.on_login(user)
        else:
            self.error_text.value = "Invalid username or password"
            self.error_text.visible = True
            self.update()
