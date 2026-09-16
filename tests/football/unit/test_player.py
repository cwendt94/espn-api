from types import SimpleNamespace
from unittest import TestCase

from espn_api.football.player import Player


def _card_player(transactions=None):
    return {
        'id': 1001,
        'fullName': 'Justin Jefferson',
        'defaultPositionId': 4,
        'eligibleSlots': [3, 4, 5, 23],
        'proTeamId': 16,
        'injuryStatus': 'ACTIVE',
        'lineupSlotId': 4,
        'player': {
            'id': 1001,
            'fullName': 'Justin Jefferson',
            'eligibleSlots': [3, 4, 5, 23],
            'proTeamId': 16,
            'injuryStatus': 'ACTIVE',
            'injured': False,
            'stats': [],
            'ownership': {'percentOwned': 99, 'percentStarted': 98},
        },
        'transactions': transactions or [],
    }


class PlayerTransactionHistoryTest(TestCase):
    def test_roster_player_has_empty_transactions(self):
        player = Player(_card_player(), 2022)
        self.assertEqual(player.transactions, [])

    def test_card_player_parses_transactions(self):
        team = SimpleNamespace(team_name='Vikes')
        player = Player(
            _card_player([{
                'teamId': 4,
                'type': 'TRADE_ACCEPT',
                'status': 'EXECUTED',
                'scoringPeriodId': 6,
                'relatedTransactionId': 'rel-1',
                'items': [{
                    'type': 'TRADE',
                    'playerId': 1001,
                    'fromTeamId': 2,
                    'toTeamId': 4,
                }],
            }]),
            2022,
            player_map={1001: 'Justin Jefferson'},
            get_team_data=lambda _: team,
        )

        self.assertEqual(len(player.transactions), 1)
        self.assertEqual(player.transactions[0].type, 'TRADE_ACCEPT')
        self.assertEqual(player.transactions[0].related_transaction_id, 'rel-1')
        self.assertEqual(player.transactions[0].items[0].player, 'Justin Jefferson')
        self.assertEqual(player.transactions[0].items[0].from_team_id, 2)
        self.assertEqual(player.transactions[0].items[0].to_team_id, 4)
