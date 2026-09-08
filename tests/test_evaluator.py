import sys
from pathlib import Path

# Allow imports from the BayesHoldem root directory
sys.path.append(str(Path(__file__).resolve().parents[1]))

from evaluator import (
    count_cards,
    evaluate_hand,
    compare_hands,
    determine_winner
)


def card(rank, suit):
    return {
        "rank": rank,
        "suit": suit
    }


def evaluate(player, community):
    rank_counts, suit_counts = count_cards(
        player,
        community
    )

    cards = player + community

    return evaluate_hand(
        cards,
        rank_counts,
        suit_counts
    )


# ============================================================
# HAND CATEGORY TESTS
# ============================================================

def test_high_card():
    player = [
        card("A", "spades"),
        card("J", "clubs")
    ]

    community = [
        card("9", "diamonds"),
        card("7", "hearts"),
        card("4", "clubs"),
        card("3", "spades"),
        card("2", "diamonds")
    ]

    result = evaluate(player, community)

    assert result == [
        "HIGH CARD",
        14, 11, 9, 7, 4
    ]


def test_pair():
    player = [
        card("A", "spades"),
        card("A", "clubs")
    ]

    community = [
        card("K", "diamonds"),
        card("Q", "hearts"),
        card("9", "clubs"),
        card("4", "spades"),
        card("2", "diamonds")
    ]

    result = evaluate(player, community)

    assert result == [
        "PAIR",
        14, 13, 12, 9
    ]


def test_two_pair():
    player = [
        card("A", "spades"),
        card("K", "clubs")
    ]

    community = [
        card("A", "diamonds"),
        card("K", "hearts"),
        card("9", "clubs"),
        card("4", "spades"),
        card("2", "diamonds")
    ]

    result = evaluate(player, community)

    assert result == [
        "TWO PAIR",
        14, 13, 9
    ]


def test_trips():
    player = [
        card("Q", "spades"),
        card("Q", "clubs")
    ]

    community = [
        card("Q", "diamonds"),
        card("A", "hearts"),
        card("10", "clubs"),
        card("5", "spades"),
        card("2", "diamonds")
    ]

    result = evaluate(player, community)

    assert result == [
        "TRIPS",
        12, 14, 10
    ]


def test_straight():
    player = [
        card("9", "spades"),
        card("8", "clubs")
    ]

    community = [
        card("7", "diamonds"),
        card("6", "hearts"),
        card("5", "clubs"),
        card("A", "spades"),
        card("2", "diamonds")
    ]

    result = evaluate(player, community)

    assert result == [
        "STRAIGHT",
        9
    ]


def test_wheel_straight():
    player = [
        card("A", "spades"),
        card("2", "clubs")
    ]

    community = [
        card("3", "diamonds"),
        card("4", "hearts"),
        card("5", "clubs"),
        card("K", "spades"),
        card("Q", "diamonds")
    ]

    result = evaluate(player, community)

    assert result == [
        "STRAIGHT",
        5
    ]


def test_flush():
    player = [
        card("A", "spades"),
        card("J", "spades")
    ]

    community = [
        card("9", "spades"),
        card("6", "spades"),
        card("3", "spades"),
        card("K", "hearts"),
        card("2", "diamonds")
    ]

    result = evaluate(player, community)

    assert result == [
        "FLUSH",
        14, 11, 9, 6, 3
    ]


def test_full_house():
    player = [
        card("K", "spades"),
        card("K", "clubs")
    ]

    community = [
        card("K", "diamonds"),
        card("9", "hearts"),
        card("9", "clubs"),
        card("4", "spades"),
        card("2", "diamonds")
    ]

    result = evaluate(player, community)

    assert result == [
        "FULL HOUSE",
        13, 9
    ]


def test_full_house_two_triplets():
    player = [
        card("K", "spades"),
        card("K", "clubs")
    ]

    community = [
        card("K", "diamonds"),
        card("9", "hearts"),
        card("9", "clubs"),
        card("9", "spades"),
        card("2", "diamonds")
    ]

    result = evaluate(player, community)

    assert result == [
        "FULL HOUSE",
        13, 9
    ]


def test_quads():
    player = [
        card("A", "spades"),
        card("A", "clubs")
    ]

    community = [
        card("A", "diamonds"),
        card("A", "hearts"),
        card("K", "clubs"),
        card("7", "spades"),
        card("2", "diamonds")
    ]

    result = evaluate(player, community)

    assert result == [
        "QUADS",
        14, 13
    ]


def test_straight_flush():
    player = [
        card("9", "spades"),
        card("8", "spades")
    ]

    community = [
        card("7", "spades"),
        card("6", "spades"),
        card("5", "spades"),
        card("A", "hearts"),
        card("2", "diamonds")
    ]

    result = evaluate(player, community)

    assert result == [
        "STRAIGHT FLUSH",
        9
    ]


# ============================================================
# TIE-BREAK TESTS
# ============================================================

def test_higher_pair_wins():
    hand1 = [
        "PAIR",
        14, 13, 12, 9
    ]

    hand2 = [
        "PAIR",
        13, 14, 12, 9
    ]

    assert compare_hands(
        hand1,
        hand2
    ) == 1


def test_pair_kicker_wins():
    hand1 = [
        "PAIR",
        14, 13, 10, 8
    ]

    hand2 = [
        "PAIR",
        14, 12, 10, 8
    ]

    assert compare_hands(
        hand1,
        hand2
    ) == 1


def test_two_pair_kicker_wins():
    hand1 = [
        "TWO PAIR",
        14, 13, 10
    ]

    hand2 = [
        "TWO PAIR",
        14, 13, 9
    ]

    assert compare_hands(
        hand1,
        hand2
    ) == 1


def test_identical_hands_tie():
    hand1 = [
        "STRAIGHT",
        10
    ]

    hand2 = [
        "STRAIGHT",
        10
    ]

    assert compare_hands(
        hand1,
        hand2
    ) == 0


# ============================================================
# END-TO-END WINNER TESTS
# ============================================================

def test_determine_winner_player_one():
    player1 = [
        card("A", "spades"),
        card("A", "clubs")
    ]

    player2 = [
        card("K", "spades"),
        card("K", "clubs")
    ]

    community = [
        card("Q", "diamonds"),
        card("9", "hearts"),
        card("7", "clubs"),
        card("4", "spades"),
        card("2", "diamonds")
    ]

    assert determine_winner(
        player1,
        player2,
        community
    ) == 1


def test_determine_winner_player_two():
    player1 = [
        card("A", "spades"),
        card("J", "clubs")
    ]

    player2 = [
        card("K", "spades"),
        card("K", "clubs")
    ]

    community = [
        card("Q", "diamonds"),
        card("9", "hearts"),
        card("7", "clubs"),
        card("4", "spades"),
        card("2", "diamonds")
    ]

    assert determine_winner(
        player1,
        player2,
        community
    ) == 2


def test_determine_winner_tie():
    player1 = [
        card("2", "spades"),
        card("3", "clubs")
    ]

    player2 = [
        card("4", "spades"),
        card("5", "clubs")
    ]

    community = [
        card("A", "diamonds"),
        card("K", "hearts"),
        card("Q", "clubs"),
        card("J", "spades"),
        card("10", "diamonds")
    ]

    assert determine_winner(
        player1,
        player2,
        community
    ) == 0