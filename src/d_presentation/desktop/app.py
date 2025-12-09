import flet as ft
from src.a_domain.types.enums import AiProvider, DatabaseProvider
from src.d_presentation.desktop.view_models.ui_vm import AdminViewModel


def main(page: ft.Page):
    page.title = "ChatFriend Admin Console"
    page.theme_mode = ft.ThemeMode.DARK

    # Window size configuration
    page.window.width = 1000
    page.window.height = 800

    vm = AdminViewModel()
    env_data, app_data, instruct_data = vm.load_data()

    # ---------------------------------------------------------------------------- #
    #                                 UI Components                                #
    # ---------------------------------------------------------------------------- #
    status_indicator = ft.Icon(name="circle", color="red")

    status_text = ft.Text("Server Stopped", color="red", weight=ft.FontWeight.BOLD)

    log_view = ft.Column(scroll=ft.ScrollMode.ALWAYS, auto_scroll=True)

    def on_log(line: str):
        log_view.controls.append(ft.Text(line.strip(), font_family="Consolas", size=12))
        page.update()

    vm.on_log_received = on_log

    def toggle_server(e):
        vm.toggle_server()
        is_running = vm.process_manager.is_running

        status_indicator.color = "green" if is_running else "red"
        status_text.value = "Server Running" if is_running else "Server Stopped"
        status_text.color = "green" if is_running else "red"

        btn_server.text = "Stop Server" if is_running else "Start Server"
        # [FIX] Use strings "stop" and "play_arrow"
        btn_server.icon = "stop" if is_running else "play_arrow"
        page.update()

    btn_server = ft.ElevatedButton(
        "Start Server",
        icon="play_arrow",  # [FIX] String literal
        on_click=toggle_server,
        style=ft.ButtonStyle(color="white", bgcolor="blue700"),
    )

    # 2. Config Controls
    dd_ai_provider = ft.Dropdown(
        label="Active AI Model",
        value=app_data.get("active_model", AiProvider.GROK),
        options=[ft.dropdown.Option(p.value) for p in AiProvider],
    )

    dd_db_provider = ft.Dropdown(
        label="Database Provider",
        value=app_data.get("database_provider", DatabaseProvider.MEMORY),
        options=[ft.dropdown.Option(p.value) for p in DatabaseProvider],
    )

    txt_system_prompt = ft.TextField(
        label="System Prompt (AI Personality)",
        value=instruct_data.get("system_prompt", ""),
        multiline=True,
        min_lines=10,
        max_lines=15,
        text_size=14,
    )

    # 3. Secrets Controls
    txt_openai_key = ft.TextField(
        label="OpenAI API Key", password=True, can_reveal_password=True, value=env_data.get("OPENAI_API_KEY", "")
    )
    txt_grok_key = ft.TextField(
        label="Grok API Key", password=True, can_reveal_password=True, value=env_data.get("GROK_API_KEY", "")
    )
    txt_line_token = ft.TextField(
        label="LINE Channel Access Token",
        password=True,
        can_reveal_password=True,
        value=env_data.get("LINE_CHANNEL_ACCESS_TOKEN", ""),
    )
    txt_line_secret = ft.TextField(
        label="LINE Channel Secret",
        password=True,
        can_reveal_password=True,
        value=env_data.get("LINE_CHANNEL_SECRET", ""),
    )

    def save_settings(e):
        # Update Data Objects
        new_env = {
            "OPENAI_API_KEY": txt_openai_key.value,
            "GROK_API_KEY": txt_grok_key.value,
            "LINE_CHANNEL_ACCESS_TOKEN": txt_line_token.value,
            "LINE_CHANNEL_SECRET": txt_line_secret.value,
        }
        app_data["active_model"] = dd_ai_provider.value
        app_data["database_provider"] = dd_db_provider.value
        instruct_data["system_prompt"] = txt_system_prompt.value

        vm.save_all(new_env, app_data, instruct_data)

        snack = ft.SnackBar(ft.Text("Settings saved! If server is running, it will hot-reload."))
        page.overlay.append(snack)
        snack.open = True
        page.update()

    # ---------------------------------------------------------------------------- #
    #                                    Layout                                    #
    # ---------------------------------------------------------------------------- #
    tab_dashboard = ft.Container(
        padding=20,
        content=ft.Column(
            [
                ft.Row(
                    [status_indicator, status_text, ft.Container(width=20), btn_server],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Divider(),
                ft.Text("Live Logs:", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=log_view, bgcolor="black87", border_radius=10, padding=10, height=500, expand=True
                ),
            ]
        ),
    )

    tab_settings = ft.Container(
        padding=20,
        content=ft.Column(
            [
                ft.Text("Application Logic", size=20, weight=ft.FontWeight.BOLD),
                dd_ai_provider,
                dd_db_provider,
                ft.Divider(),
                ft.Text("AI Persona", size=20, weight=ft.FontWeight.BOLD),
                txt_system_prompt,
                ft.ElevatedButton("Save Changes", icon="save", on_click=save_settings),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    tab_secrets = ft.Container(
        padding=20,
        content=ft.Column(
            [
                ft.Text("Security Credentials (.env)", size=20, weight=ft.FontWeight.BOLD, color="red400"),
                ft.Text("These values are stored locally in .env file.", size=12, italic=True),
                ft.Divider(),
                txt_openai_key,
                txt_grok_key,
                txt_line_token,
                txt_line_secret,
                ft.ElevatedButton("Save Secrets", icon="save", on_click=save_settings),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    t = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Dashboard", icon="dashboard", content=tab_dashboard),
            ft.Tab(text="Settings", icon="settings", content=tab_settings),
            ft.Tab(text="Secrets", icon="lock", content=tab_secrets),
        ],
        expand=1,
    )

    page.add(t)


if __name__ == "__main__":
    ft.app(target=main)
