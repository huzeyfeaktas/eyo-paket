import flet as ft
import random
import threading
import time
import socket
import json
import copy
import select
from pathlib import Path
import math

# ===================================================================================
# ============================= GENEL UI STİLLERİ (HEX'TEN) =============================
# ===================================================================================

# Ana Menü ve Sayfa Renkleri
PAGE_BG_COLOR = ft.colors.BLUE_GREY_100
TEXT_COLOR_DARK = ft.colors.BLACK87
TEXT_COLOR_HEADING = ft.colors.BLUE_GREY_900

# Standart Buton Renkleri
BUTTON_PRIMARY_COLOR = ft.colors.GREEN_700      # Ana Eylem Butonları (örn: Başlat)
BUTTON_SECONDARY_COLOR = ft.colors.BLUE_500     # İkincil Eylem Butonları (örn: Çok Oyunculu)
BUTTON_TERTIARY_COLOR = ft.colors.ORANGE_700   # Üçüncül Eylem Butonları (örn: Eğitim)
BUTTON_DANGER_COLOR = ft.colors.RED_ACCENT_400     # Tehlike/Çıkış Butonları
BUTTON_GREY_COLOR = ft.colors.BLUE_GREY_500     # Geri/Nötr Butonlar
BUTTON_TEXT_COLOR = ft.colors.WHITE

# Standart Buton Stili
STADIUM_BUTTON_STYLE = ft.ButtonStyle(shape=ft.StadiumBorder())

# ===================================================================================
# ================================= ANA MENÜ YÖNETİMİ =================================
# ===================================================================================

def master_main(page: ft.Page):
    """Uygulamanın ana giriş noktası. Master menüyü oluşturur."""
    page.title = "Oyun Merkezi"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = PAGE_BG_COLOR
    page.window_width = 1100
    page.window_height = 850
    page.window_center()

    def go_to_master_menu(e=None):
        """Sayfayı temizler ve ana oyun seçim menüsünü yeniden oluşturur."""
        page.controls.clear()
        create_master_menu()
        page.update()

    def create_master_menu():
    
        page.title = "Oyun Merkezi"
        page.controls.clear()

        # Her oyunun kendi ana menüsünü çağıran on_click fonksiyonları
        def go_to_catan(e):
            page.controls.clear()
            main_catan(page, go_to_master_menu)

        def go_to_hex(e):
            page.controls.clear()
            main_hex(page, go_to_master_menu)

        def go_to_mancala(e):
            page.controls.clear()
            main_mancala(page, go_to_master_menu)

        def go_to_memory(e):
            page.controls.clear()
            main_memory(page, go_to_master_menu)

        def go_to_nim(e):
            page.controls.clear()
            main_nim(page, go_to_master_menu)

        master_menu_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Oyun Merkezi", size=48, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_HEADING),
                    ft.Text("Lütfen Oynamak İstediğiniz Oyunu Seçin", size=20, color=ft.colors.BLUE_GREY_700, italic=True),
                    ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                    ft.ElevatedButton(
                        "Catan Strateji Oyunu",
                        on_click=go_to_catan,
                        icon=ft.icons.FOREST,
                        bgcolor=BUTTON_PRIMARY_COLOR,
                        color=BUTTON_TEXT_COLOR,
                        height=55,
                        width=320,
                        style=STADIUM_BUTTON_STYLE
                    ),
                    ft.ElevatedButton(
                        "Hex Oyunu",
                        on_click=go_to_hex,
                        icon=ft.icons.HEXAGON,
                        bgcolor=BUTTON_PRIMARY_COLOR,
                        color=BUTTON_TEXT_COLOR,
                        height=55,
                        width=320,
                        style=STADIUM_BUTTON_STYLE
                    ),
                    ft.ElevatedButton(
                        "Mancala Oyunu",
                        on_click=go_to_mancala,
                        icon=ft.icons.GRAIN,
                        bgcolor=BUTTON_PRIMARY_COLOR,
                        color=BUTTON_TEXT_COLOR,
                        height=55,
                        width=320,
                        style=STADIUM_BUTTON_STYLE
                    ),
                    ft.ElevatedButton(
                        "Sayısal Hafıza Oyunu",
                        on_click=go_to_memory,
                        icon=ft.icons.MEMORY,
                        bgcolor=BUTTON_PRIMARY_COLOR,
                        color=BUTTON_TEXT_COLOR,
                        height=55,
                        width=320,
                        style=STADIUM_BUTTON_STYLE
                    ),
                    ft.ElevatedButton(
                        "Gelişmiş Nim Oyunu",
                        on_click=go_to_nim,
                        icon=ft.icons.FORMAT_LIST_NUMBERED,
                        bgcolor=BUTTON_PRIMARY_COLOR,
                        color=BUTTON_TEXT_COLOR,
                        height=55,
                        width=320,
                        style=STADIUM_BUTTON_STYLE
                    ),
                    ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                    ft.ElevatedButton(
                        "Çıkış",
                        on_click=lambda e: page.window_close(),
                        icon=ft.icons.EXIT_TO_APP,
                        bgcolor=BUTTON_DANGER_COLOR,
                        color=BUTTON_TEXT_COLOR,
                        height=55,
                        width=320,
                        style=STADIUM_BUTTON_STYLE
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15
            ),
            padding=40,
            alignment=ft.alignment.center,
            expand=True
        )
        page.add(master_menu_container)
        page.update()

    create_master_menu()


# ===================================================================================
# =============================== CATAN OYUN KODU BAŞLANGIÇ ===============================
# ===================================================================================

# --- Catan Oyun Sabitleri ---
GRID_BOYUT_CATAN = 5
KAYNAKLAR_CATAN = ["odun", "tugla", "tahil", "yun", "cevher"]
INSAAT_FIYATLARI_CATAN = {
    "yol": {"odun": 1, "tugla": 1},
    "koy": {"odun": 1, "tugla": 1, "tahil": 1, "yun": 1},
    "sehir": {"tahil": 2, "cevher": 3}
}
PUANLAR_CATAN = {"koy": 1, "sehir": 2}
ZAFER_PUANI_CATAN = 10
SUNUCU_PORT_CATAN = 12345
RENKLER_CATAN = {
    "odun": ft.colors.GREEN_300,
    "tugla": ft.colors.RED_300,
    "tahil": ft.colors.YELLOW_300,
    "yun": ft.colors.WHITE,
    "cevher": ft.colors.GREY_400,
    "oyuncu": ft.colors.BLUE_500,
    "ai": ft.colors.RED_500
}
SIMGE_CATAN = {
    "yol": "Y",
    "koy": "K",
    "sehir": "Ş"
}

# --- Catan Oyun Durumu (Global) ---
oyun_durumu_catan = {
    "oyuncu": {
        "ad": "Oyuncu",
        "kaynaklar": {k: 5 for k in KAYNAKLAR_CATAN},
        "yollar": [],
        "koyler": [],
        "sehirler": [],
        "puan": 0,
        "son_zar_zamani": 0,
        "toplam_kaynak": 25
    },
    "ai": {
        "ad": "AI",
        "kaynaklar": {k: 5 for k in KAYNAKLAR_CATAN},
        "yollar": [],
        "koyler": [],
        "sehirler": [],
        "puan": 0,
        "toplam_kaynak": 25
    },
    "tahta": [[{"kaynak": random.choice(KAYNAKLAR_CATAN), "zar": random.randint(2, 12)} for _ in range(GRID_BOYUT_CATAN)] for _ in range(GRID_BOYUT_CATAN)],
    "sira": "Oyuncu",
    "oyun_basladi": False,
    "oyun_bitti": False,
    "cok_oyunculu": False,
    "sunucu_mu": False,
    "istemci_socket": None,
    "oyuncular": [],
    "canli_skorlar": [],
    "durum_mesaji": "Catan Strateji Oyununa Hoş Geldiniz!",
    "ai_zorluk": "Orta"
}

# --- Catan Ana Fonksiyonu ---
def main_catan(sayfa: ft.Page, go_to_master_menu_func):
    print("Catan Sayfası oluşturuluyor...")
    sayfa.title = "Catan Strateji Oyunu"
    sayfa.vertical_alignment = ft.MainAxisAlignment.CENTER
    sayfa.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    sayfa.theme_mode = ft.ThemeMode.LIGHT
    sayfa.window_width = 450
    sayfa.window_height = 700
    # sayfa.window_center() # Ana merkezleme master_main'de yapılıyor.
    sayfa.bgcolor = PAGE_BG_COLOR

    # --- Catan Ana Menü Ekranı ---
    def ana_menu_ekrani_catan():
        print("Catan ana menü ekranı oluşturuluyor...")
        sayfa.controls.clear()
        mod_secim_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Catan Strateji Oyunu", size=28, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_HEADING),
                    ft.ElevatedButton("Tek Oyunculu", on_click=lambda e: oyun_ekrani_catan(), bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.PERSON),
                    ft.ElevatedButton("Çok Oyunculu", on_click=lambda e: cok_oyunculu_ekran_catan(), bgcolor=BUTTON_SECONDARY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.PEOPLE),
                    ft.ElevatedButton("Tüm Oyunlar Menüsü", on_click=go_to_master_menu_func, bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.MENU),
                    ft.ElevatedButton("Çıkış", on_click=lambda e: sayfa.window_close(), bgcolor=BUTTON_DANGER_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.EXIT_TO_APP)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15
            ),
            padding=20,
            alignment=ft.alignment.center
        )
        sayfa.add(mod_secim_container)
        sayfa.update()

    # --- Catan Çok Oyunculu Ekran ---
    def cok_oyunculu_ekran_catan():
        print("Catan çok oyunculu ekran oluşturuluyor...")
        sayfa.controls.clear()
        oyuncu_adi_girdi = ft.Ref[ft.TextField]()
        sunucu_adresi_girdi = ft.Ref[ft.TextField]()
        durum_cubugu = ft.Ref[ft.Text]()
        sunucu_adresi_goster = ft.Ref[ft.Text]()
        baglanan_oyuncular = ft.Ref[ft.Text]()
        oyun_baslat_buton = ft.Ref[ft.ElevatedButton]()

        def sunucu_baslat_sec_catan():
            print("Catan sunucu başlatma seçildi")
            if not oyuncu_adi_girdi.current.value.strip():
                durum_cubugu.current.value = "Lütfen bir oyuncu adı girin!"
                sayfa.update()
                return
            oyun_durumu_catan["oyuncu"]["ad"] = oyuncu_adi_girdi.current.value.strip()
            oyun_durumu_catan["cok_oyunculu"] = True
            oyun_durumu_catan["sunucu_mu"] = True
            sunucu_ekran_catan()

        def sunucuya_baglan_sec_catan():
            print("Catan sunucuya bağlanma seçildi")
            if not oyuncu_adi_girdi.current.value.strip():
                durum_cubugu.current.value = "Lütfen bir oyuncu adı girin!"
                sayfa.update()
                return
            oyun_durumu_catan["oyuncu"]["ad"] = oyuncu_adi_girdi.current.value.strip()
            oyun_durumu_catan["cok_oyunculu"] = True
            oyun_durumu_catan["sunucu_mu"] = False
            sunucu_baglan_ekran_catan()

        cok_oyunculu_secim_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Çok Oyunculu Mod", size=24, weight=ft.FontWeight.BOLD),
                    ft.TextField(label="Oyuncu Adı", ref=oyuncu_adi_girdi, width=300),
                    ft.ElevatedButton("Sunucu Başlat", on_click=lambda e: sunucu_baslat_sec_catan(), bgcolor=BUTTON_SECONDARY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.DNS),
                    ft.ElevatedButton("Sunucuya Bağlan", on_click=lambda e: sunucuya_baglan_sec_catan(), bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.LINK),
                    ft.Text("", ref=durum_cubugu, size=14, color=ft.colors.RED_700, width=400, text_align=ft.TextAlign.CENTER),
                    ft.ElevatedButton("Geri", on_click=lambda e: ana_menu_ekrani_catan(), bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.ARROW_BACK)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15
            ),
            padding=20,
            alignment=ft.alignment.center,
        )
        sayfa.add(cok_oyunculu_secim_container)
        sayfa.update()

    def sunucu_ekran_catan():
        print("Catan sunucu ekranı oluşturuluyor...")
        sayfa.controls.clear()
        sunucu_adresi_goster = ft.Ref[ft.Text]()
        baglanan_oyuncular = ft.Ref[ft.Text]()
        oyun_baslat_buton = ft.Ref[ft.ElevatedButton]()
        durum_cubugu = ft.Ref[ft.Text]()

        def sunucu_baslat_fonk_catan():
            print("Catan Sunucusu başlatılıyor...")
            sunucu = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sunucu.bind(("0.0.0.0", SUNUCU_PORT_CATAN))
                sunucu.listen(5)
                sunucu_adresi_goster.current.value = f"Sunucu Adresi: {socket.gethostbyname(socket.gethostname())}:{SUNUCU_PORT_CATAN}"
                baglanan_oyuncular.current.value = f"Bağlanan Oyuncular: {oyun_durumu_catan['oyuncu']['ad']}"
                oyun_durumu_catan["oyuncular"].append({"ad": oyun_durumu_catan["oyuncu"]["ad"], "socket": None, "puan": 0})
                oyun_baslat_buton.current.disabled = False
                sayfa.update()

                def istemci_yonet_catan(istemci_socket, addr):
                    try:
                        veri = istemci_socket.recv(1024).decode()
                        mesaj = json.loads(veri)
                        if mesaj["tip"] == "baglan":
                            oyuncu_adi = mesaj["ad"]
                            oyun_durumu_catan["oyuncular"].append({"ad": oyuncu_adi, "socket": istemci_socket, "puan": 0})
                            baglanan_oyuncular.current.value = f"Bağlanan Oyuncular: {', '.join([o['ad'] for o in oyun_durumu_catan['oyuncular']])}"
                            oyun_durumu_catan["canli_skorlar"] = [{"ad": o["ad"], "puan": o["puan"]} for o in oyun_durumu_catan["oyuncular"]]
                            sayfa.update()
                            while oyun_durumu_catan["oyun_basladi"] and not oyun_durumu_catan["oyun_bitti"]:
                                try:
                                    veri = istemci_socket.recv(1024).decode()
                                    mesaj = json.loads(veri)
                                    if mesaj["tip"] == "puan":
                                        for oyuncu in oyun_durumu_catan["oyuncular"]:
                                            if oyuncu["ad"] == mesaj["ad"]:
                                                oyuncu["puan"] = mesaj["puan"]
                                                break
                                        oyun_durumu_catan["canli_skorlar"] = [{"ad": o["ad"], "puan": o["puan"]} for o in oyun_durumu_catan["oyuncular"]]
                                        for oyuncu in oyun_durumu_catan["oyuncular"]:
                                            if oyuncu["socket"]:
                                                try:
                                                    oyuncu["socket"].send(json.dumps({"tip": "canli_skorlar", "skorlar": oyun_durumu_catan["canli_skorlar"], "ai_puan": oyun_durumu_catan["ai"]["puan"]}).encode())
                                                except:
                                                    pass
                                        sayfa.update()
                                except:
                                    break
                    except:
                        istemci_socket.close()

                while not oyun_durumu_catan["oyun_basladi"]:
                    sunucu.settimeout(1.0)
                    try:
                        istemci_socket, addr = sunucu.accept()
                        threading.Thread(target=istemci_yonet_catan, args=(istemci_socket, addr), daemon=True).start()
                    except socket.timeout:
                        continue
            except Exception as e:
                durum_cubugu.current.value = f"Sunucu başlatılamadı: {e}"
                sayfa.update()

        def oyun_baslat_tiklama_catan(e):
            print("Catan oyunu başlatılıyor...")
            if not oyun_durumu_catan["sunucu_mu"]:
                return
            oyun_durumu_catan["oyun_basladi"] = True
            for oyuncu in oyun_durumu_catan["oyuncular"]:
                if oyuncu["socket"]:
                    try:
                        oyuncu["socket"].send(json.dumps({"tip": "baslat"}).encode())
                    except:
                        pass
            oyun_durumu_catan["canli_skorlar"] = [{"ad": o["ad"], "puan": o["puan"]} for o in oyun_durumu_catan["oyuncular"]]
            oyun_ekrani_catan()

        sunucu_baslat_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Sunucu Başlatıldı", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("", ref=sunucu_adresi_goster, size=16, selectable=True),
                    ft.Text("", ref=baglanan_oyuncular, size=16),
                    ft.ElevatedButton("Oyunu Başlat", ref=oyun_baslat_buton, on_click=oyun_baslat_tiklama_catan, bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.PLAY_ARROW, disabled=True),
                    ft.Text("", ref=durum_cubugu, size=14, color=ft.colors.RED_700, width=400, text_align=ft.TextAlign.CENTER),
                    ft.ElevatedButton("Geri", on_click=lambda e: cok_oyunculu_ekran_catan(), bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.ARROW_BACK)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15
            ),
            padding=20,
            alignment=ft.alignment.center
        )
        sayfa.add(sunucu_baslat_container)
        threading.Thread(target=sunucu_baslat_fonk_catan, daemon=True).start()
        sayfa.update()

    def sunucu_baglan_ekran_catan():
        print("Catan sunucu bağlan ekranı oluşturuluyor...")
        sayfa.controls.clear()
        sunucu_adresi_girdi = ft.Ref[ft.TextField]()
        durum_cubugu = ft.Ref[ft.Text]()

        def sunucuya_baglan_fonk_catan():
            print("Catan sunucuya bağlanılıyor...")
            try:
                istemci = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                adres, port = sunucu_adresi_girdi.current.value.split(":")
                istemci.connect((adres, int(port)))
                oyun_durumu_catan["istemci_socket"] = istemci
                istemci.send(json.dumps({"tip": "baglan", "ad": oyun_durumu_catan["oyuncu"]["ad"]}).encode())
                threading.Thread(target=istemci_dinle_catan, daemon=True).start()
                oyun_ekrani_catan()
            except Exception as e:
                durum_cubugu.current.value = f"Bağlantı hatası: {e}"
                sayfa.update()

        def istemci_dinle_catan():
            while oyun_durumu_catan["cok_oyunculu"] and not oyun_durumu_catan["sunucu_mu"]:
                try:
                    veri = oyun_durumu_catan["istemci_socket"].recv(1024).decode()
                    mesaj = json.loads(veri)
                    if mesaj["tip"] == "baslat":
                        oyun_durumu_catan["oyun_basladi"] = True
                        oyun_ekrani_catan()
                    elif mesaj["tip"] == "canli_skorlar":
                        oyun_durumu_catan["canli_skorlar"] = mesaj["skorlar"]
                        oyun_durumu_catan["ai"]["puan"] = mesaj["ai_puan"]
                        sayfa.update()
                except:
                    time.sleep(0.1)

        sunucu_baglan_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Sunucuya Bağlan", size=24, weight=ft.FontWeight.BOLD),
                    ft.TextField(label="Sunucu Adresi (IP:Port)", ref=sunucu_adresi_girdi, width=300, value=f"{socket.gethostbyname(socket.gethostname())}:{SUNUCU_PORT_CATAN}"),
                    ft.ElevatedButton("Bağlan", on_click=lambda e: sunucuya_baglan_fonk_catan(), bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.LOGIN),
                    ft.Text("", ref=durum_cubugu, size=14, color=ft.colors.RED_700, width=400, text_align=ft.TextAlign.CENTER),
                    ft.ElevatedButton("Geri", on_click=lambda e: cok_oyunculu_ekran_catan(), bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.ARROW_BACK)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15
            ),
            padding=20,
            alignment=ft.alignment.center
        )
        sayfa.add(sunucu_baglan_container)
        sayfa.update()

    # --- Catan Oyun Ekranı ---
    def oyun_ekrani_catan():
        print("Catan oyun ekranı oluşturuluyor...")
        sayfa.controls.clear()
        tahta_grid = ft.Ref[ft.GridView]()
        durum_cubugu = ft.Ref[ft.Text]()
        kaynak_gosterge = ft.Ref[ft.Text]()
        puan_gosterge = ft.Ref[ft.Text]()
        canli_skor_gosterge = ft.Ref[ft.Text]()
        kontrol_paneli = ft.Ref[ft.ResponsiveRow]()
        yeniden_baslat_buton = ft.Ref[ft.ElevatedButton]()
        skor_ekrani_container = ft.Ref[ft.Container]()

        def arayuz_guncelle_catan():
            print("Catan oyun arayüzü güncelleniyor...")
            if not kaynak_gosterge.current: return # Ekran kapatıldıysa güncelleme yapma
            
            kaynak_gosterge.current.value = "Kaynaklar: " + " | ".join(
                [f"{k.capitalize()}: {oyun_durumu_catan['oyuncu']['kaynaklar'][k]}" for k in KAYNAKLAR_CATAN]
            )
            puan_gosterge.current.value = f"Puan: {oyun_durumu_catan['oyuncu']['puan']} (AI: {oyun_durumu_catan['ai']['puan']})"
            durum_cubugu.current.value = oyun_durumu_catan["durum_mesaji"]
            canli_skor_gosterge.current.value = (
                "\n".join([f"{o['ad']}: {o['puan']}" for o in oyun_durumu_catan["canli_skorlar"]]) + f"\nAI: {oyun_durumu_catan['ai']['puan']}"
                if oyun_durumu_catan["cok_oyunculu"] else f"Sizin Puan: {oyun_durumu_catan['oyuncu']['puan']}\nAI Puan: {oyun_durumu_catan['ai']['puan']}"
            )
            kontrol_paneli.current.controls[0].disabled = oyun_durumu_catan["sira"] != "Oyuncu" or time.time() - oyun_durumu_catan["oyuncu"]["son_zar_zamani"] < 1
            yeniden_baslat_buton.current.visible = oyun_durumu_catan["oyun_bitti"]
            if oyun_durumu_catan["oyun_bitti"]:
                kazanan = "Oyuncu" if oyun_durumu_catan["oyuncu"]["puan"] >= ZAFER_PUANI_CATAN else "AI" if oyun_durumu_catan["ai"]["puan"] >= ZAFER_PUANI_CATAN else max(
                    oyun_durumu_catan["canli_skorlar"], key=lambda x: x["puan"], default={"ad": "AI", "puan": oyun_durumu_catan["ai"]["puan"]}
                )["ad"]
                skor_ekrani_container.current.content = ft.Column(
                    [
                        ft.Text("Oyun Bitti!", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Kazanan: {kazanan}", size=20, color=ft.colors.GREEN_700),
                        ft.Text(f"Sizin Puan: {oyun_durumu_catan['oyuncu']['puan']}", size=16),
                        ft.Text(f"AI Puan: {oyun_durumu_catan['ai']['puan']}", size=16),
                        ft.Text("\n".join([f"{o['ad']}: {o['puan']}" for o in oyun_durumu_catan["canli_skorlar"]]) if oyun_durumu_catan["cok_oyunculu"] else "", size=16),
                        ft.ElevatedButton("Yeniden Oyna", on_click=lambda e: yeniden_baslat_catan(e), bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, style=STADIUM_BUTTON_STYLE, icon=ft.icons.REFRESH)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
                skor_ekrani_container.current.visible = True
            else:
                skor_ekrani_container.current.visible = False
            tahta_guncelle_catan()
            sayfa.update()

        def tahta_guncelle_catan():
            print("Catan oyun tahtası güncelleniyor...")
            if not tahta_grid.current: return
            tahta_grid.current.controls = []
            for i in range(GRID_BOYUT_CATAN):
                for j in range(GRID_BOYUT_CATAN):
                    hucre = oyun_durumu_catan["tahta"][i][j]
                    icerik = ft.Column(
                        [
                            ft.Text(hucre["kaynak"].capitalize(), size=12),
                            ft.Text(f"Zar: {hucre['zar']}", size=12)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    )
                    renk = RENKLER_CATAN[hucre["kaynak"]]
                    if any((i, j) in oyun_durumu_catan[k]["koyler"] for k in ["oyuncu", "ai"]):
                        icerik.controls.append(ft.Text(SIMGE_CATAN["koy"], color=RENKLER_CATAN["oyuncu" if (i, j) in oyun_durumu_catan["oyuncu"]["koyler"] else "ai"], size=12))
                    elif any((i, j) in oyun_durumu_catan[k]["sehirler"] for k in ["oyuncu", "ai"]):
                        icerik.controls.append(ft.Text(SIMGE_CATAN["sehir"], color=RENKLER_CATAN["oyuncu" if (i, j) in oyun_durumu_catan["oyuncu"]["sehirler"] else "ai"], size=12))
                    elif any((i, j) in oyun_durumu_catan[k]["yollar"] for k in ["oyuncu", "ai"]):
                        icerik.controls.append(ft.Text(SIMGE_CATAN["yol"], color=RENKLER_CATAN["oyuncu" if (i, j) in oyun_durumu_catan["oyuncu"]["yollar"] else "ai"], size=12))
                    tahta_grid.current.controls.append(
                        ft.GestureDetector(
                            content=ft.Container(
                                content=icerik,
                                width=80,
                                height=80,
                                bgcolor=renk,
                                border=ft.border.all(1, ft.colors.BLACK),
                                alignment=ft.alignment.center
                            ),
                            on_tap=lambda e, i=i, j=j: insaat_yap_catan(i, j)
                        )
                    )
            sayfa.update()

        def insaat_yap_catan(i, j):
            if oyun_durumu_catan["sira"] != "Oyuncu" or not oyun_durumu_catan["oyun_basladi"] or oyun_durumu_catan["oyun_bitti"]:
                return
            def insaat_sec_catan(tip):
                print(f"Catan inşaat seçildi: {tip}")
                if tip == "yol" and (yolda_komsu_var_mi_catan(i, j, "oyuncu") or not oyun_durumu_catan["oyuncu"]["yollar"]):
                    if yeterli_kaynak_var_mi_catan("yol", "oyuncu"):
                        if harcama_tehlikeli_mi_catan("yol", "oyuncu"):
                            uyari_dialog = ft.AlertDialog(
                                title=ft.Text("Uyarı"),
                                content=ft.Text("Bu harcama kaynaklarınızı tükebilir ve ilerlemenizi riske atabilir! Devam etmek istediğinizden emin misiniz?"),
                                actions=[
                                    ft.TextButton("Evet", on_click=lambda e: devam_et_catan(tip)),
                                    ft.TextButton("Hayır", on_click=lambda e: setattr(uyari_dialog, "open", False))
                                ],
                                actions_alignment=ft.MainAxisAlignment.CENTER
                            )
                            sayfa.dialog = uyari_dialog
                            uyari_dialog.open = True
                            sayfa.update()
                        else:
                            devam_et_catan(tip)
                    else:
                        oyun_durumu_catan["durum_mesaji"] = "Yeterli kaynak yok!"
                elif tip == "koy" and koyde_komsu_yok_mu_catan(i, j) and yolda_komsu_var_mi_catan(i, j, "oyuncu"):
                    if yeterli_kaynak_var_mi_catan("koy", "oyuncu"):
                        if harcama_tehlikeli_mi_catan("koy", "oyuncu"):
                            uyari_dialog = ft.AlertDialog(
                                title=ft.Text("Uyarı"),
                                content=ft.Text("Bu harcama kaynaklarınızı tükebilir ve ilerlemenizi riske atabilir! Devam etmek istediğinizden emin misiniz?"),
                                actions=[
                                    ft.TextButton("Evet", on_click=lambda e: devam_et_catan(tip)),
                                    ft.TextButton("Hayır", on_click=lambda e: setattr(uyari_dialog, "open", False))
                                ],
                                actions_alignment=ft.MainAxisAlignment.CENTER
                            )
                            sayfa.dialog = uyari_dialog
                            uyari_dialog.open = True
                            sayfa.update()
                        else:
                            devam_et_catan(tip)
                    else:
                        oyun_durumu_catan["durum_mesaji"] = "Yeterli kaynak yok!"
                elif tip == "sehir" and (i, j) in oyun_durumu_catan["oyuncu"]["koyler"]:
                    if yeterli_kaynak_var_mi_catan("sehir", "oyuncu"):
                        if harcama_tehlikeli_mi_catan("sehir", "oyuncu"):
                            uyari_dialog = ft.AlertDialog(
                                title=ft.Text("Uyarı"),
                                content=ft.Text("Bu harcama kaynaklarınızı tükebilir ve ilerlemenizi riske atabilir! Devam etmek istediğinizden emin misiniz?"),
                                actions=[
                                    ft.TextButton("Evet", on_click=lambda e: devam_et_catan(tip)),
                                    ft.TextButton("Hayır", on_click=lambda e: setattr(uyari_dialog, "open", False))
                                ],
                                actions_alignment=ft.MainAxisAlignment.CENTER
                            )
                            sayfa.dialog = uyari_dialog
                            uyari_dialog.open = True
                            sayfa.update()
                        else:
                            devam_et_catan(tip)
                    else:
                        oyun_durumu_catan["durum_mesaji"] = "Yeterli kaynak yok!"
                dialog.open = False
                zorluk_guncelle_catan()
                arayuz_guncelle_catan()

            def devam_et_catan(tip):
                if tip == "yol":
                    oyun_durumu_catan["oyuncu"]["yollar"].append((i, j))
                    kaynak_harca_catan("yol", "oyuncu")
                    oyun_durumu_catan["durum_mesaji"] = "Yol inşa edildi! Köy kur ve zar at."
                elif tip == "koy":
                    oyun_durumu_catan["oyuncu"]["koyler"].append((i, j))
                    oyun_durumu_catan["oyuncu"]["puan"] += PUANLAR_CATAN["koy"]
                    kaynak_harca_catan("koy", "oyuncu")
                    oyun_durumu_catan["durum_mesaji"] = "Köy inşa edildi! +1 puan. Zar at."
                elif tip == "sehir":
                    oyun_durumu_catan["oyuncu"]["koyler"].remove((i, j))
                    oyun_durumu_catan["oyuncu"]["sehirler"].append((i, j))
                    oyun_durumu_catan["oyuncu"]["puan"] += PUANLAR_CATAN["sehir"] - PUANLAR_CATAN["koy"]
                    kaynak_harca_catan("sehir", "oyuncu")
                    oyun_durumu_catan["durum_mesaji"] = "Şehir inşa edildi! +1 puan. Zar at."
                sira_degis_catan()
                oyun_durumu_kontrol_catan()

            def format_kaynaklar_catan(tip):
                kaynak_listesi = []
                for kaynak, miktar in INSAAT_FIYATLARI_CATAN[tip].items():
                    mevcut = oyun_durumu_catan["oyuncu"]["kaynaklar"].get(kaynak, 0)
                    renk = ft.colors.GREEN_700 if mevcut >= miktar else ft.colors.RED_700
                    kaynak_listesi.append(f"{miktar} {kaynak.capitalize()}")
                return ", ".join(kaynak_listesi)

            dialog = ft.AlertDialog(
                title=ft.Text("İnşaat Seç"),
                content=ft.Column(
                    [
                        ft.Row([
                            ft.ElevatedButton("Yol", on_click=lambda e: insaat_sec_catan("yol")),
                            ft.Text(format_kaynaklar_catan("yol"), size=12)
                        ], alignment=ft.MainAxisAlignment.START),
                        ft.Row([
                            ft.ElevatedButton("Köy", on_click=lambda e: insaat_sec_catan("koy")),
                            ft.Text(format_kaynaklar_catan("koy"), size=12)
                        ], alignment=ft.MainAxisAlignment.START),
                        ft.Row([
                            ft.ElevatedButton("Şehir", on_click=lambda e: insaat_sec_catan("sehir")),
                            ft.Text(format_kaynaklar_catan("sehir"), size=12)
                        ], alignment=ft.MainAxisAlignment.START)
                    ],
                    tight=True,
                    spacing=10
                ),
                actions=[ft.TextButton("İptal", on_click=lambda e: setattr(dialog, "open", False))]
            )
            sayfa.dialog = dialog
            dialog.open = True
            sayfa.update()

        def yeterli_kaynak_var_mi_catan(tip, oyuncu):
            for kaynak, miktar in INSAAT_FIYATLARI_CATAN[tip].items():
                if oyun_durumu_catan[oyuncu]["kaynaklar"].get(kaynak, 0) < miktar:
                    return False
            return True

        def kaynak_harca_catan(tip, oyuncu):
            for kaynak, miktar in INSAAT_FIYATLARI_CATAN[tip].items():
                oyun_durumu_catan[oyuncu]["kaynaklar"][kaynak] -= miktar
                if oyun_durumu_catan[oyuncu]["kaynaklar"][kaynak] < 0:
                    oyun_durumu_catan[oyuncu]["kaynaklar"][kaynak] = 0

        def harcama_tehlikeli_mi_catan(tip, oyuncu):
            kalan_kaynaklar = copy.deepcopy(oyun_durumu_catan[oyuncu]["kaynaklar"])
            for kaynak, miktar in INSAAT_FIYATLARI_CATAN[tip].items():
                kalan_kaynaklar[kaynak] -= miktar
            for kaynak in KAYNAKLAR_CATAN:
                if kalan_kaynaklar.get(kaynak, 0) < 0:
                    return True
            return False

        def yolda_komsu_var_mi_catan(i, j, oyuncu):
            for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                ni, nj = i + di, j + dj
                if 0 <= ni < GRID_BOYUT_CATAN and 0 <= nj < GRID_BOYUT_CATAN:
                    if (ni, nj) in oyun_durumu_catan[oyuncu]["yollar"] or (ni, nj) in oyun_durumu_catan[oyuncu]["koyler"] or (ni, nj) in oyun_durumu_catan[oyuncu]["sehirler"]:
                        return True
            return False

        def koyde_komsu_yok_mu_catan(i, j):
            for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                ni, nj = i + di, j + dj
                if 0 <= ni < GRID_BOYUT_CATAN and 0 <= nj < GRID_BOYUT_CATAN:
                    if any((ni, nj) in oyun_durumu_catan[k]["koyler"] or (ni, nj) in oyun_durumu_catan[k]["sehirler"] for k in ["oyuncu", "ai"]):
                        return False
            return True

        def zar_at_catan(e):
            if oyun_durumu_catan["sira"] != "Oyuncu" or time.time() - oyun_durumu_catan["oyuncu"]["son_zar_zamani"] < 1 or oyun_durumu_catan["oyun_bitti"]:
                return
            print("Catan zarı atılıyor...")
            zar = random.randint(2, 12)
            kaynak_toplandi = False
            for i in range(GRID_BOYUT_CATAN):
                for j in range(GRID_BOYUT_CATAN):
                    if oyun_durumu_catan["tahta"][i][j]["zar"] == zar:
                        kaynak = oyun_durumu_catan["tahta"][i][j]["kaynak"]
                        if (i, j) in oyun_durumu_catan["oyuncu"]["koyler"]:
                            oyun_durumu_catan["oyuncu"]["kaynaklar"][kaynak] += 1
                            oyun_durumu_catan["oyuncu"]["toplam_kaynak"] += 1
                            kaynak_toplandi = True
                        elif (i, j) in oyun_durumu_catan["oyuncu"]["sehirler"]:
                            oyun_durumu_catan["oyuncu"]["kaynaklar"][kaynak] += 2
                            oyun_durumu_catan["oyuncu"]["toplam_kaynak"] += 2
                            kaynak_toplandi = True
                        if (i, j) in oyun_durumu_catan["ai"]["koyler"]:
                            oyun_durumu_catan["ai"]["kaynaklar"][kaynak] += 1
                            oyun_durumu_catan["ai"]["toplam_kaynak"] += 1
                        elif (i, j) in oyun_durumu_catan["ai"]["sehirler"]:
                            oyun_durumu_catan["ai"]["kaynaklar"][kaynak] += 2
                            oyun_durumu_catan["ai"]["toplam_kaynak"] += 2
            oyun_durumu_catan["oyuncu"]["son_zar_zamani"] = time.time()
            oyun_durumu_catan["durum_mesaji"] = (
                f"Zar: {zar}, kaynaklar toplandı!" if kaynak_toplandi else
                f"Zar: {zar}, kaynak toplanmadı. Köy kur ve tekrar dene!"
            )
            zorluk_guncelle_catan()
            sira_degis_catan()
            oyun_durumu_kontrol_catan()
            arayuz_guncelle_catan()

        def ai_hamle_catan():
            if oyun_durumu_catan["sira"] != "AI" or not oyun_durumu_catan["oyun_basladi"] or oyun_durumu_catan["oyun_bitti"]:
                return
            print("Catan AI hamle yapıyor...")
            ai_kaynaklar = copy.deepcopy(oyun_durumu_catan["ai"]["kaynaklar"])
            print(f"AI başlangıç kaynakları: {ai_kaynaklar}")

            # Tahtadaki kaynak dağılımını ve zar olasılıklarını analiz et
            tahta_degerlendirme = {}
            for i in range(GRID_BOYUT_CATAN):
                for j in range(GRID_BOYUT_CATAN):
                    zar = oyun_durumu_catan["tahta"][i][j]["zar"]
                    olasilik = 6 - abs(7 - zar)  # 6-8 zarlar daha sık
                    tahta_degerlendirme[(i, j)] = {"olasilik": olasilik, "kaynak": oyun_durumu_catan["tahta"][i][j]["kaynak"]}

            # Tüm olası hamleleri değerlendir ve uygula
            while any(ai_kaynaklar[k] > 0 for k in KAYNAKLAR_CATAN):
                hamleler = []
                for i in range(GRID_BOYUT_CATAN):
                    for j in range(GRID_BOYUT_CATAN):
                        # Köy kurma
                        if koyde_komsu_yok_mu_catan(i, j) and yolda_komsu_var_mi_catan(i, j, "ai") and not any((i, j) in oyun_durumu_catan["oyuncu"][k] for k in ["yollar", "koyler", "sehirler"]):
                            if yeterli_kaynak_var_mi_catan("koy", "ai"):
                                zar_olasilik = tahta_degerlendirme[(i, j)]["olasilik"]
                                kaynak = tahta_degerlendirme[(i, j)]["kaynak"]
                                kaynak_degeri = sum(1 for k, v in INSAAT_FIYATLARI_CATAN["koy"].items() if k == kaynak and ai_kaynaklar[k] < v)
                                deger = PUANLAR_CATAN["koy"] * 10 + zar_olasilik * 3 + kaynak_degeri * 2
                                if oyun_durumu_catan["ai_zorluk"] == "Zor":
                                    deger += 5
                                elif oyun_durumu_catan["ai_zorluk"] == "Kolay":
                                    deger -= 2
                                hamleler.append(("koy", i, j, deger))

                        # Şehir kurma
                        if (i, j) in oyun_durumu_catan["ai"]["koyler"]:
                            if yeterli_kaynak_var_mi_catan("sehir", "ai"):
                                zar_olasilik = tahta_degerlendirme[(i, j)]["olasilik"]
                                deger = (PUANLAR_CATAN["sehir"] - PUANLAR_CATAN["koy"]) * 8 + zar_olasilik * 2
                                if oyun_durumu_catan["ai_zorluk"] == "Zor":
                                    deger += 3
                                elif oyun_durumu_catan["ai_zorluk"] == "Kolay":
                                    deger -= 1
                                hamleler.append(("sehir", i, j, deger))

                        # Yol kurma
                        if (yolda_komsu_var_mi_catan(i, j, "ai") or not oyun_durumu_catan["ai"]["yollar"]) and not any((i, j) in oyun_durumu_catan["oyuncu"][k] for k in ["yollar", "koyler", "sehirler"]):
                            if yeterli_kaynak_var_mi_catan("yol", "ai"):
                                deger = 2
                                for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                                    ni, nj = i + di, j + dj
                                    if 0 <= ni < GRID_BOYUT_CATAN and 0 <= nj < GRID_BOYUT_CATAN and koyde_komsu_yok_mu_catan(ni, nj):
                                        deger += 3
                                        if oyun_durumu_catan["ai_zorluk"] == "Zor":
                                            deger += 2
                                        elif oyun_durumu_catan["ai_zorluk"] == "Kolay":
                                            deger -= 1
                                for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                                    ni, nj = i + di, j + dj
                                    if 0 <= ni < GRID_BOYUT_CATAN and 0 <= nj < GRID_BOYUT_CATAN and (ni, nj) in oyun_durumu_catan["oyuncu"]["yollar"]:
                                        deger += 4 if oyun_durumu_catan["ai_zorluk"] == "Zor" else 2
                                hamleler.append(("yol", i, j, deger))

                if hamleler:
                    hamleler.sort(key=lambda x: x[3], reverse=True)
                    tip, i, j, deger = hamleler[0]
                    print(f"AI hamle seçti: {tip} at ({i}, {j}), deger: {deger}")
                    if tip == "yol":
                        oyun_durumu_catan["ai"]["yollar"].append((i, j))
                        kaynak_harca_catan("yol", "ai")
                        oyun_durumu_catan["durum_mesaji"] = "AI yol inşa etti!"
                    elif tip == "koy":
                        oyun_durumu_catan["ai"]["koyler"].append((i, j))
                        oyun_durumu_catan["ai"]["puan"] += PUANLAR_CATAN["koy"]
                        kaynak_harca_catan("koy", "ai")
                        oyun_durumu_catan["durum_mesaji"] = "AI köy inşa etti!"
                    elif tip == "sehir":
                        oyun_durumu_catan["ai"]["koyler"].remove((i, j))
                        oyun_durumu_catan["ai"]["sehirler"].append((i, j))
                        oyun_durumu_catan["ai"]["puan"] += PUANLAR_CATAN["sehir"] - PUANLAR_CATAN["koy"]
                        kaynak_harca_catan("sehir", "ai")
                        oyun_durumu_catan["durum_mesaji"] = "AI şehir inşa etti!"
                    ai_kaynaklar = copy.deepcopy(oyun_durumu_catan["ai"]["kaynaklar"])  # Kaynakları güncelle
                else:
                    break

            # Sıra otomatik değişsin
            sira_degis_catan()

        def zorluk_guncelle_catan():
            print("Catan Zorluk güncelleniyor...")
            oyuncu_toplam_kaynak = oyun_durumu_catan["oyuncu"]["toplam_kaynak"]
            oyuncu_puan = oyun_durumu_catan["oyuncu"]["puan"]
            ai_toplam_kaynak = oyun_durumu_catan["ai"]["toplam_kaynak"]
            ai_puan = oyun_durumu_catan["ai"]["puan"]

            tur_sayisi = max(1, len(oyun_durumu_catan["oyuncu"]["yollar"]) + len(oyun_durumu_catan["oyuncu"]["koyler"]) + len(oyun_durumu_catan["oyuncu"]["sehirler"]))
            ortalama_kaynak_artis = (oyuncu_toplam_kaynak - 25) / tur_sayisi if tur_sayisi > 0 else 0
            puan_artis = oyuncu_puan / tur_sayisi if tur_sayisi > 0 else 0

            zorluk_puan = (ortalama_kaynak_artis * 0.5 + puan_artis * 2) - (ai_toplam_kaynak - 25 + ai_puan) * 0.1
            if zorluk_puan > 2:
                oyun_durumu_catan["ai_zorluk"] = "Zor"
            elif zorluk_puan < -2:
                oyun_durumu_catan["ai_zorluk"] = "Kolay"
            else:
                oyun_durumu_catan["ai_zorluk"] = "Orta"
            print(f"AI Zorluk: {oyun_durumu_catan['ai_zorluk']}, Zorluk Puan: {zorluk_puan}")

        def sira_degis_catan():
            print("Catan sıra değişiyor...")
            oyun_durumu_catan["sira"] = "AI" if oyun_durumu_catan["sira"] == "Oyuncu" else "Oyuncu"
            if oyun_durumu_catan["oyuncu"]["puan"] >= ZAFER_PUANI_CATAN or oyun_durumu_catan["ai"]["puan"] >= ZAFER_PUANI_CATAN:
                oyun_durumu_catan["oyun_bitti"] = True
            if oyun_durumu_catan["sira"] == "AI" and not oyun_durumu_catan["cok_oyunculu"]:
                threading.Timer(1, ai_hamle_catan).start()
            arayuz_guncelle_catan()

        def oyun_durumu_kontrol_catan():
            print("Catan oyun durumu kontrol ediliyor...")
            oyuncu_kaynaklar = oyun_durumu_catan["oyuncu"]["kaynaklar"]
            oyuncu_koyler = oyun_durumu_catan["oyuncu"]["koyler"]
            oyuncu_sehirler = oyun_durumu_catan["oyuncu"]["sehirler"]

            # Oyuncunun ilerleyip ilerleyemeyeceğini kontrol et
            ilerleyebilir = False
            for tip in ["yol", "koy", "sehir"]:
                for i in range(GRID_BOYUT_CATAN):
                    for j in range(GRID_BOYUT_CATAN):
                        if (tip == "yol" and (yolda_komsu_var_mi_catan(i, j, "oyuncu") or not oyun_durumu_catan["oyuncu"]["yollar"]) and not any((i, j) in oyun_durumu_catan["ai"][k] for k in ["yollar", "koyler", "sehirler"])) or \
                           (tip == "koy" and koyde_komsu_yok_mu_catan(i, j) and yolda_komsu_var_mi_catan(i, j, "oyuncu") and not any((i, j) in oyun_durumu_catan["ai"][k] for k in ["yollar", "koyler", "sehirler"])) or \
                           (tip == "sehir" and (i, j) in oyun_durumu_catan["oyuncu"]["koyler"]):
                            if yeterli_kaynak_var_mi_catan(tip, "oyuncu"):
                                ilerleyebilir = True
                                break
                        elif not yeterli_kaynak_var_mi_catan(tip, "oyuncu"):
                            # Eksik kaynak kontrolü
                            for kaynak, miktar in INSAAT_FIYATLARI_CATAN[tip].items():
                                if oyuncu_kaynaklar[kaynak] < miktar:
                                    erisilebilir = False
                                    for ti in range(GRID_BOYUT_CATAN):
                                        for tj in range(GRID_BOYUT_CATAN):
                                            if oyun_durumu_catan["tahta"][ti][tj]["kaynak"] == kaynak and ((ti, tj) in oyuncu_koyler or (ti, tj) in oyuncu_sehirler or yolda_komsu_var_mi_catan(ti, tj, "oyuncu")):
                                                erisilebilir = True
                                                break
                                        if erisilebilir:
                                            break
                                    if not erisilebilir:
                                        oyun_durumu_catan["oyun_bitti"] = True
                                        # AI simülasyonu
                                        temp_oyun_durumu = copy.deepcopy(oyun_durumu_catan)
                                        temp_oyun_durumu["sira"] = "AI"
                                        while temp_oyun_durumu["ai"]["puan"] < ZAFER_PUANI_CATAN and any(yeterli_kaynak_var_mi_catan(tip, "ai") for tip in ["yol", "koy", "sehir"]):
                                            ai_hamle_simulasyon_catan(temp_oyun_durumu)
                                        kazanan = "AI" if temp_oyun_durumu["ai"]["puan"] >= ZAFER_PUANI_CATAN else "AI"  # Varsayılan AI kazandı
                                        oyun_durumu_catan["durum_mesaji"] = f"Oyun bitti! {kazanan} kazandı çünkü oyuncu {kaynak} kaynaklarına erişemedi."
                                        arayuz_guncelle_catan()
                                        return
                    if ilerleyebilir:
                        break
                if ilerleyebilir:
                    break

            if oyun_durumu_catan["oyuncu"]["puan"] >= ZAFER_PUANI_CATAN:
                oyun_durumu_catan["oyun_bitti"] = True
                oyun_durumu_catan["durum_mesaji"] = "Oyun bitti! Oyuncu kazandı."
                arayuz_guncelle_catan()
            elif oyun_durumu_catan["ai"]["puan"] >= ZAFER_PUANI_CATAN:
                oyun_durumu_catan["oyun_bitti"] = True
                oyun_durumu_catan["durum_mesaji"] = "Oyun bitti! AI kazandı."
                arayuz_guncelle_catan()

        def ai_hamle_simulasyon_catan(temp_oyun_durumu):
            while any(temp_oyun_durumu["ai"]["kaynaklar"][k] > 0 for k in KAYNAKLAR_CATAN):
                hamleler = []
                for i in range(GRID_BOYUT_CATAN):
                    for j in range(GRID_BOYUT_CATAN):
                        if koyde_komsu_yok_mu_catan(i, j) and yolda_komsu_var_mi_catan(i, j, "ai") and not any((i, j) in temp_oyun_durumu["oyuncu"][k] for k in ["yollar", "koyler", "sehirler"]):
                            if yeterli_kaynak_var_mi_catan("koy", "ai"):
                                zar_degeri = temp_oyun_durumu["tahta"][i][j]["zar"]
                                zar_olasilik = 6 - abs(7 - zar_degeri)
                                deger = PUANLAR_CATAN["koy"] * 10 + zar_olasilik * 3
                                hamleler.append(("koy", i, j, deger))
                        if (i, j) in temp_oyun_durumu["ai"]["koyler"]:
                            if yeterli_kaynak_var_mi_catan("sehir", "ai"):
                                deger = (PUANLAR_CATAN["sehir"] - PUANLAR_CATAN["koy"]) * 8
                                hamleler.append(("sehir", i, j, deger))
                        if (yolda_komsu_var_mi_catan(i, j, "ai") or not temp_oyun_durumu["ai"]["yollar"]) and not any((i, j) in temp_oyun_durumu["oyuncu"][k] for k in ["yollar", "koyler", "sehirler"]):
                            if yeterli_kaynak_var_mi_catan("yol", "ai"):
                                deger = 2
                                for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                                    ni, nj = i + di, j + dj
                                    if 0 <= ni < GRID_BOYUT_CATAN and 0 <= nj < GRID_BOYUT_CATAN and koyde_komsu_yok_mu_catan(ni, nj):
                                        deger += 3
                                hamleler.append(("yol", i, j, deger))

                if hamleler:
                    hamleler.sort(key=lambda x: x[3], reverse=True)
                    tip, i, j, _ = hamleler[0]
                    if tip == "yol":
                        temp_oyun_durumu["ai"]["yollar"].append((i, j))
                        kaynak_harca_catan("yol", "ai")
                    elif tip == "koy":
                        temp_oyun_durumu["ai"]["koyler"].append((i, j))
                        temp_oyun_durumu["ai"]["puan"] += PUANLAR_CATAN["koy"]
                        kaynak_harca_catan("koy", "ai")
                    elif tip == "sehir":
                        temp_oyun_durumu["ai"]["koyler"].remove((i, j))
                        temp_oyun_durumu["ai"]["sehirler"].append((i, j))
                        temp_oyun_durumu["ai"]["puan"] += PUANLAR_CATAN["sehir"] - PUANLAR_CATAN["koy"]
                        kaynak_harca_catan("sehir", "ai")
                else:
                    break

        def yeniden_baslat_catan(e):
            print("Catan yeniden başlat tıklandı")
            # Orijinal oyuncu adını koru
            original_player_name = oyun_durumu_catan["oyuncu"]["ad"]
            
            # Resetleme işlemi
            oyun_durumu_catan.update({
                "oyun_basladi": False,
                "oyun_bitti": False,
                "cok_oyunculu": False,
                "sunucu_mu": False,
                "istemci_socket": None,
                "oyuncular": [],
                "canli_skorlar": [],
                "sira": "Oyuncu",
                "durum_mesaji": "Catan Strateji Oyununa Hoş Geldiniz!",
                "oyuncu": {
                    "ad": original_player_name, # Korunan adı kullan
                    "kaynaklar": {k: 5 for k in KAYNAKLAR_CATAN},
                    "yollar": [],
                    "koyler": [],
                    "sehirler": [],
                    "puan": 0,
                    "son_zar_zamani": 0,
                    "toplam_kaynak": 25
                },
                "ai": {
                    "ad": "AI",
                    "kaynaklar": {k: 5 for k in KAYNAKLAR_CATAN},
                    "yollar": [],
                    "koyler": [],
                    "sehirler": [],
                    "puan": 0,
                    "toplam_kaynak": 25
                },
                "tahta": [[{"kaynak": random.choice(KAYNAKLAR_CATAN), "zar": random.randint(2, 12)} for _ in range(GRID_BOYUT_CATAN)] for _ in range(GRID_BOYUT_CATAN)],
                "ai_zorluk": "Orta"
            })
            if oyun_durumu_catan["istemci_socket"]:
                try:
                    oyun_durumu_catan["istemci_socket"].close()
                except:
                    pass
                oyun_durumu_catan["istemci_socket"] = None
            ana_menu_ekrani_catan()

        tahta_grid.current = ft.GridView(
            runs_count=GRID_BOYUT_CATAN,
            max_extent=80,
            child_aspect_ratio=1.0,
            spacing=2,
            run_spacing=2,
            width=400,
            height=400
        )
        kaynak_gosterge.current = ft.Text("", size=14, width=400, text_align=ft.TextAlign.CENTER)
        puan_gosterge.current = ft.Text(f"Puan: {oyun_durumu_catan['oyuncu']['puan']}", size=14, width=400, text_align=ft.TextAlign.CENTER)
        durum_cubugu.current = ft.Text(oyun_durumu_catan["durum_mesaji"], size=14, color=ft.colors.BLUE_700, width=400, text_align=ft.TextAlign.CENTER)
        canli_skor_gosterge.current = ft.Text("", size=14, text_align=ft.TextAlign.LEFT)
        kontrol_paneli.current = ft.ResponsiveRow(
            controls=[
                ft.ElevatedButton("Zar At", on_click=zar_at_catan, col={"xs": 12, "md": 6}, width=200, bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, style=STADIUM_BUTTON_STYLE),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            width=400
        )
        yeniden_baslat_buton.current = ft.ElevatedButton("Yeniden Oyna", ref=yeniden_baslat_buton, on_click=yeniden_baslat_catan, bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, visible=False, width=200, style=STADIUM_BUTTON_STYLE)
        skor_ekrani_container.current = ft.Container(content=ft.Text(""), visible=False, bgcolor=ft.colors.GREY_100, padding=20, width=400, height=300)

        sayfa.add(
            ft.Column(
                [
                    ft.Text("Catan Oyun Ekranı", size=24, weight=ft.FontWeight.BOLD),
                    tahta_grid.current,
                    kaynak_gosterge.current,
                    puan_gosterge.current,
                    durum_cubugu.current,
                    kontrol_paneli.current,
                    ft.Row([yeniden_baslat_buton.current], alignment=ft.MainAxisAlignment.CENTER),
                    skor_ekrani_container.current,
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Canlı Skorlar", size=14, weight=ft.FontWeight.BOLD),
                                canli_skor_gosterge.current
                            ]
                        ),
                        width=150,
                        height=150,
                        padding=10,
                        bgcolor=ft.colors.GREY_200
                    ),
                    ft.ElevatedButton("Ana Menüye Dön", on_click=lambda e: ana_menu_ekrani_catan(), bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, width=200, style=STADIUM_BUTTON_STYLE, icon=ft.icons.ARROW_BACK)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
                scroll=ft.ScrollMode.ADAPTIVE
            )
        )
        oyun_durumu_catan["oyun_basladi"] = True
        arayuz_guncelle_catan()

    # Catan için ilk olarak ana menüyü göster
    ana_menu_ekrani_catan()

# ===================================================================================
# =============================== CATAN OYUN KODU BİTİŞ =================================
# ===================================================================================



# ===================================================================================
# =============================== HEX OYUN KODU BAŞLANGIÇ ===============================
# ===================================================================================

# --- Hex Oyun Sabitleri ---
HEX_BOARD_SIZE = 9
CELL_RADIUS = 25
CELL_SPACING_FACTOR = 0.866 # sqrt(3)/2
SUNUCU_PORTU_HEX = 12348

# === GÜÇLENDİRİLMİŞ MCTS AYARLARI ===
MCTS_SIMS_EASY = 100
MCTS_SIMS_MEDIUM = 400
MCTS_SIMS_HARD = 1000

# Zorluk Seviyesi Dosyası
ZORLUK_DOSYASI_HEX = Path("zorluk_hex.json")

# Hex Renkler
PLAYER_1_COLOR_HEX = ft.colors.BLUE_600
PLAYER_2_COLOR_HEX = ft.colors.RED_600
EMPTY_HEX_COLOR = ft.colors.GREY_400
BORDER_HEX_COLOR = ft.colors.BLACK38
WIN_PATH_HEX_COLOR = ft.colors.YELLOW_ACCENT_700
HOVER_HEX_COLOR = ft.colors.with_opacity(0.4, ft.colors.LIGHT_GREEN_ACCENT_400)

# Hex Oyun Durumu
oyun_durumu_hex = {
    "tahta": [[0 for _ in range(HEX_BOARD_SIZE)] for _ in range(HEX_BOARD_SIZE)],
    "mevcut_oyuncu": 1,
    "oyun_basladi": False,
    "oyun_bitti": False,
    "kazanan": None,
    "kazanan_adi_str": "",
    "kazanan_yol": [],
    "oyuncu_adi": "Oyuncu",
    "sira_mesaji": "Sıra: Oyuncu (Mavi)",
    "zorluk_seviyesi": "Orta",
    "egitim_modu": False,
    # === YENİLENMİŞ EĞİTİM MODU İSTATİSTİKLERİ ===
    "oyuncu_istatistikleri_hex": {
        "oynanan_egitim_oyunlari": 0,
        "kazanilan_egitim_oyunlari": 0,
        "yz_yenilgi_sayisi_egitimde": 0,
        "kazanma_yolu_uzunluklari": [],
        "son_kazanma_yolu_uzunlugu": float('inf'),
        # YZ'nin oyuncuya göre dinamik olarak ayarlanan beceri seviyesi.
        "yz_beceri_puani_hex": 75,
    },
    "egitim_modu_bitti_flag": False,
    "hovered_cell": None,
    "cok_oyunculu": False,
    "sunucu_mu": None,
    "istemci_soketi": None,
    "sunucu_soketi_referansi": None,
    "oyuncular_hex": [],
    "_cok_oyunculu_menu_aktif": False,
    "_sunucu_kurulum_aktif": False,
    "_istemci_baglanma_aktif": False,
    "p1_hedef_kenarlar_str": "Üst-Alt",
    "p2_hedef_kenarlar_str": "Sol-Sağ",
    "baslangic_oyuncusu": 1,
}

# --- Hex Zorluk Seviyesi İşlemleri ---
def zorluk_seviyesi_oku_hex():
    try:
        if ZORLUK_DOSYASI_HEX.exists():
            with open(ZORLUK_DOSYASI_HEX, "r", encoding="utf-8") as f:
                veri = json.load(f)
                oyun_durumu_hex["zorluk_seviyesi"] = veri.get("zorluk_hex", "Orta")
                oyun_durumu_hex["oyuncu_istatistikleri_hex"]["yz_beceri_puani_hex"] = veri.get("yz_beceri_puani_hex", 75)
    except Exception as e:
        print(f"Hex zorluk okuma hatası: {str(e)}")

def zorluk_seviyesi_kaydet_hex():
    try:
        with open(ZORLUK_DOSYASI_HEX, "w", encoding="utf-8") as f:
            veri_kaydet = {
                "zorluk_hex": oyun_durumu_hex["zorluk_seviyesi"],
                "yz_beceri_puani_hex": oyun_durumu_hex["oyuncu_istatistikleri_hex"]["yz_beceri_puani_hex"]
            }
            json.dump(veri_kaydet, f)
    except Exception as e:
        print(f"Hex zorluk kaydetme hatası: {str(e)}")

# --- Hex Ana Fonksiyon ---
def main_hex(sayfa: ft.Page, go_to_master_menu_func):
    sayfa.title = "Hex Oyunu"
    sayfa.vertical_alignment = ft.MainAxisAlignment.CENTER
    sayfa.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    sayfa.theme_mode = ft.ThemeMode.LIGHT

    single_hex_full_width = CELL_RADIUS * 2
    single_hex_height = CELL_RADIUS * 2 * CELL_SPACING_FACTOR
    canvas_width = (HEX_BOARD_SIZE * single_hex_full_width * 0.75) + (single_hex_full_width * 0.25) + CELL_RADIUS
    canvas_height = (HEX_BOARD_SIZE * single_hex_height) + (single_hex_height / 2 if HEX_BOARD_SIZE > 0 else 0) + CELL_RADIUS

    sayfa.window_width = max(850, int(canvas_width + 250))
    sayfa.window_height = max(750, int(canvas_height + 400))
    # sayfa.window_center() # Ana merkezleme master_main'de yapılıyor.
    sayfa.bgcolor = PAGE_BG_COLOR

    zorluk_seviyesi_oku_hex()

    mod_secim_konteyneri_hex = ft.Ref[ft.Container]()
    oyuncu_adi_girdi_hex = ft.Ref[ft.TextField]()
    mevcut_zorluk_goster_hex = ft.Ref[ft.Text]()
    cok_oyunculu_secim_konteyneri_hex = ft.Ref[ft.Container]()
    sunucu_olustur_konteyneri_hex = ft.Ref[ft.Container]()
    sunucu_baglan_konteyneri_hex = ft.Ref[ft.Container]()
    sunucu_adresi_girdi_hex = ft.Ref[ft.TextField]()
    sunucu_adresi_goster_hex = ft.Ref[ft.Text]()
    baglanan_oyuncular_goster_hex = ft.Ref[ft.Text]()
    oyun_baslat_cok_oyunculu_buton_hex = ft.Ref[ft.ElevatedButton]()

    tahta_canvas_ref = ft.Ref[ft.canvas.Canvas]()
    tahta_gesture_detector_ref = ft.Ref[ft.GestureDetector]()
    tahta_dis_konteyner_ref = ft.Ref[ft.Container]()

    oyun_bilgisi_goster_hex = ft.Ref[ft.Text]()
    geri_bildirim_goster_hex = ft.Ref[ft.Text]()
    oyun_geri_cik_buton_hex = ft.Ref[ft.ElevatedButton]()
    bitis_ekrani_konteyneri_hex = ft.Ref[ft.Container]()

    def get_hexagon_points_hex(center_x, center_y, radius):
        points = []
        for i in range(6):
            angle_rad = math.pi / 180 * (60 * i)
            points.append((center_x + radius * math.cos(angle_rad),
                           center_y + radius * math.sin(angle_rad)))
        return points

    def get_cell_center_hex(row, col, radius, spacing_factor):
        hex_width = radius * 2
        hex_height_spacing = radius * spacing_factor * 2
        center_x = (col * hex_width * 0.75) + radius
        center_y = (row * hex_height_spacing) + (hex_height_spacing / 2 if col % 2 != 0 else 0) + radius
        return center_x, center_y

    def arayuz_guncelle_hex():
        if not mod_secim_konteyneri_hex.current: return # Ekran kapatıldıysa güncelleme yapma

        is_game_active = oyun_durumu_hex["oyun_basladi"] and not oyun_durumu_hex["oyun_bitti"]
        is_game_over_screen = oyun_durumu_hex["oyun_bitti"]
        is_ana_menu_visible = not is_game_active and not is_game_over_screen and \
                              not oyun_durumu_hex.get("_cok_oyunculu_menu_aktif") and \
                              not oyun_durumu_hex.get("_sunucu_kurulum_aktif") and \
                              not oyun_durumu_hex.get("_istemci_baglanma_aktif")

        if mod_secim_konteyneri_hex.current:
            mod_secim_konteyneri_hex.current.visible = is_ana_menu_visible
            if is_ana_menu_visible and mevcut_zorluk_goster_hex.current:
                mevcut_zorluk_goster_hex.current.value = f"Mevcut YZ Zorluğu: {oyun_durumu_hex['zorluk_seviyesi']}"

        if cok_oyunculu_secim_konteyneri_hex.current: cok_oyunculu_secim_konteyneri_hex.current.visible = oyun_durumu_hex.get("_cok_oyunculu_menu_aktif", False)
        if sunucu_olustur_konteyneri_hex.current:
            sunucu_olustur_konteyneri_hex.current.visible = oyun_durumu_hex.get("_sunucu_kurulum_aktif", False)
            if oyun_durumu_hex.get("_sunucu_kurulum_aktif"):
                if sunucu_adresi_goster_hex.current: sunucu_adresi_goster_hex.current.value = oyun_durumu_hex.get("_server_address_info", "Sunucu adresi alınıyor...")
                if baglanan_oyuncular_goster_hex.current: baglanan_oyuncular_goster_hex.current.value = oyun_durumu_hex.get("_connected_players_info", "Oyuncular bekleniyor...")
                if oyun_baslat_cok_oyunculu_buton_hex.current: oyun_baslat_cok_oyunculu_buton_hex.current.disabled = oyun_durumu_hex.get("_start_game_button_disabled", True)

        if sunucu_baglan_konteyneri_hex.current: sunucu_baglan_konteyneri_hex.current.visible = oyun_durumu_hex.get("_istemci_baglanma_aktif", False)

        if tahta_dis_konteyner_ref.current: tahta_dis_konteyner_ref.current.visible = is_game_active
        if oyun_bilgisi_goster_hex.current: oyun_bilgisi_goster_hex.current.visible = is_game_active
        if oyun_geri_cik_buton_hex.current: oyun_geri_cik_buton_hex.current.visible = is_game_active
        if bitis_ekrani_konteyneri_hex.current: bitis_ekrani_konteyneri_hex.current.visible = is_game_over_screen

        if is_game_over_screen and bitis_ekrani_konteyneri_hex.current:
            bitis_ekrani_konteyneri_hex.current.content = bitis_ekrani_olustur_hex()

        if geri_bildirim_goster_hex.current:
            temp_feedback = oyun_durumu_hex.pop("_temp_feedback", None)
            if is_game_over_screen:
                mesaj = f"Oyun Bitti! Kazanan: {oyun_durumu_hex.get('kazanan_adi_str', 'Bilinmiyor')}. "
                if oyun_durumu_hex.get("egitim_modu_bitti_flag"):
                    mevcut_beceri = oyun_durumu_hex["oyuncu_istatistikleri_hex"]["yz_beceri_puani_hex"]
                    mesaj += f"Eğitim sonrası YZ zorluk: {oyun_durumu_hex['zorluk_seviyesi']} (Beceri Puanı: {mevcut_beceri})"
                geri_bildirim_goster_hex.current.value = mesaj
            elif is_game_active:
                sira_mesaji = oyun_durumu_hex["sira_mesaji"]
                if oyun_durumu_hex["egitim_modu"] and oyun_durumu_hex["mevcut_oyuncu"] == 2:
                    sira_mesaji += f" (Beceri: {oyun_durumu_hex['oyuncu_istatistikleri_hex']['yz_beceri_puani_hex']})"
                geri_bildirim_goster_hex.current.value = sira_mesaji
            elif temp_feedback:
                geri_bildirim_goster_hex.current.value = temp_feedback
            elif oyun_durumu_hex.get("_sunucu_kurulum_aktif"):
                geri_bildirim_goster_hex.current.value = "Sunucu diğer oyuncuyu bekliyor..."
            elif oyun_durumu_hex.get("_istemci_baglanma_aktif") and oyun_durumu_hex.get("istemci_soketi"):
                 geri_bildirim_goster_hex.current.value = "Sunucuya bağlandınız. Oyunun başlaması bekleniyor."
            elif oyun_durumu_hex.get("_istemci_baglanma_aktif"):
                 geri_bildirim_goster_hex.current.value = "Sunucuya bağlanılıyor..."
            elif oyun_durumu_hex.get("_cok_oyunculu_menu_aktif"):
                geri_bildirim_goster_hex.current.value = f"{oyun_durumu_hex.get('oyuncu_adi')}, çok oyunculu mod seçin."
            elif is_ana_menu_visible :
                 geri_bildirim_goster_hex.current.value = "Lütfen oyuncu adınızı girip mod seçin."
            else:
                 geri_bildirim_goster_hex.current.value = "Hex Oyununa Hoş Geldiniz!"

        if oyun_bilgisi_goster_hex.current and is_game_active:
            p1_kim = oyun_durumu_hex.get("oyuncu_adi", "Oyuncu 1") if oyun_durumu_hex["mevcut_oyuncu"] == 1 or not oyun_durumu_hex.get("cok_oyunculu") else (oyun_durumu_hex["oyuncular_hex"][0]["ad"] if oyun_durumu_hex["oyuncular_hex"] else "Oyuncu 1")
            p2_kim = "Yapay Zeka"
            if oyun_durumu_hex.get("cok_oyunculu"):
                p2_kim = oyun_durumu_hex["oyuncular_hex"][1]["ad"] if len(oyun_durumu_hex.get("oyuncular_hex",[])) > 1 else "Oyuncu 2"
            oyun_bilgisi_mesaji = f"{p1_kim} (Mavi) hedef: {oyun_durumu_hex['p1_hedef_kenarlar_str']}\n"
            oyun_bilgisi_mesaji += f"{p2_kim} (Kırmızı) hedef: {oyun_durumu_hex['p2_hedef_kenarlar_str']}"
            oyun_bilgisi_goster_hex.current.value = oyun_bilgisi_mesaji

        if tahta_canvas_ref.current and is_game_active:
            cizim_listesi = []
            for r_idx in range(HEX_BOARD_SIZE):
                for c_idx in range(HEX_BOARD_SIZE):
                    center_x, center_y = get_cell_center_hex(r_idx, c_idx, CELL_RADIUS, CELL_SPACING_FACTOR)
                    points = get_hexagon_points_hex(center_x, center_y, CELL_RADIUS * 0.92)
                    cell_value = oyun_durumu_hex["tahta"][r_idx][c_idx]
                    cell_color_val = EMPTY_HEX_COLOR
                    if cell_value == 1: cell_color_val = PLAYER_1_COLOR_HEX
                    elif cell_value == 2: cell_color_val = PLAYER_2_COLOR_HEX
                    is_on_win_path = (r_idx,c_idx) in oyun_durumu_hex["kazanan_yol"]
                    fill_color_val = WIN_PATH_HEX_COLOR if is_on_win_path else cell_color_val
                    if oyun_durumu_hex["hovered_cell"] == (r_idx,c_idx) and oyun_durumu_hex["tahta"][r_idx][c_idx] == 0 and gecerli_hamle_mi_hex(r_idx,c_idx, False):
                        fill_color_val = HOVER_HEX_COLOR
                    path_elements = [ft.canvas.Path.MoveTo(points[0][0], points[0][1])]
                    for point_idx in range(1, 6): path_elements.append(ft.canvas.Path.LineTo(points[point_idx][0], points[point_idx][1]))
                    path_elements.append(ft.canvas.Path.Close())
                    cizim_listesi.append(ft.canvas.Path(path_elements,paint=ft.Paint(style=ft.PaintingStyle.FILL,color=fill_color_val)))
                    cizim_listesi.append(ft.canvas.Path(path_elements,paint=ft.Paint(style=ft.PaintingStyle.STROKE,color=BORDER_HEX_COLOR,stroke_width=1.5)))
            tahta_canvas_ref.current.shapes = cizim_listesi
        elif tahta_canvas_ref.current:
            tahta_canvas_ref.current.shapes = []
        sayfa.update()

    def tahta_baslat_hex(egitim=False, cok_oyunculu_baslangic=False, gelen_tahta=None, gelen_ayarlar=None):
        oyun_durumu_hex["tahta"] = gelen_tahta if gelen_tahta and cok_oyunculu_baslangic else [[0 for _ in range(HEX_BOARD_SIZE)] for _ in range(HEX_BOARD_SIZE)]
        oyun_durumu_hex["egitim_modu"] = egitim if not cok_oyunculu_baslangic else False

        if cok_oyunculu_baslangic and gelen_ayarlar:
            oyun_durumu_hex["baslangic_oyuncusu"] = gelen_ayarlar.get("baslangic_oyuncusu", 1)
            oyun_durumu_hex["p1_hedef_kenarlar_str"] = gelen_ayarlar.get("p1_hedef_kenarlar_str", "Üst-Alt")
            oyun_durumu_hex["p2_hedef_kenarlar_str"] = gelen_ayarlar.get("p2_hedef_kenarlar_str", "Sol-Sağ")
            oyun_durumu_hex["oyuncular_hex"] = gelen_ayarlar.get("oyuncular_hex", [])
        else:
            oyun_durumu_hex["baslangic_oyuncusu"] = random.choice([1, 2])
            if random.choice([True, False]):
                oyun_durumu_hex["p1_hedef_kenarlar_str"] = "Üst-Alt"
                oyun_durumu_hex["p2_hedef_kenarlar_str"] = "Sol-Sağ"
            else:
                oyun_durumu_hex["p1_hedef_kenarlar_str"] = "Sol-Sağ"
                oyun_durumu_hex["p2_hedef_kenarlar_str"] = "Üst-Alt"

        oyun_durumu_hex["mevcut_oyuncu"] = oyun_durumu_hex["baslangic_oyuncusu"]

        sira_kimde_adi = ""; sira_kimde_renk_str = ""
        oyuncu_no_sira = oyun_durumu_hex["mevcut_oyuncu"]
        if oyuncu_no_sira == 1:
            sira_kimde_renk_str = "Mavi"
            sira_kimde_adi = oyun_durumu_hex.get("oyuncu_adi", "Oyuncu") if not oyun_durumu_hex["cok_oyunculu"] else (oyun_durumu_hex["oyuncular_hex"][0].get("ad", "Oyuncu 1") if oyun_durumu_hex["oyuncular_hex"] else "Oyuncu 1")
        else:
            sira_kimde_renk_str = "Kırmızı"
            sira_kimde_adi = "Yapay Zeka" if not oyun_durumu_hex["cok_oyunculu"] else (oyun_durumu_hex["oyuncular_hex"][1].get("ad", "Oyuncu 2") if len(oyun_durumu_hex.get("oyuncular_hex",[])) > 1 else "Oyuncu 2")
        oyun_durumu_hex["sira_mesaji"] = f"Sıra: {sira_kimde_adi} ({sira_kimde_renk_str})"

        oyun_durumu_hex["kazanan"] = None; oyun_durumu_hex["kazanan_adi_str"] = ""; oyun_durumu_hex["kazanan_yol"] = []
        oyun_durumu_hex["oyun_bitti"] = False; oyun_durumu_hex["oyun_basladi"] = True; oyun_durumu_hex["egitim_modu_bitti_flag"] = False

        if oyun_durumu_hex["egitim_modu"]:
            istat = oyun_durumu_hex.get("oyuncu_istatistikleri_hex", {})
            istat["oynanan_egitim_oyunlari"] = istat.get("oynanan_egitim_oyunlari",0) + 1
            istat["son_kazanma_yolu_uzunlugu"] = float('inf')
            oyun_durumu_hex["oyuncu_istatistikleri_hex"] = istat
        elif not cok_oyunculu_baslangic :
            zorluk_seviyesi_oku_hex()

        oyun_durumu_hex["_cok_oyunculu_menu_aktif"] = False
        oyun_durumu_hex["_sunucu_kurulum_aktif"] = False
        oyun_durumu_hex["_istemci_baglanma_aktif"] = False
        arayuz_guncelle_hex()

        if oyun_durumu_hex["mevcut_oyuncu"] == 2 and not oyun_durumu_hex["cok_oyunculu"] and not oyun_durumu_hex["oyun_bitti"]:
            threading.Thread(target=yapay_zeka_hamlesi_hex_wrapper, daemon=True).start()

    def gecerli_hamle_mi_hex(row, col, check_turn=True):
        if oyun_durumu_hex["oyun_bitti"] or not oyun_durumu_hex["oyun_basladi"]: return False
        if check_turn:
            is_my_turn = False
            if not oyun_durumu_hex["cok_oyunculu"]:
                if oyun_durumu_hex["mevcut_oyuncu"] == 1: is_my_turn = True
            else:
                my_player_id = 1 if oyun_durumu_hex["sunucu_mu"] else oyun_durumu_hex.get("mevcut_oyuncu_id_yerel")
                if my_player_id is not None and my_player_id == oyun_durumu_hex["mevcut_oyuncu"]:
                    is_my_turn = True
            if not is_my_turn: return False
        return 0 <= row < HEX_BOARD_SIZE and 0 <= col < HEX_BOARD_SIZE and oyun_durumu_hex["tahta"][row][col] == 0

    def komsulari_bul_hex(row, col, size):
        komsular = []
        potential_neighbors = [
            (row - 1, col), (row + 1, col),
            (row, col - 1), (row, col + 1),
            (row - 1, col + 1), (row + 1, col - 1)
        ]
        for nr, nc in potential_neighbors:
            if 0 <= nr < size and 0 <= nc < size:
                komsular.append((nr, nc))
        return komsular

    def dfs_ile_yol_bul_hex(oyuncu, start_node, hedef_kenar_kontrol_fonksiyonu, tahta_kopya, ziyaret_edilen_dfs, mevcut_yol_dfs):
        r, c = start_node
        if start_node in ziyaret_edilen_dfs or tahta_kopya[r][c] != oyuncu: return False, []
        ziyaret_edilen_dfs.add(start_node); mevcut_yol_dfs.append(start_node)
        if hedef_kenar_kontrol_fonksiyonu(r, c): return True, list(mevcut_yol_dfs)
        for komsu_r, komsu_c in komsulari_bul_hex(r, c, len(tahta_kopya)):
            sonuc, bulunan_yol = dfs_ile_yol_bul_hex(oyuncu, (komsu_r, komsu_c), hedef_kenar_kontrol_fonksiyonu, tahta_kopya, ziyaret_edilen_dfs, mevcut_yol_dfs)
            if sonuc: return True, bulunan_yol
        mevcut_yol_dfs.pop(); return False, []

    def kazanani_kontrol_et_hex_oyuncu(oyuncu_no, tahta):
        size = len(tahta)
        hedef_kenarlar_str = oyun_durumu_hex['p1_hedef_kenarlar_str'] if oyuncu_no == 1 else oyun_durumu_hex['p2_hedef_kenarlar_str']
        if hedef_kenarlar_str == "Üst-Alt":
            for c_start in range(size):
                if tahta[0][c_start] == oyuncu_no:
                    hedef_kontrol = lambda r_h, c_h: r_h == size - 1
                    kazandi, yol = dfs_ile_yol_bul_hex(oyuncu_no, (0, c_start), hedef_kontrol, tahta, set(), [])
                    if kazandi: return oyuncu_no, yol
        elif hedef_kenarlar_str == "Sol-Sağ":
            for r_start in range(size):
                if tahta[r_start][0] == oyuncu_no:
                    hedef_kontrol = lambda r_h, c_h: c_h == size - 1
                    kazandi, yol = dfs_ile_yol_bul_hex(oyuncu_no, (r_start, 0), hedef_kontrol, tahta, set(), [])
                    if kazandi: return oyuncu_no, yol
        return None, []

    def hamle_yap_ve_kontrol_et_hex(row, col, hamleyi_yapan_oyuncu_no):
        oyun_durumu_hex["tahta"][row][col] = hamleyi_yapan_oyuncu_no
        kazanan_no, yol = kazanani_kontrol_et_hex_oyuncu(hamleyi_yapan_oyuncu_no, oyun_durumu_hex["tahta"])
        if kazanan_no:
            oyun_durumu_hex["kazanan"] = kazanan_no; oyun_durumu_hex["kazanan_yol"] = yol
            if oyun_durumu_hex["egitim_modu"]:
                if kazanan_no == 1:
                    oyun_durumu_hex["oyuncu_istatistikleri_hex"]["kazanilan_egitim_oyunlari"] += 1
                    oyun_durumu_hex["oyuncu_istatistikleri_hex"]["kazanma_yolu_uzunluklari"].append(len(yol))
                    oyun_durumu_hex["oyuncu_istatistikleri_hex"]["son_kazanma_yolu_uzunlugu"] = len(yol)
                else:
                     oyun_durumu_hex["oyuncu_istatistikleri_hex"]["yz_yenilgi_sayisi_egitimde"] += 1
            oyunu_bitir_hex()
            return True
        return False

    def oyunu_bitir_hex():
        oyun_durumu_hex["oyun_bitti"] = True
        oyun_durumu_hex["oyun_basladi"] = False
        kazanan_no = oyun_durumu_hex["kazanan"]
        kazanan_kim = "Bilinmiyor"
        if kazanan_no == 1:
            kazanan_kim = oyun_durumu_hex.get("oyuncu_adi", "Oyuncu") if not oyun_durumu_hex["cok_oyunculu"] else (oyun_durumu_hex["oyuncular_hex"][0].get("ad", "Oyuncu 1") if oyun_durumu_hex["oyuncular_hex"] else "Oyuncu 1")
        elif kazanan_no == 2:
            kazanan_kim = "Yapay Zeka" if not oyun_durumu_hex["cok_oyunculu"] else (oyun_durumu_hex["oyuncular_hex"][1].get("ad", "Oyuncu 2") if len(oyun_durumu_hex.get("oyuncular_hex",[])) > 1 else "Oyuncu 2")
        oyun_durumu_hex["kazanan_adi_str"] = kazanan_kim

        if oyun_durumu_hex["egitim_modu"]:
            oyun_durumu_hex["egitim_modu_bitti_flag"] = True
            stats = oyun_durumu_hex["oyuncu_istatistikleri_hex"]
            mevcut_puan = stats.get("yz_beceri_puani_hex", 75)
            yeni_puan = mevcut_puan
            if kazanan_no == 1:
                kazanma_yolu_uzunlugu = oyun_durumu_hex.get("son_kazanma_yolu_uzunlugu", HEX_BOARD_SIZE)
                puan_azalmasi = max(5, (HEX_BOARD_SIZE * 2) - kazanma_yolu_uzunlugu)
                yeni_puan = max(10, mevcut_puan - puan_azalmasi)
            elif kazanan_no == 2:
                puan_artisi = 35
                yeni_puan = min(1200, mevcut_puan + puan_artisi)
            stats["yz_beceri_puani_hex"] = int(yeni_puan)
            if yeni_puan < 150: oyun_durumu_hex["zorluk_seviyesi"] = "Kolay"
            elif 150 <= yeni_puan < 500: oyun_durumu_hex["zorluk_seviyesi"] = "Orta"
            else: oyun_durumu_hex["zorluk_seviyesi"] = "Zor"
            zorluk_seviyesi_kaydet_hex()

        if oyun_durumu_hex.get("cok_oyunculu") and oyun_durumu_hex.get("sunucu_mu"):
            bitis_mesaji = {"tip": "oyun_bitti_hex", "kazanan_no": kazanan_no, "kazanan_ad": kazanan_kim, "kazanan_yol": oyun_durumu_hex["kazanan_yol"], "tahta": oyun_durumu_hex["tahta"]}
            if len(oyun_durumu_hex["oyuncular_hex"]) > 1 and oyun_durumu_hex["oyuncular_hex"][1].get("soket"):
                try: oyun_durumu_hex["oyuncular_hex"][1]["soket"].send(json.dumps(bitis_mesaji).encode())
                except Exception as e: print(f"Hex S bitiş mesajı gönderme hatası: {e}")
        arayuz_guncelle_hex()

    def hamle_sonrasi_islemler_hex(hamleyi_yapan_oyuncu_no, row, col):
        oyun_durumu_hex["mevcut_oyuncu"] = 3 - hamleyi_yapan_oyuncu_no
        mevcut_sira_oyuncu_no = oyun_durumu_hex["mevcut_oyuncu"]
        if mevcut_sira_oyuncu_no == 1:
            sira_kimde_renk_str, sira_kimde_adi = "Mavi", oyun_durumu_hex.get("oyuncu_adi", "Oyuncu") if not oyun_durumu_hex["cok_oyunculu"] else (oyun_durumu_hex["oyuncular_hex"][0].get("ad", "Oyuncu 1") if oyun_durumu_hex["oyuncular_hex"] else "Oyuncu 1")
        else:
            sira_kimde_renk_str, sira_kimde_adi = "Kırmızı", "Yapay Zeka" if not oyun_durumu_hex["cok_oyunculu"] else (oyun_durumu_hex["oyuncular_hex"][1].get("ad", "Oyuncu 2") if len(oyun_durumu_hex.get("oyuncular_hex",[])) > 1 else "Oyuncu 2")
        oyun_durumu_hex["sira_mesaji"] = f"Sıra: {sira_kimde_adi} ({sira_kimde_renk_str})"
        arayuz_guncelle_hex()

        if mevcut_sira_oyuncu_no == 2 and not oyun_durumu_hex["cok_oyunculu"] and not oyun_durumu_hex["oyun_bitti"]:
            threading.Thread(target=yapay_zeka_hamlesi_hex_wrapper, daemon=True).start()

    # --- === PERFORMANS İÇİN TAMAMEN YENİDEN YAZILMIŞ MCTS BÖLÜMÜ === ---
    class MCTSNode_Hex:
        def __init__(self, board_state_node, player_to_move, parent=None, move=None):
            self.board_state = board_state_node
            self.player_to_move = player_to_move
            self.parent = parent
            self.move = move
            self.children = []
            self.wins = 0
            self.visits = 0
            self.untried_moves = self._get_legal_moves_for_state_hex()

        def _get_legal_moves_for_state_hex(self):
            moves = []
            for r in range(HEX_BOARD_SIZE):
                for c in range(HEX_BOARD_SIZE):
                    if self.board_state[r][c] == 0:
                        moves.append((r,c))
            random.shuffle(moves)
            return moves

        def select_child_uct_hex(self, exploration_constant=1.414):
            best_score = -float('inf')
            best_children = []
            log_parent_visits = math.log(self.visits) if self.visits > 0 else 0

            for child in self.children:
                if child.visits == 0:
                    score = float('inf')
                else:
                    win_rate = child.wins / child.visits
                    if self.player_to_move == 1:
                        uct_score = -win_rate
                    else:
                        uct_score = win_rate
                    
                    exploration_term = exploration_constant * math.sqrt(log_parent_visits / child.visits)
                    score = uct_score + exploration_term

                if score > best_score:
                    best_score = score
                    best_children = [child]
                elif score == best_score:
                    best_children.append(child)
            
            return random.choice(best_children) if best_children else None

        def expand_hex(self):
            if not self.untried_moves: return None
            move_to_try = self.untried_moves.pop()
            new_board_state = copy.deepcopy(self.board_state)
            new_board_state[move_to_try[0]][move_to_try[1]] = self.player_to_move
            next_player_turn = 3 - self.player_to_move
            child_node = MCTSNode_Hex(new_board_state, player_to_move=next_player_turn, parent=self, move=move_to_try)
            self.children.append(child_node)
            return child_node

        def backpropagate_hex(self, winner_of_simulation):
            self.visits += 1
            if winner_of_simulation == 2: self.wins += 1
            elif winner_of_simulation == 1: self.wins -= 1
            if self.parent:
                self.parent.backpropagate_hex(winner_of_simulation)

        # === PERFORMANS İÇİN OPTİMİZE EDİLMİŞ ROLLOUT ===
        def rollout_hex(self, rollout_player_start):
            current_rollout_board = copy.deepcopy(self.board_state)
            current_rollout_player_turn = rollout_player_start
            
            empty_cells = []
            for r in range(HEX_BOARD_SIZE):
                for c in range(HEX_BOARD_SIZE):
                    if current_rollout_board[r][c] == 0:
                        empty_cells.append((r,c))
            random.shuffle(empty_cells)

            while empty_cells:
                move = self._find_best_rollout_move_hex(current_rollout_board, current_rollout_player_turn, empty_cells)
                
                current_rollout_board[move[0]][move[1]] = current_rollout_player_turn
                empty_cells.remove(move)
                
                current_rollout_player_turn = 3 - current_rollout_player_turn

            final_winner_p1, _ = kazanani_kontrol_et_hex_oyuncu(1, current_rollout_board)
            if final_winner_p1: return 1
            final_winner_p2, _ = kazanani_kontrol_et_hex_oyuncu(2, current_rollout_board)
            if final_winner_p2: return 2
            
            return 0

        # === PERFORMANS İÇİN OPTİMİZE EDİLMİŞ HEURISTIC HAMLE SEÇİMİ ===
        def _find_best_rollout_move_hex(self, board, player, available_moves):
            opponent = 3 - player
            
            # 1. Kazanma hamlesi var mı?
            for r, c in available_moves:
                board[r][c] = player
                winner, _ = kazanani_kontrol_et_hex_oyuncu(player, board)
                board[r][c] = 0
                if winner:
                    return (r, c)
            
            # 2. Rakibin kazanma hamlesini engelle
            for r, c in available_moves:
                board[r][c] = opponent
                winner, _ = kazanani_kontrol_et_hex_oyuncu(opponent, board)
                board[r][c] = 0
                if winner:
                    return (r, c)

            # 3. Kendi taşlarına komşu bir hamle bul (köprü kurma)
            good_moves = []
            for r_empty, c_empty in available_moves:
                for r_k, c_k in komsulari_bul_hex(r_empty, c_empty, HEX_BOARD_SIZE):
                    if board[r_k][c_k] == player:
                        good_moves.append((r_empty, c_empty))
                        break
            
            if good_moves:
                return random.choice(good_moves)

            # 4. Hiçbiri yoksa, rastgele bir hamle yap
            return random.choice(available_moves)

    # --- Yapay Zeka (Geliştirilmiş MCTS Temelli) ---
    def yapay_zeka_hamlesi_hex():
        if oyun_durumu_hex["oyun_bitti"] or oyun_durumu_hex["mevcut_oyuncu"] != 2: return
        start_time_yz = time.time()
        root_board = copy.deepcopy(oyun_durumu_hex["tahta"])
        root_node = MCTSNode_Hex(root_board, player_to_move=2)

        if oyun_durumu_hex["egitim_modu"]:
            beceri_puani = oyun_durumu_hex["oyuncu_istatistikleri_hex"].get("yz_beceri_puani_hex", 75)
            num_simulations = 50 + int(beceri_puani * 1.2)
        else:
            seviye = oyun_durumu_hex["zorluk_seviyesi"]
            if seviye == "Orta": num_simulations = MCTS_SIMS_MEDIUM
            elif seviye == "Zor": num_simulations = MCTS_SIMS_HARD
            else: num_simulations = MCTS_SIMS_EASY
        
        for _ in range(num_simulations):
            node = root_node
            while not node.untried_moves and node.children:
                selected_node = node.select_child_uct_hex()
                if selected_node is None: break
                node = selected_node
            
            is_terminal_p1, _ = kazanani_kontrol_et_hex_oyuncu(1, node.board_state)
            is_terminal_p2, _ = kazanani_kontrol_et_hex_oyuncu(2, node.board_state)
            if not is_terminal_p1 and not is_terminal_p2:
                if node.untried_moves:
                    expanded_node = node.expand_hex()
                    if expanded_node: node = expanded_node
            
            winner_of_rollout = node.rollout_hex(node.player_to_move)
            node.backpropagate_hex(winner_of_rollout)
        
        secilen_hamle = None
        if root_node.children:
            best_child = max(root_node.children, key=lambda c: (c.wins / c.visits) if c.visits > 0 else -float('inf'))
            secilen_hamle = best_child.move
        
        if not secilen_hamle:
            gecerli_hamleler_fallback = root_node._get_legal_moves_for_state_hex()
            if gecerli_hamleler_fallback: secilen_hamle = random.choice(gecerli_hamleler_fallback)
            else:
                if not oyun_durumu_hex["oyun_bitti"]: oyunu_bitir_hex()
                return

        end_time_yz = time.time()
        zorluk_str = oyun_durumu_hex['zorluk_seviyesi'] if not oyun_durumu_hex['egitim_modu'] else "Eğitim"
        print(f"YZ ({zorluk_str}): {num_simulations} sim., Süre: {end_time_yz - start_time_yz:.2f}s, Seçim: {secilen_hamle}")

        if secilen_hamle and oyun_durumu_hex["tahta"][secilen_hamle[0]][secilen_hamle[1]] == 0:
            oyun_bitti_mi = hamle_yap_ve_kontrol_et_hex(secilen_hamle[0], secilen_hamle[1], 2)
            if not oyun_bitti_mi:
                hamle_sonrasi_islemler_hex(2, secilen_hamle[0], secilen_hamle[1])
        else:
             gecerli_hamleler_fallback = [ (r,c) for r in range(HEX_BOARD_SIZE) for c in range(HEX_BOARD_SIZE) if oyun_durumu_hex["tahta"][r][c] == 0 ]
             if gecerli_hamleler_fallback:
                 secilen_hamle_alt = random.choice(gecerli_hamleler_fallback)
                 oyun_bitti_mi = hamle_yap_ve_kontrol_et_hex(secilen_hamle_alt[0], secilen_hamle_alt[1], 2)
                 if not oyun_bitti_mi: hamle_sonrasi_islemler_hex(2, secilen_hamle_alt[0], secilen_hamle_alt[1])
             else:
                 if not oyun_durumu_hex["oyun_bitti"]: oyunu_bitir_hex()

    def yapay_zeka_hamlesi_hex_wrapper():
        time.sleep(0.1)
        yapay_zeka_hamlesi_hex()

    def on_canvas_tap_hex(e: ft.TapEvent):
        if not oyun_durumu_hex["oyun_basladi"] or oyun_durumu_hex["oyun_bitti"]: return
        clicked_r, clicked_c = -1, -1; min_dist_sq = float('inf')
        for r_idx in range(HEX_BOARD_SIZE):
            for c_idx in range(HEX_BOARD_SIZE):
                center_x, center_y = get_cell_center_hex(r_idx, c_idx, CELL_RADIUS, CELL_SPACING_FACTOR)
                dist_sq = (e.local_x - center_x)**2 + (e.local_y - center_y)**2
                if dist_sq < (CELL_RADIUS * 0.95)**2 and dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq; clicked_r, clicked_c = r_idx, c_idx
        if clicked_r != -1:
            if gecerli_hamle_mi_hex(clicked_r, clicked_c):
                oyuncu_no_suan = oyun_durumu_hex["mevcut_oyuncu"]
                if oyun_durumu_hex["cok_oyunculu"]:
                    hamleyi_gonder_hex(clicked_r, clicked_c, oyuncu_no_suan)
                oyun_bitti_mi_bu_hamleyle = hamle_yap_ve_kontrol_et_hex(clicked_r, clicked_c, oyuncu_no_suan)
                if not oyun_bitti_mi_bu_hamleyle:
                    hamle_sonrasi_islemler_hex(oyuncu_no_suan, clicked_r, clicked_c)

    def on_canvas_hover_hex(e: ft.HoverEvent):
        if not oyun_durumu_hex["oyun_basladi"] or oyun_durumu_hex["oyun_bitti"]:
            if oyun_durumu_hex["hovered_cell"] is not None:
                oyun_durumu_hex["hovered_cell"] = None; arayuz_guncelle_hex()
            return
        hover_r, hover_c = -1, -1; min_dist_sq = float('inf')
        for r_idx in range(HEX_BOARD_SIZE):
            for c_idx in range(HEX_BOARD_SIZE):
                center_x, center_y = get_cell_center_hex(r_idx, c_idx, CELL_RADIUS, CELL_SPACING_FACTOR)
                dist_sq = (e.local_x - center_x)**2 + (e.local_y - center_y)**2
                if dist_sq < (CELL_RADIUS * 0.95)**2 and dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq; hover_r, hover_c = r_idx, c_idx
        new_hover = (hover_r, hover_c) if hover_r != -1 else None
        if oyun_durumu_hex["hovered_cell"] != new_hover:
            oyun_durumu_hex["hovered_cell"] = new_hover; arayuz_guncelle_hex()

    def tek_oyunculu_sec_hex_handler(e, is_egitim: bool):
        oyun_durumu_hex["oyuncu_adi"] = oyuncu_adi_girdi_hex.current.value.strip() or "Oyuncu"
        if is_egitim:
            oyun_durumu_hex["oyuncu_istatistikleri_hex"]["son_kazanma_yolu_uzunlugu"] = float('inf')
            zorluk_seviyesi_oku_hex() 
        oyun_durumu_hex["cok_oyunculu"] = False
        oyun_durumu_hex["_cok_oyunculu_menu_aktif"] = False
        oyun_durumu_hex["_sunucu_kurulum_aktif"] = False
        oyun_durumu_hex["_istemci_baglanma_aktif"] = False
        tahta_baslat_hex(egitim=is_egitim)

    def yeniden_baslat_hex_handler(e):
        soketler = ["istemci_soketi", "sunucu_soketi_referansi"]
        for s_key in soketler:
            if oyun_durumu_hex.get(s_key):
                try: oyun_durumu_hex[s_key].close(); oyun_durumu_hex[s_key] = None
                except: pass
        for oyuncu in oyun_durumu_hex.get("oyuncular_hex", []):
            if oyuncu.get("soket"):
                try: oyuncu["soket"].close()
                except: pass
        
        current_oyuncu_adi = oyun_durumu_hex.get("oyuncu_adi", "Oyuncu")
        preserved_stats = {key: oyun_durumu_hex.get("oyuncu_istatistikleri_hex", {}).get(key, default) for key, default in [
            ("oynanan_egitim_oyunlari", 0), ("kazanilan_egitim_oyunlari", 0), ("yz_yenilgi_sayisi_egitimde", 0),
            ("kazanma_yolu_uzunluklari", []), ("yz_beceri_puani_hex", 75)
        ]}
        preserved_stats["son_kazanma_yolu_uzunlugu"] = float('inf')
        current_zorluk = oyun_durumu_hex.get("zorluk_seviyesi", "Orta")
        
        oyun_durumu_hex.clear()
        oyun_durumu_hex.update({
            "tahta": [[0 for _ in range(HEX_BOARD_SIZE)] for _ in range(HEX_BOARD_SIZE)],
            "mevcut_oyuncu": 1, "oyun_basladi": False, "oyun_bitti": False, "kazanan": None,
            "kazanan_adi_str": "", "kazanan_yol": [], "oyuncu_adi": current_oyuncu_adi,
            "sira_mesaji": "Sıra: Oyuncu (Mavi)", "zorluk_seviyesi": current_zorluk, "egitim_modu": False,
            "oyuncu_istatistikleri_hex": preserved_stats, "hovered_cell": None, "cok_oyunculu": False,
            "p1_hedef_kenarlar_str": "Üst-Alt", "p2_hedef_kenarlar_str": "Sol-Sağ"
        })
        if oyuncu_adi_girdi_hex.current: oyuncu_adi_girdi_hex.current.value = oyun_durumu_hex["oyuncu_adi"]
        zorluk_seviyesi_oku_hex()
        arayuz_guncelle_hex()

    def bitis_ekrani_olustur_hex():
        istat = oyun_durumu_hex["oyuncu_istatistikleri_hex"]
        kazanan_adi = oyun_durumu_hex.get("kazanan_adi_str", "Bilinmiyor")
        egitim_sonuclari_text = []
        if oyun_durumu_hex.get("egitim_modu_bitti_flag"):
            oynanan = istat.get("oynanan_egitim_oyunlari",0)
            kazanilan = istat.get("kazanilan_egitim_oyunlari",0)
            oran = f"{(kazanilan / oynanan * 100) if oynanan > 0 else 0:.1f}%"
            son_yol = istat.get("son_kazanma_yolu_uzunlugu", float('inf'))
            son_yol_str = str(son_yol) if son_yol != float('inf') else "N/A"
            son_puan = istat.get("yz_beceri_puani_hex", "N/A")
            
            egitim_sonuclari_text = [
                ft.Text("Eğitim Modu Sonuçları:", weight=ft.FontWeight.BOLD, size=18, color=TEXT_COLOR_DARK),
                ft.Text(f"Toplam Eğitim Maçı: {oynanan}", color=TEXT_COLOR_DARK),
                ft.Text(f"Oyuncu Kazanma Oranı: {oran}", color=TEXT_COLOR_DARK),
                ft.Text(f"Son Galibiyet Yolu: {son_yol_str} adım", color=TEXT_COLOR_DARK),
                ft.Text(f"Güncel YZ Beceri Puanı: {son_puan}", size=16, color=TEXT_COLOR_HEADING),
                ft.Text(f"Kaydedilen Yeni YZ Zorluğu: {oyun_durumu_hex['zorluk_seviyesi']}", color=ft.colors.GREEN_700, weight=ft.FontWeight.BOLD, size=18),
            ]
        return ft.Column(
            [
                ft.Text("Oyun Sona Erdi!", size=28, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_DARK),
                ft.Text(f"Kazanan: {kazanan_adi}", size=22, weight=ft.FontWeight.BOLD, color=(PLAYER_1_COLOR_HEX if oyun_durumu_hex.get("kazanan") == 1 else (PLAYER_2_COLOR_HEX if oyun_durumu_hex.get("kazanan") == 2 else TEXT_COLOR_DARK))),
                ft.Divider(height=10, color=ft.colors.TRANSPARENT),
            ] + egitim_sonuclari_text + [
                ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                ft.ElevatedButton("Ana Menüye Dön", on_click=yeniden_baslat_hex_handler,icon=ft.icons.HOME,bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, height=50, width=250, style=STADIUM_BUTTON_STYLE)
            ],
            alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12, tight=True
        )

    def cok_oyunculu_sec_hex_handler(e):
        oyun_durumu_hex["oyuncu_adi"] = oyuncu_adi_girdi_hex.current.value.strip() or "Oyuncu"
        oyun_durumu_hex["cok_oyunculu"] = True; oyun_durumu_hex["_cok_oyunculu_menu_aktif"] = True
        arayuz_guncelle_hex()

    def sunucu_olustur_secim_hex(e):
        oyun_durumu_hex["sunucu_mu"] = True; oyun_durumu_hex["_sunucu_kurulum_aktif"] = True; oyun_durumu_hex["_cok_oyunculu_menu_aktif"] = False
        threading.Thread(target=sunucu_olustur_fonksiyonu_hex, daemon=True).start()
        arayuz_guncelle_hex()

    def sunucuya_baglan_secim_hex(e):
        oyun_durumu_hex["sunucu_mu"] = False; oyun_durumu_hex["_istemci_baglanma_aktif"] = True; oyun_durumu_hex["_cok_oyunculu_menu_aktif"] = False
        arayuz_guncelle_hex()

    def sunucuya_baglan_asıl_hex(e):
        sunucu_adresi_str = sunucu_adresi_girdi_hex.current.value.strip()
        if not sunucu_adresi_str or ":" not in sunucu_adresi_str:
            oyun_durumu_hex["_temp_feedback"] = "Geçerli adres girin (IP:Port)!"; arayuz_guncelle_hex(); return
        try:
            adres, port_str = sunucu_adresi_str.split(":"); port = int(port_str)
            oyun_durumu_hex["_temp_feedback"] = "Sunucuya bağlanılıyor..."; arayuz_guncelle_hex()
            threading.Thread(target=sunucuya_baglan_fonksiyonu_hex, args=(adres, port), daemon=True).start()
        except Exception as ex:
            oyun_durumu_hex["_temp_feedback"] = f"Adres/Port hatası: {ex}"; arayuz_guncelle_hex()

    def oyun_baslat_cok_oyunculu_hex(e):
        if len(oyun_durumu_hex.get("oyuncular_hex", [])) < 2: return
        oyun_durumu_hex["baslangic_oyuncusu"] = random.choice([1, 2])
        if random.choice([True, False]):
            oyun_durumu_hex["p1_hedef_kenarlar_str"], oyun_durumu_hex["p2_hedef_kenarlar_str"] = "Üst-Alt", "Sol-Sağ"
        else:
            oyun_durumu_hex["p1_hedef_kenarlar_str"], oyun_durumu_hex["p2_hedef_kenarlar_str"] = "Sol-Sağ", "Üst-Alt"
        oyun_durumu_hex["oyuncular_hex"][0].update({"id": 1, "renk_str": "Mavi"})
        oyun_durumu_hex["oyuncular_hex"][1].update({"id": 2, "renk_str": "Kırmızı"})
        ayarlar = {k: oyun_durumu_hex[k] for k in ["baslangic_oyuncusu", "p1_hedef_kenarlar_str", "p2_hedef_kenarlar_str", "oyuncular_hex"]}
        mesaj = {"tip": "baslat_hex", "tahta": [[0]*HEX_BOARD_SIZE for _ in range(HEX_BOARD_SIZE)], "ayarlar": ayarlar}
        try:
            oyun_durumu_hex["oyuncular_hex"][1]["soket"].send((json.dumps(mesaj) + "\n").encode())
            tahta_baslat_hex(cok_oyunculu_baslangic=True, gelen_ayarlar=ayarlar)
        except Exception as ex:
            print(f"Hex başlatma mesajı gönderme hatası: {ex}"); oyunu_bitir_hex_network_sorunu(1)

    def hamleyi_gonder_hex(row, col, oyuncu_no_hamle):
        if not oyun_durumu_hex.get("cok_oyunculu"): return
        mesaj = {"tip": "hamle_hex", "row": row, "col": col, "oyuncu_no": oyuncu_no_hamle}
        soket = None
        if oyun_durumu_hex["sunucu_mu"]:
            if len(oyun_durumu_hex["oyuncular_hex"]) > 1: soket = oyun_durumu_hex["oyuncular_hex"][1].get("soket")
        else: soket = oyun_durumu_hex.get("istemci_soketi")
        if soket:
            try: soket.send((json.dumps(mesaj) + "\n").encode())
            except Exception as ex: print(f"Hex hamle gönderme hatası: {ex}"); oyunu_bitir_hex_network_sorunu(3 - oyuncu_no_hamle)

    def sunucu_olustur_fonksiyonu_hex():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        oyun_durumu_hex["sunucu_soketi_referansi"] = server_socket
        server_socket.settimeout(1.0)
        try:
            server_socket.bind(("0.0.0.0", SUNUCU_PORTU_HEX)); server_socket.listen(1)
            oyun_durumu_hex["oyuncular_hex"] = [{"ad": oyun_durumu_hex["oyuncu_adi"]}]
            try: hostname = socket.gethostbyname(socket.gethostname())
            except: hostname = "127.0.0.1"
            oyun_durumu_hex.update({ "_server_address_info": f"Adres: {hostname}:{SUNUCU_PORTU_HEX}", "_connected_players_info": f"Bağlı: {oyun_durumu_hex['oyuncu_adi']}", "_start_game_button_disabled": True })
            if hasattr(sayfa, 'controls'): arayuz_guncelle_hex()

            while oyun_durumu_hex.get("sunucu_mu") and not oyun_durumu_hex.get("oyun_basladi"):
                if len(oyun_durumu_hex["oyuncular_hex"]) >= 2: time.sleep(0.1); continue
                try:
                    readable, _, _ = select.select([server_socket], [], [], 0.5)
                    if not readable or not oyun_durumu_hex.get("sunucu_mu"): continue
                    client_socket, _ = server_socket.accept()
                    data = client_socket.recv(1024).decode()
                    msg = json.loads(data.strip().split('\n')[0])
                    if msg.get("tip") == "baglan_hex" and len(oyun_durumu_hex["oyuncular_hex"]) < 2:
                        oyun_durumu_hex["oyuncular_hex"].append({"ad": msg["ad"], "soket": client_socket})
                        oyun_durumu_hex.update({ "_connected_players_info": f"Bağlı: {', '.join(p['ad'] for p in oyun_durumu_hex['oyuncular_hex'])}", "_start_game_button_disabled": False })
                        client_socket.send((json.dumps({"tip": "baglandi_hex", "mesaj": "Sunucuya bağlandınız.", "oyuncu_no": 2}) + "\n").encode())
                        if hasattr(sayfa, 'controls'): arayuz_guncelle_hex()
                    else: client_socket.close()
                except socket.timeout: continue
                except Exception as e: print(f"Hex sunucu kabul hatası: {e}"); break
            
            client_soket = oyun_durumu_hex.get("oyuncular_hex", [{},{}])[1].get("soket")
            while oyun_durumu_hex.get("sunucu_mu") and oyun_durumu_hex.get("oyun_basladi") and not oyun_durumu_hex.get("oyun_bitti") and client_soket:
                try:
                    readable, _, _ = select.select([client_soket], [], [], 0.2)
                    if not readable or not oyun_durumu_hex.get("sunucu_mu"): continue
                    data = client_soket.recv(1024).decode()
                    if not data: oyunu_bitir_hex_network_sorunu(1); break
                    msg = json.loads(data.strip().split('\n')[0])
                    if msg["tip"] == "hamle_hex" and oyun_durumu_hex["mevcut_oyuncu"] == msg["oyuncu_no"] == 2:
                        bitti = hamle_yap_ve_kontrol_et_hex(msg["row"], msg["col"], 2)
                        if not bitti: hamle_sonrasi_islemler_hex(2, msg["row"], msg["col"])
                    elif msg["tip"] == "oyundan_cik_hex": oyunu_bitir_hex_network_sorunu(1); break
                except (socket.timeout, json.JSONDecodeError): continue
                except (ConnectionResetError, BrokenPipeError): oyunu_bitir_hex_network_sorunu(1); break
                except Exception as e: print(f"Hex S dinleme hatası: {e}"); break
        except Exception as e: print(f"Hex sunucu ana hata: {e}")
        finally:
            if server_socket: server_socket.close()
            oyun_durumu_hex["sunucu_soketi_referansi"] = None
            if oyun_durumu_hex.get("sunucu_mu") and not oyun_durumu_hex.get("oyun_bitti") and not oyun_durumu_hex.get("oyun_basladi"):
                oyun_durumu_hex["_sunucu_kurulum_aktif"] = False; oyun_durumu_hex["sunucu_mu"] = None
                if hasattr(sayfa, 'controls'): arayuz_guncelle_hex()

    def sunucuya_baglan_fonksiyonu_hex(adres, port):
        client_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); client_s.settimeout(5.0)
        try:
            client_s.connect((adres, port)); oyun_durumu_hex["istemci_soketi"] = client_s
            client_s.send((json.dumps({"tip": "baglan_hex", "ad": oyun_durumu_hex["oyuncu_adi"]}) + "\n").encode())
            data = client_s.recv(1024).decode()
            msg = json.loads(data.strip().split('\n')[0])
            if msg["tip"] == "baglandi_hex":
                oyun_durumu_hex["mevcut_oyuncu_id_yerel"] = msg.get("oyuncu_no", 2)
                oyun_durumu_hex["_temp_feedback"] = msg.get("mesaj", "Bağlandı, oyun bekleniyor...")
                if hasattr(sayfa, 'controls'): arayuz_guncelle_hex()
                threading.Thread(target=istemci_dinle_fonksiyonu_hex, daemon=True).start()
            else:
                oyun_durumu_hex["_temp_feedback"] = msg.get("mesaj", "Bağlanılamadı.")
                client_s.close(); oyun_durumu_hex["istemci_soketi"] = None; arayuz_guncelle_hex()
        except Exception as e:
            oyun_durumu_hex["_temp_feedback"] = f"Bağlantı hatası: {e}"
            if oyun_durumu_hex["istemci_soketi"]: client_s.close(); oyun_durumu_hex["istemci_soketi"] = None
            if hasattr(sayfa, 'controls'): arayuz_guncelle_hex()

    def istemci_dinle_fonksiyonu_hex():
        soket = oyun_durumu_hex.get("istemci_soketi"); buffer = ""
        if not soket: return
        try:
            while soket and not oyun_durumu_hex.get("oyun_bitti"):
                readable, _, _ = select.select([soket], [], [], 0.2)
                if not readable or not oyun_durumu_hex.get("istemci_soketi"): continue
                data = soket.recv(2048).decode()
                if not data:
                    if not oyun_durumu_hex["oyun_bitti"]: oyunu_bitir_hex_network_sorunu(1)
                    break
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if not line: continue
                    msg = json.loads(line)
                    if msg["tip"] == "baslat_hex":
                        tahta_baslat_hex(cok_oyunculu_baslangic=True, gelen_tahta=msg.get("tahta"), gelen_ayarlar=msg.get("ayarlar"))
                    elif msg["tip"] == "hamle_hex" and oyun_durumu_hex["mevcut_oyuncu"] == msg["oyuncu_no"] == 1:
                        bitti = hamle_yap_ve_kontrol_et_hex(msg["row"], msg["col"], 1)
                        if not bitti: hamle_sonrasi_islemler_hex(1, msg["row"], msg["col"])
                    elif msg["tip"] == "oyun_bitti_hex":
                        oyun_durumu_hex.update({ "kazanan": msg.get("kazanan_no"), "kazanan_adi_str": msg.get("kazanan_ad", ""), "kazanan_yol": [tuple(y) for y in msg.get("kazanan_yol", [])], "tahta": msg.get("tahta"), "oyun_bitti": True, "oyun_basladi": False })
                        if hasattr(sayfa, 'controls'): arayuz_guncelle_hex(); break
                    elif msg["tip"] == "hata_hex":
                        oyun_durumu_hex["_temp_feedback"] = f"Sunucu hatası: {msg.get('mesaj')}"; arayuz_guncelle_hex()
        except (ConnectionAbortedError, ConnectionResetError):
            if not oyun_durumu_hex["oyun_bitti"]: oyunu_bitir_hex_network_sorunu(1)
        except Exception as e: print(f"Hex C dinleme hatası: {e}")
        finally:
            if oyun_durumu_hex.get("istemci_soketi"): oyun_durumu_hex["istemci_soketi"].close(); oyun_durumu_hex["istemci_soketi"] = None
            if not oyun_durumu_hex.get("oyun_bitti") and not oyun_durumu_hex.get("sunucu_mu"):
                oyun_durumu_hex["_istemci_baglanma_aktif"] = False; oyun_durumu_hex["cok_oyunculu"] = False; arayuz_guncelle_hex()

    def oyunu_bitir_hex_network_sorunu(kazanan_no):
        if oyun_durumu_hex["oyun_bitti"]: return
        oyun_durumu_hex.update({ "oyun_bitti": True, "oyun_basladi": False, "sira_mesaji": "Rakip bağlantısı koptu! Oyun bitti.", "kazanan": kazanan_no })
        oyuncular = oyun_durumu_hex.get("oyuncular_hex", [{},{}])
        kazanan_ad_listesi = [oyuncular[0].get("ad", "Oyuncu 1"), oyuncular[1].get("ad", "Oyuncu 2")]
        oyun_durumu_hex["kazanan_adi_str"] = kazanan_ad_listesi[kazanan_no - 1] if 0 < kazanan_no <= 2 else "Bağlantı Hatası"
        if hasattr(sayfa, 'controls'): arayuz_guncelle_hex()
        if oyun_durumu_hex.get("cok_oyunculu") and oyun_durumu_hex.get("sunucu_mu"):
            mesaj = {"tip": "oyun_bitti_hex", "kazanan_no": kazanan_no, "kazanan_ad": oyun_durumu_hex["kazanan_adi_str"], "network_sorunu": True}
            soket = oyun_durumu_hex.get("oyuncular_hex", [{},{}])[1].get("soket")
            if soket:
                try: soket.send((json.dumps(mesaj) + "\n").encode())
                except: pass

    # --- Hex Arayüz Kurulumu ---
    oyuncu_adi_girdi_hex.current = ft.TextField(label="Oyuncu Adınız", width=300, border_radius=8, text_align=ft.TextAlign.CENTER, value=oyun_durumu_hex["oyuncu_adi"])
    mevcut_zorluk_goster_hex.current = ft.Text(f"Mevcut YZ Zorluğu: {oyun_durumu_hex['zorluk_seviyesi']}", italic=True, color=ft.colors.BLACK54, text_align=ft.TextAlign.CENTER)
    mod_secim_konteyneri_hex.current = ft.Container(
        content=ft.Column([
            ft.Text("Hex Oyunu", size=40, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_HEADING),
            ft.Text("Stratejini Konuştur!", size=16, color=ft.colors.BLUE_GREY_700, italic=True, text_align=ft.TextAlign.CENTER),
            mevcut_zorluk_goster_hex.current, ft.Divider(height=15, color=ft.colors.TRANSPARENT),
            oyuncu_adi_girdi_hex.current,
            ft.ElevatedButton("Tek Oyunculu Başlat", on_click=lambda e: tek_oyunculu_sec_hex_handler(e, False),icon=ft.icons.PLAY_CIRCLE_OUTLINE, bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, height=50, width=300, style=STADIUM_BUTTON_STYLE),
            ft.ElevatedButton("Eğitim Modu (YZ Ayarı)", on_click=lambda e: tek_oyunculu_sec_hex_handler(e, True), icon=ft.icons.MODEL_TRAINING_ROUNDED, bgcolor=BUTTON_TERTIARY_COLOR, color=BUTTON_TEXT_COLOR, height=50, width=300, style=STADIUM_BUTTON_STYLE),
            ft.ElevatedButton("Çok Oyunculu", on_click=cok_oyunculu_sec_hex_handler, icon=ft.icons.PEOPLE_ALT_OUTLINED, bgcolor=BUTTON_SECONDARY_COLOR, color=BUTTON_TEXT_COLOR, height=50, width=300, style=STADIUM_BUTTON_STYLE),
            ft.ElevatedButton("Tüm Oyunlar Menüsü", on_click=go_to_master_menu_func, icon=ft.icons.MENU, bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, height=50, width=300, style=STADIUM_BUTTON_STYLE),
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
        padding=30, alignment=ft.alignment.center
    )
    cok_oyunculu_secim_konteyneri_hex.current = ft.Container(
        content=ft.Column([
            ft.Text("Çok Oyunculu Mod", size=28, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_HEADING),
            ft.ElevatedButton("Sunucu Oluştur", icon=ft.icons.ADD_TO_QUEUE_ROUNDED, on_click=sunucu_olustur_secim_hex, bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, width=280, height=50, style=STADIUM_BUTTON_STYLE),
            ft.ElevatedButton("Sunucuya Bağlan", icon=ft.icons.LINK_ROUNDED, on_click=sunucuya_baglan_secim_hex, bgcolor=BUTTON_SECONDARY_COLOR, color=BUTTON_TEXT_COLOR, width=280, height=50, style=STADIUM_BUTTON_STYLE),
            ft.ElevatedButton("Geri", icon=ft.icons.ARROW_BACK_IOS_NEW_ROUNDED, on_click=yeniden_baslat_hex_handler, width=280, height=50, bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, style=STADIUM_BUTTON_STYLE),
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=18),
        padding=30, visible=False, alignment=ft.alignment.center
    )
    try: hostname = socket.gethostbyname(socket.gethostname())
    except: hostname = "127.0.0.1"
    sunucu_adresi_girdi_hex.current = ft.TextField(label="Sunucu Adresi (IP:Port)", width=280, value=f"{hostname}:{SUNUCU_PORTU_HEX}", text_align=ft.TextAlign.CENTER)
    sunucu_adresi_goster_hex.current = ft.Text("...", selectable=True, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD)
    baglanan_oyuncular_goster_hex.current = ft.Text("Oyuncular bekleniyor...", text_align=ft.TextAlign.CENTER)
    oyun_baslat_cok_oyunculu_buton_hex.current = ft.ElevatedButton("Oyunu Başlat", on_click=oyun_baslat_cok_oyunculu_hex, disabled=True, bgcolor=BUTTON_SECONDARY_COLOR, color=BUTTON_TEXT_COLOR, width=220, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.PLAY_ARROW)
    sunucu_olustur_konteyneri_hex.current = ft.Container(
        content=ft.Column([
            ft.Text("Sunucu Kurulumu", size=26, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_HEADING),
            sunucu_adresi_goster_hex.current, ft.ProgressRing(),
            baglanan_oyuncular_goster_hex.current, oyun_baslat_cok_oyunculu_buton_hex.current,
            ft.ElevatedButton("İptal Et", icon=ft.icons.CANCEL_OUTLINED, on_click=yeniden_baslat_hex_handler, width=220, height=50, bgcolor=BUTTON_DANGER_COLOR, color=BUTTON_TEXT_COLOR, style=STADIUM_BUTTON_STYLE)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=18),
        padding=30, visible=False, alignment=ft.alignment.center
    )
    sunucu_baglan_konteyneri_hex.current = ft.Container(
        content=ft.Column([
            ft.Text("Sunucuya Bağlan", size=26, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_HEADING),
            sunucu_adresi_girdi_hex.current,
            ft.ElevatedButton("Bağlan", icon=ft.icons.LOGIN_ROUNDED, on_click=sunucuya_baglan_asıl_hex, bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, width=220, height=50, style=STADIUM_BUTTON_STYLE),
            ft.ElevatedButton("Geri", icon=ft.icons.ARROW_BACK_IOS_NEW_ROUNDED, on_click=yeniden_baslat_hex_handler, width=220, height=50, bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, style=STADIUM_BUTTON_STYLE)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=18),
        padding=30, visible=False, alignment=ft.alignment.center
    )
    tahta_canvas_ref.current = ft.canvas.Canvas(shapes=[], width=int(canvas_width), height=int(canvas_height))
    tahta_gesture_detector_ref.current = ft.GestureDetector(content=tahta_canvas_ref.current, on_tap_down=on_canvas_tap_hex, on_hover=on_canvas_hover_hex)
    tahta_dis_konteyner_ref.current = ft.Container(content=tahta_gesture_detector_ref.current, alignment=ft.alignment.center, padding=10, border_radius=10, visible=False)
    
    oyun_bilgisi_goster_hex.current = ft.Text("", size=14, text_align=ft.TextAlign.CENTER, color=TEXT_COLOR_DARK, visible=False)
    geri_bildirim_goster_hex.current = ft.Text("Hex Oyununa Hoş Geldiniz!", size=18, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=TEXT_COLOR_DARK)
    oyun_geri_cik_buton_hex.current = ft.ElevatedButton("Ana Menü", on_click=yeniden_baslat_hex_handler, icon=ft.icons.HOME_FILLED, bgcolor=BUTTON_DANGER_COLOR, color=BUTTON_TEXT_COLOR, height=45, visible=False, style=STADIUM_BUTTON_STYLE)
    bitis_ekrani_konteyneri_hex.current = ft.Container(content=ft.Text(""), padding=30, width=550, alignment=ft.alignment.center, visible=False)

    sayfa.add(
        ft.Column(
            [
                mod_secim_konteyneri_hex.current,
                cok_oyunculu_secim_konteyneri_hex.current,
                sunucu_olustur_konteyneri_hex.current,
                sunucu_baglan_konteyneri_hex.current,
                oyun_bilgisi_goster_hex.current,
                tahta_dis_konteyner_ref.current,
                geri_bildirim_goster_hex.current,
                oyun_geri_cik_buton_hex.current,
                bitis_ekrani_konteyneri_hex.current,
            ],
            alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10, expand=True, scroll=ft.ScrollMode.ADAPTIVE
        )
    )
    arayuz_guncelle_hex()

    # Hex oyununa ilk girişte ana menüyü göster
    yeniden_baslat_hex_handler(None)
    
# ===================================================================================
# =============================== HEX OYUN KODU BİTİŞ =================================
# ===================================================================================



# ===================================================================================
# =========================== MEMORY (Hafıza) OYUN KODU BAŞLANGIÇ ==========================
# ===================================================================================

# --- Memory Oyun Sabitleri ---
BASLANGIC_SEVIYESI_MEMORY = 1
MIN_SAYI_UZUNLUGU_MEMORY = 3
MAKS_SAYI_UZUNLUGU_MEMORY = 7
TEMEL_SURE_MEMORY = 3.0  # Başlangıç süresi (saniye)
MIN_SURE_MEMORY = 1.0    # Minimum süre
MAKS_SURE_MEMORY = 5.0   # Maksimum süre
SURE_AZALTMA_MEMORY = 0.2  # Doğru cevapta süre azalması
SURE_ARTIRMA_MEMORY = 0.3  # Yanlış cevapta süre artışı
OYUN_SURESI_MEMORY = 180  # 3 dakika (saniye)
SEVIYE_BASAMAK_ARTIS_MEMORY = 3  # Her 3 seviyede basamak artar
SUNUCU_PORT_MEMORY = 12347

# --- Memory Oyun Durumu ---
oyun_durumu_memory = {
    "seviye": BASLANGIC_SEVIYESI_MEMORY,
    "hatirlanacak_sayilar": [],
    "oyuncu_girdisi": "",
    "sayilar_gosteriliyor": False,
    "oyun_basladi": False,
    "oyun_bitti": False,
    "skor": 0,
    "mevcut_sure": TEMEL_SURE_MEMORY,
    "toplam_dogru": 0,
    "toplam_deneme": 0,
    "kalan_sure": OYUN_SURESI_MEMORY,
    "oyuncu_adi": "",
    "cok_oyunculu": False,
    "sunucu_mu": False,
    "istemci_socket": None,
    "oyuncular": [],
    "skorlar": []
}

# --- Memory Ana Fonksiyonu ---
def main_memory(sayfa: ft.Page, go_to_master_menu_func):
    sayfa.title = "Sayısal Hafıza Oyunu"
    sayfa.vertical_alignment = ft.MainAxisAlignment.CENTER
    sayfa.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    sayfa.theme_mode = ft.ThemeMode.LIGHT
    sayfa.window_width = 800
    sayfa.window_height = 600
    # sayfa.window_center() # Ana merkezleme master_main'de yapılıyor.
    sayfa.bgcolor = PAGE_BG_COLOR

    # --- Flet Kontrolleri (Memory) ---
    mod_secim_container_memory = ft.Ref[ft.Container]()
    cok_oyunculu_secim_container_memory = ft.Ref[ft.Container]()
    sunucu_baslat_container_memory = ft.Ref[ft.Container]()
    sunucu_baglan_container_memory = ft.Ref[ft.Container]()
    oyuncu_adi_girdi_memory = ft.Ref[ft.TextField]()
    sunucu_adresi_girdi_memory = ft.Ref[ft.TextField]()
    sunucu_adresi_goster_memory = ft.Ref[ft.Text]()
    baglanan_oyuncular_memory = ft.Ref[ft.Text]()
    oyun_baslat_buton_memory = ft.Ref[ft.ElevatedButton]()
    sayi_gosterge_ref_memory = ft.Ref[ft.Text]()
    giris_alani_ref_memory = ft.Ref[ft.TextField]()
    geri_bildirim_ref_memory = ft.Ref[ft.Text]()
    baslat_butonu_ref_memory = ft.Ref[ft.ElevatedButton]()
    gonder_butonu_ref_memory = ft.Ref[ft.ElevatedButton]()
    seviye_gosterge_ref_memory = ft.Ref[ft.Text]()
    skor_gosterge_ref_memory = ft.Ref[ft.Text]()
    yeniden_baslat_butonu_ref_memory = ft.Ref[ft.ElevatedButton]()
    istatistik_gosterge_ref_memory = ft.Ref[ft.Text]()
    zamanlayici_gosterge_ref_memory = ft.Ref[ft.Text]()
    skor_tablosu_container_memory = ft.Ref[ft.Container]()
    oyun_ekrani_container_memory = ft.Ref[ft.Column]()

    def arayuz_guncelle_memory(tam_guncelleme=False):
        if tam_guncelleme:
            # Sadece görünürlükleri ayarla, içerikleri değil
            is_main_menu = mod_secim_container_memory.current.visible
            is_multi_choice = cok_oyunculu_secim_container_memory.current.visible
            is_host_screen = sunucu_baslat_container_memory.current.visible
            is_client_screen = sunucu_baglan_container_memory.current.visible
            is_game_screen = oyun_ekrani_container_memory.current.visible
            
            if not any([is_main_menu, is_multi_choice, is_host_screen, is_client_screen, is_game_screen]):
                 mod_secim_container_memory.current.visible = True

        # Oyun ekranı görünürse içerikleri güncelle
        if oyun_ekrani_container_memory.current.visible:
            sayi_gosterge_ref_memory.current.value = "".join(map(str, oyun_durumu_memory["hatirlanacak_sayilar"])) if oyun_durumu_memory["sayilar_gosteriliyor"] else ""
            giris_alani_ref_memory.current.disabled = not oyun_durumu_memory["oyun_basladi"] or oyun_durumu_memory["sayilar_gosteriliyor"] or oyun_durumu_memory["oyun_bitti"]
            gonder_butonu_ref_memory.current.disabled = giris_alani_ref_memory.current.disabled or not oyun_durumu_memory["oyuncu_girdisi"].strip()
            seviye_gosterge_ref_memory.current.value = f"Seviye: {oyun_durumu_memory['seviye']}"
            skor_gosterge_ref_memory.current.value = f"Skor: {oyun_durumu_memory['skor']}"
            dogruluk = (oyun_durumu_memory["toplam_dogru"] / oyun_durumu_memory["toplam_deneme"] * 100) if oyun_durumu_memory["toplam_deneme"] > 0 else 0
            istatistik_gosterge_ref_memory.current.value = f"Doğru: {oyun_durumu_memory['toplam_dogru']} / {oyun_durumu_memory['toplam_deneme']} ({dogruluk:.1f}%)"
            zamanlayici_gosterge_ref_memory.current.value = f"Kalan Süre: {int(oyun_durumu_memory['kalan_sure'] // 60)}:{int(oyun_durumu_memory['kalan_sure'] % 60):02d}"
            
            if oyun_durumu_memory["oyun_bitti"]:
                 geri_bildirim_ref_memory.current.value = "Oyun Bitti!"
                 if oyun_durumu_memory["cok_oyunculu"]:
                    skor_tablosu_container_memory.current.visible = True
                    skor_tablosu_container_memory.current.content = ft.Column([
                        ft.Text("Final Skorları", weight=ft.FontWeight.BOLD),
                        ft.Text("\n".join([f"{oyuncu['ad']}: {oyuncu['skor']} puan" for oyuncu in sorted(oyun_durumu_memory.get("skorlar", []), key=lambda x: x['skor'], reverse=True)]),
                                  size=16, text_align=ft.TextAlign.CENTER)
                    ])
            elif not oyun_durumu_memory["oyun_basladi"]:
                 geri_bildirim_ref_memory.current.value = f"Hoş geldin, {oyun_durumu_memory['oyuncu_adi']}! Başlamak için butona bas."
            else:
                 geri_bildirim_ref_memory.current.value = "Sayıları hatırla ve gir!"
                 skor_tablosu_container_memory.current.visible = False

            baslat_butonu_ref_memory.current.visible = not oyun_durumu_memory["oyun_basladi"] and not oyun_durumu_memory["oyun_bitti"]
            yeniden_baslat_butonu_ref_memory.current.visible = oyun_durumu_memory["oyun_bitti"]
        
        sayfa.update()

    def show_view_memory(view_name):
        views = {
            "main_menu": mod_secim_container_memory,
            "multi_choice": cok_oyunculu_secim_container_memory,
            "host": sunucu_baslat_container_memory,
            "client": sunucu_baglan_container_memory,
            "game": oyun_ekrani_container_memory
        }
        for name, container_ref in views.items():
            if container_ref.current:
                container_ref.current.visible = (name == view_name)
        arayuz_guncelle_memory(tam_guncelleme=True)

    def sayilar_uret_memory(uzunluk):
        return [random.randint(0, 9) for _ in range(uzunluk)]

    def tur_baslat_memory():
        if oyun_durumu_memory["oyun_bitti"]: return
        basamak = min(MIN_SAYI_UZUNLUGU_MEMORY + (oyun_durumu_memory["seviye"] - 1) // SEVIYE_BASAMAK_ARTIS_MEMORY, MAKS_SAYI_UZUNLUGU_MEMORY)
        oyun_durumu_memory["hatirlanacak_sayilar"] = sayilar_uret_memory(basamak)
        oyun_durumu_memory["oyuncu_girdisi"] = ""
        oyun_durumu_memory["sayilar_gosteriliyor"] = True
        giris_alani_ref_memory.current.value = ""
        arayuz_guncelle_memory()
        threading.Timer(oyun_durumu_memory["mevcut_sure"], sayilari_gizle_memory).start()

    def sayilari_gizle_memory():
        oyun_durumu_memory["sayilar_gosteriliyor"] = False
        arayuz_guncelle_memory()

    def zamanlayici_baslat_memory():
        baslangic_zamani = time.time()
        while oyun_durumu_memory["kalan_sure"] > 0 and oyun_durumu_memory["oyun_basladi"] and not oyun_durumu_memory["oyun_bitti"]:
            gecen_sure = time.time() - baslangic_zamani
            oyun_durumu_memory["kalan_sure"] = max(OYUN_SURESI_MEMORY - gecen_sure, 0)
            if zamanlayici_gosterge_ref_memory.current:
                 zamanlayici_gosterge_ref_memory.current.value = f"Kalan Süre: {int(oyun_durumu_memory['kalan_sure'] // 60)}:{int(oyun_durumu_memory['kalan_sure'] % 60):02d}"
                 sayfa.update()
            time.sleep(0.1)
        
        if oyun_durumu_memory["kalan_sure"] <= 0 and not oyun_durumu_memory["oyun_bitti"]:
            oyun_durumu_memory["oyun_bitti"] = True
            oyun_durumu_memory["sayilar_gosteriliyor"] = False
            if oyun_durumu_memory["cok_oyunculu"]:
                if oyun_durumu_memory["sunucu_mu"]:
                    # Sunucu kendi skorunu ve bağlı istemcilerin skorlarını bekler
                    oyun_durumu_memory["skorlar"] = [{"ad": p["ad"], "skor": p.get("skor", 0)} for p in oyun_durumu_memory["oyuncular"]]
                    # Kendi skorunu güncelle
                    for p in oyun_durumu_memory["skorlar"]:
                        if not oyun_durumu_memory["oyuncular"][oyun_durumu_memory["skorlar"].index(p)].get("socket"):
                            p["skor"] = oyun_durumu_memory["skor"]
                    
                    # Tüm skorları herkese gönder
                    for oyuncu in oyun_durumu_memory["oyuncular"]:
                        if oyuncu.get("socket"):
                            try:
                                oyuncu["socket"].send(json.dumps({"tip": "skorlar", "skorlar": oyun_durumu_memory["skorlar"]}).encode())
                            except:
                                pass
                else: # İstemci ise
                    try:
                        # Kendi skorunu sunucuya gönder
                        oyun_durumu_memory["istemci_socket"].send(json.dumps({
                            "tip": "skor", "ad": oyun_durumu_memory["oyuncu_adi"], "skor": oyun_durumu_memory["skor"]
                        }).encode())
                        # Sunucudan nihai skorları bekleme işlemi istemci_dinle içinde yapılır.
                    except:
                        pass
            arayuz_guncelle_memory()

    def zorluk_ayarla_memory(dogru_mu):
        if dogru_mu:
            oyun_durumu_memory["mevcut_sure"] = max(oyun_durumu_memory["mevcut_sure"] - SURE_AZALTMA_MEMORY, MIN_SURE_MEMORY)
        else:
            oyun_durumu_memory["mevcut_sure"] = min(oyun_durumu_memory["mevcut_sure"] + SURE_ARTIRMA_MEMORY, MAKS_SURE_MEMORY)

    def cevabi_kontrol_et_memory():
        oyuncu_girdisi = oyun_durumu_memory["oyuncu_girdisi"].replace(" ", "")
        try:
            oyuncu_sayilari = [int(c) for c in oyuncu_girdisi]
            dogru_mu = oyuncu_sayilari == oyun_durumu_memory["hatirlanacak_sayilar"]
        except (ValueError, IndexError):
            dogru_mu = False

        oyun_durumu_memory["toplam_deneme"] += 1
        if dogru_mu:
            oyun_durumu_memory["toplam_dogru"] += 1
            oyun_durumu_memory["skor"] += oyun_durumu_memory["seviye"] * 10
            oyun_durumu_memory["seviye"] += 1
            geri_bildirim_ref_memory.current.color = ft.colors.GREEN_700
            geri_bildirim_ref_memory.current.value = "Doğru!"
        else:
            geri_bildirim_ref_memory.current.color = ft.colors.RED_700
            geri_bildirim_ref_memory.current.value = f"Yanlış! Doğrusu: {''.join(map(str, oyun_durumu_memory['hatirlanacak_sayilar']))}"

        zorluk_ayarla_memory(dogru_mu)
        if not oyun_durumu_memory["oyun_bitti"]:
            # Cevap kontrol edildikten sonra kısa bir bekleme
            sayfa.update()
            time.sleep(1)
            tur_baslat_memory()
        else:
            arayuz_guncelle_memory()

    def giris_degisikligi_memory(e):
        oyun_durumu_memory["oyuncu_girdisi"] = e.control.value
        gonder_butonu_ref_memory.current.disabled = not oyun_durumu_memory["oyuncu_girdisi"].strip()
        sayfa.update()

    def sunucu_baslat_fonk_memory():
        sunucu = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sunucu.bind(("0.0.0.0", SUNUCU_PORT_MEMORY))
        except OSError:
            # Port meşgulse farklı bir port dene
            new_port = SUNUCU_PORT_MEMORY + random.randint(1, 100)
            sunucu.bind(("0.0.0.0", new_port))
            oyun_durumu_memory["_port"] = new_port
        else:
            oyun_durumu_memory["_port"] = SUNUCU_PORT_MEMORY
            
        sunucu.listen(5)
        sunucu_adresi_goster_memory.current.value = f"Sunucu Adresi: {socket.gethostbyname(socket.gethostname())}:{oyun_durumu_memory['_port']}"
        baglanan_oyuncular_memory.current.value = f"Bağlanan Oyuncular: {oyun_durumu_memory['oyuncu_adi']}"
        oyun_durumu_memory["oyuncular"].append({"ad": oyun_durumu_memory["oyuncu_adi"], "socket": None, "skor": 0})
        oyun_baslat_buton_memory.current.disabled = False
        sayfa.update()

        def istemci_yonet_memory(istemci_socket, addr):
            try:
                veri = istemci_socket.recv(1024).decode()
                mesaj = json.loads(veri)
                if mesaj["tip"] == "baglan":
                    oyuncu_adi = mesaj["ad"]
                    oyun_durumu_memory["oyuncular"].append({"ad": oyuncu_adi, "socket": istemci_socket, "skor": 0})
                    baglanan_oyuncular_memory.current.value = f"Bağlanan Oyuncular: {', '.join([o['ad'] for o in oyun_durumu_memory['oyuncular']])}"
                    sayfa.update()
                    # Oyun bitene kadar istemciden skorları dinle
                    while oyun_durumu_memory["oyun_basladi"] and not oyun_durumu_memory["oyun_bitti"]:
                        try:
                            veri = istemci_socket.recv(1024).decode()
                            if not veri: break
                            mesaj = json.loads(veri)
                            if mesaj["tip"] == "skor":
                                for oyuncu in oyun_durumu_memory["oyuncular"]:
                                    if oyuncu["ad"] == mesaj["ad"]:
                                        oyuncu["skor"] = mesaj["skor"]
                                        break
                        except (ConnectionResetError, json.JSONDecodeError):
                            break # İstemci bağlantısı koptu veya bozuk veri
            except:
                pass # Genel hata
            finally:
                # Bağlantısı kopan oyuncuyu listeden çıkar
                oyun_durumu_memory["oyuncular"] = [p for p in oyun_durumu_memory["oyuncular"] if p.get("socket") != istemci_socket]
                baglanan_oyuncular_memory.current.value = f"Bağlanan Oyuncular: {', '.join([o['ad'] for o in oyun_durumu_memory['oyuncular']])}"
                try: istemci_socket.close()
                except: pass
                sayfa.update()


        while not oyun_durumu_memory["oyun_basladi"]:
            sunucu.settimeout(1.0)
            try:
                istemci_socket, addr = sunucu.accept()
                threading.Thread(target=istemci_yonet_memory, args=(istemci_socket, addr), daemon=True).start()
            except socket.timeout:
                continue

    def sunucuya_baglan_fonk_memory():
        try:
            istemci = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            adres, port = sunucu_adresi_girdi_memory.current.value.split(":")
            istemci.connect((adres, int(port)))
            oyun_durumu_memory["istemci_socket"] = istemci
            istemci.send(json.dumps({"tip": "baglan", "ad": oyun_durumu_memory["oyuncu_adi"]}).encode())
            
            geri_bildirim_ref_memory.current.value = "Sunucuya bağlanıldı, oyunun başlaması bekleniyor..."
            show_view_memory("game")
            baslat_butonu_ref_memory.current.visible = False # Oyunu sunucu başlatır
            yeniden_baslat_butonu_ref_memory.current.visible = False
            arayuz_guncelle_memory()
            
            threading.Thread(target=istemci_dinle_memory, daemon=True).start()
        except Exception as e:
            geri_bildirim_ref_memory.current.value = f"Bağlantı hatası: {e}"
            show_view_memory("client")
            arayuz_guncelle_memory()
    
    # Çok oyunculu istemci için sunucu mesajlarını dinle
    def istemci_dinle_memory():
        while oyun_durumu_memory.get("istemci_socket"):
            try:
                veri = oyun_durumu_memory["istemci_socket"].recv(1024).decode()
                if not veri: break
                mesaj = json.loads(veri)
                if mesaj["tip"] == "baslat":
                    oyun_durumu_memory["oyun_basladi"] = True
                    threading.Thread(target=zamanlayici_baslat_memory, daemon=True).start()
                    tur_baslat_memory()
                elif mesaj["tip"] == "skorlar":
                    oyun_durumu_memory["skorlar"] = mesaj["skorlar"]
                    arayuz_guncelle_memory() # Oyun bittiğinde skorları göster
                    break # Skorlar geldiyse dinlemeyi bitir
            except (ConnectionResetError, json.JSONDecodeError):
                break
            except Exception:
                time.sleep(0.1)
        # Bağlantı koptuysa
        if geri_bildirim_ref_memory.current and not oyun_durumu_memory["oyun_bitti"]:
            geri_bildirim_ref_memory.current.value = "Sunucu bağlantısı koptu!"
            oyun_durumu_memory["oyun_bitti"] = True
            arayuz_guncelle_memory()


    def tek_oyunculu_sec_memory():
        oyun_durumu_memory["cok_oyunculu"] = False
        oyun_durumu_memory["oyuncu_adi"] = "Oyuncu"
        show_view_memory("game")
        baslat_butonu_ref_memory.current.visible = True
        arayuz_guncelle_memory()

    def cok_oyunculu_sec_memory():
        show_view_memory("multi_choice")

    def sunucu_baslat_sec_memory():
        if not oyuncu_adi_girdi_memory.current.value.strip():
            # Geçici bir geri bildirim için ana ekrandakini kullanabiliriz
            if geri_bildirim_ref_memory.current:
                geri_bildirim_ref_memory.current.value = "Lütfen bir oyuncu adı girin!"
                sayfa.update()
                time.sleep(2)
                geri_bildirim_ref_memory.current.value = ""
                sayfa.update()
            return
        oyun_durumu_memory["oyuncu_adi"] = oyuncu_adi_girdi_memory.current.value.strip()
        oyun_durumu_memory["cok_oyunculu"] = True
        oyun_durumu_memory["sunucu_mu"] = True
        show_view_memory("host")
        threading.Thread(target=sunucu_baslat_fonk_memory, daemon=True).start()

    def sunucuya_baglan_sec_memory():
        if not oyuncu_adi_girdi_memory.current.value.strip():
            # Geçici geri bildirim
            return
        oyun_durumu_memory["oyuncu_adi"] = oyuncu_adi_girdi_memory.current.value.strip()
        oyun_durumu_memory["cok_oyunculu"] = True
        oyun_durumu_memory["sunucu_mu"] = False
        show_view_memory("client")

    def oyun_baslat_tiklama_memory(e):
        oyun_durumu_memory["oyun_basladi"] = True
        for oyuncu in oyun_durumu_memory["oyuncular"]:
            if oyuncu.get("socket"):
                try:
                    oyuncu["socket"].send(json.dumps({"tip": "baslat"}).encode())
                except:
                    pass # Bağlantı kopmuş olabilir
        show_view_memory("game")
        threading.Thread(target=zamanlayici_baslat_memory, daemon=True).start()
        tur_baslat_memory()

    def baslat_tiklama_memory(e):
        # Sadece tek oyunculu modda görünür
        oyun_durumu_memory.update({
            "seviye": BASLANGIC_SEVIYESI_MEMORY, "skor": 0, "oyun_basladi": True,
            "oyun_bitti": False, "mevcut_sure": TEMEL_SURE_MEMORY, "toplam_dogru": 0,
            "toplam_deneme": 0, "kalan_sure": OYUN_SURESI_MEMORY
        })
        threading.Thread(target=zamanlayici_baslat_memory, daemon=True).start()
        tur_baslat_memory()

    def gonder_tiklama_memory(e):
        if oyun_durumu_memory["oyun_basladi"] and not oyun_durumu_memory["sayilar_gosteriliyor"] and not oyun_durumu_memory["oyun_bitti"]:
            cevabi_kontrol_et_memory()

    def yeniden_baslat_tiklama_memory(e):
        # Bu fonksiyon, oyun bittiğinde ana memory menüsüne döner
        if oyun_durumu_memory.get("istemci_socket"):
            try: oyun_durumu_memory["istemci_socket"].close()
            except: pass
        
        # Reset game state
        oyun_durumu_memory.clear()
        oyun_durumu_memory.update({
            "seviye": BASLANGIC_SEVIYESI_MEMORY, "hatirlanacak_sayilar": [], "oyuncu_girdisi": "",
            "sayilar_gosteriliyor": False, "oyun_basladi": False, "oyun_bitti": False,
            "skor": 0, "mevcut_sure": TEMEL_SURE_MEMORY, "toplam_dogru": 0, "toplam_deneme": 0,
            "kalan_sure": OYUN_SURESI_MEMORY, "oyuncu_adi": "", "cok_oyunculu": False, "sunucu_mu": False,
            "istemci_socket": None, "oyuncular": [], "skorlar": []
        })
        geri_bildirim_ref_memory.current.color = TEXT_COLOR_DARK
        oyuncu_adi_girdi_memory.current.value = ""
        show_view_memory("main_menu")

    # --- Memory Arayüz Oluşturma ---
    oyuncu_adi_girdi_memory.current = ft.TextField(label="Oyuncu Adınız", width=300, text_align=ft.TextAlign.CENTER)

    mod_secim_container_memory.current = ft.Container(
        content=ft.Column(
            [
                ft.Text("Sayısal Hafıza Oyunu", size=36, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_HEADING),
                ft.ElevatedButton("Tek Oyunculu", on_click=lambda e: tek_oyunculu_sec_memory(), bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, width=300, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.PERSON),
                ft.ElevatedButton("Çok Oyunculu", on_click=lambda e: cok_oyunculu_sec_memory(), bgcolor=BUTTON_SECONDARY_COLOR, color=BUTTON_TEXT_COLOR, width=300, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.PEOPLE),
                ft.ElevatedButton("Tüm Oyunlar Menüsü", on_click=go_to_master_menu_func, bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, width=300, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.MENU),
            ],
            alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20
        ), visible=False
    )

    cok_oyunculu_secim_container_memory.current = ft.Container(
        content=ft.Column(
            [
                ft.Text("Çok Oyunculu Mod", size=32, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_HEADING),
                oyuncu_adi_girdi_memory.current,
                ft.ElevatedButton("Sunucu Başlat", on_click=lambda e: sunucu_baslat_sec_memory(), bgcolor=BUTTON_SECONDARY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.DNS),
                ft.ElevatedButton("Sunucuya Bağlan", on_click=lambda e: sunucuya_baglan_sec_memory(), bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.LINK),
                ft.ElevatedButton("Geri", on_click=lambda e: show_view_memory("main_menu"), bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.ARROW_BACK),
            ],
            alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20
        ), visible=False
    )
    
    sunucu_adresi_goster_memory.current = ft.Text("", size=16, selectable=True)
    baglanan_oyuncular_memory.current = ft.Text("", size=16)
    oyun_baslat_buton_memory.current = ft.ElevatedButton("Oyunu Başlat", on_click=oyun_baslat_tiklama_memory, bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.PLAY_ARROW, disabled=True)
    sunucu_baslat_container_memory.current = ft.Container(
        content=ft.Column(
            [
                ft.Text("Lobi", size=32, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_HEADING),
                sunucu_adresi_goster_memory.current,
                baglanan_oyuncular_memory.current,
                oyun_baslat_buton_memory.current,
                ft.ElevatedButton("Geri", on_click=lambda e: show_view_memory("multi_choice"), bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.ARROW_BACK),
            ],
            alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20
        ), visible=False
    )

    sunucu_adresi_girdi_memory.current = ft.TextField(label="Sunucu Adresi (IP:Port)", width=300, text_align=ft.TextAlign.CENTER, value=f"{socket.gethostbyname(socket.gethostname())}:{SUNUCU_PORT_MEMORY}")
    sunucu_baglan_container_memory.current = ft.Container(
        content=ft.Column(
            [
                ft.Text("Sunucuya Bağlan", size=32, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_HEADING),
                sunucu_adresi_girdi_memory.current,
                ft.ElevatedButton("Bağlan", on_click=lambda e: sunucuya_baglan_fonk_memory(), bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.LOGIN),
                ft.ElevatedButton("Geri", on_click=lambda e: show_view_memory("multi_choice"), bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.ARROW_BACK),
            ],
            alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20
        ), visible=False
    )
    
    sayi_gosterge_ref_memory.current = ft.Text("", size=48, weight=ft.FontWeight.BOLD, font_family="monospace")
    giris_alani_ref_memory.current = ft.TextField(label="Sayıları gir", on_change=giris_degisikligi_memory, width=300, text_align=ft.TextAlign.CENTER, disabled=True)
    geri_bildirim_ref_memory.current = ft.Text("Oyuna başla!", size=18)
    baslat_butonu_ref_memory.current = ft.ElevatedButton("Oyunu Başlat", on_click=baslat_tiklama_memory, bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.PLAY_ARROW)
    gonder_butonu_ref_memory.current = ft.ElevatedButton("Gönder", on_click=gonder_tiklama_memory, bgcolor=BUTTON_SECONDARY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.SEND, disabled=True)
    seviye_gosterge_ref_memory.current = ft.Text(f"Seviye: {oyun_durumu_memory['seviye']}", size=20)
    skor_gosterge_ref_memory.current = ft.Text(f"Skor: {oyun_durumu_memory['skor']}", size=20)
    istatistik_gosterge_ref_memory.current = ft.Text("Doğru: 0 / 0 (0%)", size=16)
    zamanlayici_gosterge_ref_memory.current = ft.Text(f"Kalan Süre: 3:00", size=20)
    yeniden_baslat_butonu_ref_memory.current = ft.ElevatedButton("Ana Menüye Dön", on_click=yeniden_baslat_tiklama_memory, bgcolor=BUTTON_TERTIARY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.HOME, visible=False)
    skor_tablosu_container_memory.current = ft.Container(padding=10, border_radius=8, bgcolor=ft.colors.BLUE_GREY_50, visible=False)

    oyun_ekrani_container_memory.current = ft.Column(
        [
            zamanlayici_gosterge_ref_memory.current,
            sayi_gosterge_ref_memory.current,
            giris_alani_ref_memory.current,
            gonder_butonu_ref_memory.current,
            geri_bildirim_ref_memory.current,
            istatistik_gosterge_ref_memory.current,
            ft.Row([seviye_gosterge_ref_memory.current, skor_gosterge_ref_memory.current], alignment=ft.MainAxisAlignment.SPACE_AROUND, width=600),
            skor_tablosu_container_memory.current,
            ft.Row([baslat_butonu_ref_memory.current, yeniden_baslat_butonu_ref_memory.current], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        ],
        alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, expand=True, visible=False
    )

    sayfa.add(
        mod_secim_container_memory.current,
        cok_oyunculu_secim_container_memory.current,
        sunucu_baslat_container_memory.current,
        sunucu_baglan_container_memory.current,
        oyun_ekrani_container_memory.current,
    )

    show_view_memory("main_menu")

# ===================================================================================
# =========================== MEMORY (Hafıza) OYUN KODU BİTİŞ ============================
# ===================================================================================



# ===================================================================================
# ============================== MANCALA OYUN KODU BAŞLANGIÇ ==============================
# ===================================================================================

# Mancala Oyun Sabitleri
BASLANGIC_TASLARI_MANCALA = 4
OYUNCU_BASI_KUYU_SAYISI_MANCALA = 6
SUNUCU_PORTU_MANCALA = 12346

# Zorluk Seviyesi Dosyası (Mancala)
ZORLUK_DOSYASI_MANCALA = Path("zorluk_mancala.json")

# Mancala Oyun Durumu
oyun_durumu_mancala = {
    "tahta": [BASLANGIC_TASLARI_MANCALA] * OYUNCU_BASI_KUYU_SAYISI_MANCALA + [0] + [BASLANGIC_TASLARI_MANCALA] * OYUNCU_BASI_KUYU_SAYISI_MANCALA + [0],
    "mevcut_oyuncu": 1,
    "oyun_basladi": False,
    "oyun_bitti": False,
    "oyuncu_adi": "",
    "cok_oyunculu": False,
    "sunucu_mu": None,
    "istemci_soketi": None,
    "oyuncular": [],
    "skorlar": [],
    "sira_mesaji": "1. Oyuncunun Sırası",
    "kazanan": None,
    "secilen_kuyu": None,
    "zorluk_seviyesi": "Orta",
    "egitim_modu": False,
    "oyuncu_istatistikleri": {"puan": 0, "hamleler": [], "sureler": []}, 
}

# Canlı Renk Paleti (Mancala)
RENK_KUYU_MANCALA = ft.colors.AMBER_400 
RENK_TAS_MANCALA = ft.colors.BROWN_700 
RENK_HAZINE_1_MANCALA = ft.colors.BLUE_700 
RENK_HAZINE_2_MANCALA = ft.colors.GREEN_700 
RENK_SECILI_KUYU_BORDER_MANCALA = ft.colors.RED_ACCENT_700 
RENK_NORMAL_KUYU_BORDER_MANCALA = ft.colors.BROWN_400 
RENK_MENU_ARKA_PLAN_MANCALA = ft.colors.WHITE 

# Mancala Zorluk Seviyesi İşlemleri
def zorluk_seviyesi_oku_mancala():
    try:
        if ZORLUK_DOSYASI_MANCALA.exists():
            with open(ZORLUK_DOSYASI_MANCALA, "r", encoding="utf-8") as f:
                veri = json.load(f)
                oyun_durumu_mancala["zorluk_seviyesi"] = veri.get("zorluk_mancala", "Orta")
    except Exception as e:
        print(f"Mancala Zorluk seviyesi okuma hatası: {str(e)}")

def zorluk_seviyesi_kaydet_mancala():
    try:
        with open(ZORLUK_DOSYASI_MANCALA, "w", encoding="utf-8") as f:
            json.dump({"zorluk_mancala": oyun_durumu_mancala["zorluk_seviyesi"]}, f)
    except Exception as e:
        print(f"Mancala Zorluk seviyesi kaydetme hatası: {str(e)}")

# Mancala Ana Fonksiyonu
def main_mancala(sayfa: ft.Page, go_to_master_menu_func):
    sayfa.title = "Mancala Oyunu"
    sayfa.vertical_alignment = ft.MainAxisAlignment.CENTER
    sayfa.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    sayfa.theme_mode = ft.ThemeMode.LIGHT
    sayfa.window_width = 1100
    sayfa.window_height = 800
    # sayfa.window_center() # Ana merkezleme master_main'de yapılıyor.
    sayfa.bgcolor = PAGE_BG_COLOR

    zorluk_seviyesi_oku_mancala()

    # Mancala Flet Kontrolleri
    mod_secim_konteyneri_mancala = ft.Ref[ft.Container]()
    tek_oyunculu_secim_konteyneri_mancala = ft.Ref[ft.Container]()
    cok_oyunculu_secim_konteyneri_mancala = ft.Ref[ft.Container]()
    sunucu_olustur_konteyneri_mancala = ft.Ref[ft.Container]()
    sunucu_baglan_konteyneri_mancala = ft.Ref[ft.Container]()
    oyuncu_adi_girdi_mancala = ft.Ref[ft.TextField]()
    sunucu_adresi_girdi_mancala = ft.Ref[ft.TextField]()
    sunucu_adresi_goster_mancala = ft.Ref[ft.Text]()
    baglanan_oyuncular_goster_mancala = ft.Ref[ft.Text]()
    oyun_baslat_buton_mancala = ft.Ref[ft.ElevatedButton]()
    tahta_konteyneri_mancala = ft.Ref[ft.Container]()
    geri_bildirim_goster_mancala = ft.Ref[ft.Text]()
    hamle_onayla_buton_mancala = ft.Ref[ft.ElevatedButton]()
    lider_tablosu_konteyneri_mancala = ft.Ref[ft.Container]()
    bitis_ekrani_konteyneri_mancala = ft.Ref[ft.Container]()
    oyun_kontrol_butonlari_konteyneri_mancala = ft.Ref[ft.Container]()
    
    # Geçici durumlar için kullanılan global değişkenler (Mancala için)
    _temp_feedback_mancala = ft.Ref[str]()
    _temp_sunucu_adresi_mancala = ft.Ref[str]()
    _temp_baglanan_oyuncular_mancala = ft.Ref[str]()
    _temp_oyun_baslat_disabled_mancala = ft.Ref[bool]()
    _temp_is_connected_mancala = ft.Ref[bool]()
    
    def go_to_main_menu_mancala():
        # Mancala'nın kendi ana menüsüne döner
        yeniden_baslat_tiklama_mancala(None, True)

    def arayuz_guncelle_mancala():
        if not mod_secim_konteyneri_mancala.current: return

        # Tüm konteynerleri gizle
        mod_secim_konteyneri_mancala.current.visible = False
        tek_oyunculu_secim_konteyneri_mancala.current.visible = False
        cok_oyunculu_secim_konteyneri_mancala.current.visible = False
        sunucu_olustur_konteyneri_mancala.current.visible = False
        sunucu_baglan_konteyneri_mancala.current.visible = False
        tahta_konteyneri_mancala.current.visible = False
        bitis_ekrani_konteyneri_mancala.current.visible = False
        lider_tablosu_konteyneri_mancala.current.visible = False
        geri_bildirim_goster_mancala.current.visible = True
        oyun_kontrol_butonlari_konteyneri_mancala.current.visible = False
        
        # Duruma göre doğru konteyneri göster
        if oyun_durumu_mancala["oyun_bitti"]:
            bitis_ekrani_konteyneri_mancala.current.visible = True
            bitis_ekrani_konteyneri_mancala.current.content = bitis_ekrani_olustur_mancala()
            if oyun_durumu_mancala["cok_oyunculu"]:
                lider_tablosu_konteyneri_mancala.current.visible = True
                lider_tablosu_konteyneri_mancala.current.content = ft.Text(
                    "\n".join([f"{oyuncu['ad']}: {oyuncu['skor']} puan" for oyuncu in oyun_durumu_mancala.get("skorlar", [])]),
                    size=18, text_align=ft.TextAlign.CENTER, color=ft.colors.BLUE_900)
        elif oyun_durumu_mancala["oyun_basladi"]:
            tahta_konteyneri_mancala.current.visible = True
            oyun_kontrol_butonlari_konteyneri_mancala.current.visible = True
            try:
                tahta_konteyneri_mancala.current.content = tahta_duzeni_olustur_mancala()
            except Exception as e:
                geri_bildirim_goster_mancala.current.value = f"Tahta oluşturma hatası: {str(e)}"
        else:
            if not oyun_durumu_mancala["oyuncu_adi"]:
                mod_secim_konteyneri_mancala.current.visible = True
            else:
                if oyun_durumu_mancala["cok_oyunculu"]:
                    if oyun_durumu_mancala.get("sunucu_mu") is True:
                        sunucu_olustur_konteyneri_mancala.current.visible = True
                        if _temp_sunucu_adresi_mancala.current: sunucu_adresi_goster_mancala.current.value = _temp_sunucu_adresi_mancala.current
                        if _temp_baglanan_oyuncular_mancala.current: baglanan_oyuncular_goster_mancala.current.value = _temp_baglanan_oyuncular_mancala.current
                        if _temp_oyun_baslat_disabled_mancala.current is not None: oyun_baslat_buton_mancala.current.disabled = _temp_oyun_baslat_disabled_mancala.current
                    elif oyun_durumu_mancala.get("sunucu_mu") is False:
                        sunucu_baglan_konteyneri_mancala.current.visible = True
                    else:
                        cok_oyunculu_secim_konteyneri_mancala.current.visible = True
                else:
                    tek_oyunculu_secim_konteyneri_mancala.current.visible = True
                    tek_oyunculu_secim_konteyneri_mancala.current.content.controls[1].value = f"Mevcut YZ Zorluk Seviyesi: {oyun_durumu_mancala['zorluk_seviyesi']}"
        
        # Geri bildirim mesajını güncelle
        if _temp_feedback_mancala.current:
            geri_bildirim_goster_mancala.current.value = _temp_feedback_mancala.current
            _temp_feedback_mancala.current = None
        elif oyun_durumu_mancala["oyun_bitti"]:
            mesaj = f"Oyun Bitti! Kazanan: {oyun_durumu_mancala.get('kazanan', '')}. "
            if oyun_durumu_mancala.get("egitim_modu_bitti"):
                mesaj += f"Eğitim sonrası yeni YZ Zorluk Seviyesi: {oyun_durumu_mancala['zorluk_seviyesi']}"
                oyun_durumu_mancala.pop("egitim_modu_bitti", None)
            geri_bildirim_goster_mancala.current.value = mesaj
        elif oyun_durumu_mancala["oyun_basladi"]:
            geri_bildirim_goster_mancala.current.value = oyun_durumu_mancala["sira_mesaji"]
        else:
             geri_bildirim_goster_mancala.current.value = f"Hoş geldin, {oyun_durumu_mancala.get('oyuncu_adi', '')}! Lütfen bir mod seç." if oyun_durumu_mancala.get('oyuncu_adi') else "Lütfen oyuncu adınızı girip bir mod seçin."
        
        # Hamle onayla butonunun durumunu ayarla
        is_my_turn = False
        if not oyun_durumu_mancala["cok_oyunculu"] and oyun_durumu_mancala["mevcut_oyuncu"] == 1:
            is_my_turn = True
        elif oyun_durumu_mancala["cok_oyunculu"]:
            if oyun_durumu_mancala["sunucu_mu"] and oyun_durumu_mancala["mevcut_oyuncu"] == 1:
                is_my_turn = True
            elif not oyun_durumu_mancala["sunucu_mu"] and oyun_durumu_mancala["mevcut_oyuncu"] == 2:
                is_my_turn = True
        
        hamle_onayla_buton_mancala.current.disabled = not (
            is_my_turn and 
            oyun_durumu_mancala["secilen_kuyu"] is not None and
            oyun_durumu_mancala["oyun_basladi"] and
            not oyun_durumu_mancala["oyun_bitti"] and
            gecerli_hamle_mi_mancala(oyun_durumu_mancala["secilen_kuyu"]) 
        )

        sayfa.update()

    def tahta_baslat_mancala():
        oyun_durumu_mancala["tahta"] = ([BASLANGIC_TASLARI_MANCALA] * OYUNCU_BASI_KUYU_SAYISI_MANCALA + [0] + [BASLANGIC_TASLARI_MANCALA] * OYUNCU_BASI_KUYU_SAYISI_MANCALA + [0])
        oyun_durumu_mancala["mevcut_oyuncu"] = 1
        oyuncu1_adi = "1. Oyuncu"
        if oyun_durumu_mancala.get("cok_oyunculu") and len(oyun_durumu_mancala.get("oyuncular", [])) > 0: oyuncu1_adi = oyun_durumu_mancala["oyuncular"][0]["ad"]
        elif not oyun_durumu_mancala.get("cok_oyunculu") and oyun_durumu_mancala.get("oyuncu_adi"): oyuncu1_adi = oyun_durumu_mancala["oyuncu_adi"]
        oyun_durumu_mancala["sira_mesaji"] = f"{oyuncu1_adi}'nun Sırası"
        oyun_durumu_mancala["kazanan"] = None
        oyun_durumu_mancala["secilen_kuyu"] = None
        oyun_durumu_mancala["oyun_bitti"] = False
        oyun_durumu_mancala["oyun_basladi"] = True
        oyun_durumu_mancala.pop("egitim_modu_bitti", None)
        if oyun_durumu_mancala["egitim_modu"]: oyun_durumu_mancala["oyuncu_istatistikleri"] = {"puan": 0, "hamleler": [], "sureler": []}
        arayuz_guncelle_mancala()

    def gecerli_hamle_mi_mancala(kuyu_indeksi):
        if kuyu_indeksi is None: return False
        if oyun_durumu_mancala["oyun_bitti"] or not oyun_durumu_mancala["oyun_basladi"]: return False
        
        my_turn = False
        if not oyun_durumu_mancala["cok_oyunculu"]:
            if oyun_durumu_mancala["mevcut_oyuncu"] == 1: my_turn = True
        else:
            if oyun_durumu_mancala["sunucu_mu"] and oyun_durumu_mancala["mevcut_oyuncu"] == 1: my_turn = True
            elif not oyun_durumu_mancala["sunucu_mu"] and oyun_durumu_mancala["mevcut_oyuncu"] == 2: my_turn = True

        if not my_turn: return False

        oyuncu_kuyulari_gecerli = (range(0, OYUNCU_BASI_KUYU_SAYISI_MANCALA) if oyun_durumu_mancala["mevcut_oyuncu"] == 1 else range(OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1, 2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1))
        return kuyu_indeksi in oyuncu_kuyulari_gecerli and oyun_durumu_mancala["tahta"][kuyu_indeksi] > 0

    def taslari_dagit_mancala(kuyu_indeksi):
        baslangic_zamani = None
        if oyun_durumu_mancala["egitim_modu"] and oyun_durumu_mancala["mevcut_oyuncu"] == 1: baslangic_zamani = time.time()
        
        taslar = oyun_durumu_mancala["tahta"][kuyu_indeksi]
        oyun_durumu_mancala["tahta"][kuyu_indeksi] = 0
        oyun_durumu_mancala["secilen_kuyu"] = None 
        mevcut_indeks = kuyu_indeksi
        oyuncu_hazinesi = OYUNCU_BASI_KUYU_SAYISI_MANCALA if oyun_durumu_mancala["mevcut_oyuncu"] == 1 else 2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1
        rakip_hazinesi = 2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1 if oyun_durumu_mancala["mevcut_oyuncu"] == 1 else OYUNCU_BASI_KUYU_SAYISI_MANCALA
        yakalama_yapildi = False
        ekstra_tur_kazanildi = False
        son_birakilan_kuyu = -1

        def dagitma_adimi(tas_sayisi):
            if tas_sayisi <= 0:
                dagitma_sonrasi_islemler()
                return

            nonlocal mevcut_indeks
            mevcut_indeks = (mevcut_indeks + 1) % (2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 2)
            if mevcut_indeks == rakip_hazinesi:
                threading.Timer(0.1, lambda: dagitma_adimi(tas_sayisi)).start() # Rakip hazinesini atla
                return

            oyun_durumu_mancala["tahta"][mevcut_indeks] += 1
            nonlocal son_birakilan_kuyu
            son_birakilan_kuyu = mevcut_indeks
            arayuz_guncelle_mancala()
            
            threading.Timer(0.15, lambda: dagitma_adimi(tas_sayisi - 1)).start()

        def dagitma_sonrasi_islemler():
            nonlocal ekstra_tur_kazanildi, yakalama_yapildi
            
            mevcut_oyuncu_no_sira_icin = oyun_durumu_mancala["mevcut_oyuncu"]
            oyuncu_adi_sira_icin = ""
            if oyun_durumu_mancala.get("cok_oyunculu") and len(oyun_durumu_mancala.get("oyuncular", [])) >= mevcut_oyuncu_no_sira_icin:
                oyuncu_adi_sira_icin = oyun_durumu_mancala["oyuncular"][mevcut_oyuncu_no_sira_icin-1]["ad"]
            elif not oyun_durumu_mancala.get("cok_oyunculu"):
                oyuncu_adi_sira_icin = oyun_durumu_mancala["oyuncu_adi"] if mevcut_oyuncu_no_sira_icin == 1 else "Yapay Zeka"
            else:
                oyuncu_adi_sira_icin = f"{mevcut_oyuncu_no_sira_icin}. Oyuncu"

            if son_birakilan_kuyu == oyuncu_hazinesi:
                oyun_durumu_mancala["sira_mesaji"] = f"{oyuncu_adi_sira_icin}'nun Sırası (Ekstra Tur)"
                ekstra_tur_kazanildi = True
            else:
                if son_birakilan_kuyu != -1 and oyun_durumu_mancala["tahta"][son_birakilan_kuyu] == 1:
                    mevcut_oyuncu_kuyulari_alan = (range(0, OYUNCU_BASI_KUYU_SAYISI_MANCALA) if oyun_durumu_mancala["mevcut_oyuncu"] == 1 else range(OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1, 2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1))
                    if son_birakilan_kuyu in mevcut_oyuncu_kuyulari_alan:
                        karsi_kuyu_indeksi = (2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA) - son_birakilan_kuyu
                        if karsi_kuyu_indeksi >= 0 and karsi_kuyu_indeksi < len(oyun_durumu_mancala["tahta"]) and oyun_durumu_mancala["tahta"][karsi_kuyu_indeksi] > 0:
                            yakalanan_taslar = oyun_durumu_mancala["tahta"][karsi_kuyu_indeksi] + 1
                            oyun_durumu_mancala["tahta"][oyuncu_hazinesi] += yakalanan_taslar
                            oyun_durumu_mancala["tahta"][karsi_kuyu_indeksi] = 0
                            oyun_durumu_mancala["tahta"][son_birakilan_kuyu] = 0
                            yakalama_yapildi = True
                
                oyun_durumu_mancala["mevcut_oyuncu"] = 2 if oyun_durumu_mancala["mevcut_oyuncu"] == 1 else 1
                siradaki_oyuncu_no = oyun_durumu_mancala["mevcut_oyuncu"]
                siradaki_oyuncu_adi = ""
                if oyun_durumu_mancala.get("cok_oyunculu") and len(oyun_durumu_mancala.get("oyuncular", [])) >= siradaki_oyuncu_no:
                    siradaki_oyuncu_adi = oyun_durumu_mancala["oyuncular"][siradaki_oyuncu_no-1]["ad"]
                elif not oyun_durumu_mancala.get("cok_oyunculu"):
                    siradaki_oyuncu_adi = oyun_durumu_mancala["oyuncu_adi"] if siradaki_oyuncu_no == 1 else "Yapay Zeka"
                else:
                    siradaki_oyuncu_adi = f"{siradaki_oyuncu_no}. Oyuncu"
                oyun_durumu_mancala["sira_mesaji"] = f"{siradaki_oyuncu_adi}'nun Sırası"

            if baslangic_zamani and oyun_durumu_mancala["egitim_modu"] and mevcut_oyuncu_no_sira_icin == 1 : 
                hamle_suresi = time.time() - baslangic_zamani
                hamle_puani = 10 
                if yakalama_yapildi: hamle_puani += 20
                if ekstra_tur_kazanildi: hamle_puani += 15 
                oyun_durumu_mancala["oyuncu_istatistikleri"]["hamleler"].append({"kuyu": kuyu_indeksi, "puan": hamle_puani })
                oyun_durumu_mancala["oyuncu_istatistikleri"]["sureler"].append(hamle_suresi)

            oyuncu1_kuyular_toplami = sum(oyun_durumu_mancala["tahta"][0:OYUNCU_BASI_KUYU_SAYISI_MANCALA])
            oyuncu2_kuyular_toplami = sum(oyun_durumu_mancala["tahta"][OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1:2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1])
            if oyuncu1_kuyular_toplami == 0 or oyuncu2_kuyular_toplami == 0:
                oyunu_bitir_mancala(); return

            arayuz_guncelle_mancala() 
            if not oyun_durumu_mancala["oyun_bitti"]:
                if not oyun_durumu_mancala["cok_oyunculu"] and oyun_durumu_mancala["mevcut_oyuncu"] == 2:
                    threading.Thread(target=yapay_zeka_hamlesi_wrapper_mancala, daemon=True).start()

        dagitma_adimi(taslar)

    def yapay_zeka_hamlesi_wrapper_mancala(): time.sleep(0.7); yapay_zeka_hamlesi_mancala()
    def yapay_zeka_hamlesi_mancala():
        if oyun_durumu_mancala["oyun_bitti"] or oyun_durumu_mancala["mevcut_oyuncu"] != 2: return
        oyuncu2_kuyulari = range(OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1, 2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1)
        gecerli_kuyular = [i for i in oyuncu2_kuyulari if oyun_durumu_mancala["tahta"][i] > 0]
        if not gecerli_kuyular: oyunu_bitir_mancala(); return
        kuyu_indeksi = -1
        if oyun_durumu_mancala["zorluk_seviyesi"] == "Kolay": kuyu_indeksi = random.choice(gecerli_kuyular)
        elif oyun_durumu_mancala["zorluk_seviyesi"] == "Orta":
            en_iyi_kuyu = None; en_iyi_puan = -float('inf') 
            for kuyu in gecerli_kuyular:
                puan = oyun_durumu_mancala["tahta"][kuyu] 
                if (kuyu + oyun_durumu_mancala["tahta"][kuyu]) % (2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 2) == (2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1): puan += 20 
                if puan > en_iyi_puan: en_iyi_puan = puan; en_iyi_kuyu = kuyu
            kuyu_indeksi = en_iyi_kuyu if en_iyi_kuyu is not None else random.choice(gecerli_kuyular)
        else: 
            _, kuyu_indeksi_minimax = minimax_mancala(oyun_durumu_mancala["tahta"][:], 3, True, -float('inf'), float('inf')) 
            kuyu_indeksi = kuyu_indeksi_minimax if kuyu_indeksi_minimax is not None and kuyu_indeksi_minimax in gecerli_kuyular else random.choice(gecerli_kuyular)
        if kuyu_indeksi != -1:
            oyun_durumu_mancala["secilen_kuyu"] = kuyu_indeksi 
            arayuz_guncelle_mancala()
            time.sleep(0.4) 
            taslari_dagit_mancala(kuyu_indeksi)
        elif gecerli_kuyular: taslari_dagit_mancala(random.choice(gecerli_kuyular))

    def minimax_mancala(tahta_durumu, derinlik, maksimize_eden_oyuncu_mu, alpha, beta):
        if derinlik == 0 or oyun_bitti_mi_mancala(tahta_durumu): return tahta_degerlendir_yz_icin_mancala(tahta_durumu), None 
        hamleler = []
        mevcut_oyuncu_no_minimax = 2 if maksimize_eden_oyuncu_mu else 1
        if mevcut_oyuncu_no_minimax == 2: hamleler = [i for i in range(OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1, 2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1) if tahta_durumu[i] > 0]
        else: hamleler = [i for i in range(0, OYUNCU_BASI_KUYU_SAYISI_MANCALA) if tahta_durumu[i] > 0]
        if not hamleler: return tahta_degerlendir_yz_icin_mancala(tahta_durumu), None
        en_iyi_hamle = None
        if maksimize_eden_oyuncu_mu: 
            max_eval = -float('inf')
            for hamle_kuyusu in hamleler:
                gecici_tahta = tahta_durumu[:]; son_kuyu, ekstra_tur_oldu = simulate_dagit_mancala(gecici_tahta, hamle_kuyusu, 2) 
                degerlendirme, _ = minimax_mancala(gecici_tahta, derinlik - 1, True if ekstra_tur_oldu else False, alpha, beta)
                if degerlendirme > max_eval: max_eval = degerlendirme; en_iyi_hamle = hamle_kuyusu
                alpha = max(alpha, degerlendirme)
                if beta <= alpha: break 
            return max_eval, en_iyi_hamle
        else: 
            min_eval = float('inf')
            for hamle_kuyusu in hamleler:
                gecici_tahta = tahta_durumu[:]; son_kuyu, ekstra_tur_oldu = simulate_dagit_mancala(gecici_tahta, hamle_kuyusu, 1) 
                degerlendirme, _ = minimax_mancala(gecici_tahta, derinlik - 1, False if ekstra_tur_oldu else True, alpha, beta)
                if degerlendirme < min_eval: min_eval = degerlendirme; en_iyi_hamle = hamle_kuyusu 
                beta = min(beta, degerlendirme)
                if beta <= alpha: break 
            return min_eval, en_iyi_hamle

    def simulate_dagit_mancala(tahta, kuyu_indeksi, oyuncu_no):
        taslar = tahta[kuyu_indeksi]; tahta[kuyu_indeksi] = 0; mevcut_indeks = kuyu_indeksi
        oyuncu_hazinesi = OYUNCU_BASI_KUYU_SAYISI_MANCALA if oyuncu_no == 1 else (2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1)
        rakip_hazinesi = (2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1) if oyuncu_no == 1 else OYUNCU_BASI_KUYU_SAYISI_MANCALA
        son_birakilan_kuyu = -1
        while taslar > 0:
            mevcut_indeks = (mevcut_indeks + 1) % (2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 2)
            if mevcut_indeks == rakip_hazinesi: continue
            tahta[mevcut_indeks] += 1; taslar -= 1; son_birakilan_kuyu = mevcut_indeks
        ekstra_tur = (son_birakilan_kuyu == oyuncu_hazinesi)
        if not ekstra_tur and son_birakilan_kuyu != -1 and tahta[son_birakilan_kuyu] == 1: 
            mevcut_oyuncu_kuyulari_alan_sim = (range(0, OYUNCU_BASI_KUYU_SAYISI_MANCALA) if oyuncu_no == 1 else range(OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1, 2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1))
            if son_birakilan_kuyu in mevcut_oyuncu_kuyulari_alan_sim:
                karsi_kuyu = (2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA) - son_birakilan_kuyu
                if karsi_kuyu >= 0 and karsi_kuyu < len(tahta) and tahta[karsi_kuyu] > 0 : 
                    tahta[oyuncu_hazinesi] += tahta[karsi_kuyu] + 1; tahta[karsi_kuyu] = 0; tahta[son_birakilan_kuyu] = 0
        return son_birakilan_kuyu, ekstra_tur
        
    def tahta_degerlendir_yz_icin_mancala(tahta):
        oyuncu2_hazine_indeksi = 2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1; oyuncu1_hazine_indeksi = OYUNCU_BASI_KUYU_SAYISI_MANCALA
        if oyun_bitti_mi_mancala(tahta):
            temp_tahta = tahta[:] 
            temp_tahta[oyuncu1_hazine_indeksi] += sum(temp_tahta[0:OYUNCU_BASI_KUYU_SAYISI_MANCALA])
            for i in range(0, OYUNCU_BASI_KUYU_SAYISI_MANCALA): temp_tahta[i] = 0
            temp_tahta[oyuncu2_hazine_indeksi] += sum(temp_tahta[OYUNCU_BASI_KUYU_SAYISI_MANCALA+1 : 2*OYUNCU_BASI_KUYU_SAYISI_MANCALA+1])
            for i in range(OYUNCU_BASI_KUYU_SAYISI_MANCALA+1, 2*OYUNCU_BASI_KUYU_SAYISI_MANCALA+1): temp_tahta[i] = 0
            return temp_tahta[oyuncu2_hazine_indeksi] - temp_tahta[oyuncu1_hazine_indeksi]
        return tahta[oyuncu2_hazine_indeksi] - tahta[oyuncu1_hazine_indeksi]

    def oyun_bitti_mi_mancala(tahta_durumu): 
        return all(tahta_durumu[i] == 0 for i in range(0, OYUNCU_BASI_KUYU_SAYISI_MANCALA)) or \
               all(tahta_durumu[i] == 0 for i in range(OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1, 2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1))

    def oyunu_bitir_mancala():
        oyun_durumu_mancala["oyun_bitti"] = True; oyun_durumu_mancala["oyun_basladi"] = False 
        oyuncu1_hazinesi = OYUNCU_BASI_KUYU_SAYISI_MANCALA; oyuncu2_hazinesi = 2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1
        oyun_durumu_mancala["tahta"][oyuncu1_hazinesi] += sum(oyun_durumu_mancala["tahta"][0:OYUNCU_BASI_KUYU_SAYISI_MANCALA])
        for i in range(0, OYUNCU_BASI_KUYU_SAYISI_MANCALA): oyun_durumu_mancala["tahta"][i] = 0
        oyun_durumu_mancala["tahta"][oyuncu2_hazinesi] += sum(oyun_durumu_mancala["tahta"][OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1 : 2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1])
        for i in range(OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1, 2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1): oyun_durumu_mancala["tahta"][i] = 0
        oyuncu1_skor = oyun_durumu_mancala["tahta"][oyuncu1_hazinesi]; oyuncu2_skor = oyun_durumu_mancala["tahta"][oyuncu2_hazinesi]
        
        oyuncu1_ad = (oyun_durumu_mancala["oyuncu_adi"] if not oyun_durumu_mancala["cok_oyunculu"] else (oyun_durumu_mancala["oyuncular"][0]["ad"] if len(oyun_durumu_mancala.get("oyuncular",[])) > 0 else "Oyuncu 1"))
        oyuncu2_ad = ("Yapay Zeka" if not oyun_durumu_mancala["cok_oyunculu"] else (oyun_durumu_mancala["oyuncular"][1]["ad"] if len(oyun_durumu_mancala.get("oyuncular",[])) > 1 else "Oyuncu 2"))

        if oyuncu1_skor > oyuncu2_skor: oyun_durumu_mancala["kazanan"] = oyuncu1_ad
        elif oyuncu2_skor > oyuncu1_skor: oyun_durumu_mancala["kazanan"] = oyuncu2_ad
        else: oyun_durumu_mancala["kazanan"] = "Berabere"

        if oyun_durumu_mancala["egitim_modu"]:
            oyun_durumu_mancala["oyuncu_istatistikleri"]["puan"] = oyuncu1_skor 
            zorluk_seviyesi_belirle_mancala(); oyun_durumu_mancala["egitim_modu_bitti"] = True 
        
        if oyun_durumu_mancala["cok_oyunculu"]:
            skor_listesi = [{"ad": oyuncu1_ad, "skor": oyuncu1_skor}, {"ad": oyuncu2_ad, "skor": oyuncu2_skor}]
            oyun_durumu_mancala["skorlar"] = skor_listesi
            if oyun_durumu_mancala["sunucu_mu"]:
                bitis_mesaji = {"tip": "oyun_bitti", "kazanan": oyun_durumu_mancala["kazanan"], "skorlar": oyun_durumu_mancala["skorlar"], "tahta": oyun_durumu_mancala["tahta"]}
                for oyuncu_data in oyun_durumu_mancala.get("oyuncular", []):
                    if oyuncu_data.get("soket"):
                        try: oyuncu_data["soket"].send(json.dumps(bitis_mesaji).encode())
                        except Exception as e: print(f"Skor gönderme hatası (sunucu): {e}")
        arayuz_guncelle_mancala()

    def zorluk_seviyesi_belirle_mancala():
        istat = oyun_durumu_mancala["oyuncu_istatistikleri"]
        if not istat["hamleler"]: 
            oyun_durumu_mancala["zorluk_seviyesi"] = "Orta" 
            zorluk_seviyesi_kaydet_mancala(); return

        toplam_kazanilan_skor_tas = istat["puan"]
        max_mumkun_tas_sayisi = BASLANGIC_TASLARI_MANCALA * OYUNCU_BASI_KUYU_SAYISI_MANCALA * 2
        skor_yuzdesi = (toplam_kazanilan_skor_tas / max_mumkun_tas_sayisi) * 100 if max_mumkun_tas_sayisi > 0 else 0
        ortalama_sure = sum(istat["sureler"]) / len(istat["sureler"]) if istat["sureler"] else 5.0 
        toplam_hamle_puani = sum(h["puan"] for h in istat["hamleler"])
        ortalama_hamle_puani = toplam_hamle_puani / len(istat["hamleler"]) if istat["hamleler"] else 0
        
        yeni_zorluk = oyun_durumu_mancala["zorluk_seviyesi"]
        if skor_yuzdesi < 38 or ortalama_sure > 12 or ortalama_hamle_puani < 12:
            yeni_zorluk = "Kolay"
        elif skor_yuzdesi >= 60 and ortalama_sure <= 5 and ortalama_hamle_puani >= 18:
            yeni_zorluk = "Zor"
        else:
            yeni_zorluk = "Orta"
        
        print(f"Eğitim sonu: Skor Yüzdesi: {skor_yuzdesi:.2f}%, Ortalama Süre: {ortalama_sure:.2f}s, Ort. Hamle Puanı: {ortalama_hamle_puani:.2f}. Yeni Zorluk: {yeni_zorluk}")
        oyun_durumu_mancala["zorluk_seviyesi"] = yeni_zorluk
        zorluk_seviyesi_kaydet_mancala()

    def kuyu_tiklama_mancala(kuyu_indeksi):
        def isleyici(e):
            if gecerli_hamle_mi_mancala(kuyu_indeksi): oyun_durumu_mancala["secilen_kuyu"] = kuyu_indeksi; arayuz_guncelle_mancala()
        return isleyici

    def hamle_onayla_mancala(e):
        if oyun_durumu_mancala["secilen_kuyu"] is not None:
            secilen = oyun_durumu_mancala["secilen_kuyu"]
            if gecerli_hamle_mi_mancala(secilen):
                if oyun_durumu_mancala["cok_oyunculu"]: hamleyi_gonder_mancala(secilen)
                taslari_dagit_mancala(secilen)

    def hamleyi_gonder_mancala(kuyu_indeksi):
        if oyun_durumu_mancala["cok_oyunculu"] and oyun_durumu_mancala["oyun_basladi"] and not oyun_durumu_mancala["oyun_bitti"]:
            mesaj = {"tip": "hamle", "kuyu": kuyu_indeksi, "oyuncu_no": (1 if oyun_durumu_mancala["sunucu_mu"] else 2)}
            soket_hedef = oyun_durumu_mancala.get("istemci_soketi")
            if oyun_durumu_mancala["sunucu_mu"] and len(oyun_durumu_mancala.get("oyuncular", [])) > 1:
                soket_hedef = oyun_durumu_mancala["oyuncular"][1].get("soket")
            
            if soket_hedef:
                try: soket_hedef.send(json.dumps(mesaj).encode())
                except Exception as ex: print(f"Mancala hamle gönderme hatası: {ex}")

    def tek_oyunculu_sec_mancala(e):
        oyun_durumu_mancala["oyuncu_adi"] = oyuncu_adi_girdi_mancala.current.value.strip() or "Oyuncu 1"; oyun_durumu_mancala["cok_oyunculu"] = False
        oyun_durumu_mancala["sunucu_mu"] = None; zorluk_seviyesi_oku_mancala(); arayuz_guncelle_mancala()
    
    def oyun_baslat_tek_mancala(e): oyun_durumu_mancala["cok_oyunculu"] = False; oyun_durumu_mancala["egitim_modu"] = False; tahta_baslat_mancala()
    def zorluk_ayarla_baslat_mancala(e): oyun_durumu_mancala["cok_oyunculu"] = False; oyun_durumu_mancala["egitim_modu"] = True; oyun_durumu_mancala["zorluk_seviyesi"] = "Orta"; tahta_baslat_mancala()
    
    def cok_oyunculu_sec_mancala(e):
        oyun_durumu_mancala["oyuncu_adi"] = oyuncu_adi_girdi_mancala.current.value.strip() or "Oyuncu"; oyun_durumu_mancala["cok_oyunculu"] = True
        oyun_durumu_mancala["sunucu_mu"] = None; arayuz_guncelle_mancala()
    
    def sunucu_olustur_secim_ekranindan_mancala(e): oyun_durumu_mancala["sunucu_mu"] = True; sunucu_olustur_mancala(e) 
    def sunucuya_baglan_secim_ekranindan_mancala(e): oyun_durumu_mancala["sunucu_mu"] = False; arayuz_guncelle_mancala() 
    
    def sunucu_olustur_mancala(e): 
        if not oyun_durumu_mancala["oyuncu_adi"]: 
            _temp_feedback_mancala.current = "Lütfen bir oyuncu adı girin!"
            arayuz_guncelle_mancala(); return
        threading.Thread(target=sunucu_olustur_fonksiyonu_mancala, daemon=True).start()
    
    def sunucuya_baglan_asıl_mancala(e): 
        if not oyun_durumu_mancala["oyuncu_adi"]: 
            _temp_feedback_mancala.current = "Lütfen bir oyuncu adı girin!"
            arayuz_guncelle_mancala(); return
        sunucu_adres_str = sunucu_adresi_girdi_mancala.current.value.strip()
        if not sunucu_adres_str or ":" not in sunucu_adres_str:
            _temp_feedback_mancala.current = "Lütfen geçerli bir sunucu adresi girin (IP:Port)!"
            arayuz_guncelle_mancala(); return
        try:
            adres, port_str = sunucu_adres_str.split(":"); port = int(port_str)
            threading.Thread(target=sunucuya_baglan_fonksiyonu_mancala, args=(adres, port), daemon=True).start()
        except ValueError:
            _temp_feedback_mancala.current = "Port numarası geçerli bir tamsayı olmalı!"
            arayuz_guncelle_mancala()
        except Exception as ex:
            _temp_feedback_mancala.current = f"Bağlantı başlatma hatası: {ex}"
            arayuz_guncelle_mancala()
            
    def oyun_baslat_cok_oyunculu_mancala(e): 
        if len(oyun_durumu_mancala.get("oyuncular", [])) < 2:
            _temp_feedback_mancala.current = "Oyunu başlatmak için en az 2 oyuncu gereklidir."
            arayuz_guncelle_mancala(); return
        initial_board_state = [BASLANGIC_TASLARI_MANCALA] * OYUNCU_BASI_KUYU_SAYISI_MANCALA + [0] + [BASLANGIC_TASLARI_MANCALA] * OYUNCU_BASI_KUYU_SAYISI_MANCALA + [0]
        baslat_mesaji = {"tip": "baslat", "oyuncular": [{"ad": p["ad"]} for p in oyun_durumu_mancala["oyuncular"]], "tahta": initial_board_state }
        for oyuncu_data in oyun_durumu_mancala.get("oyuncular", []):
            if oyuncu_data.get("soket"): 
                try: oyuncu_data["soket"].send(json.dumps(baslat_mesaji).encode())
                except Exception as ex: print(f"Mancala Başlatma mesajı gönderme hatası: {ex}")
        oyun_durumu_mancala["oyun_basladi"] = True; tahta_baslat_mancala() 
    
    def yeniden_baslat_tiklama_mancala(e, to_mancala_menu=False):
        if oyun_durumu_mancala.get("istemci_soketi"):
            try: oyun_durumu_mancala["istemci_soketi"].close()
            except: pass
        
        # Oyuncunun adını ve zorluk seviyesini koru
        current_oyuncu_adi = oyun_durumu_mancala.get("oyuncu_adi", "")
        current_zorluk = oyun_durumu_mancala.get("zorluk_seviyesi", "Orta")

        oyun_durumu_mancala.clear() 
        oyun_durumu_mancala.update({ 
            "tahta": [BASLANGIC_TASLARI_MANCALA] * OYUNCU_BASI_KUYU_SAYISI_MANCALA + [0] + [BASLANGIC_TASLARI_MANCALA] * OYUNCU_BASI_KUYU_SAYISI_MANCALA + [0],
            "mevcut_oyuncu": 1, "oyun_basladi": False, "oyun_bitti": False, "oyuncu_adi": current_oyuncu_adi, "cok_oyunculu": False, "sunucu_mu": None,
            "istemci_soketi": None, "oyuncular": [], "skorlar": [], "sira_mesaji": "1. Oyuncunun Sırası", "kazanan": None, "secilen_kuyu": None,
            "zorluk_seviyesi": current_zorluk, "egitim_modu": False, "oyuncu_istatistikleri": {"puan": 0, "hamleler": [], "sureler": []},
        })
        
        if oyuncu_adi_girdi_mancala.current: oyuncu_adi_girdi_mancala.current.value = current_oyuncu_adi
        if sunucu_adresi_girdi_mancala.current: 
            try: sunucu_adresi_girdi_mancala.current.value = f"{socket.gethostbyname(socket.gethostname())}:{SUNUCU_PORTU_MANCALA}"
            except socket.gaierror: sunucu_adresi_girdi_mancala.current.value = f"127.0.0.1:{SUNUCU_PORTU_MANCALA}"
        
        # Eğer sadece Mancala'nın ana menüsüne dönülecekse
        if to_mancala_menu:
             oyun_durumu_mancala["oyuncu_adi"] = ""
             if oyuncu_adi_girdi_mancala.current: oyuncu_adi_girdi_mancala.current.value = ""
        
        arayuz_guncelle_mancala()

    def geri_cik_tiklama_mancala(e):
        current_oyuncu_adi = oyun_durumu_mancala["oyuncu_adi"]
        
        # Eğer bir oyun içindeysek veya bittiyse, Mancala'nın kendi ana menüsüne dön
        if oyun_durumu_mancala["oyun_basladi"] or oyun_durumu_mancala["oyun_bitti"]:
            yeniden_baslat_tiklama_mancala(e, True)
        # Eğer çok oyunculu bir menüdeysek, bir üst menüye (çok oyunculu seçenekleri) dön
        elif (sunucu_olustur_konteyneri_mancala.current and sunucu_olustur_konteyneri_mancala.current.visible) or \
             (sunucu_baglan_konteyneri_mancala.current and sunucu_baglan_konteyneri_mancala.current.visible):
            oyun_durumu_mancala["sunucu_mu"] = None
            arayuz_guncelle_mancala()
        # Eğer tek/çok oyunculu seçim ekranındaysak, oyuncu adı girme ekranına dön
        elif (tek_oyunculu_secim_konteyneri_mancala.current and tek_oyunculu_secim_konteyneri_mancala.current.visible) or \
             (cok_oyunculu_secim_konteyneri_mancala.current and cok_oyunculu_secim_konteyneri_mancala.current.visible):
            oyun_durumu_mancala["oyuncu_adi"] = ""
            oyun_durumu_mancala["cok_oyunculu"] = False
            oyun_durumu_mancala["sunucu_mu"] = None
            if oyuncu_adi_girdi_mancala.current: oyuncu_adi_girdi_mancala.current.value = ""
            arayuz_guncelle_mancala()
        else:
             go_to_main_menu_mancala()

    def sunucu_olustur_fonksiyonu_mancala():
        sunucu_soketi = socket.socket(socket.AF_INET, socket.SOCK_STREAM); sunucu_soketi.settimeout(1.0) 
        try:
            sunucu_soketi.bind(("0.0.0.0", SUNUCU_PORTU_MANCALA)); sunucu_soketi.listen(1) 
            oyun_durumu_mancala["oyuncular"] = [{"ad": oyun_durumu_mancala["oyuncu_adi"], "soket": None, "id": 1}] 
            try: _temp_sunucu_adresi_mancala.current = f"Sunucu Adresi: {socket.gethostbyname(socket.gethostname())}:{SUNUCU_PORTU_MANCALA}"
            except socket.gaierror: _temp_sunucu_adresi_mancala.current = f"Sunucu Adresi: 127.0.0.1:{SUNUCU_PORTU_MANCALA}"
            _temp_baglanan_oyuncular_mancala.current = f"Bağlanan Oyuncular: {oyun_durumu_mancala['oyuncu_adi']}"
            _temp_oyun_baslat_disabled_mancala.current = True; arayuz_guncelle_mancala()
            
            client_socket_local = None 
            while not oyun_durumu_mancala.get("oyun_basladi") and oyun_durumu_mancala.get("sunucu_mu") is True and len(oyun_durumu_mancala.get("oyuncular", [])) < 2:
                try:
                    readable, _, _ = select.select([sunucu_soketi], [], [], 1.0)
                    if readable:
                        client_socket_local, client_address = sunucu_soketi.accept()
                        veri = client_socket_local.recv(1024).decode(); mesaj = json.loads(veri)
                        if mesaj["tip"] == "baglan":
                            if len(oyun_durumu_mancala.get("oyuncular", [])) < 2:
                                oyuncu2_data = {"ad": mesaj["ad"], "soket": client_socket_local, "id": 2}
                                oyun_durumu_mancala["oyuncular"].append(oyuncu2_data)
                                _temp_baglanan_oyuncular_mancala.current = f"Bağlanan Oyuncular: {', '.join(p['ad'] for p in oyun_durumu_mancala['oyuncular'])}"
                                _temp_oyun_baslat_disabled_mancala.current = False; arayuz_guncelle_mancala()
                                client_socket_local.send(json.dumps({"tip": "baglandi", "mesaj": "Sunucuya başarıyla bağlandınız.", "oyuncu_no": 2, "oyuncular": [{"ad": p["ad"]} for p in oyun_durumu_mancala["oyuncular"]] }).encode())
                            else: client_socket_local.send(json.dumps({"tip": "hata", "mesaj": "Sunucu dolu."}).encode()); client_socket_local.close()
                        else: client_socket_local.close()
                except socket.timeout:
                    if not oyun_durumu_mancala.get("sunucu_mu"): break 
                    continue 
                except Exception as e: print(f"Mancala İstemci kabul hatası: {e}"); break 
            
            target_client_socket = None
            if len(oyun_durumu_mancala.get("oyuncular", [])) > 1 and oyun_durumu_mancala["oyuncular"][1].get("soket"):
                target_client_socket = oyun_durumu_mancala["oyuncular"][1]["soket"]
            
            while oyun_durumu_mancala.get("oyun_basladi") and target_client_socket and oyun_durumu_mancala.get("sunucu_mu") is True:
                try:
                    readable, _, _ = select.select([target_client_socket], [], [], 0.1) 
                    if not oyun_durumu_mancala.get("sunucu_mu"): break 
                    if readable:
                        veri = target_client_socket.recv(1024).decode()
                        if not veri: 
                            if not oyun_durumu_mancala.get("oyun_bitti", False): 
                                oyun_durumu_mancala["sira_mesaji"] = "Rakip ayrıldı! Oyun bitti."
                                oyun_durumu_mancala["kazanan"] = oyun_durumu_mancala["oyuncular"][0]["ad"] if len(oyun_durumu_mancala.get("oyuncular",[])) > 0 else "Sunucu"
                                oyunu_bitir_mancala()
                            break
                        mesaj = json.loads(veri)
                        if mesaj["tip"] == "hamle":
                            if oyun_durumu_mancala["mevcut_oyuncu"] == mesaj.get("oyuncu_no") and mesaj.get("oyuncu_no") == 2: taslari_dagit_mancala(mesaj["kuyu"])
                except (ConnectionResetError, BrokenPipeError):
                    if not oyun_durumu_mancala.get("oyun_bitti", False): 
                        oyun_durumu_mancala["sira_mesaji"] = "Rakip bağlantısı kesildi! Oyun bitti."
                        oyun_durumu_mancala["kazanan"] = oyun_durumu_mancala["oyuncular"][0]["ad"] if len(oyun_durumu_mancala.get("oyuncular",[])) > 0 else "Sunucu"
                        oyunu_bitir_mancala()
                    break
                except Exception as e: print(f"Mancala Sunucu istemci dinleme hatası: {e}"); break
        except Exception as e:
            _temp_feedback_mancala.current = f"Sunucu hatası: {e}"; arayuz_guncelle_mancala()
        finally:
            if len(oyun_durumu_mancala.get("oyuncular", [])) > 1 and oyun_durumu_mancala["oyuncular"][1].get("soket"):
                try: oyun_durumu_mancala["oyuncular"][1]["soket"].close(); oyun_durumu_mancala["oyuncular"][1]["soket"] = None
                except: pass
            try: sunucu_soketi.close()
            except: pass

    def sunucuya_baglan_fonksiyonu_mancala(adres, port):
        istemci_soketi = socket.socket(socket.AF_INET, socket.SOCK_STREAM); istemci_soketi.settimeout(5.0)
        try:
            istemci_soketi.connect((adres, port)); oyun_durumu_mancala["istemci_soketi"] = istemci_soketi 
            istemci_soketi.send(json.dumps({"tip": "baglan", "ad": oyun_durumu_mancala["oyuncu_adi"]}).encode())
            veri = istemci_soketi.recv(1024).decode(); yanit = json.loads(veri)
            if yanit["tip"] == "baglandi":
                oyun_durumu_mancala["oyuncular"] = yanit.get("oyuncular", []) 
                _temp_feedback_mancala.current = yanit["mesaj"] + " Oyunun başlaması bekleniyor..."
                _temp_is_connected_mancala.current = True
                threading.Thread(target=istemci_dinle_fonksiyonu_mancala, daemon=True).start()
            else:_temp_feedback_mancala.current = f"Bağlantı hatası: {yanit.get('mesaj', 'Bilinmeyen sunucu yanıtı.')}"
            arayuz_guncelle_mancala()
        except socket.timeout: _temp_feedback_mancala.current = "Sunucuya bağlanırken zaman aşımı!"; arayuz_guncelle_mancala()
        except ConnectionRefusedError: _temp_feedback_mancala.current = "Sunucu bağlantıyı reddetti."; arayuz_guncelle_mancala()
        except Exception as e: _temp_feedback_mancala.current = f"Bağlantı hatası: {str(e)}"; arayuz_guncelle_mancala()

    def istemci_dinle_fonksiyonu_mancala():
        soket = oyun_durumu_mancala.get("istemci_soketi")
        if not soket: return
        try:
            while soket and (not oyun_durumu_mancala.get("oyun_bitti") or oyun_durumu_mancala.get("oyun_basladi")): 
                if not oyun_durumu_mancala.get("istemci_soketi"): break 
                readable, _, _ = select.select([soket], [], [], 0.2) 
                if not oyun_durumu_mancala.get("istemci_soketi"): break
                if readable:
                    veri = soket.recv(1024).decode()
                    if not veri:
                        if not oyun_durumu_mancala.get("oyun_bitti", False): 
                            oyun_durumu_mancala["sira_mesaji"] = "Sunucuyla bağlantı kesildi! Oyun bitti."
                            oyun_durumu_mancala["kazanan"] = oyun_durumu_mancala["oyuncular"][0]["ad"] if len(oyun_durumu_mancala.get("oyuncular",[])) > 0 else "Sunucu"
                            oyunu_bitir_mancala()
                        break
                    mesaj = json.loads(veri)
                    if mesaj["tip"] == "baslat":
                        oyun_durumu_mancala["oyuncular"] = mesaj.get("oyuncular", oyun_durumu_mancala.get("oyuncular", []))
                        oyun_durumu_mancala["oyun_basladi"] = True; tahta_baslat_mancala()
                    elif mesaj["tip"] == "hamle":
                        if oyun_durumu_mancala["mevcut_oyuncu"] == mesaj.get("oyuncu_no") and mesaj.get("oyuncu_no") == 1: taslari_dagit_mancala(mesaj["kuyu"])
                    elif mesaj["tip"] == "oyun_bitti":
                        oyun_durumu_mancala["kazanan"] = mesaj.get("kazanan")
                        oyun_durumu_mancala["skorlar"] = mesaj.get("skorlar", [])
                        oyun_durumu_mancala["tahta"] = mesaj.get("tahta", oyun_durumu_mancala["tahta"]); oyun_durumu_mancala["oyun_bitti"] = True
                        oyun_durumu_mancala["oyun_basladi"] = False; arayuz_guncelle_mancala(); break 
                    elif mesaj["tip"] == "hata": _temp_feedback_mancala.current = f"Sunucudan hata: {mesaj.get('mesaj')}"; arayuz_guncelle_mancala()
                if oyun_durumu_mancala.get("oyun_bitti"): break
        except (ConnectionResetError, BrokenPipeError):
            if not oyun_durumu_mancala.get("oyun_bitti", False): 
                oyun_durumu_mancala["sira_mesaji"] = "Sunucuyla bağlantı koptu! Oyun bitti."
                oyun_durumu_mancala["kazanan"] = oyun_durumu_mancala["oyuncular"][0]["ad"] if len(oyun_durumu_mancala.get("oyuncular",[])) > 0 else "Sunucu"
                oyunu_bitir_mancala()
        except Exception as e: print(f"Mancala İstemci dinleme hatası: {e}")
        finally:
            if oyun_durumu_mancala.get("istemci_soketi"): 
                try: oyun_durumu_mancala["istemci_soketi"].close()
                except: pass
            oyun_durumu_mancala["istemci_soketi"] = None
            if not oyun_durumu_mancala.get("oyun_bitti"): arayuz_guncelle_mancala() 

    def bitis_ekrani_olustur_mancala():
        oyuncu1_hazine_indeksi = OYUNCU_BASI_KUYU_SAYISI_MANCALA; oyuncu2_hazine_indeksi = 2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1
        oyuncu1_skor = oyun_durumu_mancala["tahta"][oyuncu1_hazine_indeksi]; oyuncu2_skor = oyun_durumu_mancala["tahta"][oyuncu2_hazine_indeksi]
        oyuncu1_ad = "Oyuncu 1"; oyuncu2_ad = "Oyuncu 2"
        if oyun_durumu_mancala["cok_oyunculu"]:
            if len(oyun_durumu_mancala.get("oyuncular",[])) > 0: oyuncu1_ad = oyun_durumu_mancala["oyuncular"][0]["ad"]
            if len(oyun_durumu_mancala.get("oyuncular",[])) > 1: oyuncu2_ad = oyun_durumu_mancala["oyuncular"][1]["ad"]
        else: oyuncu1_ad = oyun_durumu_mancala.get("oyuncu_adi", "Oyuncu 1"); oyuncu2_ad = "Yapay Zeka"
        bitis_ekrani_elemanlari = [
            ft.Text("Oyun Bitti!", size=24, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_HEADING, text_align=ft.TextAlign.CENTER),
            ft.Text(f"Kazanan: {oyun_durumu_mancala.get('kazanan', 'Bilinmiyor')}", size=20, weight=ft.FontWeight.BOLD, color=(ft.colors.GREEN_700 if oyun_durumu_mancala.get('kazanan') != "Berabere" and oyun_durumu_mancala.get('kazanan') is not None else ft.colors.BLUE_600), text_align=ft.TextAlign.CENTER),
            ft.Text(f"{oyuncu1_ad}: {oyuncu1_skor} puan", size=16, color=ft.colors.BLACK, text_align=ft.TextAlign.CENTER),
            ft.Text(f"{oyuncu2_ad}: {oyuncu2_skor} puan", size=16, color=ft.colors.BLACK, text_align=ft.TextAlign.CENTER),
        ]
        if "egitim_modu_bitti" in oyun_durumu_mancala and oyun_durumu_mancala["egitim_modu_bitti"]: 
            istat = oyun_durumu_mancala["oyuncu_istatistikleri"]; toplam_puan_egitim = istat["puan"]
            hamle_sayisi = len(istat["hamleler"]); ortalama_sure_str = "N/A"
            if istat["sureler"] and len(istat["sureler"]) > 0:
                ortalama_sure = sum(istat["sureler"]) / len(istat["sureler"]); ortalama_sure_str = f"{ortalama_sure:.2f} saniye"
            ortalama_hamle_puani_str = "N/A"
            if istat["hamleler"]:
                ortalama_hp = sum(h["puan"] for h in istat["hamleler"]) / len(istat["hamleler"]) if istat["hamleler"] else 0
                ortalama_hamle_puani_str = f"{ortalama_hp:.2f}"

            bitis_ekrani_elemanlari.extend([
                ft.Container(content=ft.Text("Eğitim Modu İstatistikleri:", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_600, text_align=ft.TextAlign.CENTER), margin=ft.margin.only(top=10)),
                ft.Text(f"Aldığınız Puan: {toplam_puan_egitim}", size=16, color=ft.colors.BLACK, text_align=ft.TextAlign.CENTER),
                ft.Text(f"Hamle Sayısı: {hamle_sayisi}", size=16, color=ft.colors.BLACK, text_align=ft.TextAlign.CENTER),
                ft.Text(f"Ortalama Hamle Süresi: {ortalama_sure_str}", size=16, color=ft.colors.BLACK, text_align=ft.TextAlign.CENTER),
                ft.Text(f"Ortalama Hamle Puanı: {ortalama_hamle_puani_str}", size=16, color=ft.colors.BLACK, text_align=ft.TextAlign.CENTER),
                ft.Text(f"Bu test oyunu sonrası YZ zorluk seviyesi: {oyun_durumu_mancala['zorluk_seviyesi']}", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_700, text_align=ft.TextAlign.CENTER),
            ])
        bitis_ekrani_elemanlari.append(ft.Container(content=ft.ElevatedButton(text="Ana Menüye Dön", on_click=lambda e: go_to_main_menu_mancala(), bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.HOME), margin=ft.margin.only(top=20)))
        return ft.Column(bitis_ekrani_elemanlari, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)

    def tas_create_mancala(): return ft.Container(width=16, height=16, bgcolor=RENK_TAS_MANCALA, border_radius=8, alignment=ft.alignment.center)
    def tahta_duzeni_olustur_mancala():
        kuyu_kontrolleri = []; tahta_listesi = oyun_durumu_mancala.get("tahta", [])
        if not tahta_listesi: return ft.Text("Tahta yükleniyor...")
        for i in range(2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 2):
            taslar = tahta_listesi[i]; tas_duzeni_controls = []
            if taslar > 0:
                for _ in range(min(taslar, 15)): tas_duzeni_controls.append(tas_create_mancala())
            tas_duzeni = ft.GridView(runs_count=3, max_extent=20, child_aspect_ratio=1.0, spacing=2, run_spacing=2, controls=tas_duzeni_controls, height=60 if taslar > 0 else 20, width=60 if taslar > 0 else 20)
            kuyu_icerik_listesi = []; kuyu_adi_text = ""
            oyuncu1_adi_tahta = "Oyuncu 1"; oyuncu2_adi_tahta = "Oyuncu 2 (YZ)"
            if oyun_durumu_mancala.get("cok_oyunculu"):
                if len(oyun_durumu_mancala.get("oyuncular", [])) > 0: oyuncu1_adi_tahta = oyun_durumu_mancala["oyuncular"][0]["ad"]
                if len(oyun_durumu_mancala.get("oyuncular", [])) > 1: oyuncu2_adi_tahta = oyun_durumu_mancala["oyuncular"][1]["ad"]
            else: oyuncu1_adi_tahta = oyun_durumu_mancala.get("oyuncu_adi", "Oyuncu 1"); oyuncu2_adi_tahta = "Yapay Zeka"
            if i == OYUNCU_BASI_KUYU_SAYISI_MANCALA: 
                kuyu_adi_text = f"{oyuncu1_adi_tahta} Hazine"
                kuyu_icerik_listesi.extend([ft.Text(kuyu_adi_text, size=14, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE, text_align=ft.TextAlign.CENTER), tas_duzeni, ft.Text(f"{taslar}", size=16, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD)])
                kuyu_kontrolleri.append(ft.Container(content=ft.Column(kuyu_icerik_listesi, alignment=ft.MainAxisAlignment.SPACE_AROUND, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5), width=150, height=200, bgcolor=RENK_HAZINE_1_MANCALA, border_radius=10, padding=10))
            elif i == 2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1: 
                kuyu_adi_text = f"{oyuncu2_adi_tahta} Hazine"
                kuyu_icerik_listesi.extend([ft.Text(kuyu_adi_text, size=14, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE, text_align=ft.TextAlign.CENTER), tas_duzeni, ft.Text(f"{taslar}", size=16, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD)])
                kuyu_kontrolleri.append(ft.Container(content=ft.Column(kuyu_icerik_listesi, alignment=ft.MainAxisAlignment.SPACE_AROUND, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5), width=150, height=200, bgcolor=RENK_HAZINE_2_MANCALA, border_radius=10, padding=10))
            else: 
                kuyu_disabled_durumu = not gecerli_hamle_mi_mancala(i) or oyun_durumu_mancala["oyun_bitti"]
                kuyu_icerik_listesi.extend([tas_duzeni, ft.Text(f"{taslar}", size=14, color=ft.colors.BLACK87)])
                kuyu_kontrolleri.append(
                    ft.Container(
                        content=ft.Column(kuyu_icerik_listesi, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3),
                        width=80, height=100, bgcolor=RENK_KUYU_MANCALA, 
                        border=ft.border.all(3, RENK_SECILI_KUYU_BORDER_MANCALA if oyun_durumu_mancala["secilen_kuyu"] == i else RENK_NORMAL_KUYU_BORDER_MANCALA), 
                        border_radius=10, padding=5, on_click=kuyu_tiklama_mancala(i) if not kuyu_disabled_durumu else None, 
                        disabled=kuyu_disabled_durumu, opacity=0.5 if kuyu_disabled_durumu and tahta_listesi[i] > 0 else 1.0 
                    )
                )
        ust_sira_kuyular = [kuyu_kontrolleri[i] for i in range(2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA, OYUNCU_BASI_KUYU_SAYISI_MANCALA, -1)] 
        alt_sira_kuyular = [kuyu_kontrolleri[i] for i in range(0, OYUNCU_BASI_KUYU_SAYISI_MANCALA)] 
        oyuncu1_hazine_ui = kuyu_kontrolleri[OYUNCU_BASI_KUYU_SAYISI_MANCALA]; oyuncu2_hazine_ui = kuyu_kontrolleri[2 * OYUNCU_BASI_KUYU_SAYISI_MANCALA + 1]
        hazineler_arasi_bosluk_genisligi = max(0, (OYUNCU_BASI_KUYU_SAYISI_MANCALA * (80+10)) - (150+150+20) )
        return ft.Column(
            [
                ft.Row(ust_sira_kuyular, alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                ft.Row([oyuncu2_hazine_ui, ft.Container(width=hazineler_arasi_bosluk_genisligi), oyuncu1_hazine_ui], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ft.Row(alt_sira_kuyular, alignment=ft.MainAxisAlignment.CENTER, spacing=10)
            ],
            alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15 
        )

    # Mancala Arayüz Kurulumu
    default_server_address = f"127.0.0.1:{SUNUCU_PORTU_MANCALA}"
    try: default_server_address = f"{socket.gethostbyname(socket.gethostname())}:{SUNUCU_PORTU_MANCALA}"
    except socket.gaierror: pass 

    mod_secim_konteyneri_mancala.current = ft.Container(
        content=ft.Column(
            [
                ft.Text("Mancala Oyunu", size=40, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_HEADING, text_align=ft.TextAlign.CENTER),
                ft.TextField(label="Oyuncu Adı", ref=oyuncu_adi_girdi_mancala, width=300, bgcolor=ft.colors.WHITE, border_color=ft.colors.BLUE_200, border_radius=10),
                ft.ElevatedButton(text="Tek Oyunculu", on_click=tek_oyunculu_sec_mancala, bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, width=300, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.PERSON),
                ft.ElevatedButton(text="Çok Oyunculu", on_click=cok_oyunculu_sec_mancala, bgcolor=BUTTON_SECONDARY_COLOR, color=BUTTON_TEXT_COLOR, width=300, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.PEOPLE),
                ft.ElevatedButton("Tüm Oyunlar Menüsü", on_click=go_to_master_menu_func, bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, width=300, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.MENU)
            ],
            alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20
        ),
        padding=20, border_radius=20, alignment=ft.alignment.center, visible=False,
        width=600, shadow=ft.BoxShadow(spread_radius=1,blur_radius=15,color=ft.colors.BLUE_GREY_300,offset=ft.Offset(0, 0),blur_style=ft.ShadowBlurStyle.OUTER)
    )
    tek_oyunculu_secim_konteyneri_mancala.current = ft.Container(
        content=ft.Column(
            [
                ft.Text("Tek Oyunculu Mod", size=36, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_HEADING, text_align=ft.TextAlign.CENTER),
                ft.Text(value=f"Mevcut YZ Zorluk Seviyesi: {oyun_durumu_mancala['zorluk_seviyesi']}", size=18, color=ft.colors.BLACK, text_align=ft.TextAlign.CENTER),
                ft.ElevatedButton(text="Oyunu Başlat", on_click=oyun_baslat_tek_mancala, bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, width=300, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.PLAY_ARROW),
                ft.ElevatedButton(text="YZ Zorluk Ayarı (Eğitim Modu)", on_click=zorluk_ayarla_baslat_mancala, bgcolor=BUTTON_TERTIARY_COLOR, color=BUTTON_TEXT_COLOR, width=300, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.MODEL_TRAINING),
                ft.ElevatedButton(text="Ana Menüye Dön", on_click=go_to_main_menu_mancala, bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, width=300, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.ARROW_BACK)
            ],
            alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20
        ),
        padding=20, border_radius=20, alignment=ft.alignment.center, visible=False,
        width=600, shadow=ft.BoxShadow(spread_radius=1,blur_radius=15,color=ft.colors.BLUE_GREY_300,offset=ft.Offset(0, 0),blur_style=ft.ShadowBlurStyle.OUTER)
    )
    cok_oyunculu_secim_konteyneri_mancala.current = ft.Container(
        content=ft.Column(
            [
                ft.Text("Çok Oyunculu Mod", size=36, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_HEADING, text_align=ft.TextAlign.CENTER),
                ft.ElevatedButton(text="Sunucu Oluştur", on_click=sunucu_olustur_secim_ekranindan_mancala, bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, width=300, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.DNS),
                ft.ElevatedButton(text="Sunucuya Bağlan", on_click=sunucuya_baglan_secim_ekranindan_mancala, bgcolor=BUTTON_SECONDARY_COLOR, color=BUTTON_TEXT_COLOR, width=300, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.LINK),
                ft.ElevatedButton(text="Ana Menüye Dön", on_click=go_to_main_menu_mancala, bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, width=300, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.ARROW_BACK)
            ],
            alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=25
        ),
        padding=20, border_radius=20, alignment=ft.alignment.center, visible=False,
        width=600, shadow=ft.BoxShadow(spread_radius=1,blur_radius=15,color=ft.colors.BLUE_GREY_300,offset=ft.Offset(0, 0),blur_style=ft.ShadowBlurStyle.OUTER)
    )
    sunucu_olustur_konteyneri_mancala.current = ft.Container(
        content=ft.Column(
            [
                ft.Text("Sunucu Kurulumu", size=36, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_HEADING),
                ft.Text("", ref=sunucu_adresi_goster_mancala, size=18, color=ft.colors.BLACK, text_align=ft.TextAlign.CENTER, selectable=True),
                ft.Text("Oyuncular bekleniyor...", ref=baglanan_oyuncular_goster_mancala, size=16, color=ft.colors.BLACK, text_align=ft.TextAlign.CENTER),
                ft.ElevatedButton(text="Oyunu Başlat", ref=oyun_baslat_buton_mancala, on_click=oyun_baslat_cok_oyunculu_mancala, bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, width=300, height=50, disabled=True, style=STADIUM_BUTTON_STYLE, icon=ft.icons.PLAY_ARROW),
                ft.ElevatedButton(text="Geri", on_click=geri_cik_tiklama_mancala, bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, width=300, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.ARROW_BACK)
            ],
            alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=25
        ),
        padding=20, border_radius=20, alignment=ft.alignment.center, visible=False,
        width=600, shadow=ft.BoxShadow(spread_radius=1,blur_radius=15,color=ft.colors.BLUE_GREY_300,offset=ft.Offset(0, 0),blur_style=ft.ShadowBlurStyle.OUTER)
    )
    sunucu_baglan_konteyneri_mancala.current = ft.Container(
        content=ft.Column(
            [
                ft.Text("Sunucuya Bağlan", size=36, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_HEADING),
                ft.TextField(label="Sunucu Adresi (IP:Port)", ref=sunucu_adresi_girdi_mancala, width=300, value=default_server_address, bgcolor=ft.colors.WHITE, border_color=ft.colors.BLUE_200, border_radius=10),
                ft.ElevatedButton(text="Bağlan", on_click=sunucuya_baglan_asıl_mancala, bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, width=300, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.LOGIN),
                ft.ElevatedButton(text="Geri", on_click=geri_cik_tiklama_mancala, bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, width=300, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.ARROW_BACK)
            ],
            alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=25
        ),
        padding=20, border_radius=20, alignment=ft.alignment.center, visible=False,
        width=600, shadow=ft.BoxShadow(spread_radius=1,blur_radius=15,color=ft.colors.BLUE_GREY_300,offset=ft.Offset(0, 0),blur_style=ft.ShadowBlurStyle.OUTER)
    )

    tahta_konteyneri_mancala.current = ft.Container(content=ft.Text("Oyun yükleniyor..."), padding=ft.padding.symmetric(vertical=10), border_radius=10, visible=False, alignment=ft.alignment.center)
    geri_bildirim_goster_mancala.current = ft.Text("...", size=18, color=ft.colors.BLUE_GREY_800, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.W_500, visible=True)
    
    hamle_onayla_buton_mancala.current = ft.ElevatedButton(text="Hamleyi Onayla", on_click=hamle_onayla_mancala, bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, width=220, height=50, style=STADIUM_BUTTON_STYLE, disabled=True, icon=ft.icons.CHECK_CIRCLE)
    
    oyun_kontrol_butonlari_konteyneri_mancala.current = ft.Container(
        content=ft.Row(
            [
                hamle_onayla_buton_mancala.current,
                ft.ElevatedButton(text="Oyundan Çık", on_click=geri_cik_tiklama_mancala, bgcolor=BUTTON_DANGER_COLOR, color=BUTTON_TEXT_COLOR, width=220, height=50, style=STADIUM_BUTTON_STYLE, icon=ft.icons.EXIT_TO_APP)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        ),
        padding=ft.padding.symmetric(vertical=10),
        alignment=ft.alignment.center,
        visible=False 
    )

    lider_tablosu_konteyneri_mancala.current = ft.Container(content=ft.Text(""), padding=10, border_radius=10, visible=False, alignment=ft.alignment.center)
    bitis_ekrani_konteyneri_mancala.current = ft.Container(content=ft.Text(""), padding=20, border_radius=20, alignment=ft.alignment.center, visible=False, width=600, shadow=ft.BoxShadow(spread_radius=1,blur_radius=15,color=ft.colors.BLUE_GREY_300,offset=ft.Offset(0, 0),blur_style=ft.ShadowBlurStyle.OUTER))

    ana_sutun = ft.Column(
            [
                mod_secim_konteyneri_mancala.current,
                tek_oyunculu_secim_konteyneri_mancala.current,
                cok_oyunculu_secim_konteyneri_mancala.current,
                sunucu_olustur_konteyneri_mancala.current,
                sunucu_baglan_konteyneri_mancala.current,
                tahta_konteyneri_mancala.current,
                bitis_ekrani_konteyneri_mancala.current,
                lider_tablosu_konteyneri_mancala.current, 
                geri_bildirim_goster_mancala.current,
                oyun_kontrol_butonlari_konteyneri_mancala.current 
            ],
            alignment=ft.MainAxisAlignment.CENTER, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.ADAPTIVE, 
            expand=True, 
            spacing=15 
        )
    
    sayfa.add(
        ft.Container(
            content=ana_sutun,
            expand=True,
            alignment=ft.alignment.center,
            padding=10 
        )
    )
    
    # Mancala oyununa ilk girişte ana menüyü göster
    yeniden_baslat_tiklama_mancala(None, True)

# ===================================================================================
# =============================== MANCALA OYUN KODU BİTİŞ ===============================
# ===================================================================================



# ===================================================================================
# ================================= NIM OYUN KODU BAŞLANGIÇ =================================
# ===================================================================================

# --- Nim Oyun Sabitleri ---
CORRECT_MOVE_SCORE_NIM = 10
FINISH_GAME_BONUS_NIM = CORRECT_MOVE_SCORE_NIM * 2
PENALTY_SCORE_NIM = -5
MAX_SELECT_FROM_PILE_NIM = 3
MIN_PILES_NIM = 3
MAX_PILES_NIM = 5
MIN_STONES_PER_PILE_NIM = 3
MAX_STONES_PER_PILE_NIM = 7
CALIBRATION_GAME_PILES_NIM = [3, 4, 5]

# --- Nim Ağ Sabitleri ---
DEFAULT_PORT_NIM = 12349
BUFFER_SIZE_NIM = 1024

# --- Nim Oyun Durumu ---
game_state_nim = {
    "piles": [],
    "current_player": 1,
    "selected_stones_ui": set(),  
    "scores": {"Player 1": 0, "Player 2": 0, "AI": 0},
    "game_mode": None, 
    "game_over": False,
    "winner": None,
    "my_player_number": 1,
    "ai_thinking": False,
    "ai_difficulty": "standart",
    "calibration_optimal_moves": 0,
    "calibration_player_moves": 0,
    "game_mode_before_end": None,
}

# --- Nim Ağ Bağlantı Değişkenleri ---
server_socket_nim = None
client_socket_nim = None
connection_nim = None
client_thread_nim = None
server_thread_nim = None
local_ip_address_for_display_nim = "Bilinmiyor"

# --- Nim Ana Fonksiyonu ---
def main_nim(page: ft.Page, go_to_master_menu_func):
    page.title = "Gelişmiş Nim Oyunu"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    
    page.window_width = 800
    page.window_height = 750
    page.bgcolor = PAGE_BG_COLOR

    # --- Flet Kontrolleri Referansları (Nim) ---
    piles_container_ref_nim = ft.Ref[ft.Row]()
    turn_indicator_ref_nim = ft.Ref[ft.Text]()
    score_display_p1_ref_nim = ft.Ref[ft.Text]()
    score_display_p2_ai_ref_nim = ft.Ref[ft.Text]()
    confirm_button_ref_nim = ft.Ref[ft.ElevatedButton]()
    feedback_text_ref_nim = ft.Ref[ft.Text]()

    game_area_view_ref_nim = ft.Ref[ft.Column]()
    main_menu_view_ref_nim = ft.Ref[ft.Column]()
    multiplayer_options_view_ref_nim = ft.Ref[ft.Column]()
    server_info_view_ref_nim = ft.Ref[ft.Column]()
    client_connect_view_ref_nim = ft.Ref[ft.Column]()
    end_game_view_ref_nim = ft.Ref[ft.Column]()
    setting_level_view_ref_nim = ft.Ref[ft.Column]()

    end_game_winner_text_ref_nim = ft.Ref[ft.Text]()
    end_game_score_text_ref_nim = ft.Ref[ft.Text]()

    server_ip_text_ref_nim = ft.Ref[ft.Text]()
    start_multiplayer_game_button_host_ref_nim = ft.Ref[ft.ElevatedButton]()
    server_ip_input_ref_nim = ft.Ref[ft.TextField]()
    client_status_text_ref_nim = ft.Ref[ft.Text]()
    connect_button_client_ref_nim = ft.Ref[ft.ElevatedButton]()

    def update_ui_scores_nim():
        if not page.client_storage: return
        if score_display_p1_ref_nim.current:
            score_display_p1_ref_nim.current.value = f"Oyuncu 1: {game_state_nim['scores']['Player 1']}"
        if score_display_p2_ai_ref_nim.current:
            current_game_mode = game_state_nim.get("game_mode")
            ai_name = "Kalibrasyon YZ" if current_game_mode == "calibration_play" else "Yapay Zeka"
            if current_game_mode in ["single", "calibration_play"]:
                score_display_p2_ai_ref_nim.current.value = f"{ai_name}: {game_state_nim['scores']['AI']}"
            else:
                score_display_p2_ai_ref_nim.current.value = f"Oyuncu 2: {game_state_nim['scores']['Player 2']}"
        page.update()

    def update_ui_turn_indicator_nim():
        if not page.client_storage or not turn_indicator_ref_nim.current: return
        player_name = ""
        current_game_mode = game_state_nim.get("game_mode")
        if game_state_nim["current_player"] == 1:
            player_name = "Oyuncu 1"
        elif current_game_mode in ["single", "calibration_play"]:
            player_name = "Kalibrasyon YZ" if current_game_mode == "calibration_play" else "Yapay Zeka"
        else:
            player_name = "Oyuncu 2"
        
        turn_indicator_ref_nim.current.value = f"Sıra: {player_name}"
        if current_game_mode in ["single", "calibration_play"] and \
           game_state_nim["current_player"] == 2 and game_state_nim["ai_thinking"]:
            turn_indicator_ref_nim.current.value += " (Düşünüyor...)"
        page.update()

    def show_feedback_nim(message, is_error=False):
        if not page.client_storage or not feedback_text_ref_nim.current: return
        feedback_text_ref_nim.current.value = message
        feedback_text_ref_nim.current.color = ft.colors.RED if is_error else ft.colors.GREEN
        page.update()

    # DÜZELTME: Arayüz orijinal haline geri döndürüldü
    def render_piles_nim():
        if not page.client_storage or not piles_container_ref_nim.current: return
        piles_container_ref_nim.current.controls.clear()
        
        is_my_turn_or_single_player_human_turn = True
        current_game_mode = game_state_nim.get("game_mode")
        
        if current_game_mode in ["single", "calibration_play"]:
            is_my_turn_or_single_player_human_turn = game_state_nim["current_player"] == 1 and not game_state_nim["ai_thinking"]
        elif current_game_mode in ["multi_host", "multi_client"]:
            is_my_turn_or_single_player_human_turn = game_state_nim["current_player"] == game_state_nim["my_player_number"]
            
        disable_stones = game_state_nim["game_over"] or not is_my_turn_or_single_player_human_turn
        
        for i, pile_size in enumerate(game_state_nim["piles"]):
            pile_display_row = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=10
            )
            pile_label = ft.Text(f"Deste {i+1}:", weight=ft.FontWeight.BOLD, size=16)
            pile_display_row.controls.append(pile_label)
            stones_column = ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=1
            )
            for j in range(pile_size):
                is_selected = (i, j) in game_state_nim["selected_stones_ui"]
                stone = ft.IconButton(
                    icon=ft.icons.CIRCLE,
                    icon_color=ft.colors.GREEN if is_selected else ft.colors.RED,
                    icon_size=24,
                    tooltip=f"Deste {i+1}, Taş {j+1}",
                    data={"pile_idx": i, "stone_idx": j},
                    on_click=on_stone_click_nim,
                    disabled=disable_stones
                )
                stones_column.controls.append(stone)
            pile_display_row.controls.append(stones_column)
            piles_container_ref_nim.current.controls.append(pile_display_row)
            
        page.update()

    def reset_selected_stones_ui_nim():
        game_state_nim["selected_stones_ui"].clear()
        if confirm_button_ref_nim.current:
            confirm_button_ref_nim.current.disabled = True
        render_piles_nim() 
        
    def switch_player_nim():
        game_state_nim["current_player"] = 2 if game_state_nim["current_player"] == 1 else 1
        update_ui_turn_indicator_nim()
        reset_selected_stones_ui_nim() 

    def check_game_over_nim():
        current_game_mode = game_state_nim.get("game_mode")
        if all(p == 0 for p in game_state_nim["piles"]):
            game_state_nim["game_over"] = True
            winner_player_number = game_state_nim["current_player"]
            
            winner_name = ""
            if current_game_mode in ["single", "calibration_play"]:
                winner_name = "Player 1" if winner_player_number == 1 else "AI"
            else:
                winner_name = "Player 1" if winner_player_number == 1 else "Player 2"
            game_state_nim["winner"] = winner_name
            
            if current_game_mode != "calibration_play":
                game_state_nim["scores"][winner_name] += FINISH_GAME_BONUS_NIM
            
            if not page.client_storage: return True

            update_ui_scores_nim()
            
            if current_game_mode == "calibration_play":
                evaluate_calibration_performance_and_show_setting_level_screen_nim()
            else:
                display_winner_name = game_state_nim['winner']
                if display_winner_name == "AI": display_winner_name = "Yapay Zeka"
                end_game_winner_text_ref_nim.current.value = f"Oyun Bitti! Kazanan: {display_winner_name}"
                
                p1_score = game_state_nim['scores']['Player 1']
                p2_score_key = "AI" if current_game_mode == "single" else "Player 2"
                p2_score = game_state_nim['scores'][p2_score_key]
                p2_name = "Yapay Zeka" if current_game_mode == "single" else "Oyuncu 2"
                end_game_score_text_ref_nim.current.value = f"Skorlar:\nOyuncu 1: {p1_score}\n{p2_name}: {p2_score}"
                
                confirm_button_ref_nim.current.disabled = True
                
                if current_game_mode == "multi_host" and connection_nim:
                    send_data_to_peer_nim({"type": "game_over", "winner": game_state_nim["winner"], "scores": game_state_nim["scores"]})
                
                game_state_nim["game_mode_before_end"] = current_game_mode
                show_view_nim(end_game_view_ref_nim)
            return True
        return False

    def initialize_game_nim(is_main_game=True, network_piles=None):
        if is_main_game:
            current_mode = game_state_nim.get("game_mode")
            if current_mode not in ["multi_host", "multi_client"]:
                game_state_nim["game_mode"] = "single"
            
            game_state_nim["piles"] = network_piles if network_piles else [
                random.randint(MIN_STONES_PER_PILE_NIM, MAX_STONES_PER_PILE_NIM)
                for _ in range(random.randint(MIN_PILES_NIM, MAX_PILES_NIM))
            ]
            game_state_nim["current_player"] = random.choice([1, 2]) if not network_piles else 1
            game_state_nim["scores"] = {"Player 1": 0, "Player 2": 0, "AI": 0}
        else:
            game_state_nim["game_mode"] = "calibration_play"
            game_state_nim["piles"] = list(CALIBRATION_GAME_PILES_NIM)
            game_state_nim["current_player"] = 1
            game_state_nim["scores"] = {"Player 1": 0, "AI": 0, "Player 2": 0}
            game_state_nim["calibration_optimal_moves"] = 0
            game_state_nim["calibration_player_moves"] = 0

        game_state_nim["selected_stones_ui"].clear()
        game_state_nim["game_over"] = False
        game_state_nim["winner"] = None
        game_state_nim["ai_thinking"] = False
        
        update_ui_scores_nim()
        update_ui_turn_indicator_nim()
        
        show_view_nim(game_area_view_ref_nim)
        
        render_piles_nim()
        confirm_button_ref_nim.current.disabled = True
        
        if feedback_text_ref_nim.current:
            if is_main_game:
                feedback_text_ref_nim.current.value = f"Oyun Başladı! YZ Seviyesi: {game_state_nim['ai_difficulty']}"
            else:
                feedback_text_ref_nim.current.value = "Kalibrasyon Oyunu: Lütfen bir hamle yapın."
            feedback_text_ref_nim.current.color = ft.colors.BLUE_700
            
        page.update()

        if game_state_nim["current_player"] == 2 and not game_state_nim["game_over"] and \
           game_state_nim["game_mode"] in ["single", "calibration_play"]:
            game_state_nim["ai_thinking"] = True
            update_ui_turn_indicator_nim()
            render_piles_nim()
            threading.Thread(target=run_ai_move_background_nim, daemon=True).start()

    def on_stone_click_nim(e: ft.ControlEvent):
        pile_idx = e.control.data["pile_idx"]
        stone_idx = e.control.data["stone_idx"]
        current_game_mode = game_state_nim.get("game_mode")
        
        is_ai_turn = (current_game_mode in ["single", "calibration_play"] and game_state_nim["current_player"] == 2 and game_state_nim["ai_thinking"])
        is_opponent_turn_multi = (current_game_mode in ["multi_host", "multi_client"] and game_state_nim["current_player"] != game_state_nim["my_player_number"])

        if game_state_nim["game_over"] or is_ai_turn or is_opponent_turn_multi:
            return

        ui_key = (pile_idx, stone_idx)
        if ui_key in game_state_nim["selected_stones_ui"]:
            game_state_nim["selected_stones_ui"].remove(ui_key)
        else:
            current_selected_pile = -1
            if game_state_nim["selected_stones_ui"]:
                current_selected_pile = next(iter(game_state_nim["selected_stones_ui"]))[0]
            
            if current_selected_pile != -1 and pile_idx != current_selected_pile:
                show_feedback_nim(f"Sadece aynı desteden taş seçebilirsiniz! ({PENALTY_SCORE_NIM} Puan)", is_error=True)
                if current_game_mode != "calibration_play":
                    player_key = "Player 1" if game_state_nim["current_player"] == 1 else "Player 2"
                    game_state_nim["scores"][player_key] += PENALTY_SCORE_NIM
                    update_ui_scores_nim()
                reset_selected_stones_ui_nim()
                return
            
            count_from_this_pile = sum(1 for p_idx, _ in game_state_nim["selected_stones_ui"] if p_idx == pile_idx)
            if count_from_this_pile >= MAX_SELECT_FROM_PILE_NIM:
                show_feedback_nim(f"Bir desteden en fazla {MAX_SELECT_FROM_PILE_NIM} taş seçebilirsiniz! ({PENALTY_SCORE_NIM} Puan)", is_error=True)
                if current_game_mode != "calibration_play":
                    player_key = "Player 1" if game_state_nim["current_player"] == 1 else "Player 2"
                    game_state_nim["scores"][player_key] += PENALTY_SCORE_NIM
                    update_ui_scores_nim()
                return
            
            game_state_nim["selected_stones_ui"].add(ui_key)
        
        confirm_button_ref_nim.current.disabled = not game_state_nim["selected_stones_ui"]
        render_piles_nim()

    def apply_move_nim(pile_idx, num_to_remove, is_ai_move=False):
        if not (0 <= pile_idx < len(game_state_nim["piles"]) and 0 < num_to_remove <= game_state_nim["piles"][pile_idx]):
            show_feedback_nim("Geçersiz hamle denemesi!", is_error=True)
            return False
        
        game_state_nim["piles"][pile_idx] -= num_to_remove
        current_game_mode = game_state_nim.get("game_mode")
        
        player_key = "Player 1" if game_state_nim["current_player"] == 1 else ("AI" if current_game_mode in ["single", "calibration_play"] else "Player 2")
        
        if current_game_mode != "calibration_play":
            game_state_nim["scores"][player_key] += CORRECT_MOVE_SCORE_NIM
        
        if not page.client_storage: return False
        
        update_ui_scores_nim()
        
        game_ended = check_game_over_nim()
        
        if not game_ended:
            switch_player_nim()
            
            if game_state_nim["game_mode"] in ["single", "calibration_play"] and game_state_nim["current_player"] == 2:
                game_state_nim["ai_thinking"] = True
                update_ui_turn_indicator_nim()
                render_piles_nim()
                threading.Thread(target=run_ai_move_background_nim, daemon=True).start()
        
        return True

    def on_confirm_move_click_nim(e):
        if not game_state_nim["selected_stones_ui"] or game_state_nim["game_over"]: return
        
        p_idx_list = {p_idx for p_idx, _ in game_state_nim["selected_stones_ui"]}
        if len(p_idx_list) != 1:
            show_feedback_nim("Hata: Birden fazla desteden taş seçilmiş!", is_error=True)
            reset_selected_stones_ui_nim()
            return

        selected_pile_idx = p_idx_list.pop()
        num_selected = len(game_state_nim["selected_stones_ui"])
        current_game_mode = game_state_nim.get("game_mode")

        if current_game_mode == "calibration_play":
            temp_piles = list(game_state_nim["piles"])
            temp_piles[selected_pile_idx] -= num_selected
            if calculate_nim_sum_nim(temp_piles) == 0:
                game_state_nim["calibration_optimal_moves"] += 1
            game_state_nim["calibration_player_moves"] += 1
        
        if current_game_mode in ["multi_host", "multi_client"]:
            send_data_to_peer_nim({"type": "move", "pile_idx": selected_pile_idx, "num_removed": num_selected})
        
        apply_move_nim(selected_pile_idx, num_selected, is_ai_move=False)

    def calculate_nim_sum_nim(piles):
        nim_sum = 0
        for pile_size in piles:
            nim_sum ^= pile_size
        return nim_sum

    def ai_find_optimal_move_nim():
        current_piles = list(game_state_nim["piles"])
        nim_sum = calculate_nim_sum_nim(current_piles)
        
        if nim_sum != 0:
            for i, pile_size in enumerate(current_piles):
                if pile_size > 0:
                    target_size = pile_size ^ nim_sum
                    if target_size < pile_size:
                        num_to_remove = pile_size - target_size
                        if 1 <= num_to_remove <= MAX_SELECT_FROM_PILE_NIM:
                            return i, num_to_remove
        
        possible_moves = []
        for i, pile_size in enumerate(current_piles):
            if pile_size > 0:
                for k in range(1, min(pile_size, MAX_SELECT_FROM_PILE_NIM) + 1):
                    possible_moves.append((i, k))
        
        if not possible_moves: return None
        
        if game_state_nim.get("ai_difficulty") == "zor":
            for move in possible_moves:
                temp_piles = list(current_piles)
                temp_piles[move[0]] -= move[1]
                if calculate_nim_sum_nim(temp_piles) != 0:
                    return move
            return random.choice(possible_moves)
        else:
            return random.choice(possible_moves)

    # DÜZELTME: page.run_thread kaldırıldı.
    def run_ai_move_background_nim():
        time.sleep(random.uniform(0.5, 1.5))
        move = ai_find_optimal_move_nim()
        
        def ui_thread_task():
            if not page.client_storage: return 
            if move:
                apply_move_nim(move[0], move[1], is_ai_move=True)
            else:
                show_feedback_nim("AI hamle bulamadı, oyun durumu kontrol ediliyor.", is_error=True)
                check_game_over_nim()
            game_state_nim["ai_thinking"] = False
            update_ui_turn_indicator_nim()
            render_piles_nim()

        ui_thread_task() # Flet'in page.update() yönetimine güveniyoruz.
                
    def send_data_to_peer_nim(data):
        global connection_nim, client_socket_nim
        try:
            payload = json.dumps(data).encode('utf-8')
            target_socket = connection_nim if game_state_nim["game_mode"] == "multi_host" else client_socket_nim
            if target_socket:
                target_socket.sendall(payload)
        except Exception as e:
            handle_disconnect_nim(f"Veri gönderme hatası: {e}")

    def process_received_data_nim(data):
        if not page.client_storage: return
        message_type = data.get("type")
        if message_type == "game_start_ack":
            initialize_game_nim(is_main_game=True, network_piles=data["piles"])
        elif message_type == "move":
            if game_state_nim["current_player"] != game_state_nim["my_player_number"]:
                show_feedback_nim(f"Rakip {data['pile_idx']+1}. desteden {data['num_removed']} taş aldı.")
                apply_move_nim(data['pile_idx'], data['num_removed'], is_ai_move=False)
        elif message_type == "game_over":
            game_state_nim["game_over"] = True
            game_state_nim["winner"] = data["winner"]
            game_state_nim["scores"] = data["scores"]
            display_winner_name = data['winner']
            end_game_winner_text_ref_nim.current.value = f"Oyun Bitti! Kazanan: {display_winner_name}"
            end_game_score_text_ref_nim.current.value = f"Skorlar:\nOyuncu 1: {data['scores']['Player 1']}\nOyuncu 2: {data['scores']['Player 2']}"
            confirm_button_ref_nim.current.disabled = True
            render_piles_nim()
            show_view_nim(end_game_view_ref_nim)

    def receive_data_loop_nim(sock):
        while True:
            try:
                data_bytes = sock.recv(BUFFER_SIZE_NIM)
                if not data_bytes:
                    handle_disconnect_nim("Rakip bağlantıyı kapattı.")
                    break
                message = json.loads(data_bytes.decode('utf-8'))
                if page.client_storage:
                    process_received_data_nim(message)
            except (ConnectionResetError, socket.timeout, socket.error, json.JSONDecodeError) as e:
                handle_disconnect_nim(f"Ağ hatası: {e}")
                break
            except Exception as e:
                handle_disconnect_nim(f"Bilinmeyen ağ hatası: {e}")
                break
                
    def start_server_logic_background_nim():
        global server_socket_nim, connection_nim, server_thread_nim, local_ip_address_for_display_nim
        try:
            s_temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s_temp.connect(("8.8.8.8", 80))
            local_ip_address_for_display_nim = s_temp.getsockname()[0]
            s_temp.close()
        except: local_ip_address_for_display_nim = "127.0.0.1"
        
        try:
            server_socket_nim = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket_nim.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket_nim.bind(("", DEFAULT_PORT_NIM))
            server_socket_nim.listen(1)
            msg = f"Sunucu Başlatıldı.\nAdres: {local_ip_address_for_display_nim}:{DEFAULT_PORT_NIM}\nOyuncu bekleniyor..."
            server_ip_text_ref_nim.current.value = msg; page.update()
            
            conn, addr = server_socket_nim.accept()
            connection_nim = conn
            
            server_ip_text_ref_nim.current.value = f"Oyuncu bağlandı: {addr[0]}\nOyunu başlatmak için butona basın."
            start_multiplayer_game_button_host_ref_nim.current.disabled = False; page.update()

            server_thread_nim = threading.Thread(target=receive_data_loop_nim, args=(connection_nim,), daemon=True)
            server_thread_nim.start()
        except Exception as e:
            server_ip_text_ref_nim.current.value = f"Sunucu başlatma hatası: {e}"; page.update()

    def connect_to_server_logic_background_nim(server_ip):
        global client_socket_nim, client_thread_nim
        try:
            ip, port = server_ip.split(":") if ":" in server_ip else (server_ip, DEFAULT_PORT_NIM)
            client_socket_nim = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket_nim.settimeout(5)
            client_socket_nim.connect((ip, int(port)))
            client_socket_nim.settimeout(None)
            msg = f"Sunucuya ({ip}:{port}) bağlanıldı.\nOyunun başlaması bekleniyor..."
            client_status_text_ref_nim.current.value = msg
            connect_button_client_ref_nim.current.disabled = True; page.update()
            
            client_thread_nim = threading.Thread(target=receive_data_loop_nim, args=(client_socket_nim,), daemon=True)
            client_thread_nim.start()
        except Exception as e:
            msg = f"Bağlantı hatası: {e}"
            client_status_text_ref_nim.current.value = msg
            connect_button_client_ref_nim.current.disabled = False; page.update()

    def handle_disconnect_nim(reason):
        global client_socket_nim, connection_nim, server_socket_nim
        show_feedback_nim(f"Bağlantı sorunu: {reason}. Oyun sonlandırıldı.", is_error=True)
        game_state_nim["game_over"] = True
        
        if page.client_storage:
            turn_indicator_ref_nim.current.value = "Bağlantı Koptu"
            confirm_button_ref_nim.current.disabled = True
            
            if game_area_view_ref_nim.current.visible:
                game_state_nim["game_mode_before_end"] = game_state_nim["game_mode"]
                show_view_nim(end_game_view_ref_nim)
                end_game_winner_text_ref_nim.current.value = "Bağlantı Koptu!"
                end_game_score_text_ref_nim.current.value = f"Sebep: {reason}"
        
        sockets_to_close = [client_socket_nim, connection_nim, server_socket_nim]
        for sock in sockets_to_close:
            if sock:
                try: sock.close()
                except: pass
        client_socket_nim, connection_nim, server_socket_nim = None, None, None
    
    all_view_refs_nim = [main_menu_view_ref_nim, multiplayer_options_view_ref_nim, server_info_view_ref_nim, client_connect_view_ref_nim, game_area_view_ref_nim, end_game_view_ref_nim, setting_level_view_ref_nim]

    def show_view_nim(view_to_show_ref: ft.Ref[ft.Column]):
        if not page.client_storage: return
        for view_ref in all_view_refs_nim:
            if view_ref.current:
                view_ref.current.visible = view_ref == view_to_show_ref
        page.update()

    def go_to_main_menu_and_reset_network_nim(e):
        global client_socket_nim, connection_nim, server_socket_nim
        sockets = [client_socket_nim, connection_nim, server_socket_nim]
        for sock in sockets:
            if sock:
                try: sock.close()
                except: pass
        client_socket_nim, connection_nim, server_socket_nim = None, None, None
        
        game_state_nim["game_mode"] = None
        game_state_nim["game_over"] = True
        show_view_nim(main_menu_view_ref_nim)

    def go_to_nim_main_menu(e):
        go_to_main_menu_and_reset_network_nim(e)

    def start_single_player_nim(e):
        game_state_nim["my_player_number"] = 1
        score_display_p2_ai_ref_nim.current.value = "Yapay Zeka: 0"
        initiate_calibration_game_nim()
    
    def initiate_calibration_game_nim():
        initialize_game_nim(is_main_game=False)

    def evaluate_calibration_performance_and_show_setting_level_screen_nim():
        if game_state_nim.get("game_over"):
            player_won = game_state_nim.get("winner") == "Player 1"
        else:
            player_won = True
            
        game_state_nim["ai_difficulty"] = "zor" if player_won else "standart"
        
        if not page.client_storage or not setting_level_view_ref_nim.current: return

        setting_level_view_ref_nim.current.controls[0].value = f"YZ Seviyesi '{game_state_nim['ai_difficulty']}' olarak ayarlandı.\nAsıl oyun 3 saniye içinde başlayacak..."
        show_view_nim(setting_level_view_ref_nim)
        
        def proceed_after_calibration():
            time.sleep(3)
            if page.client_storage:
                start_main_game_after_calibration_nim()

        threading.Thread(target=proceed_after_calibration, daemon=True).start()
    
    def start_main_game_after_calibration_nim():
        initialize_game_nim(is_main_game=True)

    def restart_current_game_mode_nim(e):
        mode = game_state_nim.get("game_mode_before_end", "single")
        if mode == "single" or mode == "calibration_play": 
            start_single_player_nim(None)
        else: 
            go_to_main_menu_and_reset_network_nim(None)

    def go_to_multiplayer_options_nim(e): show_view_nim(multiplayer_options_view_ref_nim)
    def host_game_nim(e):
        game_state_nim["game_mode"] = "multi_host"; game_state_nim["my_player_number"] = 1
        score_display_p2_ai_ref_nim.current.value = "Oyuncu 2: 0"
        start_multiplayer_game_button_host_ref_nim.current.disabled = True
        show_view_nim(server_info_view_ref_nim)
        threading.Thread(target=start_server_logic_background_nim, daemon=True).start()
    def join_game_prompt_nim(e):
        game_state_nim["game_mode"] = "multi_client"; game_state_nim["my_player_number"] = 2
        score_display_p2_ai_ref_nim.current.value = "Oyuncu 2: 0"
        show_view_nim(client_connect_view_ref_nim)
    def actual_join_game_nim(e):
        ip = server_ip_input_ref_nim.current.value.strip()
        if not ip:
            client_status_text_ref_nim.current.value = "Lütfen geçerli bir IP adresi girin."
            page.update(); return
        client_status_text_ref_nim.current.value = f"{ip} adresine bağlanılıyor..."
        connect_button_client_ref_nim.current.disabled = True; page.update()
        threading.Thread(target=connect_to_server_logic_background_nim, args=(ip,), daemon=True).start()

    def start_multiplayer_game_as_host_nim(e):
        if not connection_nim:
            show_feedback_nim("Oyuncu bağlı değil!", is_error=True); return
        piles = [random.randint(MIN_STONES_PER_PILE_NIM, MAX_STONES_PER_PILE_NIM) for _ in range(random.randint(MIN_PILES_NIM, MAX_PILES_NIM))]
        start_data = {"type": "game_start_ack", "piles": piles}
        send_data_to_peer_nim(start_data)
        initialize_game_nim(is_main_game=True, network_piles=piles)

    # --- Nim Arayüz Elementleri Tanımlamaları ---
    setting_level_view_ref_nim.current = ft.Column([ft.Text("YZ Seviyesi Ayarlanıyor...", size=20, weight=ft.FontWeight.BOLD), ft.ProgressRing()], visible=False, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
    end_game_winner_text_ref_nim.current = ft.Text("Oyun Bitti!", size=24, weight=ft.FontWeight.BOLD)
    end_game_score_text_ref_nim.current = ft.Text("Skorlar:", size=16)
    end_game_view_ref_nim.current = ft.Column(
        [
            end_game_winner_text_ref_nim.current, end_game_score_text_ref_nim.current,
            ft.ElevatedButton("Tekrar Oyna", on_click=restart_current_game_mode_nim, icon=ft.icons.REFRESH, width=200, height=50, bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, style=STADIUM_BUTTON_STYLE),
            ft.ElevatedButton("Ana Menü", on_click=go_to_nim_main_menu, icon=ft.icons.MENU, width=200, height=50, bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, style=STADIUM_BUTTON_STYLE),
        ],
        visible=False, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20
    )
    main_menu_view_ref_nim.current = ft.Column(
        [
            ft.Text("Nim Oyunu", size=32, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_HEADING),
            ft.ElevatedButton("Tek Oyunculu", on_click=start_single_player_nim, width=250, height=50, icon=ft.icons.PERSON_OUTLINE, bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, style=STADIUM_BUTTON_STYLE),
            ft.ElevatedButton("Çok Oyunculu", on_click=go_to_multiplayer_options_nim, width=250, height=50, icon=ft.icons.PEOPLE_OUTLINE, bgcolor=BUTTON_SECONDARY_COLOR, color=BUTTON_TEXT_COLOR, style=STADIUM_BUTTON_STYLE),
            ft.ElevatedButton("Tüm Oyunlar Menüsü", on_click=go_to_master_menu_func, width=250, height=50, icon=ft.icons.MENU, bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, style=STADIUM_BUTTON_STYLE),
        ],
        visible=True, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20
    )
    multiplayer_options_view_ref_nim.current = ft.Column(
        [
            ft.Text("Çok Oyunculu Mod", size=28, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_HEADING),
            ft.ElevatedButton("Sunucu Başlat", on_click=host_game_nim, width=250, height=50, icon=ft.icons.DNS_OUTLINED, bgcolor=BUTTON_SECONDARY_COLOR, color=BUTTON_TEXT_COLOR, style=STADIUM_BUTTON_STYLE),
            ft.ElevatedButton("Sunucuya Bağlan", on_click=join_game_prompt_nim, width=250, height=50, icon=ft.icons.SETTINGS_ETHERNET_ROUNDED, bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, style=STADIUM_BUTTON_STYLE),
            ft.ElevatedButton("Geri Dön", on_click=go_to_nim_main_menu, icon=ft.icons.ARROW_BACK, bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, width=250, height=50, style=STADIUM_BUTTON_STYLE),
        ],
        visible=False, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15
    )
    server_ip_text_ref_nim.current = ft.Text("Sunucu bilgisi burada gösterilecek.", size=16, text_align=ft.TextAlign.CENTER, selectable=True)
    start_multiplayer_game_button_host_ref_nim.current = ft.ElevatedButton("Oyunu Başlat", on_click=start_multiplayer_game_as_host_nim, disabled=True, icon=ft.icons.PLAY_CIRCLE_FILL_ROUNDED, bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, width=300, height=50, style=STADIUM_BUTTON_STYLE)
    server_info_view_ref_nim.current = ft.Column(
        [
            ft.Text("Sunucu Modu", size=24, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_HEADING),
            server_ip_text_ref_nim.current,
            start_multiplayer_game_button_host_ref_nim.current,
            ft.ElevatedButton("Geri Dön", on_click=lambda _: show_view_nim(multiplayer_options_view_ref_nim), icon=ft.icons.ARROW_BACK, bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, width=300, height=50, style=STADIUM_BUTTON_STYLE),
        ],
        visible=False, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15
    )
    server_ip_input_ref_nim.current = ft.TextField(label="Sunucu Adresi (IP veya IP:Port)", width=300, text_align=ft.TextAlign.CENTER)
    client_status_text_ref_nim.current = ft.Text("Sunucu IP adresini girin.", size=16, text_align=ft.TextAlign.CENTER)
    connect_button_client_ref_nim.current = ft.ElevatedButton("Bağlan", on_click=actual_join_game_nim, icon=ft.icons.LINK_ROUNDED, bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, width=200, height=50, style=STADIUM_BUTTON_STYLE)
    client_connect_view_ref_nim.current = ft.Column(
        [
            ft.Text("Sunucuya Bağlan", size=24, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_HEADING),
            server_ip_input_ref_nim.current,
            connect_button_client_ref_nim.current,
            client_status_text_ref_nim.current,
            ft.ElevatedButton("Geri Dön", on_click=lambda _: show_view_nim(multiplayer_options_view_ref_nim), icon=ft.icons.ARROW_BACK, bgcolor=BUTTON_GREY_COLOR, color=BUTTON_TEXT_COLOR, width=200, height=50, style=STADIUM_BUTTON_STYLE),
        ],
        visible=False, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15
    )
    score_display_p1_ref_nim.current = ft.Text("Oyuncu 1: 0", size=16)
    score_display_p2_ai_ref_nim.current = ft.Text("Oyuncu 2/AI: 0", size=16)
    turn_indicator_ref_nim.current = ft.Text("Sıra: Oyuncu 1", size=20, weight=ft.FontWeight.BOLD)
    feedback_text_ref_nim.current = ft.Text("", size=14, weight=ft.FontWeight.BOLD)
    piles_container_ref_nim.current = ft.Row(spacing=15, alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.START, scroll=ft.ScrollMode.ADAPTIVE)
    confirm_button_ref_nim.current = ft.ElevatedButton(text="Hamleyi Onayla", on_click=on_confirm_move_click_nim, icon=ft.icons.CHECK_CIRCLE_OUTLINE, bgcolor=BUTTON_PRIMARY_COLOR, color=BUTTON_TEXT_COLOR, height=50, disabled=True, style=STADIUM_BUTTON_STYLE)
    game_area_view_ref_nim.current = ft.Column(
        [
            ft.Row([score_display_p1_ref_nim.current, score_display_p2_ai_ref_nim.current], alignment=ft.MainAxisAlignment.SPACE_AROUND, width=600),
            turn_indicator_ref_nim.current,
            feedback_text_ref_nim.current,
            piles_container_ref_nim.current,
            confirm_button_ref_nim.current,
            ft.ElevatedButton("Oyundan Çık & Ana Menü", on_click=go_to_nim_main_menu, icon=ft.icons.EXIT_TO_APP, bgcolor=BUTTON_DANGER_COLOR, color=BUTTON_TEXT_COLOR, style=STADIUM_BUTTON_STYLE),
        ],
        visible=False, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10
    )

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    main_menu_view_ref_nim.current,
                    multiplayer_options_view_ref_nim.current,
                    server_info_view_ref_nim.current,
                    client_connect_view_ref_nim.current,
                    game_area_view_ref_nim.current,
                    end_game_view_ref_nim.current,
                    setting_level_view_ref_nim.current,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            expand=True
        )
    )
    show_view_nim(main_menu_view_ref_nim)

# ===================================================================================
# ================================= NIM OYUN KODU BİTİŞ =================================
# ===================================================================================


# ===================================================================================
# ================================= UYGULAMA GİRİŞ NOKTASI =================================
# ===================================================================================
if __name__ == "__main__":
    ft.app(target=master_main)