import flet as ft
import threading
import warnings
from auth_handler import start_login_flow
from anilist_client import AniListClient
from config_manager import ConfigManager
from logic_thread import WorkerThread

warnings.filterwarnings("ignore", category=DeprecationWarning)

client = None
current_user = None
sync_worker = None


def main(page: ft.Page):
    page.title = "Anime Sync Tool"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 450
    page.window_height = 800
    page.scroll = ft.ScrollMode.AUTO

    cm = ConfigManager()

    def app_log(message):
        print(message)
        txt_logs.value += f"{message}\n"
        page.update()

    txt_status = ft.Text("Not logged in", color="red400")
    txt_user_info = ft.Text("")
    txt_logs = ft.Text("", size=12, font_family="Consolas")
    log_container = ft.Container(
        content=ft.Column([txt_logs], scroll=ft.ScrollMode.ALWAYS),
        height=200,
        border=ft.Border.all(1, "#333333"),
        border_radius=5,
        padding=10,
        bgcolor="#1a1a1a"
    )

    def save_cr_token(e):
        token_val = tf_cr_token.value.strip()
        if token_val.startswith('"') and token_val.endswith('"'):
            token_val = token_val[1:-1]

        cm.set("CR_TOKEN", token_val)
        btn_save_cr.text = "Saved!"
        btn_save_cr.icon = "check"
        page.update()
        threading.Timer(2.0, reset_save_btn).start()

    def reset_save_btn():
        btn_save_cr.text = "Save Token"
        btn_save_cr.icon = "save"
        page.update()

    tf_cr_token = ft.TextField(
        label="Crunchyroll Token (etp_rt cookie or Bearer)",
        password=True,
        can_reveal_password=True,
        text_size=12,
        value=cm.get("CR_TOKEN", "")
    )
    btn_save_cr = ft.ElevatedButton(
        "Save Token",
        icon="save",
        on_click=save_cr_token
    )
    def app_log(message):
        print(message)
        txt_logs.value += f"{message}\n"
        page.update()

    async def refresh_ui_state(args=None):
        global client, current_user

        if client and client.token:
            user = client.validate_token()
            if user:
                current_user = user
                txt_status.value = "Connected to AniList"
                txt_status.color = "green400"
                txt_user_info.value = f"Logged in as: {user['name']} (ID: {user['id']})"

                btn_login.disabled = True
                btn_sync.disabled = False
                btn_logout.disabled = False
            else:
                txt_status.value = "Invalid or Expired Token"
                txt_status.color = "red400"
                ConfigManager.clear_token()
        else:
            txt_status.value = "Not Logged In"
            txt_status.color = "red400"

        page.update()

    def on_token_received(token):
        global client
        app_log("🔑 Token received!")
        ConfigManager.save_token(token)
        client = AniListClient(token=token, log_func=app_log)
        page.run_task(refresh_ui_state)

    def login_click(e):
        txt_status.value = "Waiting for browser login..."
        txt_status.color = "yellow400"
        page.update()
        t = threading.Thread(target=start_login_flow, args=(on_token_received,))
        t.daemon = True
        t.start()

    def logout_click(e):
        global client, current_user
        ConfigManager.clear_token()
        client = None
        current_user = None

        txt_status.value = "Logged Out"
        txt_status.color = "red400"
        txt_user_info.value = ""
        txt_logs.value = ""

        btn_login.disabled = False
        btn_sync.disabled = True
        btn_logout.disabled = True
        page.update()

    def on_sync_done():
        app_log("🏁 Task Complete.")
        btn_sync.disabled = False
        page.update()

    def sync_click(e):
        global sync_worker
        if not cm.get("CR_TOKEN"):
            app_log("❌ Error: Please save your Crunchyroll Token first!")
            return

        if not client or not client.token:
            return

        btn_sync.disabled = True
        txt_logs.value = ""
        page.update()

        sync_worker = WorkerThread(
            mode="full_sync",
            token=client.token,
            log_callback=app_log,
            done_callback=on_sync_done
        )
        sync_worker.start()

    def check_saved_login():
        saved_token = ConfigManager.get_token()
        if saved_token:
            app_log("💾 Found saved AniList token...")
            on_token_received(saved_token)

    btn_login = ft.ElevatedButton(
        content=ft.Text("Login with AniList"),
        on_click=login_click,
        disabled=False,
    )

    btn_logout = ft.ElevatedButton(
        content=ft.Text("Logout", color="red400"),
        on_click=logout_click,
        disabled=True,
    )

    btn_sync = ft.ElevatedButton(
        content=ft.Text("Sync Crunchyroll -> AniList"),
        on_click=sync_click,
        disabled=True,
        bgcolor=ft.Colors.BLUE_900,
        color=ft.Colors.WHITE
    )

    container_border = ft.Border.all(1, "#333333")

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text("Anime Sync Tool", size=30, weight=ft.FontWeight.BOLD),
                    ft.Divider(),

                    ft.Text("1. AniList Connection", weight=ft.FontWeight.BOLD),
                    txt_status,
                    txt_user_info,
                    ft.Row([btn_login, btn_logout], alignment=ft.MainAxisAlignment.CENTER),

                    ft.Divider(),

                    ft.Text("2. Crunchyroll Settings", weight=ft.FontWeight.BOLD),
                    tf_cr_token,
                    btn_save_cr,

                    ft.Divider(),

                    ft.Text("3. Actions", weight=ft.FontWeight.BOLD),
                    btn_sync,
                    log_container,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15
            ),
            padding=30,
            border=container_border,
            border_radius=10,
            alignment=ft.Alignment(0, 0)
        )
    )

    check_saved_login()


ft.run(main)