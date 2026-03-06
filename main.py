import flet as ft
import urllib.request
import time
import json
import os

# iOS 18 Apple Dark Theme Palette
IOS_BG = "#000000"
IOS_CARD = "#1C1C1E"
IOS_BLUE = "#007AFF"
IOS_GRAY = "#8E8E93"
IOS_SECONDARY_BG = "#161617" 
IOS_DIVIDER = "#38383A"

DEFAULT_REPOS = ["https://raw.githubusercontent.com/P4Installer/asda/main/repo.json"]
PROXY_ESIGN_URL = "https://applejr.net/post/esignpwerchina.plist"
SAVE_FILE = "repos_config.json"

def main(page: ft.Page):
    page.title = "TrollStore"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = IOS_BG
    page.padding = 0
    
    page.fonts = {
        "SF Pro": "https://github.com/google/fonts/raw/main/ofl/inter/Inter-VariableFont_slnt%2Cwght.ttf",
    }
    page.theme = ft.Theme(font_family="SF Pro")

    user_repos = []

    def load_from_file():
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f: return json.load(f)
            except: return []
        return []

    def open_url(url):
        page.launch_url(url)

    def create_app_tile(name, desc, color, url, is_last=False):
        icon = ft.Container(
            content=ft.Text(name[0].upper(), weight="bold", size=22, color="white"),
            width=54, height=54, border_radius=12, 
            alignment=ft.Alignment(0, 0) 
        )
        
        if isinstance(color, list):
            icon.gradient = ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=color
            )
        else:
            icon.bgcolor = color or "#2fb5d2"

        tile = ft.Container(
            content=ft.Row([
                icon,
                ft.Column([
                    ft.Text(name, size=17, weight="w600", color="white"),
                    ft.Text(desc, size=13, color=IOS_GRAY, width=180, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                ], expand=True, spacing=1),
                ft.Container(
                    content=ft.Text("GET", color=IOS_BLUE, weight="bold", size=13),
                    bgcolor="#2c2c2e", 
                    padding=ft.Padding(16, 6, 16, 6), 
                    border_radius=18,
                    on_click=lambda _: open_url(url)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.Padding(0, 10, 0, 10)
        )
        
        if not is_last:
            return ft.Column([tile, ft.Divider(height=1, color=IOS_DIVIDER, thickness=0.5)], spacing=0)
        return tile

    repo_apps_list = ft.Column(spacing=0)
    repo_sources_list = ft.Column(spacing=0)

    apps_view = ft.Column(
        scroll=ft.ScrollMode.HIDDEN,
        expand=True,
        controls=[
            ft.Container(ft.Text("Apps", size=34, weight="bold"), padding=ft.Padding(0, 40, 0, 10)),
            ft.Container(ft.Text("SYSTEM", size=13, color=IOS_GRAY), padding=ft.Padding(10, 0, 0, 5)),
            ft.Container(
                content=ft.Column([
                    create_app_tile("ESign", "Signed Proxy Installer", ["#5856d6", "#007AFF"], f"itms-services://?action=download-manifest&url={PROXY_ESIGN_URL}", True)
                ], spacing=0),
                bgcolor=IOS_CARD, border_radius=12, padding=ft.Padding(15, 0, 15, 0)
            ),
            ft.Container(height=10),
            repo_apps_list,
            ft.Container(height=80) 
        ]
    )

    repo_input = ft.TextField(
        hint_text="Enter repository URL", 
        expand=True, 
        bgcolor=IOS_CARD, 
        border_radius=10, 
        border_color="transparent",
        text_size=14,
        content_padding=12
    )
    
    sources_view = ft.Column(
        scroll=ft.ScrollMode.HIDDEN, 
        expand=True, 
        visible=False,
        controls=[
            ft.Container(ft.Text("Sources", size=34, weight="bold"), padding=ft.Padding(0, 40, 0, 10)),
            ft.Row([
                repo_input, 
                ft.IconButton(ft.Icons.ADD_CIRCLE, on_click=lambda e: add_repo_click(e), icon_color=IOS_BLUE, icon_size=30)
            ]),
            ft.Container(height=20),
            ft.Container(ft.Text("INSTALLED REPOS", size=13, color=IOS_GRAY), padding=ft.Padding(10, 0, 0, 5)),
            ft.Container(repo_sources_list, bgcolor=IOS_CARD, border_radius=12, padding=ft.Padding(15, 0, 15, 0)),
            ft.Container(height=80)
        ]
    )

    def fetch_repo_data():
        repo_apps_list.controls = [ft.Container(ft.ProgressRing(color=IOS_BLUE), alignment=ft.Alignment(0, 0), padding=40)]
        page.update()

        all_urls = list(set(DEFAULT_REPOS + user_repos))
        loaded_apps = []
        loaded_sources = []

        for url in all_urls:
            try:
                req_url = f"{url}?t={int(time.time())}"
                with urllib.request.urlopen(req_url, timeout=5) as response:
                    data = json.loads(response.read().decode())
                    
                    loaded_sources.append(ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.LANGUAGE, color=IOS_BLUE),
                            title=ft.Text(url, size=14, color="white", no_wrap=True, overflow="ellipsis"),
                            trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, color=IOS_DIVIDER),
                        ),
                        ft.Divider(height=1, color=IOS_DIVIDER, thickness=0.5)
                    ], spacing=0))

                    if "packages" in data:
                        loaded_apps.append(ft.Container(ft.Text(data.get("repo_name", "Third-party").upper(), size=13, color=IOS_GRAY), padding=ft.Padding(10, 20, 0, 5)))
                        pkgs = data["packages"]
                        repo_container = ft.Column([
                            create_app_tile(p['name'], p['description'], p.get("color"), p['url'], j==len(pkgs)-1) 
                            for j, p in enumerate(pkgs)
                        ], spacing=0)
                        loaded_apps.append(ft.Container(content=repo_container, bgcolor=IOS_CARD, border_radius=12, padding=ft.Padding(15, 0, 15, 0)))
            except Exception as e:
                print(f"Error loading {url}: {e}")

        repo_apps_list.controls = loaded_apps if loaded_apps else [ft.Container(ft.Text("No sources found", color=IOS_GRAY), alignment=ft.Alignment(0, 0), padding=40)]
        repo_sources_list.controls = loaded_sources
        page.update()

    def add_repo_click(e):
        u = repo_input.value.strip()
        if u and u not in user_repos:
            user_repos.append(u)
            with open(SAVE_FILE, "w") as f: json.dump(user_repos, f)
            repo_input.value = ""
            page.run_thread(fetch_repo_data)

    def switch_tab(index):
        apps_view.visible = (index == 0)
        sources_view.visible = (index == 1)
        for i, item in enumerate(nav_items.controls):
            is_selected = (i == index)
            item.content.controls[0].color = IOS_BLUE if is_selected else IOS_GRAY
            item.content.controls[1].color = IOS_BLUE if is_selected else IOS_GRAY
        page.update()

    def nav_item(icon, label, index):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=23, color=IOS_GRAY),
                ft.Text(label, size=10, weight="w500", color=IOS_GRAY)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
            on_click=lambda _: switch_tab(index),
            expand=True,
            height=65
        )

    nav_items = ft.Row([
        nav_item(ft.Icons.GRID_VIEW_ROUNDED, "Apps", 0),
        nav_item(ft.Icons.FORMAT_LIST_BULLETED_ROUNDED, "Sources", 1)
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=0)

    nav_items.controls[0].content.controls[0].color = IOS_BLUE
    nav_items.controls[0].content.controls[1].color = IOS_BLUE

    ios_tab_bar = ft.Container(
        content=nav_items,
        bgcolor=IOS_SECONDARY_BG,
        height=65,
        padding=0,
        border=ft.Border(top=ft.BorderSide(0.5, IOS_DIVIDER)),
    )

    user_repos.extend(load_from_file())
    
    page.add(
        ft.Stack([
            ft.SafeArea(
                ft.Container(
                    content=ft.Stack([apps_view, sources_view]),
                    padding=ft.Padding(20, 0, 20, 0),
                    expand=True
                ),
                expand=True
            ),
            ft.Container(
                content=ios_tab_bar,
                alignment=ft.Alignment(0, 1),
            )
        ], expand=True)
    )
    page.run_thread(fetch_repo_data)

if __name__ == "__main__":
    ft.run(main)