import flet as ft

def main(page: ft.Page):
    page.title = "PreventPlus - Test"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1200
    page.window_height = 800
    
    # Set theme colors
    page.theme = ft.Theme(
        color_scheme_seed=ft.colors.BLUE,
    )
    
    # Create a simple login form
    username_field = ft.TextField(
        label="Username",
        hint_text="Enter your username",
        prefix_icon=ft.icons.PERSON,
        width=300,
    )
    
    password_field = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        prefix_icon=ft.icons.LOCK,
        password=True,
        can_reveal_password=True,
        width=300,
    )
    
    error_text = ft.Text(
        color=ft.colors.RED_500,
        size=12,
        visible=False,
    )
    
    def login_clicked(e):
        if username_field.value == "admin" and password_field.value == "admin":
            # Show dashboard
            login_container.visible = False
            dashboard_container.visible = True
            page.update()
        else:
            error_text.value = "Invalid username or password"
            error_text.visible = True
            page.update()
    
    login_button = ft.ElevatedButton(
        text="Login",
        icon=ft.icons.LOGIN,
        on_click=login_clicked,
        width=300,
    )
    
    # Create login container
    login_container = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Text(
                        "PreventPlus",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE_700,
                    ),
                    alignment=ft.alignment.center,
                ),
                ft.Text(
                    "Technical Intervention Logbook",
                    size=16,
                    color=ft.colors.BLUE_GREY_700,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=30),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Container(
                                    content=ft.Text(
                                        "Login to your account",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    padding=ft.padding.only(20, 20, 20, 0),
                                ),
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            username_field,
                                            ft.Container(height=10),
                                            password_field,
                                            ft.Container(height=5),
                                            error_text,
                                            ft.Container(height=10),
                                            login_button,
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
        bgcolor=ft.colors.BLUE_50,
    )
    
    # Create a simple dashboard
    def create_stat_card(title, value, icon, color):
        return ft.Card(
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(
                            icon,
                            size=40,
                            color=color,
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    title,
                                    size=14,
                                    color=ft.colors.BLUE_GREY_700,
                                ),
                                ft.Text(
                                    value,
                                    size=28,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                            spacing=5,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=20,
                    alignment=ft.MainAxisAlignment.START,
                ),
                padding=ft.padding.all(20),
                width=250,
            ),
            elevation=3,
        )
    
    # Create dashboard container
    dashboard_container = ft.Container(
        content=ft.Column(
            [
                ft.AppBar(
                    leading=ft.Icon(ft.icons.ENGINEERING),
                    leading_width=40,
                    title=ft.Text("PreventPlus"),
                    center_title=False,
                    bgcolor=ft.colors.BLUE_700,
                    actions=[
                        ft.IconButton(
                            icon=ft.icons.LOGOUT,
                            tooltip="Logout",
                            on_click=lambda e: logout(),
                        ),
                    ],
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Dashboard",
                                size=30,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Container(height=20),
                            ft.Row(
                                [
                                    create_stat_card("Total Entries", "124", ft.icons.BOOK, ft.colors.BLUE_500),
                                    create_stat_card("Open", "18", ft.icons.PENDING_ACTIONS, ft.colors.AMBER_500),
                                    create_stat_card("Completed", "98", ft.icons.TASK_ALT, ft.colors.GREEN_500),
                                    create_stat_card("Escalated", "8", ft.icons.PRIORITY_HIGH, ft.colors.RED_500),
                                ],
                                wrap=True,
                                spacing=20,
                            ),
                            ft.Container(height=30),
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Text(
                                                "Quick Actions",
                                                size=20,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                            ft.Container(height=10),
                                            ft.Row(
                                                [
                                                    ft.ElevatedButton(
                                                        "New Entry",
                                                        icon=ft.icons.ADD,
                                                    ),
                                                    ft.ElevatedButton(
                                                        "Search",
                                                        icon=ft.icons.SEARCH,
                                                    ),
                                                    ft.ElevatedButton(
                                                        "Generate Report",
                                                        icon=ft.icons.SUMMARIZE,
                                                    ),
                                                ],
                                                spacing=10,
                                            ),
                                        ],
                                    ),
                                    padding=ft.padding.all(20),
                                ),
                                elevation=3,
                            ),
                        ],
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    padding=ft.padding.all(20),
                    expand=True,
                ),
            ],
            expand=True,
        ),
        visible=False,
        expand=True,
    )
    
    def logout():
        login_container.visible = True
        dashboard_container.visible = False
        username_field.value = ""
        password_field.value = ""
        error_text.visible = False
        page.update()
    
    # Add containers to page
    page.add(login_container, dashboard_container)

ft.app(target=main)
