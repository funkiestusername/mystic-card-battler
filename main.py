import pygame, sys, random, time


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
MAX_ARCANA = 3
MAX_GENERIC = 17
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
        self.health_icon_image = pygame.transform.scale(self.health_icon_image, (39, 36))
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

        self.hide_cards_in_hand = False

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
        card.play()
        self.hand.remove(card)
        self.deck.append(type(card)) # recycle card

    def finish_turn(self):
        self.playing_turn = False
        self.num_cards_to_play_this_turn = 1
        self.num_cards_to_draw_this_turn = 1
        self.opponent.start_turn()

    def update(self): # decide whether they finished their turn
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
            if not self.hide_cards_in_hand:
                card = self.hand[i]

                card.rect.left = self.deck_rect.right + i * card.rect.width + 10 * (i + 1)
                card.rect.y = self.deck_rect.y

                surface.blit(card.image, card.rect)

                if card.rect.collidepoint(mouse_pos) and self.playing_turn and self.num_cards_to_play_this_turn > 0:
                    pygame.draw.rect(surface, RED, card.rect, width=3)
            else:
                rect = pygame.Rect(0, self.deck_rect.y, self.deck_rect.width, self.deck_rect.height)
                rect.right = self.deck_rect.left - i * self.deck_rect.width - 10 * (i + 1)
                surface.blit(self.deck_image, rect)

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

        self.deck_rect.topright = (WINDOW_WIDTH - 20, 20)
        self.deck_card_count_y_offset = 125
        self.hide_cards_in_hand = True
        self.health_icon_rect.bottom = 300

    def have_turn(self, dt):
        # computer turn logic
        # will sleep briefly between moves so player can process what they're doing

        # general algorithm
        # draw a card
        # if a card dealing more damage than player has health, play it
        # if self health less than a threshold, heal if available

        self.move_timer += dt
        if self.move_timer >= 0.5:
            self.move_timer = 0

            # currently just plays a random card
            for i in range(self.num_cards_to_draw_this_turn):
                self.draw_card()
                return

            for i in range(self.num_cards_to_play_this_turn):
                self.play_card(random.choice(self.hand))
                return


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
        self.is_marked = False
        self.is_damage_random = False
        self.upright_tooltip = ""
        self.revered_tooltip = ""
        self.tooltip = None

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
        self.upright_tooltip = f"Play two cards next turn"
        self.revered_tooltip = f"Deal 1 to 4 damage to opponent, deal 4-X to yourself"
        self.create_tooltip()

        self.is_damage_random = True
        self.damage_amount = random.randint(1, 4)

    def play(self):
        if self.upright:
            ##Play two cards on the Users next turn
            self.played_from.num_cards_to_play_next_turn = 2
        else:
            ##deal between 1 and 4 damage to the opponent, deals 4-X to the user
            self.played_on.health -= self.damage_amount
            self.played_from.health -= 4 - self.damage_amount

class TheMagician(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "")
        self.create_tooltip()

    def play(self):
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
        self.create_tooltip()

    def play(self):
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
        super().__init__(upright, played_on, played_from, "")
        self.damage_amount = random.randint(1, 4)
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##Block the next card the opponent plays
            pass
        else:
            ##deal between 1 and 4 damage to the opponent, same to yourself
            self.played_on.health -= self.damage_amount
            self.played_from.health -= self.damage_amount

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

    player.init_hand()
    computer.init_hand()

    player.start_turn()

    fps_clock = pygame.time.Clock()
    running = True
    while running:
        dt = fps_clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    if player.playing_turn:
                        player.handle_mouse_click(pygame.mouse.get_pos())

        if not player.has_won and not computer.has_won:
            computer.update()
            player.update()

            if computer.playing_turn:
                computer.have_turn(dt)

        window.fill(BLACK)

        player.draw(window)
        computer.draw(window)

        if player.has_won:
            draw_text(window, "You won the battle!", YELLOW, 64, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        elif computer.has_won:
            draw_text(window, "Tough luck, the computer won.", YELLOW, 64, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
