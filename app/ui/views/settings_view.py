import flet as ft
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import User, Location, Category, Setting, RoleEnum
from werkzeug.security import generate_password_hash
import uuid


class UserManagementTab(ft.Column):
    def __init__(self):
        super().__init__()
        self.page = None
        self.db = SessionLocal()
        
        # Load users from database
        self.load_users_from_db()
        
        # Search field
        self.search_field = ft.TextField(
            label="Search Users",
            icon=ft.icons.SEARCH,
            expand=True,
        )
        
        # Add user button
        print("Creating Add User button")
        self.add_user_button = ft.ElevatedButton(
            text="Add User",
            icon=ft.icons.PERSON_ADD,
            on_click=self.show_add_user_dialog,
            bgcolor=ft.colors.ORANGE_600,  # Make it more visible
            color=ft.colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
            )
        )
        print(f"Add User button created with on_click={self.show_add_user_dialog}")
        
        # User table
        self.user_table = self.build_user_table()
        
        # Set up the controls
        self.controls = [
            ft.Row(
                [
                    self.search_field,
                    self.add_user_button,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Container(height=20),
            self.user_table,
        ]
        self.scroll = ft.ScrollMode.AUTO
    
    def show_add_user_dialog(self, e):
        """Show the add user dialog."""
        print("show_add_user_dialog called")
        try:
            if self.page:
                print(f"self.page is {self.page}")
                # Create form fields
                self.username_field = ft.TextField(
                    label="Username",
                    hint_text="Enter username",
                    border_color=ft.colors.BLUE_GREY_400,
                    color=ft.colors.BLACK,
                    width=300,
                )
                
                self.full_name_field = ft.TextField(
                    label="Full Name",
                    hint_text="Enter full name",
                    border_color=ft.colors.BLUE_GREY_400,
                    color=ft.colors.BLACK,
                    width=300,
                )
                
                self.email_field = ft.TextField(
                    label="Email",
                    hint_text="Enter email address",
                    border_color=ft.colors.BLUE_GREY_400,
                    color=ft.colors.BLACK,
                    width=300,
                )
                
                self.password_field = ft.TextField(
                    label="Password",
                    hint_text="Enter password",
                    password=True,
                    border_color=ft.colors.BLUE_GREY_400,
                    color=ft.colors.BLACK,
                    width=300,
                )
                
                self.role_dropdown = ft.Dropdown(
                    label="Role",
                    hint_text="Select role",
                    options=[
                        ft.dropdown.Option("admin", "Admin"),
                        ft.dropdown.Option("manager", "Manager"),
                        ft.dropdown.Option("technician", "Technician"),
                    ],
                    border_color=ft.colors.BLUE_GREY_400,
                    color=ft.colors.BLACK,
                    width=300,
                )
                
                self.department_field = ft.TextField(
                    label="Department",
                    hint_text="Enter department",
                    border_color=ft.colors.BLUE_GREY_400,
                    color=ft.colors.BLACK,
                    width=300,
                )
                
                # Create form container
                form_content = ft.Container(
                    content=ft.Column(
                        [
                            self.username_field,
                            self.full_name_field,
                            self.email_field,
                            self.password_field,
                            self.role_dropdown,
                            self.department_field,
                        ],
                        spacing=15,
                        width=300,
                        height=400,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    padding=10,
                )
                
                # Create the dialog directly here instead of using a class variable
                dialog = ft.AlertDialog(
                    title=ft.Text("Add New User", color=ft.colors.BLACK),
                    content=form_content,
                    actions=[
                        ft.TextButton("Cancel", on_click=self.close_dialog),
                        ft.TextButton("Add", on_click=self.add_user),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                    modal=True,
                )
                
                # Set the dialog
                self.page.dialog = dialog
                self.page.dialog.open = True
                
                # Update the page to show the dialog
                print("Updating page to show dialog")
                self.page.update()
                print("Dialog should be visible now")
            else:
                print("ERROR: self.page is None in show_add_user_dialog")
        except Exception as ex:
            print(f"Exception in show_add_user_dialog: {ex}")
            import traceback
            traceback.print_exc()
    
    def close_dialog(self, e):
        """Close the dialog."""
        if self.page and self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
    
    def load_users_from_db(self):
        """Load users from the database."""
        try:
            # Query all users from the database
            db_users = self.db.query(User).all()
            
            # Convert database users to dictionary format for the UI
            self.users = []
            for user in db_users:
                self.users.append({
                    "id": str(user.id),
                    "username": user.username,
                    "full_name": user.full_name,
                    "email": user.email,
                    "role": user.role.value,
                    "department": user.department or "",
                    "is_active": user.is_active,
                })
                
        except Exception as e:
            print(f"Error loading users from database: {e}")
            # Fallback to sample data if database connection fails
            self.users = [
                {
                    "id": "1",
                    "username": "admin",
                    "full_name": "Admin User",
                    "email": "admin@example.com",
                    "role": "admin",
                    "department": "IT",
                    "is_active": True,
                },
                {
                    "id": "2",
                    "username": "jsmith",
                    "full_name": "John Smith",
                    "email": "john.smith@example.com",
                    "role": "technician",
                    "department": "Maintenance",
                    "is_active": True,
                },
                {
                    "id": "3",
                    "username": "jdoe",
                    "full_name": "Jane Doe",
                    "email": "jane.doe@example.com",
                    "role": "manager",
                    "department": "Operations",
                    "is_active": True,
                },
                {
                    "id": "4",
                    "username": "mjohnson",
                    "full_name": "Mike Johnson",
                    "email": "mike.johnson@example.com",
                    "role": "technician",
                    "department": "Maintenance",
                "is_active": True,
            },
            {
                "id": "2",
                "username": "jsmith",
                "full_name": "John Smith",
                "email": "john.smith@example.com",
                "role": "technician",
                "department": "Maintenance",
                "is_active": True,
            },
            {
                "id": "3",
                "username": "jdoe",
                "full_name": "Jane Doe",
                "email": "jane.doe@example.com",
                "role": "manager",
                "department": "Operations",
                "is_active": True,
            },
            {
                "id": "4",
                "username": "mjohnson",
                "full_name": "Mike Johnson",
                "email": "mike.johnson@example.com",
                "role": "technician",
                "department": "Maintenance",
                "is_active": False,
            },
        ]
    
    def add_user(self, e):
        """Add a new user to the database."""
        try:
            print("add_user method called")
            # Get values from form fields
            username = self.username_field.value
            full_name = self.full_name_field.value
            email = self.email_field.value
            password = self.password_field.value
            role = self.role_dropdown.value
            department = self.department_field.value
            
            print(f"Form values: username={username}, role={role}")
            
            # Validate required fields
            if not username or not password or not role:
                print("Validation failed: missing required fields")
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Username, password, and role are required"),
                        bgcolor=ft.colors.RED_400
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                return
            
            # Convert role to RoleEnum
            role_enum = RoleEnum.TECHNICIAN  # Default
            if role == "admin":
                role_enum = RoleEnum.ADMIN
            elif role == "manager":
                role_enum = RoleEnum.MANAGER
            elif role == "technician":
                role_enum = RoleEnum.TECHNICIAN
            
            print(f"Role converted to: {role_enum}")
            
            # Create new user
            new_user = User(
                username=username,
                full_name=full_name,
                email=email,
                password_hash=generate_password_hash(password),
                role=role_enum,
                department=department,
                is_active=True
            )
            
            print("User object created, adding to database")
            
            # Add user to database
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            
            print(f"User added to database with ID: {new_user.id}")
            
            # Close dialog
            if self.page and self.page.dialog:
                self.page.dialog.open = False
            
            # Show success message
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"User {username} added successfully"),
                    bgcolor=ft.colors.GREEN_400
                )
                self.page.snack_bar.open = True
                self.page.update()
            
            # Reload users
            self.load_users_from_db()
            
        except Exception as ex:
            print(f"Error adding user: {ex}")
            import traceback
            traceback.print_exc()
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error adding user: {ex}"),
                    bgcolor=ft.colors.RED_400
                )
                self.page.snack_bar.open = True
                self.page.update()
        
    def edit_user(self, e):
        """Edit an existing user."""
        try:
            # Get the user ID from the event data
            user_id = e.control.data
            
            # Find the user in the database
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if user:
                # Show edit user dialog (to be implemented)
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Editing user {user.username}", color=ft.colors.WHITE),
                        bgcolor=ft.colors.BLUE_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            else:
                # User not found
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("User not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error editing user: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error: {str(e)}", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()

    def delete_user(self, e):
        """Delete a user from the system."""
        try:
            # Get the user ID from the event data
            user_id = e.control.data
            
            # Show confirmation dialog
            self.confirm_delete_user(user_id)
            
        except Exception as e:
            print(f"Error deleting user: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error: {str(e)}", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()

    def confirm_delete_user(self, user_id):
        """Confirm deletion of a user."""
        try:
            # Find the user in the database
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if user:
                # Show confirmation dialog
                if self.page:
                    self.page.dialog = ft.AlertDialog(
                        title=ft.Text("Confirm Deletion", color=ft.colors.BLACK),
                        content=ft.Text(f"Are you sure you want to delete user {user.username}?", color=ft.colors.BLACK),
                        actions=[
                            ft.TextButton("Cancel", on_click=self.close_dialog),
                            ft.TextButton(
                                "Delete",
                                on_click=lambda e: self.perform_delete_user(user_id),
                                style=ft.ButtonStyle(
                                    color={ft.MaterialState.DEFAULT: ft.colors.RED_600}
                                ),
                            ),
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    self.page.dialog.open = True
                    self.page.update()
            else:
                # User not found
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("User not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error confirming delete user: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error deleting user", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
    
    def perform_delete_user(self, user_id):
        """Actually delete the user after confirmation."""
        try:
            # Find the user in the database
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if user:
                # Delete from database
                self.db.delete(user)
                self.db.commit()
                
                # Remove from UI list
                self.users = [u for u in self.users if u["id"] != str(user_id)]
                
                # Rebuild the user table
                self.user_table = self.build_user_table()
                
                # Update the controls
                self.controls = [
                    ft.Row(
                        [
                            self.search_field,
                            self.add_user_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=20),
                    self.user_table,
                ]
                self.update()
                
                # Show success message
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"User deleted successfully", color=ft.colors.WHITE),
                        bgcolor=ft.colors.GREEN_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("User not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error deleting user: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error: {str(e)}", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        # Close the dialog
        self.close_dialog(None)
    
    def build_user_table(self):
        """Build the user table with current users."""
        try:
            columns = [
                ft.DataColumn(ft.Text("Username", color=ft.colors.BLACK)),
                ft.DataColumn(ft.Text("Full Name", color=ft.colors.BLACK)),
                ft.DataColumn(ft.Text("Email", color=ft.colors.BLACK)),
                ft.DataColumn(ft.Text("Role", color=ft.colors.BLACK)),
                ft.DataColumn(ft.Text("Department", color=ft.colors.BLACK)),
                ft.DataColumn(ft.Text("Status", color=ft.colors.BLACK)),
                ft.DataColumn(ft.Text("Actions", color=ft.colors.BLACK)),
            ]
            
            rows = []
            for user in self.users:
                # Create row
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(user["username"], color=ft.colors.BLACK)),
                            ft.DataCell(ft.Text(user["full_name"], color=ft.colors.BLACK)),
                            ft.DataCell(ft.Text(user["email"], color=ft.colors.BLACK)),
                            ft.DataCell(ft.Text(user["role"], color=ft.colors.BLACK)),
                            ft.DataCell(ft.Text(user["department"], color=ft.colors.BLACK)),
                            ft.DataCell(
                                ft.Text(
                                    "Active" if user["is_active"] else "Inactive",
                                    color=ft.colors.GREEN if user["is_active"] else ft.colors.RED,
                                )
                            ),
                            ft.DataCell(
                                ft.Row(
                                    [
                                        ft.IconButton(
                                            icon=ft.icons.EDIT,
                                            tooltip="Edit User",
                                            icon_color=ft.colors.BLUE,
                                            data=user["id"],
                                            on_click=self.edit_user,
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.DELETE,
                                            tooltip="Delete User",
                                            icon_color=ft.colors.RED,
                                            data=user["id"],
                                            on_click=self.delete_user,
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.TOGGLE_ON if user["is_active"] else ft.icons.TOGGLE_OFF,
                                            tooltip="Toggle Status",
                                            icon_color=ft.colors.GREEN if user["is_active"] else ft.colors.GREY,
                                            data=user["id"],
                                            on_click=self.toggle_user_status,
                                        ),
                                    ]
                                )
                            ),
                        ]
                    )
                )
            
            return ft.DataTable(
                columns=columns,
                rows=rows,
                border=ft.border.all(1, ft.colors.GREY_400),
                border_radius=10,
                vertical_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
                horizontal_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
                sort_column_index=0,
                sort_ascending=True,
                heading_row_height=70,
                data_row_min_height=60,
                width=1200,
            )
        except Exception as e:
            print(f"Error building user table: {e}")
            return ft.Text(f"Error loading users: {str(e)}")

    def toggle_user_status(self, e):
        """Toggle user active status."""
        try:
            # Get the user ID from the event data
            user_id = e.control.data
            
            # Find the user in the database
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if user:
                # Toggle the user's active status
                user.is_active = not user.is_active
                self.db.commit()
                
                # Update the user in the UI list
                for u in self.users:
                    if u["id"] == str(user_id):
                        u["is_active"] = user.is_active
                        break
                
                # Rebuild the user table
                self.user_table = self.build_user_table()
                
                # Update the controls
                self.controls = [
                    ft.Row(
                        [
                            self.search_field,
                            self.add_user_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=20),
                    self.user_table,
                ]
                
                # Show success message
                status = "activated" if user.is_active else "deactivated"
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"User {user.username} {status} successfully", color=ft.colors.WHITE),
                        bgcolor=ft.colors.GREEN_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("User not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error toggling user status: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error toggling user status", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()

class LocationsTab(ft.Column):
    def __init__(self):
        super().__init__()
        self.page = None
        self.db = SessionLocal()
        
        # Load locations from database
        self.load_locations_from_db()
        
        # Search field
        self.search_field = ft.TextField(
            label="Search Locations",
            icon=ft.icons.SEARCH,
            expand=True,
        )
        
        # Add location button
        self.add_location_button = ft.ElevatedButton(
            text="Add Location",
            icon=ft.icons.ADD_LOCATION,
            on_click=self.show_add_location_dialog
        )
        
        # Location table
        self.location_table = self.build_location_table()
        
        # Set up the controls
        self.controls = [
            ft.Row(
                [
                    self.search_field,
                    self.add_location_button,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Container(height=20),
            self.location_table,
        ]
        self.scroll = ft.ScrollMode.AUTO
    
    def build_location_table(self):
        """Build the location table with current locations."""
        columns = [
            ft.DataColumn(ft.Text("Name", color=ft.colors.BLACK)),
            ft.DataColumn(ft.Text("Description", color=ft.colors.BLACK)),
            ft.DataColumn(ft.Text("Address", color=ft.colors.BLACK)),
            ft.DataColumn(ft.Text("Status", color=ft.colors.BLACK)),
            ft.DataColumn(ft.Text("Actions", color=ft.colors.BLACK)),
        ]
        
        rows = []
        for location in self.locations:
            # Create row
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(location["name"], color=ft.colors.BLACK)),
                        ft.DataCell(ft.Text(location["description"], color=ft.colors.BLACK)),
                        ft.DataCell(ft.Text(location["address"], color=ft.colors.BLACK)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(
                                    "Active" if location["is_active"] else "Inactive",
                                    color=ft.colors.WHITE,
                                    size=12,
                                ),
                                bgcolor=ft.colors.GREEN if location["is_active"] else ft.colors.GREY,
                                border_radius=20,
                                padding=ft.padding.only(left=10, right=10, top=5, bottom=5),
                                alignment=ft.alignment.center,
                            )
                        ),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        tooltip="Edit",
                                        icon_color=ft.colors.BLUE,
                                        on_click=self.edit_location,
                                        data=location["id"],
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        tooltip="Delete",
                                        icon_color=ft.colors.RED,
                                        on_click=self.delete_location,
                                        data=location["id"],
                                    ),
                                ],
                                spacing=0,
                            )
                        ),
                    ]
                )
            )
        
        return ft.DataTable(
            columns=columns,
            rows=rows,
            border=ft.border.all(1, ft.colors.BLUE_GREY_200),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_100),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_100),
            heading_row_height=70,
            data_row_min_height=70,
            data_row_max_height=100,
            column_spacing=5,
        )
    
    def load_locations_from_db(self):
        """Load locations from the database."""
        try:
            # Query all locations from the database
            db_locations = self.db.query(Location).all()
            
            # Convert database locations to dictionary format for the UI
            self.locations = []
            for location in db_locations:
                self.locations.append({
                    "id": str(location.id),
                    "name": location.name,
                    "description": location.description or "",
                    "address": location.description or "",  # Using description as address for now
                    "is_active": location.is_active,
                })
                
        except Exception as e:
            print(f"Error loading locations from database: {e}")
            # Fallback to sample data if database connection fails
            self.locations = [
                {
                    "id": "1",
                    "name": "Main Office",
                    "description": "Headquarters",
                    "address": "123 Main St",
                    "is_active": True,
                },
                {
                    "id": "2",
                    "name": "Factory Floor",
                    "description": "Production area",
                    "address": "Building A, Floor 1",
                    "is_active": True,
                },
            ]
    
    def show_add_location_dialog(self, e):
        """Show dialog to add a new location."""
        if self.page:
            # Create text fields for the dialog
            self.name_field = ft.TextField(label="Location Name", autofocus=True)
            self.description_field = ft.TextField(label="Description")
            self.address_field = ft.TextField(label="Address")
            
            # Create the dialog
            self.add_location_dialog = ft.AlertDialog(
                title=ft.Text("Add New Location"),
                content=ft.Column(
                    [
                        self.name_field,
                        self.description_field,
                        self.address_field,
                    ],
                    width=400,
                    height=300,
                    scroll=ft.ScrollMode.AUTO,
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=self.close_dialog),
                    ft.TextButton("Add", on_click=self.add_location),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            # Show the dialog
            self.page.dialog = self.add_location_dialog
            self.page.dialog.open = True
            self.page.update()
    
    def close_dialog(self, e):
        """Close the dialog."""
        if self.page and self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
    
    def add_location(self, e):
        """Add a new location to the system."""
        # Validate form fields
        if not self.name_field.value:
            # Show error message
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Please enter a location name", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
            return
        
        try:
            # Get the first user as the creator (in a real app, this would be the current user)
            user = self.db.query(User).first()
            if not user:
                raise Exception("No users found in the database")
            
            # Create a new location in the database
            new_location_db = Location(
                name=self.name_field.value,
                description=self.description_field.value,
                created_by_id=user.id,
                is_active=True
            )
            
            self.db.add(new_location_db)
            self.db.commit()
            self.db.refresh(new_location_db)
            
            # Add the new location to the UI list
            new_location = {
                "id": str(new_location_db.id),
                "name": new_location_db.name,
                "description": new_location_db.description or "",
                "address": new_location_db.description or "",  # Using description as address for now
                "is_active": new_location_db.is_active,
            }
            self.locations.append(new_location)
            
        except Exception as e:
            # If database operation fails, show error and add to local list only
            print(f"Error adding location to database: {e}")
            new_location = {
                "id": str(len(self.locations) + 1),
                "name": self.name_field.value,
                "description": self.description_field.value,
                "address": self.address_field.value,
                "is_active": True,
            }
            self.locations.append(new_location)
        
        # Rebuild the location table with the updated data
        self.location_table = self.build_location_table()
        
        # Update the controls
        self.controls = [
            ft.Row(
                [
                    self.search_field,
                    self.add_location_button,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Container(height=20),
            self.location_table,
        ]
        
        # Show success message
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Location {new_location['name']} added successfully", color=ft.colors.WHITE),
                bgcolor=ft.colors.GREEN_600,
            )
            self.page.snack_bar.open = True
            self.page.update()
        
        # Close the dialog
        self.close_dialog(None)
    
    def edit_location(self, e):
        """Edit an existing location."""
        try:
            # Get the location ID from the event data
            location_id = e.control.data
            
            # Find the location in the database
            location = self.db.query(Location).filter(Location.id == location_id).first()
            
            if location:
                # Create text fields for the dialog with current values
                self.edit_name_field = ft.TextField(label="Location Name", value=location.name)
                self.edit_description_field = ft.TextField(label="Description", value=location.description or "")
                self.edit_address_field = ft.TextField(label="Address", value=location.description or "")
                
                # Create the dialog
                self.edit_location_dialog = ft.AlertDialog(
                    title=ft.Text(f"Edit Location: {location.name}"),
                    content=ft.Column(
                        [
                            self.edit_name_field,
                            self.edit_description_field,
                            self.edit_address_field,
                        ],
                        width=400,
                        height=300,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    actions=[
                        ft.TextButton("Cancel", on_click=self.close_dialog),
                        ft.TextButton("Save", on_click=lambda e: self.save_location_edit(location_id)),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                
                # Show the dialog
                if self.page:
                    self.page.dialog = self.edit_location_dialog
                    self.page.dialog.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Location not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error editing location: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error editing location", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
    
    def save_location_edit(self, location_id):
        """Save the edited location."""
        try:
            # Find the location in the database
            location = self.db.query(Location).filter(Location.id == location_id).first()
            
            if location:
                # Update the location in the database
                location.name = self.edit_name_field.value
                location.description = self.edit_description_field.value
                self.db.commit()
                
                # Update the location in the UI list
                for loc in self.locations:
                    if loc["id"] == str(location_id):
                        loc["name"] = location.name
                        loc["description"] = location.description or ""
                        loc["address"] = location.description or ""
                        break
                
                # Rebuild the location table
                self.location_table = self.build_location_table()
                
                # Update the controls
                self.controls = [
                    ft.Row(
                        [
                            self.search_field,
                            self.add_location_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=20),
                    self.location_table,
                ]
                
                # Show success message
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Location {location.name} updated successfully", color=ft.colors.WHITE),
                        bgcolor=ft.colors.GREEN_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Location not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error saving location edit: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error saving location", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        # Close the dialog
        self.close_dialog(None)
    
    def delete_location(self, e):
        """Delete a location."""
        try:
            # Get the location ID from the event data
            location_id = e.control.data
            
            # Find the location in the database
            location = self.db.query(Location).filter(Location.id == location_id).first()
            
            if location:
                # Show confirmation dialog
                if self.page:
                    self.page.dialog = ft.AlertDialog(
                        title=ft.Text(f"Delete Location: {location.name}"),
                        content=ft.Text("Are you sure you want to delete this location? This action cannot be undone."),
                        actions=[
                            ft.TextButton("Cancel", on_click=self.close_dialog),
                            ft.TextButton("Delete", on_click=lambda e: self.confirm_delete_location(location_id)),
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    self.page.dialog.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Location not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error deleting location: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error deleting location", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
                
    def confirm_delete_location(self, location_id):
        """Confirm deletion of a location."""
        try:
            # Find the location in the database
            location = self.db.query(Location).filter(Location.id == location_id).first()
            
            if location:
                # Delete the location from the database
                self.db.delete(location)
                self.db.commit()
                
                # Remove the location from the UI list
                self.locations = [loc for loc in self.locations if loc["id"] != str(location_id)]
                
                # Rebuild the location table
                self.location_table = self.build_location_table()
                
                # Update the controls
                self.controls = [
                    ft.Row(
                        [
                            self.search_field,
                            self.add_location_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=20),
                    self.location_table,
                ]
                
                # Show success message
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Location deleted successfully", color=ft.colors.WHITE),
                        bgcolor=ft.colors.GREEN_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Location not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error confirming delete location: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error deleting location", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        # Close the dialog
        self.close_dialog(None)


class CategoriesTab(ft.Column):
    def __init__(self):
        super().__init__()
        self.page = None
        self.db = SessionLocal()
        
        # Load categories from database
        self.load_categories_from_db()
        
        # Search field
        self.search_field = ft.TextField(
            label="Search Categories",
            icon=ft.icons.SEARCH,
            expand=True,
        )
        
        # Add category button
        self.add_category_button = ft.ElevatedButton(
            text="Add Category",
            icon=ft.icons.ADD_CHART,
        )
        
        # Category table
        self.category_table = self.build_category_table()
        
        # Set up the controls
        self.controls = [
            ft.Row(
                [
                    self.search_field,
                    self.add_category_button,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Container(height=20),
            self.category_table,
        ]
        self.scroll = ft.ScrollMode.AUTO
    
    def build_category_table(self):
        """Build the category table with current categories."""
        columns = [
            ft.DataColumn(ft.Text("Name", color=ft.colors.BLACK)),
            ft.DataColumn(ft.Text("Description", color=ft.colors.BLACK)),
            ft.DataColumn(ft.Text("Subcategories", color=ft.colors.BLACK)),
            ft.DataColumn(ft.Text("Color", color=ft.colors.BLACK)),
            ft.DataColumn(ft.Text("Status", color=ft.colors.BLACK)),
            ft.DataColumn(ft.Text("Actions", color=ft.colors.BLACK)),
        ]
        
        rows = []
        for category in self.categories:
            # Create row
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(category["name"], color=ft.colors.BLACK)),
                        ft.DataCell(ft.Text(category["description"], color=ft.colors.BLACK)),
                        ft.DataCell(ft.Text(", ".join(category["subcategories"]), color=ft.colors.BLACK)),
                        ft.DataCell(
                            ft.Container(
                                bgcolor=category["color"],
                                width=30,
                                height=30,
                                border_radius=15,
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(
                                    "Active" if category["is_active"] else "Inactive",
                                    color=ft.colors.WHITE,
                                    size=12,
                                ),
                                bgcolor=ft.colors.GREEN if category["is_active"] else ft.colors.GREY,
                                border_radius=20,
                                padding=ft.padding.only(left=10, right=10, top=5, bottom=5),
                                alignment=ft.alignment.center,
                            )
                        ),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        tooltip="Edit",
                                        icon_color=ft.colors.BLUE,
                                        on_click=self.edit_category,
                                        data=category["id"],
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        tooltip="Delete",
                                        icon_color=ft.colors.RED,
                                        on_click=self.delete_category,
                                        data=category["id"],
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.BLOCK if category["is_active"] else ft.icons.CHECK_CIRCLE,
                                        tooltip="Disable" if category["is_active"] else "Enable",
                                        icon_color=ft.colors.RED if category["is_active"] else ft.colors.GREEN,
                                        on_click=self.toggle_category_status,
                                        data=category["id"],
                                    ),
                                ],
                                spacing=0,
                            )
                        ),
                    ]
                )
            )
        
        return ft.DataTable(
            columns=columns,
            rows=rows,
            border=ft.border.all(1, ft.colors.BLUE_GREY_200),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_100),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_100),
            heading_row_height=70,
            data_row_min_height=70,
            data_row_max_height=100,
            column_spacing=5,
        )
    
    def load_categories_from_db(self):
        """Load categories from the database."""
        try:
            # Query all categories from the database
            db_categories = self.db.query(Category).all()
            
            # Convert database categories to dictionary format for the UI
            self.categories = []
            for category in db_categories:
                # Map color code to flet color
                color = ft.colors.BLUE
                if category.color_code:
                    if category.color_code.startswith('#'):
                        color = category.color_code
                    else:
                        # Try to map string color names to flet colors
                        color_map = {
                            'red': ft.colors.RED,
                            'blue': ft.colors.BLUE,
                            'green': ft.colors.GREEN,
                            'yellow': ft.colors.YELLOW,
                            'purple': ft.colors.PURPLE,
                            'orange': ft.colors.ORANGE,
                        }
                        color = color_map.get(category.color_code.lower(), ft.colors.BLUE)
                
                self.categories.append({
                    "id": str(category.id),
                    "name": category.name,
                    "description": category.description or "",
                    "color": color,
                    "subcategories": [],  # No subcategories in the database model yet
                    "is_active": category.is_active,
                })
                
        except Exception as e:
            print(f"Error loading categories from database: {e}")
            # Fallback to sample data if database connection fails
            self.categories = [
                {
                    "id": "1",
                    "name": "Hardware",
                    "description": "Physical equipment issues",
                    "color": ft.colors.RED,
                    "subcategories": ["Computers", "Printers"],
                    "is_active": True,
                },
                {
                    "id": "2",
                    "name": "Software",
                    "description": "Application and OS issues",
                    "color": ft.colors.BLUE,
                    "subcategories": ["Operating Systems", "Apps"],
                    "is_active": True,
                },
            ]
    
    def close_dialog(self, e):
        """Close the dialog."""
        if self.page and self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
            
    def show_add_category_dialog(self, e):
        """Show dialog to add a new category."""
        if self.page:
            # Create text fields for the dialog
            self.name_field = ft.TextField(label="Category Name", autofocus=True)
            self.description_field = ft.TextField(label="Description")
            
            # Create color dropdown
            self.color_dropdown = ft.Dropdown(
                label="Color",
                options=[
                    ft.dropdown.Option("RED", text="Red"),
                    ft.dropdown.Option("BLUE", text="Blue"),
                    ft.dropdown.Option("GREEN", text="Green"),
                    ft.dropdown.Option("YELLOW", text="Yellow"),
                    ft.dropdown.Option("PURPLE", text="Purple"),
                    ft.dropdown.Option("ORANGE", text="Orange"),
                ],
                value="BLUE",
            )
            
            # Create the dialog
            self.add_category_dialog = ft.AlertDialog(
                title=ft.Text("Add New Category"),
                content=ft.Column(
                    [
                        self.name_field,
                        self.description_field,
                        self.color_dropdown,
                    ],
                    width=400,
                    height=300,
                    scroll=ft.ScrollMode.AUTO,
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=self.close_dialog),
                    ft.TextButton("Add", on_click=self.add_category),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            # Show the dialog
            self.page.dialog = self.add_category_dialog
            self.page.dialog.open = True
            self.page.update()
    
    def add_category(self, e):
        """Add a new category to the system."""
        # Validate form fields
        if not self.name_field.value:
            # Show error message
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Please enter a category name", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
            return
        
        try:
            # Get the first user as the creator (in a real app, this would be the current user)
            user = self.db.query(User).first()
            if not user:
                raise Exception("No users found in the database")
            
            # Map color string to color code
            color_code = self.color_dropdown.value.lower()
            
            # Create a new category in the database
            new_category_db = Category(
                name=self.name_field.value,
                description=self.description_field.value,
                color_code=color_code,
                created_by_id=user.id,
                is_active=True
            )
            
            self.db.add(new_category_db)
            self.db.commit()
            self.db.refresh(new_category_db)
            
            # Map color to flet color
            color_map = {
                'red': ft.colors.RED,
                'blue': ft.colors.BLUE,
                'green': ft.colors.GREEN,
                'yellow': ft.colors.YELLOW,
                'purple': ft.colors.PURPLE,
                'orange': ft.colors.ORANGE,
            }
            color = color_map.get(color_code.lower(), ft.colors.BLUE)
            
            # Add the new category to the UI list
            new_category = {
                "id": str(new_category_db.id),
                "name": new_category_db.name,
                "description": new_category_db.description or "",
                "color": color,
                "subcategories": [],
                "is_active": new_category_db.is_active,
            }
            self.categories.append(new_category)
            
        except Exception as e:
            # If database operation fails, show error and add to local list only
            print(f"Error adding category to database: {e}")
            new_category = {
                "id": str(len(self.categories) + 1),
                "name": self.name_field.value,
                "description": self.description_field.value,
                "color": getattr(ft.colors, self.color_dropdown.value),
                "subcategories": [],
                "is_active": True,
            }
            self.categories.append(new_category)
        
        # Rebuild the category table with the updated data
        self.category_table = self.build_category_table()
        
        # Update the controls
        self.controls = [
            ft.Row(
                [
                    self.search_field,
                    self.add_category_button,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Container(height=20),
            self.category_table,
        ]
        
        # Show success message
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Category {new_category['name']} added successfully", color=ft.colors.WHITE),
                bgcolor=ft.colors.GREEN_600,
            )
            self.page.snack_bar.open = True
            self.page.update()
        
        # Close the dialog
        self.close_dialog(None)
    
    def edit_category(self, e):
        """Edit an existing category."""
        try:
            # Get the category ID from the event data
            category_id = e.control.data
            
            # Find the category in the database
            category = self.db.query(Category).filter(Category.id == category_id).first()
            
            if category:
                # Get color value for dropdown
                color_value = "BLUE"
                if category.color_code:
                    color_value = category.color_code.upper()
                
                # Create text fields for the dialog with current values
                self.edit_name_field = ft.TextField(label="Category Name", value=category.name)
                self.edit_description_field = ft.TextField(label="Description", value=category.description or "")
                
                # Create color dropdown
                self.edit_color_dropdown = ft.Dropdown(
                    label="Color",
                    options=[
                        ft.dropdown.Option("RED", text="Red"),
                        ft.dropdown.Option("BLUE", text="Blue"),
                        ft.dropdown.Option("GREEN", text="Green"),
                        ft.dropdown.Option("YELLOW", text="Yellow"),
                        ft.dropdown.Option("PURPLE", text="Purple"),
                        ft.dropdown.Option("ORANGE", text="Orange"),
                    ],
                    value=color_value,
                )
                
                # Create the dialog
                self.edit_category_dialog = ft.AlertDialog(
                    title=ft.Text(f"Edit Category: {category.name}"),
                    content=ft.Column(
                        [
                            self.edit_name_field,
                            self.edit_description_field,
                            self.edit_color_dropdown,
                        ],
                        width=400,
                        height=300,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    actions=[
                        ft.TextButton("Cancel", on_click=self.close_dialog),
                        ft.TextButton("Save", on_click=lambda e: self.save_category_edit(category_id)),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                
                # Show the dialog
                if self.page:
                    self.page.dialog = self.edit_category_dialog
                    self.page.dialog.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Category not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error editing category: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error editing category", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
    
    def save_category_edit(self, category_id):
        """Save the edited category."""
        try:
            # Find the category in the database
            category = self.db.query(Category).filter(Category.id == category_id).first()
            
            if category:
                # Update the category in the database
                category.name = self.edit_name_field.value
                category.description = self.edit_description_field.value
                category.color_code = self.edit_color_dropdown.value.lower()
                self.db.commit()
                
                # Map color to flet color
                color_map = {
                    'red': ft.colors.RED,
                    'blue': ft.colors.BLUE,
                    'green': ft.colors.GREEN,
                    'yellow': ft.colors.YELLOW,
                    'purple': ft.colors.PURPLE,
                    'orange': ft.colors.ORANGE,
                }
                color = color_map.get(category.color_code.lower(), ft.colors.BLUE)
                
                # Update the category in the UI list
                for cat in self.categories:
                    if cat["id"] == str(category_id):
                        cat["name"] = category.name
                        cat["description"] = category.description or ""
                        cat["color"] = color
                        break
                
                # Rebuild the category table
                self.category_table = self.build_category_table()
                
                # Update the controls
                self.controls = [
                    ft.Row(
                        [
                            self.search_field,
                            self.add_category_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=20),
                    self.category_table,
                ]
                
                # Show success message
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Category {category.name} updated successfully", color=ft.colors.WHITE),
                        bgcolor=ft.colors.GREEN_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Category not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error saving category edit: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error saving category", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        # Close the dialog
        self.close_dialog(None)
    
    def delete_category(self, e):
        """Delete a category."""
        try:
            # Get the category ID from the event data
            category_id = e.control.data
            
            # Find the category in the database
            category = self.db.query(Category).filter(Category.id == category_id).first()
            
            if category:
                # Show confirmation dialog
                if self.page:
                    self.page.dialog = ft.AlertDialog(
                        title=ft.Text(f"Delete Category: {category.name}"),
                        content=ft.Text("Are you sure you want to delete this category? This action cannot be undone."),
                        actions=[
                            ft.TextButton("Cancel", on_click=self.close_dialog),
                            ft.TextButton("Delete", on_click=lambda e: self.confirm_delete_category(category_id)),
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    self.page.dialog.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Category not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error deleting category: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error deleting category", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
    
    def confirm_delete_category(self, category_id):
        """Confirm deletion of a category."""
        try:
            # Find the category in the database
            category = self.db.query(Category).filter(Category.id == category_id).first()
            
            if category:
                # Delete the category from the database
                self.db.delete(category)
                self.db.commit()
                
                # Remove the category from the UI list
                self.categories = [cat for cat in self.categories if cat["id"] != str(category_id)]
                
                # Rebuild the category table
                self.category_table = self.build_category_table()
                
                # Update the controls
                self.controls = [
                    ft.Row(
                        [
                            self.search_field,
                            self.add_category_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=20),
                    self.category_table,
                ]
                
                # Show success message
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Category deleted successfully", color=ft.colors.WHITE),
                        bgcolor=ft.colors.GREEN_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Category not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error confirming delete category: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error deleting category", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        # Close the dialog
        self.close_dialog(None)
    
    def toggle_category_status(self, e):
        """Toggle category active status."""
        try:
            # Get the category ID from the event data
            category_id = e.control.data
            
            # Find the category in the database
            category = self.db.query(Category).filter(Category.id == category_id).first()
            
            if category:
                # Toggle the category's active status
                category.is_active = not category.is_active
                self.db.commit()
                
                # Update the category in the UI list
                for cat in self.categories:
                    if cat["id"] == str(category_id):
                        cat["is_active"] = category.is_active
                        break
                
                # Rebuild the category table
                self.category_table = self.build_category_table()
                
                # Update the controls
                self.controls = [
                    ft.Row(
                        [
                            self.search_field,
                            self.add_category_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=20),
                    self.category_table,
                ]
                
                # Show success message
                status = "activated" if category.is_active else "deactivated"
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Category {category.name} {status} successfully", color=ft.colors.WHITE),
                        bgcolor=ft.colors.GREEN_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Category not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error toggling category status: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error toggling category status", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()


class SystemSettingsTab(ft.Column):
    def __init__(self):
        super().__init__()
        self.page = None
        
    def backup_now(self, e):
        """Perform a manual backup."""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Backup initiated successfully", color=ft.colors.WHITE),
                bgcolor=ft.colors.BLUE_600,
            )
            self.page.snack_bar.open = True
            self.page.update()
            
    def save_settings(self, e):
        """Save system settings."""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Settings saved successfully", color=ft.colors.WHITE),
                bgcolor=ft.colors.GREEN_600,
            )
            self.page.snack_bar.open = True
            self.page.update()
        
        # Application settings
        self.app_name_field = ft.TextField(
            label="Application Name",
            value="PreventPlus",
            width=300,
        )
        
        self.company_name_field = ft.TextField(
            label="Company Name",
            value="Acme Corporation",
            width=300,
        )
        
        self.logo_upload_button = ft.ElevatedButton(
            text="Upload Logo",
            icon=ft.icons.UPLOAD_FILE,
        )
        
        self.theme_dropdown = ft.Dropdown(
            label="Default Theme",
            width=300,
            options=[
                ft.dropdown.Option("light", "Light"),
                ft.dropdown.Option("dark", "Dark"),
                ft.dropdown.Option("system", "System Default"),
            ],
            value="light",
        )
        
        # Email settings
        self.smtp_server_field = ft.TextField(
            label="SMTP Server",
            value="smtp.example.com",
            width=300,
        )
        
        self.smtp_port_field = ft.TextField(
            label="SMTP Port",
            value="587",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        self.smtp_username_field = ft.TextField(
            label="SMTP Username",
            value="user@example.com",
            width=300,
        )
        
        self.smtp_password_field = ft.TextField(
            label="SMTP Password",
            password=True,
            can_reveal_password=True,
            width=300,
        )
        
        # Notification settings
        self.enable_email_notifications = ft.Row(
            [
                ft.Text("Enable Email Notifications"),
                ft.Switch(value=True),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        self.enable_in_app_notifications = ft.Row(
            [
                ft.Text("Enable In-App Notifications"),
                ft.Switch(value=True),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        # Backup settings
        self.auto_backup_switch = ft.Row(
            [
                ft.Text("Enable Automatic Backups"),
                ft.Switch(value=True),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        self.backup_frequency_dropdown = ft.Dropdown(
            label="Backup Frequency",
            width=300,
            options=[
                ft.dropdown.Option("daily", "Daily"),
                ft.dropdown.Option("weekly", "Weekly"),
                ft.dropdown.Option("monthly", "Monthly"),
            ],
            value="weekly",
        )
        
        self.backup_retention_field = ft.TextField(
            label="Backup Retention (days)",
            value="30",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        self.backup_now_button = ft.OutlinedButton(
            text="Backup Now",
            icon=ft.icons.BACKUP,
            on_click=self.backup_now
        )
        
        # Save settings button
        self.save_settings_button = ft.ElevatedButton(
            text="Save Settings",
            icon=ft.icons.SAVE,
            bgcolor=ft.colors.GREEN,
            color=ft.colors.WHITE,
            on_click=self.save_settings
        )
        
        # Set up the controls
        self.controls = [self.build_content()]
        self.scroll = ft.ScrollMode.AUTO
    
    def build_content(self):
        return ft.Column(
            [
                # Application Settings
                ft.Text(
                    "Application Settings",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(height=10),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                self.app_name_field,
                                self.company_name_field,
                                self.logo_upload_button,
                                self.theme_dropdown,
                            ],
                            spacing=10,
                        ),
                        padding=ft.padding.all(20),
                    ),
                ),
                ft.Container(height=30),
                
                # Email Settings
                ft.Text(
                    "Email Settings",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(height=10),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                self.smtp_server_field,
                                self.smtp_port_field,
                                self.smtp_username_field,
                                self.smtp_password_field,
                            ],
                            spacing=10,
                        ),
                        padding=ft.padding.all(20),
                    ),
                ),
                ft.Container(height=30),
                
                # Notification Settings
                ft.Text(
                    "Notification Settings",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(height=10),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                self.enable_email_notifications,
                                self.enable_in_app_notifications,
                            ],
                            spacing=10,
                        ),
                        padding=ft.padding.all(20),
                    ),
                ),
                ft.Container(height=30),
                
                # Backup Settings
                ft.Text(
                    "Backup Settings",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(height=10),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                self.auto_backup_switch,
                                self.backup_frequency_dropdown,
                                self.backup_retention_field,
                                self.backup_now_button,
                            ],
                            spacing=10,
                        ),
                        padding=ft.padding.all(20),
                    ),
                ),
                ft.Container(height=30),
                
                # Save Button
                self.save_settings_button,
            ],
            scroll=ft.ScrollMode.AUTO,
        )


class SettingsView(ft.Container):
    def __init__(self):
        super().__init__()
        self._page = None
        
        # Create tab contents
        self.user_management_tab = UserManagementTab()
        self.locations_tab = LocationsTab()
        self.categories_tab = CategoriesTab()
        self.system_settings_tab = SystemSettingsTab()
        
        # Set up on_mount event handler
        self.on_mount = lambda _: self.did_mount()
        
    @property
    def page(self):
        return self._page
        
    @page.setter
    def page(self, value):
        print(f"SettingsView: Setting page to {value}")
        self._page = value
        # Pass the page to all tabs immediately when it's set
        if value is not None:
            print("SettingsView: Passing page to all tabs")
            self.user_management_tab.page = value
            self.locations_tab.page = value
            self.categories_tab.page = value
            self.system_settings_tab.page = value
        
        # Initialize tabs
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Users",
                    icon=ft.icons.PEOPLE,
                    content=ft.Container(
                        content=self.user_management_tab,
                        padding=ft.padding.only(top=20),
                    ),
                ),
                ft.Tab(
                    text="Locations",
                    icon=ft.icons.LOCATION_ON,
                    content=ft.Container(
                        content=self.locations_tab,
                        padding=ft.padding.only(top=20),
                    ),
                ),
                ft.Tab(
                    text="Categories",
                    icon=ft.icons.CATEGORY,
                    content=ft.Container(
                        content=self.categories_tab,
                        padding=ft.padding.only(top=20),
                    ),
                ),
                ft.Tab(
                    text="System",
                    icon=ft.icons.SETTINGS,
                    content=ft.Container(
                        content=self.system_settings_tab,
                        padding=ft.padding.only(top=20),
                    ),
                ),
            ],
            expand=1,
        )
        
        # Set up the container
        self.content = self.build_content()
        self.expand = True
    
    def did_mount(self):
        """Called when the view is mounted to the page."""
        print("SettingsView.did_mount called")
        # No need to pass the page to tabs here as it's done in the page setter
        # Just make sure we have a page
        if self.page is None:
            print("WARNING: self.page is None in did_mount")
        else:
            print(f"SettingsView.did_mount: self.page is {self.page}")
            print(f"UserManagementTab.page is {self.user_management_tab.page}")
    
    def build_content(self):
        return ft.Column(
            [
                ft.Text(
                    "Settings",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(height=20),
                self.tabs,
            ],
        )
