import requests
import json

URL = "https://lichess.org/api/team/ruby-satranc/users"

def main():
    try:
        # User-Agent şart, Lichess bot engeline takılmamak için
        headers = {
            "Accept": "application/x-ndjson",
            "User-Agent": "RubyChessLeague/1.0 (Contact: admin@rubyleague.com)"
        }
        
        response = requests.get(URL, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"API Hatası: {response.status_code}")
            return

        lines = response.text.strip().split('\n')
        members = [json.loads(line) for line in lines if line.strip()]
        
        if not members:
            print("Üye bulunamadı!")
            return

        blitz_data = []
        for m in members:
            # Lichess bazen 'username', bazen 'id' verir. İkisini de kontrol edelim:
            username = m.get('username') or m.get('id') or m.get('name')
            
            # Eğer bir şekilde isim çekilemediyse 'null' basmasın, o oyuncuyu atlasın
            if not username:
                continue
                
            rating = m.get('perfs', {}).get('blitz', {}).get('rating', 1500)
            blitz_data.append({"username": username, "rating": rating})

        final_data = {
            "blitz": blitz_data,
            "games": [],
            "h2h": []
        }
        
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
            
        print(f"Başarıyla {len(blitz_data)} oyuncu yazıldı!")
        
    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    main()
