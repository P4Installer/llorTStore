import flet as ft
import httpx
import asyncio
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

async def main(page: ft.Page):
    page.title = "TrollStore"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = IOS_BG
    page.padding = 0
    
    # Custom SF Pro-like font (Inter is very similar)
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

    async def open_url(url):
        await page.launch_url(url)

    # iOS 18 Style App Tile
    def create_app_tile(name, desc, color, url, is_last=False):
        # FIXED: Using ft.Alignment(0, 0) for center alignment
        icon = ft.Container(
            content=ft.Text(name[0].upper(), weight="bold", size=22, color="white"),
            width=54, height=54, border_radius=12, alignment=ft.Alignment(0, 0)
        )
        
        if isinstance(color, list):
            icon.gradient = ft.LinearGradient(
                begin=ft.Alignment(-1, -1), # top_left
                end=ft.Alignment(1, 1),    # bottom_right
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
                    padding=ft.padding.only(left=16, right=16, top=6, bottom=6), 
                    border_radius=18,
                    on_click=lambda e: page.run_task(open_url, url)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.only(top=10, bottom=10)
        )
        
        if not is_last:
            return ft.Column([tile, ft.Divider(height=1, color=IOS_DIVIDER, thickness=0.5)], spacing=0)
        return tile

    repo_apps_list = ft.Column(spacing=0)
    repo_sources_list = ft.Column(spacing=0)

    # Apps View
    apps_view = ft.Column(
        scroll=ft.ScrollMode.HIDDEN,
        expand=True,
        controls=[
            # FIXED: Proper Margin usage
            ft.Text("Apps", size=34, weight="bold", margin=ft.padding.only(top=40, bottom=10)),
            ft.Text("SYSTEM", size=13, color=IOS_GRAY, margin=ft.padding.only(left=10, bottom=5)),
            ft.Container(
                content=ft.Column([
                    create_app_tile("ESign", "Signed Proxy Installer", ["#5856d6", "#007AFF"], f"itms-services://?action=download-manifest&url={PROXY_ESIGN_URL}", True)
                ], spacing=0),
                bgcolor=IOS_CARD, border_radius=12, padding=ft.padding.symmetric(horizontal=15)
            ),
            ft.Container(height=10),
            repo_apps_list,
            ft.Container(height=120)
        ]
    )

    # Sources View
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
            ft.Text("Sources", size=34, weight="bold", margin=ft.padding.only(top=40, bottom=10)),
            ft.Row([
                repo_input, 
                ft.IconButton(ft.Icons.ADD_CIRCLE, on_click=lambda e: page.run_task(add_repo_click), icon_color=IOS_BLUE, icon_size=30)
            ]),
            ft.Container(height=20),
            ft.Text("INSTALLED REPOS", size=13, color=IOS_GRAY, margin=ft.padding.only(left=10, bottom=5)),
            ft.Container(repo_sources_list, bgcolor=IOS_CARD, border_radius=12),
            ft.Container(height=120)
        ]
    )

    async def load_repos():
        repo_apps_list.controls = [ft.Container(ft.ProgressRing(color=IOS_BLUE), alignment=ft.Alignment(0, 0), padding=40)]
        page.update()

        all_urls = list(set(DEFAULT_REPOS + user_repos))
        loaded_apps = []
        loaded_sources = []

        async with httpx.AsyncClient() as client:
            tasks = [client.get(f"{u}?t={int(time.time())}", timeout=5.0) for u in all_urls]
            for i, task in enumerate(asyncio.as_completed(tasks)):
                try:
                    resp = await task
                    if resp.status_code == 200:
                        data = resp.json()
                        url = str(resp.url).split('?')[0]
                        
                        loaded_sources.append(ft.Column([
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.LANGUAGE, color=IOS_BLUE),
                                title=ft.Text(url, size=14, color="white", no_wrap=True, overflow="ellipsis"),
                                trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, color=IOS_DIVIDER),
                                dense=True
                            ),
                            ft.Divider(height=1, color=IOS_DIVIDER, thickness=0.5)
                        ], spacing=0))

                        if "packages" in data:
                            loaded_apps.append(ft.Text(data.get("repo_name", "Third-party").upper(), size=13, color=IOS_GRAY, margin=ft.padding.only(left=10, top=20, bottom=5)))
                            pkgs = data["packages"]
                            repo_container = ft.Column([
                                create_app_tile(p['name'], p['description'], p.get("color"), p['url'], j==len(pkgs)-1) 
                                for j, p in enumerate(pkgs)
                            ], spacing=0)
                            loaded_apps.append(ft.Container(content=repo_container, bgcolor=IOS_CARD, border_radius=12, padding=ft.padding.symmetric(horizontal=15)))
                        
                        repo_apps_list.controls = loaded_apps
                        repo_sources_list.controls = loaded_sources
                        page.update()
                except: continue

        if not loaded_apps:
            repo_apps_list.controls = [ft.Container(ft.Text("No sources found", color=IOS_GRAY), alignment=ft.Alignment(0, 0), padding=40)]
            page.update()

    async def add_repo_click(e):
        u = repo_input.value.strip()
        if u and u not in user_repos:
            user_repos.append(u)
            with open(SAVE_FILE, "w") as f: json.dump(user_repos, f)
            repo_input.value = ""
            await load_repos()

    # Navigation Bar
    page.navigation_bar = ft.NavigationBar(
        bgcolor=IOS_SECONDARY_BG,
        selected_index=0,
        indicator_color=ft.Colors.TRANSPARENT,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.GRID_VIEW_ROUNDED, label="Apps"),
            ft.NavigationBarDestination(icon=ft.Icons.FORMAT_LIST_BULLETED_ROUNDED, label="Sources"),
        ],
        on_change=lambda e: (
            setattr(apps_view, 'visible', e.control.selected_index == 0), 
            setattr(sources_view, 'visible', e.control.selected_index == 1), 
            page.update()
        ),
    )

    user_repos.extend(load_from_file())
    
    page.add(
        ft.SafeArea(
            ft.Container(
                content=ft.Stack([apps_view, sources_view], expand=True),
                padding=ft.padding.symmetric(horizontal=20),
                expand=True
            ),
            expand=True
        )
    )
    
    asyncio.create_task(load_repos())

if __name__ == "__main__":
    ft.run(main)