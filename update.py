import requests
import json
import time

TEAM_ID = "ruby-satranc"
HEADERS = {
    "Accept": "application/x-ndjson",
    "User-Agent": "RubyChessLeague-AutoUpdater/1.0"
}

def get_team_members():
    url = f"https://lichess.org/api/team/{TEAM_ID}/users"
    print(f"Veri çekiliyor: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            # Lichess her satıra bir JSON objesi koyar
            members = []
            for line in response.text.splitlines():
                if line.strip():
                    user_obj = json.loads(line)
                    # Burası önemli: Lichess JSON'da 'id' veya 'username' anahtarı ile isim gelir
                    username = user_obj.get('username') or user_obj.get('id')
                    if username:
                        members.append(user_obj)
            print(f"Toplam {len(members)} üye bulundu ve isimleri ayrıştırıldı.")
            return members
    except Exception as e:
        print(f"Hata: {e}")
    return []

# ... (get_h2h_matches fonksiyonun aynı kalsın) ...

def main():
    members = get_team_members()
    if not members:
        return

    blitz_list = []
    games_list = []
    usernames = [] # Set yerine liste yapalım
    
    for m in members:
        username = m.get('username') or m.get('id')
        usernames.append(username)
        # ... (diğer işlemler)
