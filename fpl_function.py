import pandas as pd
import numpy as np

#create a generic, customizable function that return the top players for a given position, sorted on a given column
def top_players(df, position, sorting, asc, count, minutes_req = False):
    #only return players who played greater than or equal to the average minutes for their position
    avg_min = df.loc[df['position'] == position]['minutes'].mean()
    columns = ['web_name', 'team', 'now_cost', 'selected_by_percent', 'bps', 'percent_of_season_played', 'ppm', 'next_match', 'next_5_avg_FDRs']
    if position == 'Goalkeeper':
        columns = columns + ['clean_sheets', 'saves', 'goals_conceded', 'expected_goals_conceded', 'gc_vs_xgc', 'total_points']
    elif position == 'Defender':
        columns = columns + ['goals_scored', 'assists', 'goal_involvements', 'expected_goal_involvements', 'gi_vs_xgi', 'expected_goal_involvements_per_90', 'clean_sheets', 'goals_conceded', 'expected_goals_conceded', 'gc_vs_xgc', 'total_points']
    else:
        columns = columns + ['goals_scored', 'assists', 'goal_involvements', 'expected_goal_involvements', 'gi_vs_xgi', 'expected_goal_involvements_per_90', 'total_points']
    if minutes_req:
        return df.loc[(df['position'] == position) & (df['minutes'] >= avg_min)][columns].sort_values(by=sorting, ascending=asc).head(count)
    else:
        return df.loc[df['position'] == position][columns].sort_values(by=sorting, ascending=asc).head(count)
    
def average_by_cost(df, metric, position):
    min_cost = df.loc[df['position'] == position]['now_cost'].min()
    max_cost = df.loc[df['position'] == position]['now_cost'].max()
    x = min_cost
    col_title = 'avg_' + metric
    col_title_min = 'min_' + metric
    col_title_max = 'max_' + metric
    df_x = pd.DataFrame({'price': [], col_title: [], col_title_min: [], col_title_max: [], '# of players': []})
    while x <= max_cost:
        #tried weighted average, got error
        #average_pts = np.average(df.loc[(df['position'] == position) & (df['now_cost'] == x)]['total_points'], weights=df.loc[(df['position'] == position) & (df['now_cost'] == x)]['minutes'])
        average = np.round(df.loc[(df['position'] == position) & (df['now_cost'] == x)][metric].mean(), 2)
        min = np.round(df.loc[(df['position'] == position) & (df['now_cost'] == x)][metric].min(), 2)
        max = np.round(df.loc[(df['position'] == position) & (df['now_cost'] == x)][metric].max(), 2)
        num_players = df.loc[(df['position'] == position) & (df['now_cost'] == x)][metric].count()
        temp = pd.DataFrame({'price': [x], col_title: [average], col_title_min: [min], col_title_max: [max], '# of players': [num_players]})
        df_x = pd.concat([df_x, temp])
        x += 0.5
    df_x.dropna(inplace=True)
    return df_x

def top_players_by_cost(df, position, cost, metric, count, asc = False, minutes_req = False):
    avg_min = df.loc[df['position'] == position]['minutes'].mean()
    columns = ['web_name', 'team', 'now_cost', 'selected_by_percent', 'bps', 'percent_of_season_played', 'ppm', 'next_match', 'next_5_avg_FDRs']
    if position == 'Goalkeeper':
        columns = columns + ['clean_sheets', 'saves', 'goals_conceded', 'expected_goals_conceded', 'gc_vs_xgc', 'total_points']
    elif position == 'Defender':
        columns = columns + ['goals_scored', 'assists', 'goal_involvements', 'expected_goal_involvements', 'gi_vs_xgi', 'expected_goal_involvements_per_90', 'clean_sheets', 'goals_conceded', 'expected_goals_conceded', 'gc_vs_xgc', 'total_points']
    else:
        columns = columns + ['goals_scored', 'assists', 'goal_involvements', 'expected_goal_involvements', 'gi_vs_xgi', 'expected_goal_involvements_per_90', 'total_points']
    if minutes_req:
        return df.loc[(df['position'] == position) & (df['minutes'] >= avg_min) & (df['now_cost'] <= cost)][columns].sort_values(by=metric, ascending=asc).head(count)
    else:
        return df.loc[(df['position'] == position) & (df['now_cost'] <= cost)][columns].sort_values(by=metric, ascending=asc).head(count)
    
def get_team(df, players):
    columns = ['web_name', 'position', 'team', 'now_cost', 'selected_by_percent', 'percent_of_season_played', 'ppm', 'next_match', 'next_5_avg_FDRs',
               'goals_scored', 'assists', 'goal_involvements', 'clean_sheets', 'expected_goal_involvements', 'gi_vs_xgi', 'expected_goal_involvements_per_90', 'total_points']
    
    team = df.loc[df['web_name'].isin(players)][columns].sort_values(by='total_points', ascending=False)
    #change column types to str so they are not included in final summation row
    team = team.astype({'now_cost': str, 'selected_by_percent': str, 'percent_of_season_played': str, 'ppm': str, 'next_5_avg_FDRs': str})
    team.loc['Total']= team.sum(numeric_only=True, axis=0)
    team.fillna('-', inplace=True)
    return team

def compare_teams(df, team1, team2, captain1=None, captain2=None):
    columns = ['web_name', 'team', 'now_cost', 'selected_by_percent', 'percent_of_season_played', 'ppm', 'next_match', 'next_5_avg_FDRs',
               'goals_scored', 'assists', 'goal_involvements', 'expected_goal_involvements', 'gi_vs_xgi', 'expected_goal_involvements_per_90', 'total_points']
    cap_columns = ['bps', 'ppm', 'points_per_minute', 'gi_vs_xgi', 'total_points', 'goals_scored', 'assists', 'expected_goals', 'expected_assists', 'expected_goal_involvements', 
                   'expected_goals_per_90', 'expected_assists_per_90', 'expected_goal_involvements_per_90']
    table1 = df.loc[df['web_name'].isin(team1)][columns]
    table2 = df.loc[df['web_name'].isin(team2)][columns]
    if captain1:
        table1.loc[table1['web_name'] == captain1, cap_columns] = table1[cap_columns].apply(lambda x: x*2)
    if captain2:
        table2.loc[table2['web_name'] == captain2, cap_columns] = table2[cap_columns].apply(lambda x: x*2)

    sum1 = pd.DataFrame(table1.sum(numeric_only=True))
    sum2 = pd.DataFrame(table2.sum(numeric_only=True))

    final = pd.DataFrame(pd.concat([sum1.T, sum2.T], ignore_index=True))
    final.rename(index={0: 'Team1', 1: 'Team2'}, inplace=True)
    return final

def fixtures_by_team(fixtures, team, gameweek):
    away = fixtures.loc[fixtures['team_a'] == team]
    away.drop(['team_h_difficulty'], axis=1, inplace=True)
    away.rename(columns={'team_a': 'selected_team', 'team_h': 'opponent', 'team_a_difficulty': 'FDR', 'team_a_score': 'selected_team_score', 'team_h_score': 'opponent_score'}, inplace=True)
    away['h_or_a'] = 'Away'
    home = fixtures.loc[fixtures['team_h'] == team]
    home.drop(['team_a_difficulty'], axis=1, inplace=True)
    home.rename(columns={'team_h': 'selected_team', 'team_a': 'opponent', 'team_h_difficulty': 'FDR', 'team_h_score': 'selected_team_score',  'team_a_score': 'opponent_score'}, inplace=True)
    home['h_or_a'] = 'Home'
    combined = pd.concat([away, home])
    return combined.loc[combined['Gameweek'] <= gameweek].sort_values(by='Gameweek')
