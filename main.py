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


def draw_text(surface, text, colour, size, centre):
    font = pygame.font.Font("freesansbold.ttf", size)
    text_surface = font.render(text, True, colour)
    text_rect = text_surface.get_rect(center=centre)
    surface.blit(text_surface, text_rect)

MAX_CARDS = 20
MAX_ARCANA = 3
MAX_GENERIC = 17
MAX_HEALTH = 10

class Competitor:
    def __init__(self):
        self.deck = []
        self.hand = []
        self.max_health = MAX_HEALTH
        self.health = self.max_health

        self.opponent = None

        self.deck_image = pygame.image.load("card-back.jpg")
        self.deck_image = pygame.transform.scale(self.deck_image, (100, 200))
        self.deck_rect = self.deck_image.get_rect()
        self.deck_card_count_y_offset = 0

        self.num_cards_to_draw_this_turn = 1
        self.num_cards_to_draw_next_turn = 1
        self.num_cards_to_play_this_turn = 1
        self.num_cards_to_play_next_turn = 1

        self.is_next_card_forced = False
        self.is_next_card_halved = False
        
        self.playing_turn = False

        self.init_deck()

    def init_deck(self):
        for i in range(MAX_ARCANA):
            self.deck.append(random.choice(ALL_ARCANA_CARDS))

        for i in range(MAX_GENERIC):
            # self.deck.append(random.choice(ALL_GENERIC_CARDS))
            pass

        random.shuffle(self.deck)
        
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

        
        self.num_cards_to_draw_next_turn = 1

    def update(self) -> bool: # return whether they finished their turn
        # check if turn over
        if self.num_cards_to_draw_this_turn <= 0 or self.num_cards_to_play_this_turn <= 0:
            self.playing_turn = False
            self.opponent.playing_turn = True
            return True

        return False

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()

        # draw the deck
        if len(self.deck) > 0:
            draw_text(surface, str(len(self.deck)), WHITE, 36, (self.deck_rect.centerx, self.deck_rect.centery + self.deck_card_count_y_offset))
            surface.blit(self.deck_image, self.deck_rect)

            if self.deck_rect.collidepoint(mouse_pos) and self.playing_turn:
                pygame.draw.rect(surface, RED, self.deck_rect, width=3)

        # draw the hand
        for card in self.hand:
            pass

        # draw the health and lives


class Player(Competitor):
    def __init__(self):
        super().__init__()
        self.deck_rect.bottomleft = (20, WINDOW_HEIGHT - 20)
        self.deck_card_count_y_offset = -125

    def handle_mouse_click(self, mouse_pos):
        # saves having all the clicky logic in the main function, plus player is only thing that takes clicky input
        # only gets called if player is playing their turn
        if self.deck_rect.collidepoint(mouse_pos) and self.num_cards_to_draw_this_turn > 0:
            # draw a card
            self.hand.append(self.deck[0](random.choice((True, False)), self.opponent, self))
            self.deck = self.deck[1:]

class Computer(Competitor):
    def __init__(self):
        super().__init__()
        self.deck_rect.topright = (WINDOW_WIDTH - 20, 20)


class Card:
    def __init__(self, upright, played_on, played_from, image_file):
        self.damage_amount = 0
        self.heal_amount = 0
        self.upright = upright
        self.played_on = played_on
        self.played_from = played_from
        self.is_marked = False

        self.image = pygame.image.load(image_file).convert_alpha()
        self.rect = self.image.get_rect()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class GenericDamage(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "")

        if self.upright:
            # deal some damage to opponent
            pass
        else:
            # heal small amount to player of card
            pass


class GenericHeal(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "")

        if self.upright:
            # heal some health to the player of card
            pass
        else:
            # deal small damage to opponent
            pass

class TheFool(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "TheFool.jpg")

        if self.upright:
            ##Play two cards on the Users next turn
            self.played_from.num_cards_to_play_next_turn = 2
        else:
            ##deal between 1 and 4 damage to the opponent, deals 4-X to the user
            foolrandom: int = random.randint(1,4)
            self.played_on.health -= foolrandom
            self.played_from.health -= 4 - foolrandom

class TheMagician(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "")

        if self.upright:
            ##Draw 1 more card next turn
            self.played_from.num_cards_to_draw_next_turn = 2
        else:
            pass
            ##makes the opponent chose a random card
            ##no idea how implent

class TheHighPriestess(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "")

        if self.upright:
            pass
            ##Read and mark 1 card of the opponent
        ##no idea how implent
        else:
            pass
            ##Swap a card with the opponent
            ##no idea how implent

class TheEmpress(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "TheEmpress.jpg")

        if self.upright:
            ##Increase health by two
            self.played_from.max_health = self.played_from.max_health + 2
            self.played_from.health = self.played_from.health + 2
        else:
            ##half the effectiveness of the next card played by an opponent, rounded down
            self.played_on.is_next_card_halved = True

class TheEmporer(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "")

        if self.upright:
            ##Block the next card the opponent plays
            pass
        else:
            ##deal between 1 and 4 damage to the opponent, am
            emprandom: int = random.randint(1, 4)
            self.played_on.health -= emprandom
            self.played_from.health -= emprandom

ALL_ARCANA_CARDS = [TheFool, TheEmpress]
ALL_GENERIC_CARDS = [GenericDamage, GenericHeal]

def main():
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_CAPTION)

    player = Player()
    computer = Computer()
    player.opponent = computer
    computer.opponent = player

    player.playing_turn = True

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    if player.playing_turn:
                        player.handle_mouse_click(pygame.mouse.get_pos())

        player.update()
        computer.update()

        window.fill(BLACK)

        player.draw(window)
        computer.draw(window)

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()



