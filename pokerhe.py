
def convert_old(hand):
    ranks = [x[0] for x in hand]
    suits = [x[1] for x in hand]

    h = "".join(ranks)

    if suits.count(suits[0]) != 5:
        h += "N" #off-suited
    else:
        h += "Y" #on-suited

    return "".join(sorted(h))



def convert(hand):
    ranks = [x[0] for x in hand]
    cards = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
            "9": 9, "T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
    ranks = sorted([cards[i] for i in ranks])
    suits = [x[1] for x in hand]


    if suits.count(suits[0]) == 5: #on-suited
        if ranks == ranks == [2,3,4,5,14]:
            return (1,5,4,3,2,14)
        if ranks == [ranks[0] + i for i in range(5)]: #straight flush
            return (1,max(ranks))

        else: #flush
            return tuple([4] + ranks[::-1])

    else: #off-suited
        counts = sorted([ranks.count(i) for i in set(ranks)])
        rankcounts = sorted(list(set(ranks)),key = lambda x: (ranks.count(x),x))

        if len(set(ranks)) == 1: #five of a kind
            hand_value = 0

        elif len(set(ranks)) == 2:
            if counts == [1,4]: #four of a kind
                hand_value = 2

            elif counts == [2,3]: #full house
                hand_value = 3

        elif len(set(ranks)) == 3:
            if counts == [1,1,3]: #three of a kind
                hand_value = 6
            if counts == [1,2,2]: #two pair
                hand_value = 7

        elif len(set(ranks)) == 4: #one pair
            hand_value = 8

        else:
            if ranks == [2, 3, 4, 5, 14]:
                return (5, 5, 4, 3, 2, 14)
            if ranks == [ranks[0] + i for i in range(5)]:  #straight
                hand_value = 5
            else: #shit
                hand_value = 9

        return tuple([hand_value] + rankcounts[::-1])



def name(hand):
    '''
       0 - five of a kind
       1 - straight flush
       2 - four of a kind
       3 - full house
       4 - flush
       5 - straight
       6 - three of a kind
       7 - two pair
       8 - pair
       9 - shit
       '''

    rank_names = ["","","Deuce","Trey","Four","Five","Six","Seven","Eight","Nine","Ten","Jack","Queen","King","Ace"]

    plural = lambda x: rank_names[hand[x]] + "s"
    single = lambda x: rank_names[hand[x]]

    if hand[0] == 0:
        return "Five " + plural(1)
    elif hand[0] == 1:
        if hand[1] == 14:
            return "Royal Flush"
        else:
            return single(1) + "-High Straight Flush"

    elif hand[0] == 2:
        return "Four " + plural(1)

    elif hand[0] == 3:
        return plural(1) + " Full Over " + plural(2)

    elif hand[0] == 4:
        return single(1) + "-High Flush"

    elif hand[0] == 5:
        return single(1) + "-High Straight"

    elif hand[0] == 6:
        return "Three " + plural(1)

    elif hand[0] == 7:
        return plural(1) + " and " + plural(2)

    elif hand[0] == 8:
        return "Pair of " + plural(1)

    elif hand[0] == 9:
        if hand == [9,7,5,4,3,2]:
            return "Kansas City"
        else:
            return single(1) + "-High"