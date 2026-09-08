import random
from cards import create_deck
from evaluator import determine_winner

def monte_carlo_equity(user_cards, community_cards, simulations):
    # Build a fresh full deck
    full_deck = create_deck()

    # Remove all cards we already know
    remaining_deck = full_deck.copy()
    known_cards = user_cards + community_cards
    community_cards_needed = 5 - len(community_cards)
    cards_needed = 2 + community_cards_needed

    for card in known_cards:
        remaining_deck.remove(card)

    wins = 0
    losses = 0
    ties = 0

    for i in range(simulations):
        sample = random.sample(remaining_deck, cards_needed)
        opponent_cards = sample[0:2]
        future_community = sample[2:]

        completed_community = community_cards + future_community

        result = determine_winner(
            user_cards,
            opponent_cards,
            completed_community
        )

        if result == 1:
            wins += 1

        elif result == 2:
            losses += 1

        else:
            ties += 1

    total = wins + losses + ties

    equity = (wins + 0.5 * ties) / total

    return {
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "total": total,
        "win_probability": wins / total,
        "loss_probability": losses / total,
        "tie_probability": ties / total,
        "equity": equity
    }



def exact_river_equity(user_cards, community_cards):
    # Build a fresh full deck
    full_deck = create_deck()

    # Remove all cards we already know
    remaining_deck = full_deck.copy()
    known_cards = user_cards + community_cards

    for card in known_cards:
        remaining_deck.remove(card)

    wins = 0
    losses = 0
    ties = 0

    # Generate every possible 2-card opponent hand
    for i in range(len(remaining_deck)):
        for j in range(i + 1, len(remaining_deck)):
            opponent_cards = [
                remaining_deck[i],
                remaining_deck[j]
            ]

            result = determine_winner(
                user_cards,
                opponent_cards,
                community_cards
            )

            if result == 1:
                wins += 1

            elif result == 2:
                losses += 1

            else:
                ties += 1

    total = wins + losses + ties

    equity = (wins + 0.5 * ties) / total

    return {
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "total": total,
        "win_probability": wins / total,
        "loss_probability": losses / total,
        "tie_probability": ties / total,
        "equity": equity
    }



def exact_turn_equity(user_cards, community_cards):
    # Build a fresh full deck
    full_deck = create_deck()

    # Remove known cards
    remaining_deck = full_deck.copy()
    known_cards = user_cards + community_cards

    for card in known_cards:
        remaining_deck.remove(card)

    wins = 0
    losses = 0
    ties = 0

    # Generate every possible opponent hand
    for i in range(len(remaining_deck)):
        for j in range(i + 1, len(remaining_deck)):

            opponent_cards = [
                remaining_deck[i],
                remaining_deck[j]
            ]

            # Remove opponent's cards
            remaining_after_opponent = remaining_deck.copy()

            for card in opponent_cards:
                remaining_after_opponent.remove(card)

            # Try every possible river card
            for river_card in remaining_after_opponent:

                completed_community = community_cards + [river_card]

                result = determine_winner(
                    user_cards,
                    opponent_cards,
                    completed_community
                )

                if result == 1:
                    wins += 1

                elif result == 2:
                    losses += 1

                else:
                    ties += 1

    total = wins + losses + ties

    equity = (wins + 0.5 * ties) / total

    return {
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "total": total,
        "win_probability": wins / total,
        "loss_probability": losses / total,
        "tie_probability": ties / total,
        "equity": equity
    }



def exact_flop_equity(user_cards, community_cards):
    # Build a fresh full deck
    full_deck = create_deck()

    remaining_deck = full_deck.copy()
    known_cards = user_cards + community_cards

    for card in known_cards:
        remaining_deck.remove(card)

    wins = 0
    losses = 0
    ties = 0

    for i in range(len(remaining_deck)):
        for j in range(i+1, len(remaining_deck)):
            pair = [remaining_deck[i], remaining_deck[j]]
            remaining_deck_after_opponent = remaining_deck.copy()
            for item in pair:
                remaining_deck_after_opponent.remove(item)

            for k in range(len(remaining_deck_after_opponent)):
                for l in range(k+1, len(remaining_deck_after_opponent)):
                    future_community = [remaining_deck_after_opponent[k], remaining_deck_after_opponent[l]]
                    completed_community = community_cards + future_community

                    result = determine_winner(
                        user_cards,
                        pair,
                        completed_community
                    )

                    if result == 1:
                        wins += 1

                    elif result == 2:
                        losses += 1

                    else:
                        ties += 1

    total = wins + losses + ties

    equity = (wins + 0.5 * ties) / total

    return {
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "total": total,
        "win_probability": wins / total,
        "loss_probability": losses / total,
        "tie_probability": ties / total,
        "equity": equity
    }




def bayesian_equity(user_cards, community_cards, hand_groups, posteriors, simulations):
    wins = 0
    losses = 0
    ties = 0

    # Build deck ONCE
    full_deck = create_deck()

    base_remaining_deck = full_deck.copy()

    for card in user_cards + community_cards:
        base_remaining_deck.remove(card)

    community_cards_needed = 5 - len(community_cards)

    for i in range(simulations):

        # Bayesian weighted strength selection
        strength = random.choices(
            ["WEAK", "MEDIUM", "STRONG", "VERY STRONG"],
            weights=[
                posteriors["WEAK"],
                posteriors["MEDIUM"],
                posteriors["STRONG"],
                posteriors["VERY STRONG"]
            ],
            k=1
        )[0]

        # Uniform exact hand within selected category
        opponent_cards = random.choice(
            hand_groups[strength]
        )

        # Fresh copy for this simulated world
        remaining_deck = base_remaining_deck.copy()

        for card in opponent_cards:
            remaining_deck.remove(card)

        future_community = random.sample(
            remaining_deck,
            community_cards_needed
        )

        completed_community = (
            community_cards + future_community
        )

        result = determine_winner(
            user_cards,
            opponent_cards,
            completed_community
        )

        if result == 1:
            wins += 1
        elif result == 2:
            losses += 1
        else:
            ties += 1

    total = wins + losses + ties

    equity = (wins + 0.5 * ties) / total

    return {
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "total": total,
        "win_probability": wins / total,
        "loss_probability": losses / total,
        "tie_probability": ties / total,
        "equity": equity
    }



def exact_bayesian_flop_equity(user_cards, community_cards, hand_groups, posteriors):
    total_bayesian_equity = 0

    full_deck = create_deck()

    # Remove user's cards and known flop
    base_remaining_deck = full_deck.copy()

    for card in user_cards + community_cards:
        base_remaining_deck.remove(card)

    # Go through each strength category
    for strength, opponent_hands in hand_groups.items():

        # Skip categories with no possible hands
        if len(opponent_hands) == 0:
            continue

        # Split this category's posterior probability
        # equally between its exact hands
        weight_per_hand = (
            posteriors[strength] / len(opponent_hands)
        )

        # Go through every exact opponent hand
        for opponent_cards in opponent_hands:

            remaining_deck = base_remaining_deck.copy()

            for card in opponent_cards:
                remaining_deck.remove(card)

            wins = 0
            losses = 0
            ties = 0

            # Enumerate every possible turn + river
            for i in range(len(remaining_deck)):
                for j in range(i + 1, len(remaining_deck)):

                    future_community = [
                        remaining_deck[i],
                        remaining_deck[j]
                    ]

                    completed_community = (
                        community_cards + future_community
                    )

                    result = determine_winner(
                        user_cards,
                        opponent_cards,
                        completed_community
                    )

                    if result == 1:
                        wins += 1

                    elif result == 2:
                        losses += 1

                    else:
                        ties += 1

            total = wins + losses + ties

            hand_equity = (
                wins + 0.5 * ties
            ) / total

            # Weight this exact hand by its Bayesian probability
            total_bayesian_equity += (
                hand_equity * weight_per_hand
            )

    return total_bayesian_equity