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
while start_year <= end_year:
    print (f"Getting All Teams from the year { start_year }")
    teams = requests.request("GET", f"http://lookup-service-prod.mlb.com/json/named.team_all_season.bam?sport_code='mlb'&sort_order=name_asc&season='{ start_year }'", headers=headers)
    teamsJSON = teams.json()
    teamList = teamsJSON['team_all_season']['queryResults']['row']

# -------------------------
# Single Team
# -------------------------

    allTeamList = []
    allRostersList = []
    for team in teamList:
        if team['mlb_org'] != "Office of the Commissioner":
            singleTeam = team
            allTeamList.append(singleTeam)

# -------------------------
# All Rosters
# -------------------------

        print (f"Getting Roster from the year { start_year } for team { singleTeam['mlb_org'].replace('/',' ') }")
        if singleTeam['mlb_org']:
            roster = requests.request("GET", f"http://lookup-service-prod.mlb.com/json/named.roster_team_alltime.bam?start_season={ start_year }&end_season={ start_year }&team_id={ singleTeam['team_id'] }", headers=headers)
            rosterJSON = roster.json()
            if rosterJSON['roster_team_alltime']['queryResults']['totalSize'] != "0":
                rosterList = rosterJSON['roster_team_alltime']['queryResults']['row']
                allRostersList.append(rosterList)


# -------------------------
# Team Template
# -------------------------

                parsed_all_output = team_template.render(
                    singleTeam = singleTeam,
                    singleRoster = rosterList,
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
        rosterList = allRostersList
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