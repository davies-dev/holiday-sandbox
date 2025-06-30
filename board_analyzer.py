# board_analyzer.py

def analyze_board(cards: list[str]) -> set[str]:
    """
    Analyzes a list of board cards and returns a set of texture tags.
    e.g., ['Ah', 'Kh', '2h'] -> {'monotone', 'broadway_present', 'A-high'}
    """
    if not cards:
        return set()

    ranks = "23456789TJQKA"
    rank_map = {r: i for i, r in enumerate(ranks)}
    
    card_ranks = sorted([rank_map[c[0]] for c in cards], reverse=True)
    card_suits = [c[1] for c in cards]

    textures = set()

    # 1. Suit-based textures
    unique_suits = set(card_suits)
    suit_count = len(unique_suits)
    if suit_count == 1:
        textures.add('monotone')
    elif suit_count == 2:
        textures.add('two_tone')
    elif suit_count == 3:
        textures.add('rainbow')

    # 2. Pair-based textures
    rank_counts = {}
    for rank in card_ranks:
        rank_counts[rank] = rank_counts.get(rank, 0) + 1
    
    if 4 in rank_counts.values():
        textures.add('quads')
    elif 3 in rank_counts.values():
        textures.add('trips')
        if 2 in rank_counts.values():
            textures.add('full_house')
    elif list(rank_counts.values()).count(2) == 2:
        textures.add('two_pair')
    elif 2 in rank_counts.values():
        textures.add('paired')
    
    # 3. High card textures
    if card_ranks:
        highest_rank_char = ranks[card_ranks[0]]
        textures.add(f'{highest_rank_char}-high')

    # 4. Broadway textures (T, J, Q, K, A)
    broadway_count = sum(1 for r in card_ranks if r >= rank_map['T'])
    if len(cards) >= 3:  # Only apply broadway logic for 3+ cards
        if broadway_count == len(cards):
            textures.add('broadway_heavy')
        elif broadway_count >= 2:
            textures.add('broadway_present')

    return textures 