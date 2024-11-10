import pygame, sys, random


# colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (0, 255, 255)
MAGENTA = (255, 0, 255)
TURQUOISE = (255, 255, 0)

# window settings
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 900
WINDOW_CAPTION = "Mystic Tarot Card Game Battler Thingmy"


def draw_text(surface, text, colour, size, centre) -> pygame.Rect:
    font = pygame.font.Font("freesansbold.ttf", size)
    text_surface = font.render(text, True, colour)
    text_rect = text_surface.get_rect(center=centre)
    surface.blit(text_surface, text_rect)
    return text_rect

MAX_CARDS = 20
MAX_ARCANA = 10
MAX_GENERIC = 10
assert MAX_CARDS - MAX_ARCANA - MAX_GENERIC == 0, f"arcana max and generic max MUST add to {MAX_CARDS}"
STARTING_HAND_CARD_COUNT = 5
MAX_HEALTH = 10

class Tooltip:
    def __init__(self, upright_text, reversed_text, upright):
        self.upright_text = upright_text
        self.reversed_text = reversed_text
        self.upright = upright
        self.upright_colour = GREEN if upright else WHITE
        self.reversed_colour = GREEN if not upright else WHITE

        self.font = pygame.font.Font("freesansbold.ttf", 14)
        self.upright_word_text_surface = self.font.render("Upright:", True, self.upright_colour)
        self.reversed_word_text_surface = self.font.render("Reversed:", True, self.reversed_colour)
        self.upright_text_surface = self.font.render(self.upright_text, True, self.upright_colour)
        self.reversed_text_surface = self.font.render(self.reversed_text, True, self.reversed_colour)
        self.upright_text_rect = self.upright_text_surface.get_rect()
        self.reversed_text_rect = self.reversed_text_surface.get_rect()
        self.upright_word_text_rect = self.upright_word_text_surface.get_rect()
        self.reversed_word_text_rect = self.reversed_word_text_surface.get_rect()
        self.box_rect = pygame.Rect(0, 0, max(self.upright_text_rect.width, self.reversed_text_rect.width), self.upright_text_rect.height + self.reversed_text_rect.height + self.upright_word_text_rect.height + self.reversed_word_text_rect.height)

    def draw(self, surface, mouse_pos):
        if self.box_rect.width > WINDOW_WIDTH - mouse_pos[0]:
            self.box_rect.bottomright = mouse_pos
        else:
            self.box_rect.bottomleft = mouse_pos

        self.reversed_text_rect.bottomleft = self.box_rect.bottomleft
        self.reversed_word_text_rect.bottomleft = self.reversed_text_rect.topleft
        self.upright_text_rect.bottomleft = self.reversed_word_text_rect.topleft
        self.upright_word_text_rect.bottomleft = self.upright_text_rect.topleft

        pygame.draw.rect(surface, BLACK, self.box_rect)
        surface.blit(self.upright_word_text_surface, self.upright_word_text_rect)
        surface.blit(self.upright_text_surface, self.upright_text_rect)
        surface.blit(self.reversed_word_text_surface, self.reversed_word_text_rect)
        surface.blit(self.reversed_text_surface, self.reversed_text_rect)


class Competitor:
    def __init__(self):
        self.deck = []
        self.hand = []

        self.max_health = MAX_HEALTH
        self.health = self.max_health
        self.health_icon_image = pygame.image.load("images/heart.png")
        self.emptyhealth_icon_image = pygame.image.load("images/empty-heart.png")
        self.health_icon_image = pygame.transform.scale(self.health_icon_image, (39, 36))
        self.emptyhealth_icon_image = pygame.transform.scale(self.emptyhealth_icon_image, (39, 36))
        self.health_icon_rect = self.health_icon_image.get_rect()

        self.opponent = None

        self.deck_image = pygame.image.load("images/card-back.jpg")
        self.deck_image = pygame.transform.scale(self.deck_image, (100, 200))
        self.deck_rect = self.deck_image.get_rect()
        self.deck_card_count_y_offset = 0

        self.num_cards_to_draw_this_turn = 1
        self.num_cards_to_draw_next_turn = 1
        self.num_cards_to_play_this_turn = 1
        self.num_cards_to_play_next_turn = 1

        self.is_next_card_forced = False
        self.is_next_card_halved = False
        self.is_next_card_doubled = False
        self.is_next_card_blocked = False
        self.is_next_card_reversed = False

        self.is_computer = False

        self.has_won = False
        self.playing_turn = False

        self.init_deck()

    def init_deck(self):
        for i in range(MAX_ARCANA):
            self.deck.append(random.choice(ALL_ARCANA_CARDS))

        for i in range(MAX_GENERIC):
            self.deck.append(random.choice(ALL_GENERIC_CARDS))

        random.shuffle(self.deck)

    def init_hand(self):
        # give 5 starting cards from the deck to start off with
        for i in range(STARTING_HAND_CARD_COUNT):
            self.draw_card()
        
    def start_turn(self):
        # called at the start of the turn only once
        self.playing_turn = True
        self.num_cards_to_play_this_turn = self.num_cards_to_play_next_turn
        self.num_cards_to_play_next_turn = 1

        # auto card drawing
        # for i in range(self.num_cards_to_draw_next_turn):
        #     self.hand.append(self.deck[0])
        #     self.deck = self.deck[1:]

        # manual card drawing
        self.num_cards_to_draw_this_turn = self.num_cards_to_play_next_turn
        self.num_cards_to_draw_next_turn = 1

        if self.is_next_card_forced:
            for i in range(self.num_cards_to_play_this_turn):
                # all cards played are random :(
                card = random.choice(self.hand)
                self.play_card(card)

    def draw_card(self):
        # take the top card from the deck
        self.num_cards_to_draw_this_turn -= 1
        self.hand.append(self.deck[0](random.choice((True, False)), self.opponent, self))
        self.deck = self.deck[1:]

    def play_card(self, card):
        self.num_cards_to_play_this_turn -= 1
        self.hand.remove(card)
        self.deck.append(type(card))  # recycle card
        if not self.is_next_card_blocked:
            # only properly play the card if it hasn't been blocked
            card.play()
        else:
            self.is_next_card_blocked = False

    def finish_turn(self):
        self.playing_turn = False
        self.num_cards_to_play_this_turn = 1
        self.num_cards_to_draw_this_turn = 1
        self.opponent.start_turn()

    def update(self): # decide whether they finished their turn
        # clamp health to max health
        self.health = min(self.health, self.max_health)

        # check if done all card moves
        if self.num_cards_to_draw_this_turn <= 0 and self.num_cards_to_play_this_turn <= 0:
            self.finish_turn()

        # another turn ending condition for time limit running out

        # check if dead
        if self.health <= 0:
            self.opponent.has_won = True

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()

        # draw the deck
        if len(self.deck) > 0:
            draw_text(surface, str(len(self.deck)), WHITE, 36, (self.deck_rect.centerx, self.deck_rect.centery + self.deck_card_count_y_offset))
            surface.blit(self.deck_image, self.deck_rect)

            if self.deck_rect.collidepoint(mouse_pos) and self.playing_turn and self.num_cards_to_draw_this_turn > 0:
                pygame.draw.rect(surface, RED, self.deck_rect, width=3)

        # draw the hand
        for i in range(len(self.hand)):
            card = self.hand[i]
            if not self.is_computer:
                card.rect.left = self.deck_rect.right + i * card.rect.width + 10 * (i + 1)
                card.rect.y = self.deck_rect.y

                surface.blit(card.image, card.rect)

                if card.rect.collidepoint(mouse_pos) and self.playing_turn and self.num_cards_to_play_this_turn > 0:
                    pygame.draw.rect(surface, RED, card.rect, width=3)
            elif self.is_computer:
                if card.is_hidden:
                    rect = pygame.Rect(0, self.deck_rect.y, self.deck_rect.width, self.deck_rect.height)
                    rect.right = self.deck_rect.left - i * self.deck_rect.width - 10 * (i + 1)
                    surface.blit(self.deck_image, rect)
                else:
                    rect = pygame.Rect(0, self.deck_rect.y, self.deck_rect.width, self.deck_rect.height)
                    rect.right = self.deck_rect.left - i * self.deck_rect.width - 10 * (i + 1)
                    surface.blit(card.image, rect)

        if not self.is_computer:
            for card in self.hand:
                # render a tooltip for the card
                if card.rect.collidepoint(mouse_pos):
                    card.tooltip.draw(surface, mouse_pos)

        # draw the health and lives
        for i in range(self.health):
            # print(self.health)
            rect = pygame.Rect(0, self.health_icon_rect.y, self.health_icon_rect.width, self.health_icon_rect.height)
            rect.left = self.health_icon_rect.left + i * self.health_icon_rect.width
            surface.blit(self.health_icon_image, rect)


class Player(Competitor):
    def __init__(self):
        super().__init__()
        self.deck_rect.bottomleft = (20, WINDOW_HEIGHT - 20)
        self.deck_card_count_y_offset = -125
        self.health_icon_rect.top = WINDOW_HEIGHT - 300

    def handle_mouse_click(self, mouse_pos):
        # saves having all the clicky logic in the main function, plus player is only thing that takes clicky input
        # only gets called if player is playing their turn
        if self.deck_rect.collidepoint(mouse_pos) and self.num_cards_to_draw_this_turn > 0:
            # draw a card
            self.draw_card()

        for card in self.hand.copy():
            if card.rect.collidepoint(mouse_pos) and self.num_cards_to_play_this_turn > 0:
                # play the clicked card
                self.play_card(card)

class Computer(Competitor):
    def __init__(self):
        super().__init__()
        self.move_timer = 0
        self.revealed_cards = 0
        self.card_to_play = None

        self.deck_rect.topright = (WINDOW_WIDTH - 20, 20)
        self.deck_card_count_y_offset = 125
        self.is_computer = True
        self.health_icon_rect.bottom = 300

    def have_turn(self, dt):
        # computer turn logic
        # will sleep briefly between moves so player can process what they're doing

        # general algorithm (in no particular order)
        # draw a card
        # if a card dealing more damage than player has health, play it
        # if self health less than a threshold, heal if available
        # if at max health, try not to play healing card

        # currently plays randomly
        self.move_timer += dt
        if self.move_timer >= 0.8:
            self.move_timer = 0

            if self.num_cards_to_draw_this_turn > 0:
                self.draw_card()
                return

            if self.revealed_cards == 1:
                self.revealed_cards = 0
                self.play_card(self.card_to_play)
            else:
                if self.num_cards_to_play_this_turn > 0:
                    card = random.choice(self.hand)
                    card.is_hidden = False
                    self.card_to_play = card
                    self.revealed_cards = 1

class Card:
    def __init__(self, upright, played_on, played_from, image_file):
        self.upright = upright
        self.played_on = played_on
        self.played_from = played_from
        self.image = pygame.image.load(image_file).convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 200))
        self.rect = self.image.get_rect()
        if not self.upright:
            self.image = pygame.transform.flip(self.image, False, True)

        self.damage_amount = 0
        self.heal_amount = 0
        self.draw_increase_amount = 0
        self.play_increase_amount = 0
        self.is_marked = False
        self.is_damage_random = False
        self.upright_tooltip = ""
        self.revered_tooltip = ""
        self.tooltip = None
        self.is_hidden = True

    def create_tooltip(self):
        self.tooltip = Tooltip(self.upright_tooltip, self.revered_tooltip, self.upright)

    def play(self):
        # override to add custom play logic
        pass

class GenericDamage(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/generic-damage.png")
        self.damage_amount = 2
        self.heal_amount = 1

        self.upright_tooltip = f"Deal {self.damage_amount} to opponent"
        self.revered_tooltip = f"Heal {self.heal_amount} to yourself"
        self.create_tooltip()

    def play(self):
        if self.upright:
            # deal some damage to opponent
            self.played_on.health -= self.damage_amount
        else:
            # heal small amount to player of card
            self.played_from.health += self.heal_amount

class GenericHeal(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/generic-heal.png")
        self.damage_amount = 1
        self.heal_amount = 2

        self.upright_tooltip = f"Heal {self.heal_amount} to yourself"
        self.revered_tooltip = f"Damage {self.damage_amount} to opponent"
        self.create_tooltip()

    def play(self):
        if self.upright:
            # heal some health to the player of card
            self.played_from.health += self.heal_amount
        else:
            # deal small damage to opponent
            self.played_on.health -= self.damage_amount

class TheFool(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/TheFool.jpg")
        self.is_damage_random = True
        self.damage_amount = random.randint(1, 4)
        self.play_increase_amount = 1

        self.upright_tooltip = f"Play {self.play_increase_amount} extra card(s) next turn"
        self.revered_tooltip = f"Deal 1 to 4 damage to opponent, deal 4-X to yourself"
        self.create_tooltip()


    def play(self):
        if self.upright:
            ##Play two cards on the Users next turn
            self.played_from.num_cards_to_play_next_turn += self.play_increase_amount
        else:
            ##deal between 1 and 4 damage to the opponent, deals 4-X to the user
            self.played_on.health -= self.damage_amount
            self.played_from.health -= 4 - self.damage_amount

class TheMagician(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/Magician.jpg")
        self.draw_increase_amount = 1

        self.upright_tooltip = f"Draw {self.draw_increase_amount} extra card(s) next turn"
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##Draw 1 more card next turn
            self.played_from.num_cards_to_draw_next_turn += self.draw_increase_amount
        else:
            pass
            ##makes the opponent chose a random card
            ##no idea how implent

class TheHighPriestess(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/the-high-priestess.jpg")
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##Read and mark 1 card of the opponent
            card_to_mark = random.choice(self.played_on.hand)
            card_to_mark.is_marked = True
        else:
            ##Swap a card with the opponent
            self.played_from.hand.remove(self) # so this card doesn't get chosen to swap
            opponent_card_index = random.randint(0, len(self.played_on.hand) - 1)
            own_card_index = random.randint(0, len(self.played_from.hand) - 1)

            tmp = self.played_from.hand[own_card_index]
            self.played_from.hand[own_card_index] = self.played_on.hand[opponent_card_index]
            self.played_on.hand[opponent_card_index] = tmp


class TheEmpress(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/TheEmpress.jpg")
        self.upright_tooltip = f"Increase max health by 2"
        self.revered_tooltip = f"Half numerical effectiveness of next opponent card"
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##Increase health by two
            self.played_from.max_health = self.played_from.max_health + 2
            self.played_from.health = self.played_from.health + 2
        else:
            ##half the effectiveness of the next card played by an opponent, rounded down
            self.played_on.is_next_card_halved = True

class TheEmperor(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/the-emperor.jpg")
        self.damage_amount = random.randint(1, 4)

        self.upright_tooltip = "Block the next card played by your opponent"
        self.revered_tooltip = "Deal between 1 and 4 damage to both you and your opponent"
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##Block the next card the opponent plays
            self.played_on.is_next_card_blocked = True
        else:
            ##deal between 1 and 4 damage to the opponent, same to yourself
            self.played_on.health -= self.damage_amount
            self.played_from.health -= self.damage_amount

class TheHierophant(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/the-hierophant.jpg.jpg")


        self.upright_tooltip = "Double's the effectiveness of the next card played"
        self.revered_tooltip = "Doubles the negative effects cards played by opponent"
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##Double's the effectiveness of the next card played
            self.played_from.is_next_card_doubled = True
            pass
        else:
            ##Doubles the negative effects cards played by opponent
            pass

class TheLovers(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/the-lovers.jpg")


        self.upright_tooltip = "Play the next card the opponent play"
        self.revered_tooltip = "Shuffle both you and your opponents decks"
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##Play the next card the opponent play
            pass
        else:
            ##Shuffle both you and your opponents decks
            pass

class TheChariot(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/TheChariot.jpg")


        self.upright_tooltip = "Deal 2 damage to the opponent and heal 2"
        self.revered_tooltip = "Deal 5 damage to the opponent and half rounded down to use"
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##Deal 2 damage to the opponent and add 2 health
            self.damage_amount = 2
            self.heal_amount = 2
            self.played_on.health -= self.damage_amount
            self.played_from.health += self.heal_amount
        else:
            ##Deal 5 damage to the opponent and half rounded down to use
            self.damage_amount = 5
            self.played_on.health -= self.damage_amount
            self.played_from.health -= int(self.damage_amount/2)

class Strength(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/strength.jpg")


        self.upright_tooltip = "Increases all damage by 1 for 3 turns"
        self.revered_tooltip = "Decreases all damage from opponent by 1 for 3 turns"
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##Increases all damage by 1 for 3 turns

            pass
        else:
            ##Decreases all damage from opponent by 1 for 3 turns
            pass

class TheHermit(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/the-hermit.jpg.jpg")


        self.upright_tooltip = "See the next three cards in your deck, in order they will be drawn"
        self.revered_tooltip = "No cards can effect you on the next turn, and you cannot play any cards"
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##see the next three cards in your deck, in order they will be drawn

            pass
        else:
            ##Decreases all damage from opponent by 1 for 3 turns
            pass


class TheWheelOfFortune(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/the-wheel-of-fortune.jpg.jpg")


        self.upright_tooltip = "See the next three cards in your deck, in order they will be drawn"
        self.revered_tooltip = "Decreases all damage from opponent by 1 for 3 turns"
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##See the next three cards in your deck, in order they will be drawn

            pass
        else:
            ##Decreases all damage from opponent by 1 for 3 turns
            pass

class Justice(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/justice.jpg.jpg")


        self.upright_tooltip = "See the next three cards in your deck, in order they will be drawn"
        self.revered_tooltip = "Decreases all damage from opponent by 1 for 3 turns"
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##Mirror the card the opponent plays:
            ##.i.e damage opponent if they damage you or heal if they heal themselves

            pass
        else:
            ##reverse the target of the opponents card
            self.played_on.is_next_card_reversed = True
            pass

class TheHangedMan(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/the-hanged-man.jpg.jpg")


        self.upright_tooltip = "Sacrifice health in exchange for dealing damage"
        self.revered_tooltip = "Skips the opponents turn"
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##Sacrifice health in exchange for dealing (health*1.5) damage rounded down
            self.damage_amount = int(self.sacrificed_health*1.5)
            self.played_on.health -= self.damage_amount
            pass
        else:
            ##Skip the opponents turn
            pass

class Death(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/death.jpg")


        self.upright_tooltip = "Double time limit for the rest of the level"
        self.revered_tooltip = "Deal 1 damage per turn to the opponent for 5 turns"
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##Double time limit for the rest of the level
           pass
        else:
            ##Deal 1 damage per turn to the opponent for 5 turns

            pass

class Temperance(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/temperance.jpg.jpg")

        self.play_increase_amount = 2

        self.upright_tooltip = "Double time limit for the rest of the level"
        self.revered_tooltip = "Next turn play 3 cards"
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##Double time limit for the rest of the level
           pass
        else:
            ##Next turn play 3 cards
            self.played_from.num_cards_to_play_next_turn += self.play_increase_amount

class TheDevil(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/the-devil.jpg")


        self.upright_tooltip = "The opponent has all healing cards removed from deck"
        self.revered_tooltip = "Remove all healing cards from your deck and double your damage"
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##The opponent has all healing cards removed from deck

           pass
        else:
            ##remove all healing cards from your deck but double damage (excluding arcana's) for level
            pass

class TheTower(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/the-tower.jpg")

        self.damage_amount = 8
        self.heal_amount = 8
        self.upright_tooltip = "In 5 turns deal 8 damage to the opponent"
        self.revered_tooltip = "Stop The Tower, and delay any incoming damage to in two turns time"
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##In 5 turns deal 8 damage to the opponent
            self.played_from.health -= self.damage_amount
            self.played_on.health -= self.damage_amount

        else:
            ##Stop The Tower, and delay any incoming damage to in two turns time
            self.played_from.health += self.heal_amount
            self.played_on.health += self.heal_amount

class TheStar(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/the-star.jpg")

        self.heal_amount = MAX_HEALTH-self.played_from.health
        self.upright_tooltip = "Full Heal"
        self.revered_tooltip = "Stop The Tower, and delay any incoming damage to in two turns time"
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##Full Heal
            self.played_from.health += self.heal_amount
        else:
            ##For 5 turns opponent heals go to you instead

            pass

class TheMoon(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/the-moon.jpg")

        self.upright_tooltip = "Learn what arcana's the opponent has"
        self.revered_tooltip = "Stop The Tower, and delay any incoming damage to in two turns time"
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##In 5 turns deal 8 damage to the opponent
           pass
        else:
            ##The opponent now doesn't know their health or how much damage they are taking
            pass



ALL_ARCANA_CARDS = [TheFool, TheEmpress, TheEmperor,TheChariot,TheTower]
ALL_GENERIC_CARDS = [GenericDamage, GenericHeal]

def main():
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_CAPTION)
    player = Player()
    computer = Computer()
    player.opponent = computer
    computer.opponent = player
    player.init_hand()
    computer.init_hand()
    background = pygame.image.load("images/background.png").convert_alpha()
    background = pygame.transform.scale(background, (900, 900))
    player.start_turn()

    fps_clock = pygame.time.Clock()
    running = True
    while running:
        dt = fps_clock.tick(60) / 1000
        game_over = player.has_won or computer.has_won

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    if player.playing_turn and not game_over:
                        player.handle_mouse_click(pygame.mouse.get_pos())

        if not game_over:
            computer.update()
            player.update()

            if computer.playing_turn:
                computer.have_turn(dt)

        window.blit(background, (0, 0))
        player.draw(window)
        computer.draw(window)

        if player.has_won:
            draw_text(window, "You won the battle!", YELLOW, 64, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        elif computer.has_won:
            draw_text(window, "The computer won.", YELLOW, 64, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
