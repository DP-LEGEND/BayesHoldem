rank_values = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14
}

ranks = [
    "2", "3", "4", "5", "6", "7", "8",
    "9", "10", "J", "Q", "K", "A"
]

suits = [
    "spades",
    "hearts",
    "diamonds",
    "clubs"
]


def create_deck():
    deck = []

    for rank in ranks:
        for suit in suits:
            deck.append({
                "rank": rank,
                "suit": suit
            })

    return deck