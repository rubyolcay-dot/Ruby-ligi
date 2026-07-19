import requests
import json
import time

TEAM_ID = "ruby-satranc"

def get_team_members():
    url = f"https://lichess.org/api/team/{TEAM_ID}/users"
    response = requests.get(url)
    if response.status_code == 200:
        lines = response.text.strip().split('\n')
        members = []
        for line in lines:
            if line.strip():
                try:
                    members.append(json.loads(line))
                except:
                    continue
        return members
    return []

def get_h2h_matches(usernames):
    h2h_data = {}
    for username in usernames:
        time.sleep(1.5)
        url = f"https://lichess.org/api/games/user/{username}?max=80&perfType=blitz"
        headers = {"Accept": "application/x-ndjson"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
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
    if not members:
        return
    blitz_list = []
    games_list = []
    usernames = set()
    for m in members:
        username = m.get('username')
        usernames.add(username)
        perfs = m.get('perfs', {})
        blitz_rating = perfs.get('blitz', {}).get('rating', 1500)
        blitz_list.append({"username": username, "rating": blitz_rating})
        total_games = m.get('count', {}).get('all', 0)
        games_list.append({"username": username, "games": total_games})
    blitz_list.sort(key=lambda x: x['rating'], reverse=True)
    games_list.sort(key=lambda x: x['games'], reverse=True)
    h2h_list = get_h2h_matches(usernames)
    output_data = {"blitz": blitz_list, "games": games_list, "h2h": h2h_list}
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
