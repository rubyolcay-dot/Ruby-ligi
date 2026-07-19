import requests
import json
import time

TEAM_ID = "ruby-satranc"

# Lichess'in bizi bot sanıp engellememesi için özel Kimlik Kartı (User-Agent) ekledik
HEADERS = {
    "Accept": "application/x-ndjson",
    "User-Agent": "RubyChessLeague-AutoUpdater/1.0 (https://github.com/rubyolcay-dot)"
}

def get_team_members():
    url = f"https://lichess.org/api/team/{TEAM_ID}/users"
    print(f"{url} adresinden takım verileri çekiliyor...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        print(f"API Yanıt Kodu: {response.status_code}")
        
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            members = []
            for line in lines:
                if line.strip():
                    try:
                        members.append(json.loads(line))
                    except Exception as e:
                        continue
            print(f"Harika! Toplam {len(members)} üye bulundu.")
            return members
        else:
            print(f"HATA: Lichess veriyi vermedi. Hata Detayı: {response.text}")
    except Exception as e:
        print(f"Bağlantı hatası: {e}")
    return []

def get_h2h_matches(usernames):
    h2h_data = {}
    for username in usernames:
        time.sleep(2.0) # Lichess'i sinirlendirmemek için 2 saniye mola
        url = f"https://lichess.org/api/games/user/{username}?max=50&perfType=blitz"
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code != 200:
                print(f"{username} oyuncusunun verisi çekilemedi. Kod: {response.status_code}")
                continue
            
            lines = response.text.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                try:
                    game = json.loads(line)
                    players = game.get('players', {})
                    white_user = players.get('white', {}).get('user', {})
                    black_user = players.get('black', {}).get('user', {})
                    
                    if not white_user or not black_user:
                        continue
                        
                    white = white_user.get('name')
                    black = black_user.get('name')
                    
                    if not white or not black:
                        continue
                        
                    if white in usernames and black in usernames and white != black:
                        p1, p2 = sorted([white, black])
                        pair_key = f"{p1}_vs_{p2}"
                        winner = game.get('winner')
                        
                        if pair_key not in h2h_data:
                            h2h_data[pair_key] = {"p1": p1, "p2": p2, "p1Win": 0, "p2Win": 0, "total": 0}
                            
                        h2h_data[pair_key]["total"] += 1
                        
                        if winner == 'white':
                            win_name = white
                        elif winner == 'black':
                            win_name = black
                        else:
                            win_name = None
                            
                        if win_name == p1:
                            h2h_data[pair_key]["p1Win"] += 1
                        elif win_name == p2:
                            h2h_data[pair_key]["p2Win"] += 1
                except:
                    continue
        except:
            continue

    final_h2h = []
    for key, data in h2h_data.items():
        data["total"] = max(1, round(data["total"] / 2))
        data["p1Win"] = round(data["p1Win"] / 2)
        data["p2Win"] = round(data["p2Win"] / 2)
        if data["total"] > 0:
            final_h2h.append(data)
    return final_h2h

def main():
    members = get_team_members()
    
    # EĞER LİCHESS YİNE ENGEL KOYARSA, MEVCUT SİTEYİ PATLATMAMAK İÇİN SİGORTA:
    if not members:
        print("KRİTİK UYARI: Takım üyeleri bulunamadı! Site null olmasın diye işlem iptal edildi.")
        return

    blitz_list = []
    games_list = []
    usernames = set()
    
    for m in members:
        username = m.get('username')
        if not username:
            continue
        usernames.add(username)
        perfs = m.get('perfs', {})
        blitz_rating = perfs.get('blitz', {}).get('rating', 1500)
        blitz_list.append({"username": username, "rating": blitz_rating})
        total_games = m.get('count', {}).get('all', 0)
        games_list.append({"username": username, "games": total_games})
        
    blitz_list.sort(key=lambda x: x['rating'], reverse=True)
    games_list.sort(key=lambda x: x['games'], reverse=True)
    
    print(f"Toplam {len(usernames)} oyuncunun geçmiş maçları taranıyor...")
    h2h_list = get_h2h_matches(usernames)
    print(f"Tarama bitti! Bulunan H2H (Ezeli Rekabet) eşleşme sayısı: {len(h2h_list)}")
    
    output_data = {"blitz": blitz_list, "games": games_list, "h2h": h2h_list}
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)
    print("Mükemmel! Sistem başarıyla güncellendi ve data.json dosyasına yazıldı.")

if __name__ == "__main__":
    main()
