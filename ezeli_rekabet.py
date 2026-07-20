import requests
import json
import itertools
import time
import os

TEAM_URL = "https://lichess.org/api/team/ruby-satranc/users"
CROSSTABLE_URL = "https://lichess.org/api/crosstable/{user1}/{user2}"
RIVALRIES_FILE = "rivalries.json"
STATE_FILE = "scan_state.json"

def main():
    print("Sistem Başlatılıyor...")
    headers = {"User-Agent": "RubyChessLeague-Bot/1.0"}
    
    # 1. Takım üyelerini çek
    res = requests.get(TEAM_URL, headers=headers)
    users = []
    for line in res.text.strip().split('\n'):
        if line:
            try:
                data = json.loads(line)
                users.append(data.get("username", data.get("id")))
            except: pass

    users = [u for u in users if u]
    print(f"Takımda toplam {len(users)} oyuncu bulundu.")

    # 2. Tüm 2'li kombinasyonları oluştur (102 oyuncu için ~5151 ihtimal)
    all_pairs = list(itertools.combinations(users, 2))
    all_pairs = [tuple(sorted(p)) for p in all_pairs] 

    # 3. Hafızayı (Önceki kayıtları) Yükle
    known_rivalries = []
    scanned_pairs = []
    
    if os.path.exists(RIVALRIES_FILE):
        try:
            with open(RIVALRIES_FILE, "r", encoding="utf-8") as f:
                known_rivalries = json.load(f)
        except: pass

    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                scanned_pairs = json.load(f)
        except: pass

    scanned_pairs_set = set(tuple(p) for p in scanned_pairs)
    known_pairs_set = set(tuple(sorted([r["player1"], r["player2"]])) for r in known_rivalries)

    # 4. Bu turda taranacakları belirle (Eskileri güncelle + 150 yeni eşleşme keşfet)
    pairs_to_scan_new = []
    for p in all_pairs:
        if p not in scanned_pairs_set:
            pairs_to_scan_new.append(p)
        if len(pairs_to_scan_new) >= 150: # Limit aşımını önlemek için 150 adet kota koyduk
            break

    targets_for_this_run = list(known_pairs_set) + pairs_to_scan_new
    
    print(f"Bilinen aktif rekabet sayısı: {len(known_pairs_set)}")
    print(f"Bu turda keşfedilecek yeni ihtimal: {len(pairs_to_scan_new)}")

    new_known_rivalries = []
    
    # 5. Lichess'ten skorları sorgula
    for idx, (u1, u2) in enumerate(targets_for_this_run):
        try:
            time.sleep(0.4) # Bot engeli yememek için bekleme
            url = CROSSTABLE_URL.format(user1=u1, user2=u2)
            r = requests.get(url, headers=headers)
            
            if r.status_code == 200:
                data = r.json()
                s1 = data.get("users", {}).get(u1.lower(), 0)
                s2 = data.get("users", {}).get(u2.lower(), 0)
                total = s1 + s2
                
                if total > 0: # Eğer aralarında maç varsa hafızaya al
                    new_known_rivalries.append({
                        "player1": u1,
                        "player2": u2,
                        "score1": s1,
                        "score2": s2,
                        "totalMatches": int(total)
                    })
            elif r.status_code == 429:
                print("Lichess engeli (Rate Limit) yaklaştı! İşlem erken bitiriliyor ve kaydediliyor.")
                break
                
        except Exception as e:
            print(f"Hata: {e}")
            
        # Taranan yeni ihtimalleri, bir daha taranmamak üzere işaretle
        if (u1, u2) in pairs_to_scan_new:
            scanned_pairs.append((u1, u2))

    # Toplam maç sayısına göre liderlik sıralaması
    new_known_rivalries.sort(key=lambda x: x["totalMatches"], reverse=True)

    # 6. Verileri Dosyalara Kaydet
    with open(RIVALRIES_FILE, "w", encoding="utf-8") as f:
        json.dump(new_known_rivalries, f, ensure_ascii=False, indent=2)

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(scanned_pairs, f, ensure_ascii=False, indent=2)

    print("İşlem başarıyla tamamlandı! Gerçek rekabetler kaydedildi.")

if __name__ == "__main__":
    main()
