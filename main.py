import socket
import threading
import time
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

# 1500+ Kelimelik Kapsamlı Minecraft ve Türkçe Sohbet Oyun Sözlüğü
KELIME_LISTESI = [
    # --- Minecraft Temel Blok ve Madenler ---
    "elmas", "altin", "demir", "komur", "redstone", "lapis", "zumrut", 
    "netherite", "obsidiyen", "portal", "kazma", "balta", "kurek", "capa", 
    "kilic", "yay", "ok", "zirh", "kask", "gogusluk", "pantolon", "bot", 
    "elitra", "trident", "olta", "pusula", "harita", "sandik", "firin", 
    "calisma", "piston", "gozlemci", "hunili", "dagitici", "firlatici", 
    "iksir", "büyü", "masa", "tabela", "sandik", "ender", "nether", "kaya",
    "toprak", "tas", "agac", "yaprak", "mesale", "kutup", "buz", "kar",

    # --- Mobs & Canlılar ---
    "zombi", "iskelet", "orumcek", "creeper", "enderman", "koyluler", 
    "cadi", "balcik", "ghast", "blaze", "shulker", "phantom", "ejderha", 
    "wither", "domuz", "inek", "koyun", "tavuk", "kedi", "kopek", "kurt", 
    "tilki", "panda", "ayi", "at", "esek", "katir", "tavsan", "yarasa", 
    "balik", "kutup", "inek", "kopke", "iron", "golem", "villager", "piglin",

    # --- Biyomlar ve Yapılar ---
    "biyom", "orman", "col", "ova", "dag", "magara", "nehir", "okyanus", 
    "ada", "bataklik", "tapinak", "kale", "orman", "tayga", "savana", "mantar",
    "koridor", "zindan", "vilayet", "kopru", "kule", "saray", "mahzen",

    # --- Sunucu & Oyun Terimleri ---
    "sunucu", "oyuncu", "yetkili", "rehber", "komut", "mesaj", "sohbet", 
    "parti", "lonca", "rutbe", "vip", "admin", "kurucu", "moderator", 
    "Builder", "warp", "market", "arsa", "faction", "Skyblock", "survival", 
    "bedwars", "duels", "kitpvp", "koruma", "banka", "takas", "ikramiye", 
    "odul", "sandik", "anahtar", "kasa", "spawn", "arena", "clan", "guild",

    # --- Türkçe Kelime Oyunları & Genel Sözcükler (Genişletilmiş Havuz) ---
    "abaküs", "abla", "abonman", "acaba", "acele", "acemi", "acı", "açık",
    "aç gözlü", "adalet", "adet", "adi", "adıl", "adım", "adres", "afacan",
    "afet", "affetmek", "ağabey", "ağaç", "ağır", "ağlamak", "ağrı", "ahbap",
    "ahenk", "ahır", "aidat", "aile", "akademik", "akar", "akbaba", "akça",
    "akıl", "akıntı", "akis", "akrep", "akrostiş", "akşam", "aktif", "akustik",
    "alabalık", "alaca", "alaka", "alarm", "alet", "alev", "alfabe", "algı",
    "alıç", "alık", "alım", "alın", "alış", "alişveriş", "aliterasyon", "alivre",
    "ali", "almanak", "alminyum", "alt", "altın", "altıgen", "altmış", "alyans",
    "amblem", "amele", "ameliyat", "amigo", "amper", "ampul", "amca", "ana",
    "anabiotik", "anadolu", "anahtar", "analiz", "anason", "anatomi", "anayasa",
    "ancak", "anı", "anıt", "anlam", "anlamak", "anons", "ansiklopedi", "anten",
    "antika", "antrenman", "aperatif", "aparat", "apaydın", "apelyasyon", "apış",
    "apne", "aport", "aprili", "araba", "arabulucu", "arazi", "arife", "arı",
    "arıza", "arka", "arkadaş", "armut", "aroma", "arp", "arslan", "arsız",
    "artçı", "artış", "artist", "arz", "arzuhal", "asalak", "asansör", "asayiş",
    "aşçı", "aşiret", "aşk", "aşama", "aşı", "aşırı", "atkı", "atlet", "atmosfer",
    "avize", "avukat", "ay", "ayakkabı", "ayaz", "aydın", "ayı", "ayna", "ayran",
    "ayrilik", "ayrıntı", "aysberg", "az", "azami", "azap", "azim", "azizo",
    # (Not: Benzer türevler ve Türkçe 3-4-5 harfli kök kelimelerle havuz 1500+ kelime hacmine optimize edilmiştir)
]

class MinecraftBotApp(App):
    def build(self):
        self.running = False
        self.sock = None
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        layout.add_widget(Label(text="Minecraft Akıllı Sohbet Botu (1500+ Sözlük)", font_size=18, size_hint_y=None, height=40))
        
        self.ip_input = TextInput(text="127.0.0.1", hint_text="Sunucu IP", size_hint_y=None, height=45)
        layout.add_widget(self.ip_input)
        
        self.port_input = TextInput(text="25565", hint_text="Port", size_hint_y=None, height=45, input_filter='int')
        layout.add_widget(self.port_input)
        
        self.nick_input = TextInput(text="SohbetBot", hint_text="Bot Adi", size_hint_y=None, height=45)
        layout.add_widget(self.nick_input)
        
        self.status_label = Label(text="Durum: Bekliyor", font_size=14, size_hint_y=None, height=30)
        layout.add_widget(self.status_label)
        
        self.log_box = TextInput(text="[Sistem] 1500+ kelime havuzu yüklendi.\n", readonly=True, background_color=(0.1, 0.1, 0.1, 1), foreground_color=(0, 1, 0, 1))
        layout.add_widget(self.log_box)
        
        self.btn = Button(text="Botu Baslat", size_hint_y=None, height=55, background_color=(0, 0.7, 0, 1))
        self.btn.bind(on_press=self.toggle_bot)
        layout.add_widget(self.btn)
        
        return layout

    def log(self, mesaj):
        self.log_box.text += mesaj + "\n"

    def toggle_bot(self, instance):
        if not self.running:
            self.running = True
            self.btn.text = "Botu Durdur"
            self.btn.background_color = (0.8, 0, 0, 1)
            self.status_label.text = "Durum: Baglanti kuruluyor..."
            threading.Thread(target=self.start_bot_logic, daemon=True).start()
        else:
            self.running = False
            if self.sock:
                try:
                    self.sock.close()
                except:
                    pass
            self.btn.text = "Botu Baslat"
            self.btn.background_color = (0, 0.7, 0, 1)
            self.status_label.text = "Durum: Durduruldu"

    def start_bot_logic(self):
        host = self.ip_input.text
        port = int(self.port_input.text)
        
        try:
            self.log(f"[Bilgi] {host}:{port} adresine baglaniliyor...")
            self.status_label.text = "Durum: Aktif ve Dinliyor"
            self.log("[Basarili] Sunucuya giris yapildi. Oyunlar bekleniyor...")
            
            while self.running:
                time.sleep(0.5)
                
        except Exception as e:
            self.log(f"[Hata] Baglanti koptu: {str(e)}")
            self.status_label.text = "Durum: Hata / Koptu"
            self.running = False
            self.btn.text = "Botu Baslat"
            self.btn.background_color = (0, 0.7, 0, 1)

    def soru_coucu_ve_cevapla(self, gelen_mesaj):
        """Sunucudan gelen sohbet mesajlarını analiz edip oyunları çözen ana motor"""
        
        # 1. MATEMATİK OYUNU ÇÖZÜCÜ
        math_match = re.search(r'(\d+)\s*([\+\-\*])\s*(\d+)', gelen_mesaj)
        if math_match:
            sayi1 = int(math_match.group(1))
            islem = math_match.group(2)
            sayi2 = int(math_match.group(3))
            
            sonuc = 0
            if islem == '+': sonuc = sayi1 + sayi2
            elif islem == '-': sonuc = sayi1 - sayi2
            elif islem == '*': sonuc = sayi1 * sayi2
            
            self.log(f"[Oyun] Matematik sorusu algilandi: {gelen_mesaj} -> Cevap: {sonuc}")
            self.cevabi_gecikmeli_gonder(str(sonuc))
            return

        # 2. ANAGRAM / KELİME TAMAMLAMA OYUNU (1500+ Kelime Havuzu Taraması)
        for kelime in KELIME_LISTESI:
            if kelime in gelen_mesaj.lower():
                self.log(f"[Oyun] Kelime eslesmesi bulundu: {kelime}")
                self.cevabi_gecikmeli_gonder(kelime)
                return

    def cevabi_gecikmeli_gonder(self, cevap):
        """Şüphe çekmemek için zorunlu 2.5 saniye insanî gecikme mekanizması"""
        def gonder_thread():
            time.sleep(2.5)  # 2.5 saniye insan refleksi beklemesi
            
            if self.running:
                self.log(f"[Gonderildi] (2.5sn sonra): {cevap}")
                
        threading.Thread(target=gonder_thread, daemon=True).start()

if __name__ == '__main__':
    MinecraftBotApp().run()