# Mini Project #4 - Memory

# Install SimpleGUICS2Pygame
# $ python -m pip install SimpleGUICS2Pygame
try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
import random

CARD_WIDTH = 50
CARD_HEIGHT = 100


def new_game():
    global deck, expose, state, card1, card2, curentcard, turns, text_label
    deck = []
    l1 = range(8)
    l2 = range(8)
    deck.extend(l1)
    deck.extend(l2)
    random.shuffle(deck)
    expose = []
    for lc in range(len(deck)):
        expose.append(False)
    state = 0
    card1 = 0
    card2 = 0
    curentcard = 0
    turns = 0
    label.set_text("Turns = 0")  # need that for restart game


# define event handlers
def mouseclick(pos):
    global expose, state, card1, card2, curentcard, turns

    pos_click = pos[0] // 50

    if expose[pos_click] == False:
        card2 = card1
        card1 = curentcard
        curentcard = pos_click
        # main logic
        if state == 0:
            state = 1
            expose[pos_click] = True
            card1 = pos_click
        elif state == 1:
            state = 2
            expose[pos_click] = True
            card2 = pos_click
        else:
            if deck[card1] != deck[card2]:
                expose[card1] = False
                expose[card2] = False
            state = 1
            expose[pos_click] = True
            turns += 1
            text_label = "Turns = " + str(turns)
            label.set_text(text_label)


def draw(canvas):
    posx = 0
    i = 0
    for cards in deck:
        # draw the deck
        canvas.draw_text(str(cards), (posx + 10, 70), 70, "White")
        # cover the deck, or show the cards if they are exposed
        if expose[i] == False:
            canvas.draw_polygon(
                [(posx, 0), (posx + CARD_WIDTH, 0), (posx + CARD_WIDTH, CARD_HEIGHT), (posx, CARD_HEIGHT)], 1, "Red",
                "Green")
        posx += CARD_WIDTH
        i += 1

frame = simplegui.create_frame("Memory", 800, 100)
frame.add_button("Reset", new_game)
label = frame.add_label("Turns = 0")

frame.set_mouseclick_handler(mouseclick)
frame.set_draw_handler(draw)

# get things rolling
new_game()
frame.start()
