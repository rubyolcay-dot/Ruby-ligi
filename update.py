import requests
import json
import time

# Lichess'in bize vereceği en temiz veri kaynağı
URL = "https://lichess.org/api/team/ruby-satranc/users"

def main():
    try:
        # Veriyi çek
        response = requests.get(URL, headers={"Accept": "application/x-ndjson"}, timeout=30)
        if response.status_code != 200:
            print(f"API Hatası: {response.status_code}")
            return

        # Üyeleri ayıkla
        lines = response.text.strip().split('\n')
        members = [json.loads(line) for line in lines if line.strip()]
        
        if not members:
            print("Üye bulunamadı!")
            return

        blitz_data = []
        # Sadece ilk 20 üyeyi alalım ki Lichess engeline takılmayalım (hız için)
        for m in members[:20]: 
            name = m.get('username')
            rating = m.get('perfs', {}).get('blitz', {}).get('rating', 1500)
            blitz_data.append({"username": name, "rating": rating})

        # Dosyaya yaz (Ezeli rekabeti geçici olarak boş bırakıyoruz ki site null vermesin)
        final_data = {"blitz": blitz_data, "games": [], "h2h": []}
        
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        print("Veriler başarıyla yazıldı!")
        
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    main()
