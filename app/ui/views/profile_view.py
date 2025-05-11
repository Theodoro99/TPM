import flet as ft
from flet import (
    Card,
    Column,
    Container,
    Divider,
    ElevatedButton,
    Icon,
    Image,
    OutlinedButton,
    Row,
    Text,
    TextField,
    UserControl,
    colors,
    icons,
    padding,
)


class ProfileView(UserControl):
    def __init__(self, on_logout=None):
        super().__init__()
        self.on_logout = on_logout
        
        # Sample user data (would be replaced with actual user data)
        self.user = {
            "username": "admin",
            "full_name": "Admin User",
            "email": "admin@example.com",
            "role": "admin",
            "department": "IT",
            "last_login": "2025-05-07 21:45",
            "created_at": "2024-01-15",
        }
        
        # Profile information fields
        self.full_name_field = TextField(
            label="Full Name",
            value=self.user["full_name"],
            width=300,
        )
        
        self.email_field = TextField(
            label="Email",
            value=self.user["email"],
            width=300,
        )
        
        self.department_field = TextField(
            label="Department",
            value=self.user["department"],
            width=300,
        )
        
        # Password change fields
        self.current_password_field = TextField(
            label="Current Password",
            password=True,
            can_reveal_password=True,
            width=300,
        )
        
        self.new_password_field = TextField(
            label="New Password",
            password=True,
            can_reveal_password=True,
            width=300,
        )
        
        self.confirm_password_field = TextField(
            label="Confirm New Password",
            password=True,
            can_reveal_password=True,
            width=300,
        )
        
        # Theme preference
        self.theme_toggle = ft.Switch(
            label="Dark Mode",
            value=False,
        )
        
        # Notification preferences
        self.email_notifications = ft.Switch(
            label="Email Notifications",
            value=True,
        )
        
        self.in_app_notifications = ft.Switch(
            label="In-App Notifications",
            value=True,
        )
        
        # Buttons
        self.update_profile_button = ElevatedButton(
            text="Update Profile",
            icon=icons.SAVE,
            on_click=self.update_profile,
        )
        
        self.change_password_button = ElevatedButton(
            text="Change Password",
            icon=icons.LOCK_RESET,
            on_click=self.change_password,
        )
        
        self.logout_button = OutlinedButton(
            text="Logout",
            icon=icons.LOGOUT,
            on_click=self.logout,
        )
    
    def build(self):
        return Container(
            content=Column(
                [
                    Text(
                        "User Profile",
                        size=30,
                        weight=ft.FontWeight.BOLD,
                    ),
                    Container(height=20),
                    
                    # Profile Overview Card
                    Card(
                        content=Container(
                            content=Row(
                                [
                                    Container(
                                        content=Column(
                                            [
                                                Container(
                                                    content=Image(
                                                        src="/static/avatar.png",
                                                        width=150,
                                                        height=150,
                                                        fit=ft.ImageFit.CONTAIN,
                                                        border_radius=ft.border_radius.all(75),
                                                    ),
                                                    bgcolor=colors.BLUE_50,
                                                    width=150,
                                                    height=150,
                                                    border_radius=75,
                                                    alignment=ft.alignment.center,
                                                ),
                                                Container(height=10),
                                                ElevatedButton(
                                                    text="Change Avatar",
                                                    icon=icons.PHOTO_CAMERA,
                                                ),
                                            ],
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                        padding=padding.all(20),
                                    ),
                                    VerticalDivider(
                                        width=1,
                                        color=colors.BLUE_GREY_200,
                                    ),
                                    Container(
                                        content=Column(
                                            [
                                                Text(
                                                    self.user["full_name"],
                                                    size=24,
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                                Text(
                                                    f"@{self.user['username']}",
                                                    size=16,
                                                    color=colors.BLUE_GREY_400,
                                                ),
                                                Container(height=10),
                                                Row(
                                                    [
                                                        Icon(
                                                            icons.BADGE,
                                                            color=colors.BLUE,
                                                            size=20,
                                                        ),
                                                        Text(
                                                            f"Role: {self.user['role'].capitalize()}",
                                                            size=16,
                                                        ),
                                                    ],
                                                    spacing=5,
                                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                                ),
                                                Row(
                                                    [
                                                        Icon(
                                                            icons.BUSINESS,
                                                            color=colors.BLUE,
                                                            size=20,
                                                        ),
                                                        Text(
                                                            f"Department: {self.user['department']}",
                                                            size=16,
                                                        ),
                                                    ],
                                                    spacing=5,
                                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                                ),
                                                Row(
                                                    [
                                                        Icon(
                                                            icons.LOGIN,
                                                            color=colors.BLUE,
                                                            size=20,
                                                        ),
                                                        Text(
                                                            f"Last Login: {self.user['last_login']}",
                                                            size=16,
                                                        ),
                                                    ],
                                                    spacing=5,
                                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                                ),
                                                Row(
                                                    [
                                                        Icon(
                                                            icons.CALENDAR_TODAY,
                                                            color=colors.BLUE,
                                                            size=20,
                                                        ),
                                                        Text(
                                                            f"Member Since: {self.user['created_at']}",
                                                            size=16,
                                                        ),
                                                    ],
                                                    spacing=5,
                                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                                ),
                                            ],
                                        ),
                                        padding=padding.all(20),
                                        expand=True,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.START,
                            ),
                            padding=padding.all(0),
                        ),
                        elevation=3,
                    ),
                    Container(height=30),
                    
                    # Profile Information Card
                    Card(
                        content=Container(
                            content=Column(
                                [
                                    Text(
                                        "Profile Information",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    Container(height=20),
                                    self.full_name_field,
                                    Container(height=10),
                                    self.email_field,
                                    Container(height=10),
                                    self.department_field,
                                    Container(height=20),
                                    self.update_profile_button,
                                ],
                            ),
                            padding=padding.all(20),
                        ),
                        elevation=3,
                    ),
                    Container(height=30),
                    
                    # Password Change Card
                    Card(
                        content=Container(
                            content=Column(
                                [
                                    Text(
                                        "Change Password",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    Container(height=20),
                                    self.current_password_field,
                                    Container(height=10),
                                    self.new_password_field,
                                    Container(height=10),
                                    self.confirm_password_field,
                                    Container(height=20),
                                    self.change_password_button,
                                ],
                            ),
                            padding=padding.all(20),
                        ),
                        elevation=3,
                    ),
                    Container(height=30),
                    
                    # Preferences Card
                    Card(
                        content=Container(
                            content=Column(
                                [
                                    Text(
                                        "Preferences",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    Container(height=20),
                                    self.theme_toggle,
                                    Container(height=10),
                                    self.email_notifications,
                                    Container(height=10),
                                    self.in_app_notifications,
                                ],
                            ),
                            padding=padding.all(20),
                        ),
                        elevation=3,
                    ),
                    Container(height=30),
                    
                    # Logout Button
                    self.logout_button,
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
        )
    
    def update_profile(self, e):
        """Handle profile update."""
        # TODO: Implement profile update with API
        print("Update profile")
    
    def change_password(self, e):
        """Handle password change."""
        # TODO: Implement password change with API
        print("Change password")
    
    def logout(self, e):
        """Handle logout."""
        if self.on_logout:
            self.on_logout(e)
