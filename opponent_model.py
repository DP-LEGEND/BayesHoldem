from cards import rank_values, create_deck
from evaluator import count_cards, evaluate_hand, hand_values

bet_likelihoods = {
    "WEAK": 0.20,
    "MEDIUM": 0.45,
    "STRONG": 0.70,
    "VERY STRONG": 0.90
}

def classify_starting_hand(card1, card2):
    rank1 = card1["rank"]
    rank2 = card2["rank"]

    # Pocket pair
    if rank1 == rank2:
        return rank1 + rank2

    # Put the higher rank first
    if rank_values[rank1] > rank_values[rank2]:
        high_rank = rank1
        low_rank = rank2
    else:
        high_rank = rank2
        low_rank = rank1

    # Determine suited or offsuit
    if card1["suit"] == card2["suit"]:
        suffix = "s"
    else:
        suffix = "o"

    return high_rank + low_rank + suffix



def classify_hand_strength(player_cards, community_cards):
    rank_count, suit_count = count_cards(player_cards, community_cards)
    cards = player_cards + community_cards
    result = evaluate_hand(cards, rank_count, suit_count)
    strength = hand_values[result[0]]

    if strength >= 3:
        return "VERY STRONG"

    elif strength == 2:
        return "STRONG"

    elif strength == 1:
        return "MEDIUM"

    else:
        return "WEAK"



def calculate_strength_priors(user_cards, community_cards):
    strength_counts = {
        "WEAK": 0,
        "MEDIUM": 0,
        "STRONG": 0,
        "VERY STRONG": 0
    }
    full_deck = create_deck()

    remaining_deck = full_deck.copy()
    known_cards = user_cards + community_cards

    for card in known_cards:
        remaining_deck.remove(card)

    for i in range(len(remaining_deck)):
        for j in range(i+1, len(remaining_deck)):
            strength = classify_hand_strength([remaining_deck[i], remaining_deck[j]], community_cards)
            strength_counts[strength] += 1

    total = sum(strength_counts.values())
    priors = {}
    for strength, count in strength_counts.items():
        priors[strength] = count / total

    return priors



def group_opponent_hands(user_cards, community_cards):
    hand_groups = {
        "WEAK": [],
        "MEDIUM": [],
        "STRONG": [],
        "VERY STRONG": []
    }

    # Build full deck
    full_deck = create_deck()
    
    # Remove cards we already know
    remaining_deck = full_deck.copy()
    known_cards = user_cards + community_cards

    for card in known_cards:
        remaining_deck.remove(card)

    # Generate every possible opponent hand
    for i in range(len(remaining_deck)):
        for j in range(i + 1, len(remaining_deck)):
            opponent_hand = [
                remaining_deck[i],
                remaining_deck[j]
            ]

            strength = classify_hand_strength(
                opponent_hand,
                community_cards
            )

            hand_groups[strength].append(opponent_hand)

    return hand_groups



def bayesian_update(priors, bet_likelihoods, action):
    posteriors = {}
    p_bet = 0
    for strength in priors:
        p_bet += bet_likelihoods[strength] * priors[strength]

    p_check = 1 - p_bet

    for strength in priors:
        if action == "BET":
            posteriors[strength] = (
                bet_likelihoods[strength] * priors[strength]
            ) / p_bet

        elif action == "CHECK":
            posteriors[strength] = (
            (1 - bet_likelihoods[strength]) * priors[strength]
            ) / p_check

        else:
            raise ValueError("Action must be BET or CHECK")

    return posteriors