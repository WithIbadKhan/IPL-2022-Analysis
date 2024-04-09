import dash
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load IPL match data
ipl_data = pd.read_csv("IPL_Matches_2022.csv")
player_data = pd.read_csv("IPL_Data.csv")
teams = player_data['Team'].unique()

total_matches_played = ipl_data['team1'].value_counts().add(ipl_data['team2'].value_counts(), fill_value=0).astype(int)
total_won = ipl_data['match_winner'].value_counts()
win_percentage = ((total_won / total_matches_played) * 100).sort_values(ascending=False).astype(int)

team_performance = pd.DataFrame({
    'Total Matches Played': total_matches_played,
    'Total Matches Won': total_won,
    'Win Percentage (%)': win_percentage
}).sort_values(by='Win Percentage (%)', ascending=False)

#####

pom = ipl_data.groupby('player_of_the_match')['match_id'].count().sort_values(ascending=False)[:10]
score = ipl_data.groupby('top_scorer')['highscore'].sum().sort_values(ascending=False)[:10]
toss_match_won = ipl_data[ipl_data['toss_winner'] == ipl_data['match_winner']]['match_winner'].value_counts()
match_won = ipl_data['match_winner'].value_counts()
percentage_won = (toss_match_won / match_won * 100).astype(int).sort_values(ascending=False)
win_method_counts = ipl_data["won_by"].value_counts()
Defender = ipl_data[ipl_data['won_by'] == 'Runs']
bowler = ipl_data.groupby('best_bowling')['match_id'].count().sort_values(ascending=False)[:10]
venue_counts = ipl_data['venue'].value_counts()

#######

app = dash.Dash(__name__)

# CSS styles for cards
card_style = {
    'padding': '20px',
    'margin': '10px',
    'borderRadius': '5px',
    'background': '#FAFAFA',
    'boxShadow': '2px 2px 2px lightgrey',
    'textAlign': 'center'
}

# Layout of the app
app.layout = html.Div(children=[
    html.H1("Cricket Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            dcc.Dropdown(
                id='team-dropdown',
                options=[{'label': team, 'value': team} for team in teams],
                value=teams[0],  # Default value
                style={'marginBottom': '20px'}
            ),
            dcc.Dropdown(id='player-dropdown', style={'marginBottom': '20px'}),
            html.Div(id='player-url', style={'padding': '10px', 'margin': '20px', 'borderRadius': '5px', 'background': '#FAFAFA', 'boxShadow': '2px 2px 2px lightgrey'}),
        ], style={'padding': '20px', 'margin': '10px', 'borderRadius': '5px', 'background': '#FAFAFA', 'boxShadow': '2px 2px 2px lightgrey', 'textAlign': 'center', 'flex': '1'}),

        html.Div(id='player-performance-board-div', style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center'}),
    ]),

    dcc.Graph(id='player-performance', style={'padding': '20px', 'margin': '10px', 'borderRadius': '5px', 'background': '#FAFAFA', 'boxShadow': '2px 2px 2px lightgrey', 'width': '45%'}),
    dcc.Graph(id='top-wicket-takers-bar-chart', style={'padding': '20px', 'margin': '10px', 'borderRadius': '5px', 'background': '#FAFAFA', 'boxShadow': '2px 2px 2px lightgrey', 'width': '45%'}),

    dcc.Graph(id='dismissal-types', style={'padding': '20px', 'margin': '10px', 'borderRadius': '5px', 'background': '#FAFAFA', 'boxShadow': '2px 2px 2px lightgrey', 'flexBasis': '45%'}),  # New graph for dismissal types
    dcc.Graph(id='most-wins-chart', style={'padding': '20px', 'margin': '10px', 'borderRadius': '5px', 'background': '#FAFAFA', 'boxShadow': '2px 2px 2px lightgrey', 'width': '45%'}),

    dcc.Graph(
        id='team-performance-graph',
        figure=px.bar(
            team_performance, x=team_performance.index, y=['Total Matches Played', 'Total Matches Won'],
            title='Team Performance in IPL 2022', text_auto=True, barmode='group',
            labels={'index': 'IPL Team'}, color_discrete_map={'Total Matches Played': 'lightblue', 'Total Matches Won': 'blue'}
        ).update_layout(legend_title_text='Performance', yaxis_title='Match Counts Played & Won')
    ),

    dcc.Graph(
        id='win-percentage-graph',
        figure=px.bar(
            win_percentage, x=win_percentage.index, y=win_percentage,
            title='Win Percentage by Each Team', text_auto=True, color=win_percentage,
            labels={'index': 'IPL Teams', 'y': 'Win Percentage'}
        ).update_layout(yaxis_ticksuffix='%')
    ),

    dcc.Graph(
        id='player-of-the-match-graph',
        figure=px.bar(
            pom, y='match_id', text='match_id',
            title='Most Player of the Match Awards', color='match_id',
            labels={'match_id': 'Match Counts'}
        ).update_traces(textfont_size=20)
    ),

    dcc.Graph(
        id='top-scorers-graph',
        figure=px.bar(
            score, y='highscore', color='highscore',
            title='Top Scorers in IPL 2022', text='highscore',
            labels={'highscore': 'Season Total Score'}
        )
    ),

    dcc.Graph(
        id='toss-winner-graph',
        figure=px.bar(
            x=ipl_data['toss_winner'].value_counts().index.tolist(),
            y=ipl_data['toss_winner'].value_counts(), text=ipl_data['toss_winner'].value_counts(),
            color=ipl_data['toss_winner'].value_counts(),
            title='Most Toss Winner Team',
            labels={'x': 'Toss Winner', 'y': 'Match Count'}
        ).update_traces(textfont_size=20)
    ),
])

# Callbacks for updating components
@app.callback(
    Output('player-dropdown', 'options'),
    Input('team-dropdown', 'value')
)
def set_player_options(selected_team):
    filtered_df = player_data[player_data['Team'] == selected_team]
    return [{'label': name, 'value': name} for name in filtered_df['Name']]

@app.callback(
    Output('player-dropdown', 'value'),
    Input('player-dropdown', 'options')
)
def set_player_value(available_options):
    return available_options[0]['value'] if available_options else None

@app.callback(
    Output('player-url', 'children'),
    Input('player-dropdown', 'value')
)
def update_player_url(selected_player):
    if selected_player:
        player_row = player_data[player_data['Name'] == selected_player]
        if not player_row.empty:
            url = player_row['Url'].iloc[0]
            return dcc.Link(url, href=url, target='_blank', style={'textDecoration': 'none'})
    return "Select a player to see URL."

@app.callback(
    Output('player-performance-board-div', 'children'),
    Input('player-dropdown', 'value')
)
def update_player_performance_board(selected_player):
    if selected_player:
        # Filter player data based on selected player
        player = player_data[player_data['Name'] == selected_player].iloc[0]

        # Extract relevant performance metrics
        runs_scored = player['RunsScored']
        batting_avg = player['BattingAVG']
        batting_sr = player['BattingS/R']
        centuries = player['100s']
        half_centuries = player['50s']
        fours = player['4s']
        sixes = player['6s']
        catches_taken = player['CatchesTaken']
        stumpings_made = player['StumpingsMade']
        ducks = player['Ducks']
        overs_bowled = player['Overs']
        maidens = player['Maidens']
        runs_conceded = player['RunsConceded']
        wickets_taken = player['Wickets']
        best_bowling = player['Best']
        bowling_avg = player['BowlingAVG']
        economy_rate = player['EconomyRate']
        bowling_sr = player['S/R']

        # Create HTML content to display player performance
        performance_content = [
            html.Div([
                html.Div([
                    html.P(f"Runs Scored: {runs_scored}"),
                    html.P(f"Batting Average: {batting_avg}"),
                    html.P(f"Batting Strike Rate: {batting_sr}"),
                    html.P(f"Centuries: {centuries}"),
                    html.P(f"Half-centuries: {half_centuries}"),
                ], style=card_style),
                html.Div([
                    html.P(f"Fours: {fours}"),
                    html.P(f"Sixes: {sixes}"),
                    html.P(f"Catches Taken: {catches_taken}"),
                    html.P(f"Stumpings Made: {stumpings_made}"),
                    html.P(f"Ducks: {ducks}"),
                ], style=card_style),
                html.Div([
                    html.P(f"Overs Bowled: {overs_bowled}"),
                    html.P(f"Maidens: {maidens}"),
                    html.P(f"Runs Conceded: {runs_conceded}"),
                    html.P(f"Wickets Taken: {wickets_taken}"),
                    html.P(f"Best Bowling: {best_bowling}"),
                ], style=card_style),
                html.Div([
                    html.P(f"Bowling Average: {bowling_avg}"),
                    html.P(f"Economy Rate: {economy_rate}"),
                    html.P(f"Bowling Strike Rate: {bowling_sr}"),
                ], style=card_style),
            ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center'}),
        ]

        return performance_content
    return "Select a player to see performance."


# Define app layout
if __name__ == '__main__':
    app.run_server(debug=True)
