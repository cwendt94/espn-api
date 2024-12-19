import pandas as pd
from espn_api.football import League


'''
Algorithm: Draft Score (Scaled) ->  Value Added From Acquisitions (Straight Addition) -> Lineup Setting  -> (Bench Output)
'''
league_id = 44356805
year = 2024
swid = '{F8014DC0-556B-4952-AC13-98FA88F24081}'
espn_s2 = 'AEB%2BnXVSBDwR0k6uRFDJz%2Ft73KjhXlHta8mtA05%2BlW0fVF7boPlz6%2FJK4J71B57S%2FvAYDQMA%2B1FoZU%2Bhf7oU2ybOi7%2BWtzHPiS7wQwEhh9WqKfUt6wKKklb9KzHvkuhxlro%2FSLUsZkaWpaW51ckTjN9v9sVFVzSQt3%2FN6deYEs4AbwJJxEq%2Bx6sd4bWpLxgRkMSyX5%2FXyp5xb1P6sv%2FWdxL2uVuH4gdyZ%2FHxxrnqTQuaYMZCFQyBa%2Fc5uU56GclYq3AEeJEth01IljeokzoQe1D%2FFHrT3ajd0hAZvZu3m1iLOudkf49cIa16gaRVxo1x710%3D'




league = League(league_id=league_id, year=year,swid=swid,espn_s2=espn_s2)
league.fetch_league()
league.refresh_draft()
print(league.draftEvaluation())
