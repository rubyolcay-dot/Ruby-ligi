import requests
import json

URL = "https://lichess.org/api/team/ruby-satranc/users"

def main():
    try:
        headers = {
            "Accept": "application/x-ndjson",
            "User-Agent": "RubyChessLeague/1.0"
        }

        response = requests.get(URL, headers=headers)

        if response.status_code != 200:
            print(f"API Hatası: {response.status_code}")
            return

        lines = response.text.strip().split('\n')
        members = [json.loads(line) for line in lines if line.strip()]

        if not members:
            print("Üye bulunamadı!")
            return

        players = []

        for m in members:
            # Kullanıcı adı kontrolü
            username = m.get("username") or m.get("id") or m.get("name")
            if not username:
                continue

            # Reyting ve Performans Verileri
            perfs = m.get("perfs", {})
            blitz_perf = perfs.get("blitz", {})
            blitz_rating = blitz_perf.get("rating", 1500)
            blitz_games = blitz_perf.get("games", 0)

            # Toplam Oyun İstatistikleri
            count_data = m.get("count", {})
            total_games = count_data.get("all", blitz_games)
            wins = count_data.get("win", 0)
            losses = count_data.get("loss", 0)
            draws = count_data.get("draw", 0)

            players.append({
                "username": username,
                "blitz": blitz_rating,
                "totalGames": total_games,
                "win": wins,
                "loss": losses,
                "draw": draws
            })

        # Blitz puanına göre yüksekten düşüğe sırala
        players.sort(key=lambda x: x["blitz"], reverse=True)

        data = {
            "players": players,
            "rivalries": []
        }

        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print("data.json başarıyla güncellendi!")

    except Exception as e:
        print(f"Bir hata oluştu: {e}")

if __name__ == "__main__":
    main()
