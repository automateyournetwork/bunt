import requests
import json
import time

# -------------------------
# Jinja2
# -------------------------

from jinja2 import Environment, FileSystemLoader
template_dir = 'Templates/'
env = Environment(loader=FileSystemLoader(template_dir))
allMLB_template = env.get_template('MLB_Season.j2')

# -------------------------
# Headers
# -------------------------

headers = {
  'Accept': 'application/json',
  'Content-Type': 'application/json',
}

# -------------------------
# All Teams
# -------------------------

start_year = 1876
end_year = 2021
team_template = env.get_template('team.j2')
allTeamList = []
while start_year <= end_year:
    print (f"Getting All Teams from the year { start_year }")
    teams = requests.request("GET", f"http://lookup-service-prod.mlb.com/json/named.team_all_season.bam?sport_code='mlb'&sort_order=name_asc&season='{ start_year }'", headers=headers)
    teamsJSON = teams.json()
    teamList = teamsJSON['team_all_season']['queryResults']['row']

# -------------------------
# Single Team
# -------------------------
    for team in teamList:
        if team['mlb_org'] != "Office of the Commissioner":
            singleTeam = team
            allTeamList.append(singleTeam)

# -------------------------
# All Rosters
# -------------------------

        print (f"Getting Roster from the year { start_year } for team { singleTeam['mlb_org'].replace('/',' ') }")
        if singleTeam['mlb_org']:
            print(singleTeam['mlb_org'])
            print(singleTeam['team_id'])
            roster = requests.request("GET", f"http://lookup-service-prod.mlb.com/json/named.roster_team_alltime.bam?start_season={ start_year }&end_season={ start_year }&team_id={ singleTeam['team_id'] }", headers=headers)
            rosterJSON = roster.json()
            if rosterJSON['roster_team_alltime']['queryResults']['totalSize'] > "1":
                rosterList = rosterJSON['roster_team_alltime']['queryResults']['row']
                for player in rosterList:
                    if player['primary_position'] != "P":
                        playerStatsAPI = requests.request("GET", f"http://lookup-service-prod.mlb.com//json/named.sport_hitting_tm.bam?league_list_id='mlb'&game_type='R'&season={ start_year }&player_id={ player['player_id'] }", headers=headers)
                        statsJSON = playerStatsAPI.json()
                        if statsJSON['sport_hitting_tm']['queryResults']['totalSize'] != "0":
                            playerStats = statsJSON['sport_hitting_tm']['queryResults']['row']
                    else:
                        playerStatsAPI = requests.request("GET", f"http://lookup-service-prod.mlb.com//json/named.sport_pitching_tm.bam?league_list_id='mlb'&game_type='R'&season={ start_year }&player_id={ player['player_id'] }", headers=headers)
                        statsJSON = playerStatsAPI.json()
                        if statsJSON['sport_pitching_tm']['queryResults']['totalSize'] != "0":
                            playerStats = statsJSON['sport_pitching_tm']['queryResults']['row']

# -------------------------
# Team Template
# -------------------------

                parsed_all_output = team_template.render(
                    singleTeam = singleTeam,
                    singleRoster = rosterList,
                    playerStats = playerStats
                    )

# -------------------------
# Save Team File
# -------------------------

        if singleTeam['mlb_org']:
            with open(f"Baseball/{ start_year } Season/{ singleTeam['mlb_org'].replace('/',' ')}.md", "w") as fh:
                fh.write(parsed_all_output)                
                fh.close()

        print(f"File Baseball/{ start_year } Season/{ singleTeam['mlb_org'].replace('/',' ')}.md Saved")

# -------------------------
# All MLB Template
# -------------------------

    parsed_all_output = allMLB_template.render(
        teamList = allTeamList,
        )

# -------------------------
# Save MLB 2022 file File
# -------------------------

    with open(f"Baseball/{ start_year } Season/Major League Baseball { start_year }.md", "w") as fh:
        fh.write(parsed_all_output)               
        fh.close()
    
    print(f"File Baseball/{ start_year } Season/Major League Baseball { start_year }.md Saved")
    start_year = start_year + 1
    time.sleep(0.5)