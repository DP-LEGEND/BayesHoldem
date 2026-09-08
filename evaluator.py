from cards import rank_values

hand_values = {
    "HIGH CARD": 0,
    "PAIR": 1,
    "TWO PAIR": 2,
    "TRIPS": 3,
    "STRAIGHT": 4,
    "FLUSH": 5,
    "FULL HOUSE": 6,
    "QUADS": 7,
    "STRAIGHT FLUSH": 8
}



def highest_rank(ranks):
    highest = ranks[0]
    for i in range(1, len(ranks)):
        if rank_values[ranks[i]] > rank_values[highest]:
            highest = ranks[i]

    return highest



def get_kickers(rank_counts, excluded_ranks):
    kickers = []

    for rank in rank_counts:
        if rank not in excluded_ranks:
            kickers.append(rank_values[rank])

    kickers.sort(reverse=True)

    return kickers



def count_cards(player, community):
    total = player + community
    length = len(total)
    rank_counts = {}
    suit_counts = {}
    for i in range(length):
        if total[i]["rank"] in rank_counts:
            rank_counts[total[i]["rank"]] += 1

        else:
            rank_counts[total[i]["rank"]] = 1

        if total[i]["suit"] in suit_counts:
            suit_counts[total[i]["suit"]] += 1

        else:
            suit_counts[total[i]["suit"]] = 1

    return rank_counts, suit_counts



def check_straight(rank_counts):
    ranks = []
    if len(rank_counts) >= 5:
        for rank in rank_counts:
            ranks.append(rank_values[rank])

        ranks.sort(reverse=True)
        if ranks[0] == 14:
            ranks.append(1)

        count = 1
        for i in range(1, len(ranks)):
            if ranks[i-1] - ranks[i] == 1:
                count += 1

                if count == 5:
                    return ["STRAIGHT", ranks[i-4]]
            else:
                count = 1

    return None



def check_flush(cards, suit_counts):
    flush_suit = None

    for suit, count in suit_counts.items():
        if count >= 5:
            flush_suit = suit
            break

    if flush_suit is None:
        return None

    flush_ranks = []

    for card in cards:
        if card["suit"] == flush_suit:
            flush_ranks.append(rank_values[card["rank"]])

    flush_ranks.sort(reverse=True)

    return ["FLUSH"] + flush_ranks[:5]



def check_straight_flush(cards, suit_counts):
    flush_suit = None

    for suit, count in suit_counts.items():
        if count >= 5:
            flush_suit = suit
            break

    if flush_suit is None:
        return None

    suited_rank_counts = {}

    for card in cards:
        if card["suit"] == flush_suit:
            rank = card["rank"]

            if rank in suited_rank_counts:
                suited_rank_counts[rank] += 1
            else:
                suited_rank_counts[rank] = 1

    straight = check_straight(suited_rank_counts)

    if straight is not None:
        return ["STRAIGHT FLUSH", straight[1]]

    return None



def check_high_card(rank_counts):
    high_cards = get_kickers(rank_counts, [])

    return ["HIGH CARD"] + high_cards[:5]



def evaluate_hand(cards, rank_counts, suit_counts):
    straight = check_straight(rank_counts)
    flush = check_flush(cards, suit_counts)
    straight_flush = check_straight_flush(cards, suit_counts)

    pairs = []
    trips = []
    quads = []

    for rank, count in rank_counts.items():
        if count == 2:
            pairs.append(rank)

        elif count == 3:
            trips.append(rank)

        elif count == 4:
            quads.append(rank)

    if straight_flush is not None:
        return straight_flush

    # FOUR OF A KIND
    if len(quads) != 0:
        kickers = get_kickers(rank_counts, [quads[0]])

        return ["QUADS",
                rank_values[quads[0]],
                kickers[0]]

    # FULL HOUSE — two sets of trips
    elif len(trips) == 2:
        if rank_values[trips[0]] > rank_values[trips[1]]:
            return ["FULL HOUSE",
                    rank_values[trips[0]],
                    rank_values[trips[1]]]

        else:
            return ["FULL HOUSE",
                    rank_values[trips[1]],
                    rank_values[trips[0]]]

    # FULL HOUSE — trips + pair(s)
    elif len(trips) == 1 and len(pairs) >= 1:
        highest_pair = highest_rank(pairs)

        return ["FULL HOUSE",
                rank_values[trips[0]],
                rank_values[highest_pair]]

    elif flush is not None:
        return flush

    elif straight is not None:
        return straight

    # THREE OF A KIND
    elif len(trips) == 1:
        kickers = get_kickers(rank_counts, [trips[0]])

        return ["TRIPS",
                rank_values[trips[0]]] + kickers[:2]

    # TWO PAIR
    elif len(pairs) >= 2:
        remaining_pairs = pairs.copy()

        highest = highest_rank(remaining_pairs)
        remaining_pairs.remove(highest)
        second_highest = highest_rank(remaining_pairs)

        kickers = get_kickers(
            rank_counts,
            [highest, second_highest]
        )

        return ["TWO PAIR",
                rank_values[highest],
                rank_values[second_highest],
                kickers[0]]

    # ONE PAIR
    elif len(pairs) == 1:
        kickers = get_kickers(rank_counts, [pairs[0]])

        return ["PAIR",
                rank_values[pairs[0]]] + kickers[:3]

    else:
        return check_high_card(rank_counts)



def compare_hands(hand1, hand2):
    # First compare the hand categories
    value1 = hand_values[hand1[0]]
    value2 = hand_values[hand2[0]]

    if value1 > value2:
        return 1

    elif value2 > value1:
        return 2

    # Same category: compare ranks/kickers in order
    for i in range(1, len(hand1)):
        if hand1[i] > hand2[i]:
            return 1

        elif hand2[i] > hand1[i]:
            return 2

    # Everything was identical
    return 0



def determine_winner(player1, player2, community):
    # Count ranks and suits for Player 1
    rank_counts1, suit_counts1 = count_cards(player1, community)

    # Count ranks and suits for Player 2
    rank_counts2, suit_counts2 = count_cards(player2, community)

    # Create each player's full 7-card list
    cards1 = player1 + community
    cards2 = player2 + community

    # Evaluate each player's best hand
    hand1 = evaluate_hand(cards1, rank_counts1, suit_counts1)
    hand2 = evaluate_hand(cards2, rank_counts2, suit_counts2)

    # Compare them
    return compare_hands(hand1, hand2)