"""
Live validation script — tests all new functionality against a real ESPN league.
Run with: python live_validate.py
"""
from datetime import datetime
from espn_api.baseball import League

LEAGUE_ID = 172485424
YEAR = 2026
ESPN_S2 = "AECS1B4%2FtSyHNLY51yM9xCcNSC8VLCnDrpKP8MHwBXNEsiaK6bxOP3hh0znGC3q%2Fv84es1vIf9C2rHVBek8XHV8f2C89TGT2lSPjrGISZ%2FPdfQrNe0pWsfq5Vg7pnaguOX%2BpEHK%2BMPy2Jf%2FZFbsn5RGlwrYYDWELRwNpxekgrdwwVFcfqGc6ceSZiQzTZC4IJpGj1pDJDfZuanMZ39UlXK0MesWDe7gKa7SPXpKV%2FAZLPiNdxH7GP0J7AKyEnxD%2FZDc30WRwObpLtIrtZ2jAtp33jWwSVEOyeznqYFV8ZpS5qA%3D%3D"
SWID = "{9C54CF32-99DC-4BF4-BF08-425534175CB8}"

PASS = "  [PASS]"
FAIL = "  [FAIL]"

failures = []

def check(label, value, condition, display=True):
    ok = bool(condition)
    status = PASS if ok else FAIL
    if display:
        print(f"{status} {label}: {value!r}")
    if not ok:
        failures.append(label)
    return ok

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


print("Connecting to ESPN league...")
league = League(league_id=LEAGUE_ID, year=YEAR, espn_s2=ESPN_S2, swid=SWID)
print(f"Connected: {league.settings.name} ({len(league.teams)} teams)\n")


# ── Settings ─────────────────────────────────────────────────────────────────
section("Settings")
s = league.settings
check("position_slot_counts is dict",       s.position_slot_counts, isinstance(s.position_slot_counts, dict))
check("acquisition_limit",                  s.acquisition_limit,    s.acquisition_limit is not None)
check("matchup_acquisition_limit",          s.matchup_acquisition_limit, s.matchup_acquisition_limit is not None)
check("matchup_limit_per_scoring_period",   s.matchup_limit_per_scoring_period, s.matchup_limit_per_scoring_period is not None)
check("minimum_bid",                        s.minimum_bid,          s.minimum_bid is not None)
check("waiver_process_days is list",        s.waiver_process_days,  isinstance(s.waiver_process_days, list))
check("waiver_process_hour",                s.waiver_process_hour,  s.waiver_process_hour is not None)
check("trade_revision_hours",               s.trade_revision_hours, s.trade_revision_hours is not None)
check("faab is bool",                       s.faab,                 isinstance(s.faab, bool))
check("acquisition_budget",                 s.acquisition_budget,   s.acquisition_budget is not None)


# ── Teams ─────────────────────────────────────────────────────────────────────
section("Teams")
team = league.teams[0]
check("wins",                   team.wins,                    isinstance(team.wins, int))
check("losses",                 team.losses,                  isinstance(team.losses, int))
check("ties",                   team.ties,                    isinstance(team.ties, int))
check("points_for",             team.points_for,              isinstance(team.points_for, float))
check("points_against",         team.points_against,          isinstance(team.points_against, float))
check("streak_type",            team.streak_type,             isinstance(team.streak_type, str))
check("streak_length",          team.streak_length,           isinstance(team.streak_length, int))
check("home_wins",              team.home_wins,               isinstance(team.home_wins, int))
check("home_losses",            team.home_losses,             isinstance(team.home_losses, int))
check("away_wins",              team.away_wins,               isinstance(team.away_wins, int))
check("away_losses",            team.away_losses,             isinstance(team.away_losses, int))
check("division_wins",          team.division_wins,           isinstance(team.division_wins, int))
check("division_losses",        team.division_losses,         isinstance(team.division_losses, int))
check("current_projected_rank", team.current_projected_rank,  team.current_projected_rank is not None)
check("waiver_rank",            team.waiver_rank,             team.waiver_rank is not None)
check("points (live week)",     team.points,                  isinstance(team.points, (int, float)))

print("\n  Standings (wins / losses / PF / PA):")
for t in sorted(league.teams, key=lambda t: -t.wins):
    print(f"    {t.team_name:<35} {t.wins}-{t.losses}  PF:{t.points_for}  PA:{t.points_against}  streak:{t.streak_length}{t.streak_type[0]}")


# ── Roster Player ─────────────────────────────────────────────────────────────
section("Player (roster)")
roster_player = league.teams[0].roster[0]
p = roster_player
check("name",                   p.name,                 isinstance(p.name, str) and p.name)
check("first_name",             p.first_name,           isinstance(p.first_name, str))
check("last_name",              p.last_name,            isinstance(p.last_name, str))
check("active is bool",         p.active,               isinstance(p.active, bool))
check("droppable is bool",      p.droppable,            isinstance(p.droppable, bool))
check("keeper_value",           p.keeper_value,         p.keeper_value is not None)
check("keeper_value_future",    p.keeper_value_future,  p.keeper_value_future is not None)
check("lineup_locked is bool",  p.lineup_locked,        isinstance(p.lineup_locked, bool))
check("roster_locked is bool",  p.roster_locked,        isinstance(p.roster_locked, bool))
check("trade_locked is bool",   p.trade_locked,         isinstance(p.trade_locked, bool))
check("on_team_id",             p.on_team_id,           p.on_team_id is not None)
check("percent_owned",          p.percent_owned,        isinstance(p.percent_owned, float))
check("percent_owned_change",   p.percent_owned_change, p.percent_owned_change is not None)
check("adp",                    p.adp,                  p.adp is not None)
check("auction_value",          p.auction_value,        p.auction_value is not None)
check("draft_ranks is dict",    p.draft_ranks,          isinstance(p.draft_ranks, dict))
check("acquisitionDate",        p.acquisitionDate,      p.acquisitionDate is not None)


# ── player_info (player card) ─────────────────────────────────────────────────
section("player_info (card) — Spencer Schwellenbach")
pi = league.player_info(name="Spencer Schwellenbach")
check("name",               pi.name,            pi.name == "Spencer Schwellenbach")
check("jersey",             pi.jersey,          pi.jersey is not None)
check("laterality",         pi.laterality,      pi.laterality is not None)
check("stance",             pi.stance,          pi.stance is not None)
check("adp",                pi.adp,             pi.adp is not None)
check("adp_change",         pi.adp_change,      pi.adp_change is not None)
check("auction_value",      pi.auction_value,   pi.auction_value is not None)
check("auction_value_change", pi.auction_value_change, pi.auction_value_change is not None)
check("draft_ranks",        pi.draft_ranks,     isinstance(pi.draft_ranks, dict) and pi.draft_ranks)
check("last_news_date",     pi.last_news_date,  isinstance(pi.last_news_date, datetime))
check("season_outlook",     pi.season_outlook,  isinstance(pi.season_outlook, str) and pi.season_outlook)

print(f"\n  season_outlook preview: {pi.season_outlook[:100]}...")


# ── player_info batch ─────────────────────────────────────────────────────────
section("player_info (batch) — Nick Ramirez + Jason Adam")
batch = league.player_info(playerId=[32140, 32145])
check("returns list",       batch,              isinstance(batch, list))
check("two players",        len(batch),         len(batch) == 2)
check("player names",       [p.name for p in batch], all(p.name for p in batch))


# ── Transactions ──────────────────────────────────────────────────────────────
section("Transactions")
txns = league.transactions()
check("returns list", txns, isinstance(txns, list))
if not txns:
    print("  (no transactions in current scoring period — skipping field checks)")
else:
    t = txns[0]
    check("type is str",        t.type,             isinstance(t.type, str))
    check("date is datetime",   t.date,             isinstance(t.date, datetime))
    check("isPending is bool",  t.isPending,        isinstance(t.isPending, bool))
    check("rating",             t.rating,           t.rating is not None)
    check("execution_type",     t.execution_type,   t.execution_type is not None)
    check("has items",          t.items,            len(t.items) > 0)
    item = t.items[0]
    check("item.player_name",   item.player_name,   item.player_name)
    check("item.isKeeper bool", item.isKeeper,      isinstance(item.isKeeper, bool))
    check("item.fromLineupSlotId", item.fromLineupSlotId, item.fromLineupSlotId is not None)
    check("item.toLineupSlotId",   item.toLineupSlotId,   item.toLineupSlotId is not None)

    print("\n  Sample transactions:")
    for txn in txns[:3]:
        print(f"    {txn}  |  date={txn.date}  rating={txn.rating}  exec={txn.execution_type}")
        i = txn.items[0]
        print(f"      item: {i.player_name}  keeper={i.isKeeper}  slots={i.fromLineupSlotId}->{i.toLineupSlotId}")


# ── Draft ─────────────────────────────────────────────────────────────────────
section("Draft")
check("draft list populated", len(league.draft), len(league.draft) > 0)
pick = league.draft[0]
check("pick round",         pick.round_num,     pick.round_num is not None)
check("pick number",        pick.round_pick,    pick.round_pick is not None)
check("pick player name",   pick.playerName,    isinstance(pick.playerName, str) and pick.playerName)
check("pick team",          pick.team,          pick.team is not None)
check("pick keeper status", pick.keeper_status, isinstance(pick.keeper_status, bool))
print(f"\n  First 3 picks:")
for pick in league.draft[:3]:
    print(f"    R{pick.round_num} P{pick.round_pick}: {pick.playerName} → {pick.team}  keeper={pick.keeper_status}")


# ── Roto Box Scores ───────────────────────────────────────────────────────────
section("Roto Box Scores (POINTS_ESPN_LEAGUE_ID)")
ROTO_LEAGUE_ID = 682009972
roto_league = League(league_id=ROTO_LEAGUE_ID, year=YEAR, espn_s2=ESPN_S2, swid=SWID)
check("scoring_type is ROTO", roto_league.scoring_type, roto_league.scoring_type == 'ROTO')

from espn_api.baseball.box_score import RotoBoxScore
roto_bs = roto_league.box_scores()
check("box_scores() returns list",    roto_bs,    isinstance(roto_bs, list))
check("entries are RotoBoxScore",     roto_bs[0], isinstance(roto_bs[0], RotoBoxScore))

roto = roto_bs[0]
check("matchup_period set",           roto.matchup_period, roto.matchup_period is not None)
check("teams list len == league size",len(roto.teams),     len(roto.teams) == len(roto_league.teams))

entry = roto.teams[0]
check("entry has team object",        entry['team'],        hasattr(entry['team'], 'team_name'))
check("entry has total_points float", entry['total_points'],isinstance(entry['total_points'], float))
check("entry has stats dict",         entry['stats'],       isinstance(entry['stats'], dict) and entry['stats'])
check("entry has lineup list",        entry['lineup'],      isinstance(entry['lineup'], list))

# Verify each stat has score + rank
first_stat = next(iter(entry['stats'].values()))
check("stat has score key",           first_stat,           'score' in first_stat)
check("stat has rank key",            first_stat,           'rank' in first_stat)
check("rank is numeric",              first_stat['rank'],   isinstance(first_stat['rank'], (int, float)))

print("\n  Category ranks (sorted by total roto pts):")
stat_names = list(entry['stats'].keys())
print(f"  {'Team':<35} {'Total':>7}  " + "  ".join(f"{s:>5}" for s in stat_names[:8]))
for e in sorted(roto.teams, key=lambda x: -x['total_points']):
    name = e['team'].team_name
    ranks = "  ".join(f"{e['stats'][s]['rank']:>5.1f}" for s in stat_names[:8])
    print(f"  {name:<35} {e['total_points']:>7.1f}  {ranks}")


# ── Summary ───────────────────────────────────────────────────────────────────
section("Summary")
total = 80 - len(failures)  # rough count
if failures:
    print(f"  FAILURES ({len(failures)}):")
    for f in failures:
        print(f"    - {f}")
else:
    print("  All checks passed!")
