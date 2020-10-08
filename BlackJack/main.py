# Mini-project #6 - Blackjack

try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
import random

CARD_SIZE = (72, 96)
CARD_CENTER = (36, 48)
card_images = simplegui.load_image("http://storage.googleapis.com/codeskulptor-assets/cards_jfitz.png")

CARD_BACK_SIZE = (72, 96)
CARD_BACK_CENTER = (36, 48)
card_back = simplegui.load_image("http://storage.googleapis.com/codeskulptor-assets/card_jfitz_back.png")

# initialize some useful global variables
in_play = False
outcome = ""
score = 0

# define globals for cards
SUITS = ('C', 'S', 'H', 'D')
RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K')
VALUES = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 10, 'Q': 10, 'K': 10}


class Card:
    def __init__(self, suit, rank):
        if (suit in SUITS) and (rank in RANKS):
            self.suit = suit
            self.rank = rank
        else:
            self.suit = None
            self.rank = None
            print
            "Invalid card: ", suit, rank

    def __str__(self):
        return self.suit + self.rank

    def get_suit(self):
        return self.suit

    def get_rank(self):
        return self.rank

    def draw(self, canvas, pos):
        card_loc = (CARD_CENTER[0] + CARD_SIZE[0] * RANKS.index(self.rank),
                    CARD_CENTER[1] + CARD_SIZE[1] * SUITS.index(self.suit))
        canvas.draw_image(card_images, card_loc, CARD_SIZE, [pos[0] + CARD_CENTER[0], pos[1] + CARD_CENTER[1]],
                          CARD_SIZE)


# define hand class
class Hand:
    def __init__(self):
        self.cards = []

    def __str__(self):
        return str(self.get_value())


    def add_card(self, card):
        self.cards.append(card)

    def get_value(self):
        value = 0
        ace = False
        for c in self.cards:
            value += VALUES[c.get_rank()]
            if c.get_rank() == 'A':
                ace = True
        if ace and value < 12:
            value += 10
        return value

    def draw(self, canvas, pos):
        for c in self.cards:
            pos[0] = pos[0] + CARD_SIZE[0] + 10
            c.draw(canvas, pos)


# define deck class
class Deck:
    def __init__(self):
        self.cards = []
        for suit in SUITS:
            for rank in RANKS:
                self.cards.append(Card(suit, rank))

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop()

    def __str__(self):
        st = ""
        for c in self.cards:
            st = st + str(c) + " "
        return "Deck contains " + st


# define event handlers for buttons
def deal():
    global outcome, in_play, player, dealer, score, my_deck
    if in_play:
        score -= 1
    outcome = ""
    my_deck = Deck()
    player = Hand()
    dealer = Hand()
    my_deck.shuffle()
    player.add_card(my_deck.deal_card())
    player.add_card(my_deck.deal_card())
    dealer.add_card(my_deck.deal_card())
    dealer.add_card(my_deck.deal_card())
    in_play = True


def hit():
    global outcome, in_play, player, score, my_deck
    if in_play:
        if player.get_value() <= 21:
            player.add_card(my_deck.deal_card())
            if player.get_value() > 21:
                outcome = "You have busted!"
                score -= 1
                in_play = False


def stand():
    global outcome, in_play, player, dealer, score, my_deck
    if in_play:
        while dealer.get_value() < 17:
            dealer.add_card(my_deck.deal_card())
        if dealer.get_value() > 21:
            outcome = "Daeler Busted! You Won!"
            score += 1
        elif dealer.get_value() < player.get_value():
            outcome = "You Won!"
            score += 1
        else:
            outcome = "You Lost!"
            score -= 1
        in_play = False


def reset():
    global score
    deal()
    score = 0


# draw handler
def draw(canvas):
    canvas.draw_line((0, 50), (800, 50), 2, '#32CD32')
    canvas.draw_line((0, 390), (800, 390), 5, '#32CD32')
    canvas.draw_line((0, 330), (800, 330), 5, '#32CD32')
    canvas.draw_text("BLACK JACK", [300, 45], 40, "#8B0000", "sans-serif")
    canvas.draw_text("The dealer wins ties and must stand on 17", [237, 70], 20, "#191970", "sans-serif")
    canvas.draw_text(outcome, [450, 370], 30, "#191970", "sans-serif")
    canvas.draw_text("Dealer", [50, 200], 35, "#8B0000", "sans-serif")
    canvas.draw_text("Player", [50, 530], 35, "#8B0000", "sans-serif")
    canvas.draw_text("Score " + str(score), [630, 120], 30, "#DCDCDC", "sans-serif")
    canvas.draw_text(str(player), [180, 528], 20, "#DCDCDC")
    if in_play:
        canvas.draw_text("Hit or stand?", [50, 370], 35, "#191970", "sans-serif")
    else:
        canvas.draw_text("New Deal?", [50, 370], 35, "#191970", "sans-serif")
        canvas.draw_text(str(dealer), [180, 200], 20, "#DCDCDC")
    player.draw(canvas, [-40, 400])
    dealer.draw(canvas, [-40, 220])
    if in_play:
        canvas.draw_image(card_back, CARD_BACK_CENTER, CARD_BACK_SIZE, (78, 268), (70, 94))


# initialization frame
frame = simplegui.create_frame("Blackjack", 800, 600)
frame.set_canvas_background("Green")

# create buttons and canvas callback
frame.add_button("Deal", deal, 150)
frame.add_button("Hit", hit, 150)
frame.add_button("Stand", stand, 150)
frame.add_label(" ")
frame.add_button("Reset", reset, 150)
frame.set_draw_handler(draw)

# get things rolling
deal()
frame.start()