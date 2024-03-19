import csv
import re
from bs4 import BeautifulSoup, Comment
from urllib.request import urlopen

teams = {
    'ARI': 'Arizona Diamondbacks',
    'ATL': 'Atlanta Braves',
    'BAL': 'Baltimore Orioles',
    'BOS': 'Boston Red Sox',
    'CHC': 'Chicago Cubs',
    'CHW': 'Chicago White Sox',
    'CIN': 'Cincinnati Reds',
    'CLE': 'Cleveland Guardians',
    'COL': 'Colorado Rockies',
    'DET': 'Detroit Tigers',
    'HOU': 'Houston Astros',
    'KCR': 'Kansas City Royals',
    'LAA': 'Los Angeles Angels',
    'LAD': 'Los Angeles Dodgers',
    'MIA': 'Miami Marlins',
    'MIL': 'Milwaukee Brewers',
    'MIN': 'Minnesota Twins',
    'NYM': 'New York Mets',
    'NYY': 'New York Yankees',
    'OAK': 'Oakland Athletics',
    'PHI': 'Philadelphia Phillies',
    'PIT': 'Pittsburgh Pirates',
    'SDP': 'San Diego Padres',
    'SEA': 'Seattle Mariners',
    'SFG': 'San Francisco Giants',
    'STL': 'St. Louis Cardinals',
    'TBR': 'Tampa Bay Rays',
    'TEX': 'Texas Rangers',
    'TOR': 'Toronto Blue Jays',
    'WSN': 'Washington Nationals'
}

path = '../years/2024.csv'

def parse_stats(url):
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    tdiv = [ln.strip() for ln in str(soup.find('div', id='all_players_standard_batting')
                .find(string=lambda text: isinstance(text, Comment))).split('\n')
                if (tm := ln.strip()) and 'data-stat="player"' in tm]
    stats = []
    for ln in tdiv:
        soup = BeautifulSoup(ln, 'html.parser')
        els = soup.find_all(attrs={"data-stat": True})
        stats.append({el['data-stat']: el.get_text() for el in els})
        
    return stats

def make_csv(stats):
    # write to file
    with open(path, mode='w', newline='',encoding='utf-8') as csvfile:
        fields = ['Rank', 'Name', 'Age', 'TmFull', 'team_ID', 'G', 'PA', 'AB', 'R', 'H', 
                  '2B', '3B', 'HR', 'RBI', 'SB', 'CS', 'BB', 'SO', 'BA', 'OBP',
                  'SLG', 'OPS', 'OPS+', 'TB', 'GDP', 'HBP', 'SH', 'SH', 'SF', 
                  'IBB', 'BC%', 'Total BC']
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        for row in stats:
            if (row['player'] == 'Name'):
                continue
                
            if (int(row['G']) < 30):
                continue
            
            row['Rank'] = 0
            row['Name'] = re.sub(r'[^a-zA-Z]+$', '', row.pop('player', ''))
            row['Age'] = row.pop('age', '')
            row['TmFull'] = teams.get(row['team_ID'], '')
            row['BA'] = row.pop('batting_avg', '')
            row['OBP'] = row.pop('onbase_perc', '')
            row['SLG'] = row.pop('slugging_perc', '')
            row['OPS'] = row.pop('onbase_plus_slugging', '')
            row['OPS+'] = row.pop('onbase_plus_slugging_plus', '')
            row['GDP'] = row.pop('GIDP', '')
            row['Total BC'] = f"{(int(row['TB']) + int(row['BB']) + int(row['IBB']) + int(row['HBP']) + int(row['SB']) - int(row['CS']) - int(row['GDP']))}"
            row['BC%'] = f"{(int(row['Total BC']) / int(row['PA'])):.4f}" if int(row['PA']) != 0 else '0.0'
            frow = {key: value for key, value in row.items() if key in fields}
            writer.writerow(frow)
        
    # sort by BC%
    with open(path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = list(reader)
        data.sort(key=lambda x: float(x['BC%']), reverse=True)
        for i, row in enumerate(data, start=1):
            row['Rank'] = i
        with open(path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(data)
    

def main():
    url = "https://www.baseball-reference.com/leagues/majors/2023-standard-batting.shtml"
    stats = parse_stats(url)
    make_csv(stats)
    
    
if __name__ == "__main__":
    main()