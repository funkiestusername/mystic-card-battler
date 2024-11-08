import pygame, sys, random


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
            self.deck.append(random.choice(ALL_GENERIC_CARDS))

        random.shuffle(self.deck)
        
    def start_turn(self):
        # called at the start of the turn only once
        self.playing_turn = True
        self.num_cards_to_play_this_turn = self.num_cards_to_play_next_turn
        self.num_cards_to_play_next_turn = 1
        
        for i in range(self.num_cards_to_draw_next_turn):
            pass

        if self.is_next_card_forced:
            for i in range(self.num_cards_to_play_this_turn):
                # all cards played are random :(
                card = random.choice(self.hand)

        
        self.num_cards_to_draw_next_turn = 1


class Player(Competitor):
    pass

class Computer(Competitor):
    pass


class Card:
    def __init__(self, upright, played_on, played_from):
        self.damage_amount = 0
        self.heal_amount = 0
        self.upright = upright
        self.played_on = played_on
        self.played_from = played_from
        self.is_marked = False
        self.image = None

    def draw(self, surface, x, y):
        pass


class TheFool(Card):
    def __init(self):
        if self.upright:
            ##Play two cards on the Users next turn
            self.played_from.num_cards_to_play_next_turn = 2
        else:
            ##deal between 1 and 4 damage to the opponent, deals 4-X to the user
            foolrandom: int = random.randint(1,4)
            self.played_on.health -= foolrandom
            self.played_from.health -= 4 - foolrandom

class TheMagician(Card):
    def __init(self):
        if self.upright:
            ##Draw 1 more card next turn
            self.played_from.num_cards_to_draw_next_turn = 2
        else:
            pass
            ##makes the opponent chose a random card
            ##no idea how implent

class TheHighPriestess(Card):
    def __init(self):
        if self.upright:
            pass
            ##Read and mark 1 card of the opponent
        ##no idea how implent
        else:
            pass
            ##Swap a card with the opponent
            ##no idea how implent

class TheEmpress(Card):
    def __init(self):
        if self.upright:
            ##Increase health by two
            self.played_from.max_health = self.played_from.max_health + 2
            self.played_from.health = self.played_from.health + 2
        else:
            ##half the effectiveness of the next card played by an opponent, rounded down
            self.played_on.is_next_card_halved = True

class TheEmporer(Card):
    def __init(self):
        if self.upright:
            ##Block the next card the opponent plays
            pass
        else:
            ##deal between 1 and 4 damage to the opponent, am
            emprandom: int = random.randint(1, 4)
            self.played_on.health -= emprandom
            self.played_from.health -= emprandom

ALL_ARCANA_CARDS = [TheFool, TheEmpress]
ALL_GENERIC_CARDS = []

def update():
    # called every frame
    pass

def draw(window):
    # called every frame
    pass

def main():
    pygame.init()
    window = pygame.display.set_mode((800, 800))
    pygame.display.set_caption("Test")

    player = Player()
    computer = Computer()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        update()

        window.fill((0, 0, 0))



        pygame.display.flip()

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()



