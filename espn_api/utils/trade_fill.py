PLAYER_CARD_BATCH = 40


def player_card_transactions(data):
    """Raw transaction dicts from a kona_playercard player wrap."""
    if not isinstance(data, dict):
        return []
    candidates = [data.get("transactions")]
    inner = data.get("player")
    if isinstance(inner, dict):
        candidates.append(inner.get("transactions"))
    for raw in candidates:
        if isinstance(raw, list):
            return [row for row in raw if isinstance(row, dict)]
    return []


def player_transactions(data, transaction_class, player_map=None, get_team_data=None):
    names = player_map if player_map is not None else {}
    team_fn = get_team_data or (lambda _id: None)
    return [
        transaction_class(raw, names, team_fn) for raw in player_card_transactions(data)
    ]


def transaction_trade_legs(txn):
    return [
        item
        for item in (getattr(txn, "items", None) or [])
        if getattr(item, "type", None) == "TRADE"
    ]


def transaction_related_key(txn):
    return str(
        getattr(txn, "related_transaction_id", None) or getattr(txn, "id", None) or ""
    )


def transaction_id_key(txn):
    return str(getattr(txn, "id", None) or "")


def best_player_transactions(players):
    """Keep the TRADE_ACCEPT with the most TRADE legs per related id."""
    best = {}
    for player in players or []:
        for txn in getattr(player, "transactions", None) or []:
            if getattr(txn, "type", None) != "TRADE_ACCEPT":
                continue
            if getattr(txn, "status", None) != "EXECUTED":
                continue
            items = transaction_trade_legs(txn)
            if not items:
                continue
            key = transaction_related_key(txn)
            if not key:
                continue
            current = best.get(key)
            current_n = len(transaction_trade_legs(current)) if current else -1
            if current is None or len(items) > current_n:
                best[key] = txn
    return best


def fill_trade_accept_from_players(transactions, players, scoring_period=None):
    """Fill empty TRADE_ACCEPT rows from Player.transactions; append card-only deals."""
    best = best_player_transactions(players)
    seen = set()
    for txn in transactions:
        related = transaction_related_key(txn)
        txn_id = transaction_id_key(txn)
        if related:
            seen.add(related)
        if txn_id:
            seen.add(txn_id)
        if getattr(txn, "type", None) != "TRADE_ACCEPT":
            continue
        if transaction_trade_legs(txn):
            continue
        card = best.get(related) or best.get(txn_id)
        if not card:
            continue
        txn.items = list(card.items)
        if not getattr(txn, "related_transaction_id", None) and getattr(
            card, "related_transaction_id", None
        ):
            txn.related_transaction_id = card.related_transaction_id

    for key, card in best.items():
        card_id = transaction_id_key(card)
        if key in seen or card_id in seen:
            continue
        if (
            scoring_period is not None
            and getattr(card, "scoring_period", None) != scoring_period
        ):
            continue
        transactions.append(card)
        seen.add(key)
        if card_id:
            seen.add(card_id)
    return transactions


def chunked(values, size):
    for index in range(0, len(values), size):
        yield values[index : index + size]
