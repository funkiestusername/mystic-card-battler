import pygame, sys, random, time

from main import ALL_ARCANA_CARDS

# colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
TURQUOISE = (0, 255, 255)
ORANGE = (255, 150, 0)

# window settings
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 900
WINDOW_CAPTION = "Mystic Tarot Card Game Battler Thingmy"


def draw_text(surface, text, colour, size, centre=None, left_centre=None, right_centre=None) -> pygame.Rect:
    font = pygame.font.Font("freesansbold.ttf", size)
    text_surface = font.render(text, True, colour)
    text_rect = text_surface.get_rect()
    if centre is not None:
        text_rect.center = centre
    elif left_centre is not None:
        text_rect.left = left_centre[0]
        text_rect.centery = left_centre[1]
    elif right_centre is not None:
        text_rect.midright = right_centre
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
        self.box_rect = pygame.Rect(0, 0, max(self.upright_text_rect.width, self.reversed_text_rect.width),
                                    self.upright_text_rect.height + self.reversed_text_rect.height + self.upright_word_text_rect.height + self.reversed_word_text_rect.height)

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

        self.lives = 3

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

        self.play_opponent_card_next = False
        self.last_card_played = None

        self.is_next_card_forced = False
        self.is_next_card_halved = False
        self.is_next_card_blocked = False
        self.is_next_card_reversed = False
        self.is_next_card_mirrored = False

        self.is_computer = False

        self.has_won = False
        self.playing_turn = False

        self.init_deck()

    def init_deck(self):
        self.deck.clear()
        for i in range(MAX_ARCANA):
            self.deck.append(random.choice(ALL_ARCANA_CARDS))

        for i in range(MAX_GENERIC):
            self.deck.append(random.choice(ALL_GENERIC_CARDS))

        random.shuffle(self.deck)

    def init_hand(self):
        self.hand.clear()
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
        self.num_cards_to_draw_this_turn = self.num_cards_to_draw_next_turn
        self.num_cards_to_draw_next_turn = 1

    def draw_card(self):
        # take the top card from the deck
        self.num_cards_to_draw_this_turn -= 1
        self.hand.append(self.deck[0](random.choice((True, False)), self.opponent, self))
        self.deck = self.deck[1:]

    def reset(self):
        self.deck = []
        self.hand = []

        self.max_health = MAX_HEALTH
        self.health = self.max_health

        self.num_cards_to_draw_this_turn = 1
        self.num_cards_to_draw_next_turn = 1
        self.num_cards_to_play_this_turn = 1
        self.num_cards_to_play_next_turn = 1

        self.play_opponent_card_next = False
        self.last_card_played = None

        self.is_next_card_forced = False
        self.is_next_card_halved = False
        self.is_next_card_blocked = False
        self.is_next_card_reversed = False
        self.is_next_card_mirrored = False

        self.has_won = False
        self.playing_turn = False

    def play_card(self, card):
        if self.is_next_card_reversed:
            self.is_next_card_reversed = False
            card.played_from = self.opponent
            card.played_on = self

        if self.is_next_card_mirrored:
            self.is_next_card_mirrored = False
            card.play()
            card.played_from = self.opponent
            card.played_on = self

        if self.is_next_card_halved:
            self.is_next_card_halved = False
            card.damage_amount = card.damage_amount // 2
            card.heal_amount = card.heal_amount // 2
            card.draw_increase_amount = card.draw_increase_amount // 2
            card.play_increase_amount = card.play_increase_amount // 2

        self.last_card_played = card
        self.num_cards_to_play_this_turn -= 1
        if not self.play_opponent_card_next:
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

    def update(self):
        # clamp health to max health
        self.health = min(self.health, self.max_health)

        # check if done all card moves
        if self.num_cards_to_draw_this_turn <= 0 and self.num_cards_to_play_this_turn <= 0:
            self.finish_turn()

        if self.play_opponent_card_next and self.playing_turn and self.opponent.last_card_played is not None:
            self.opponent.last_card_played.played_from = self
            self.opponent.last_card_played.played_on = self.opponent
            self.play_card(self.opponent.last_card_played)
            self.play_opponent_card_next = False

        # check if dead
        if self.health <= 0:
            self.opponent.has_won = True



    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()

        # draw the deck
        if len(self.deck) > 0:
            draw_text(surface, str(len(self.deck)), WHITE, 36,
                      (self.deck_rect.centerx, self.deck_rect.centery + self.deck_card_count_y_offset))
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
            if self.is_computer:
                rect = pygame.Rect(0, self.health_icon_rect.y, self.health_icon_rect.width, self.health_icon_rect.height)
                rect.left = self.health_icon_rect.left + i * self.health_icon_rect.width
                surface.blit(self.health_icon_image, rect)
            else:
                rect = pygame.Rect(0, self.health_icon_rect.y, self.health_icon_rect.width, self.health_icon_rect.height)
                rect.right = self.health_icon_rect.right - i * self.health_icon_rect.width
                surface.blit(self.health_icon_image, rect)

        if not self.is_computer:
            draw_text(surface, f"Lives: {self.lives}", TURQUOISE, 48, right_centre=(WINDOW_WIDTH, WINDOW_HEIGHT // 2 + 120))

class Player(Competitor):
    def __init__(self):
        super().__init__()
        self.deck_rect.bottomleft = (20, WINDOW_HEIGHT - 20)
        self.deck_card_count_y_offset = -125
        self.health_icon_rect.top = WINDOW_HEIGHT - 300
        self.health_icon_rect.right = WINDOW_WIDTH

        self.forced_card_timer = 0

        self.time_limit = 10
        self.time_limit_timer = 0
        self.ran_out_of_time = False

    def start_turn(self):
        super().start_turn()

        self.time_limit_timer = 0

    def update(self, dt):
        super().update()

        if self.playing_turn:
            self.time_limit_timer += dt
            if self.time_limit_timer >= self.time_limit:
                # ran out of time
                self.ran_out_of_time = True

    def draw(self, surface):
        super().draw(surface)

        bar_length = (self.time_limit_timer / self.time_limit * 100) * 5
        pygame.draw.rect(surface, BLUE, (0, 0, bar_length, 50))

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

    def force_next_card(self, dt):
        self.forced_card_timer += dt
        if self.forced_card_timer > 0.8:
            self.forced_card_timer = 0

            card = random.choice(self.hand)
            self.play_card(card)

            if self.num_cards_to_play_this_turn <= 0:
                self.is_next_card_forced = False


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

        if not self.is_next_card_forced:
            # play a smart move
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
                    else:
                        self.is_next_card_forced = False
        else:
            # play randomly
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
                    else:
                        self.is_next_card_forced = False


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
        self.revered_tooltip = f"Opponent will be forced to play random cards on next turn"
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##Draw 1 more card next turn
            self.played_from.num_cards_to_draw_next_turn += self.draw_increase_amount
        else:
            ##makes the opponent chose a random card
            self.played_on.is_next_card_forced = True

class TheHighPriestess(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/the-high-priestess.jpg")
        self.upright_tooltip = "View 1 of the opponents cards"
        self.revered_tooltip = "Swap a random card with opponent"
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##Read and mark 1 card of the opponent
            card_to_mark = random.choice(self.played_on.hand)
            card_to_mark.is_hidden = False
        else:
            ##Swap a card with the opponent
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

class TheLovers(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/the-lovers.jpg")

        self.upright_tooltip = "Play the next card the opponent play"
        self.revered_tooltip = "Shuffle both you and your opponents decks"
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##Play the next card the opponent plays
            self.played_from.play_opponent_card_next = True
        else:
            ##Shuffle both you and your opponents decks
            random.shuffle(self.played_on.deck)
            random.shuffle(self.played_from.deck)

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

class Justice(Card):
    def __init__(self, upright, played_on, played_from):
        super().__init__(upright, played_on, played_from, "images/justice.jpg")

        self.upright_tooltip = "Mirror the card played by opponent"
        self.revered_tooltip = "Reverse the target of opponents next card"
        self.create_tooltip()

    def play(self):
        if self.upright:
            ##Mirror the card the opponent plays:
            ##.i.e damage opponent if they damage you or heal if they heal themselves
            self.played_on.is_next_card_mirrored = True
        else:
            ##reverse the target of the opponents card
            self.played_on.is_next_card_reversed = True
            pass


ALL_ARCANA_CARDS = [TheFool, TheChariot, TheMagician, TheEmpress, TheEmperor, TheHighPriestess, TheLovers, Justice]
ALL_GENERIC_CARDS = [GenericDamage, GenericHeal]

player = Player()
computer = Computer()
player.opponent = computer
computer.opponent = player

def play_level(window, level):
    background = pygame.image.load("images/background.png").convert_alpha()
    background = pygame.transform.scale(background, (900, 900))

    pygame.mixer.init()
    bg_music = pygame.mixer.Sound(background_music)
    bg_music.play(-1)

    player.reset()
    computer.reset()

    player.init_deck()
    computer.init_deck()
    player.init_hand()
    computer.init_hand()

    player.start_turn()

    fps_clock = pygame.time.Clock()
    playing = True
    while playing:
        dt = fps_clock.tick(60) / 1000
        game_over = player.has_won or computer.has_won or player.ran_out_of_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    if player.playing_turn and not game_over:
                        player.handle_mouse_click(pygame.mouse.get_pos())

        if not game_over:
            computer.update()
            player.update(dt)

            if computer.playing_turn:
                computer.have_turn(dt)

            if player.playing_turn and player.is_next_card_forced:
                player.force_next_card(dt)

        window.fill(BLACK)

        window.blit(background, (0, 0))

        player.draw(window)
        computer.draw(window)

        if player.has_won:
            draw_text(window, "You won the battle!", YELLOW, 64, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        elif computer.has_won:
            draw_text(window, "The computer won.", YELLOW, 64, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        elif player.ran_out_of_time:
            draw_text(window, "You ran out of time.", YELLOW, 64, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

        # draw level number
        draw_text(window, f"Level: {level}", ORANGE, 64, left_centre=(0, WINDOW_HEIGHT // 2))

        pygame.display.flip()

        if player.has_won:
            time.sleep(3)
            return True
        elif computer.has_won or player.ran_out_of_time:
            time.sleep(3)
            return False

class MenuButton:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text

    def draw(self, surface):
        draw_text(surface, self.text, WHITE, 64, centre=self.rect.center)

        if self.is_over(pygame.mouse.get_pos()):
            pygame.draw.rect(surface, YELLOW, self.rect, width=3)

    def is_over(self, pos):
        return self.rect.left < pos[0] < self.rect.right and self.rect.top < pos[1] < self.rect.bottom

def main_menu(window):
    music_options = ["alt-rock.wav", "testmusic2.wav"]
    selected_music = 0

    quit_button = MenuButton(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100, 100, 75, "Quit")
    play_button = MenuButton(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, 100, 70, "Play")


    in_menu = True
    while in_menu:
        music_button = MenuButton(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100, 100, 70,
                                  f"Music: {music_options[selected_music]}")
        global background_music
        background_music = music_options[selected_music]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if quit_button.is_over(mouse_pos):
                    pygame.quit()
                    sys.exit()

                elif play_button.is_over(mouse_pos):
                    in_menu = False

                elif music_button.is_over(mouse_pos):
                    selected_music = 1 if selected_music == 0 else 0

        window.fill(BLACK)

        quit_button.draw(window)
        play_button.draw(window)
        music_button.draw(window)

        pygame.display.flip()

background_music = "testmusic2.wav"

def main():
    global player, computer
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_CAPTION)

    main_menu(window)

    level = 1

    running = True
    while running:
        beat_level = play_level(window, level)

        if not beat_level:
            player.lives -= 1
            tmp = player.lives
            player = Player()
            player.lives = tmp
            computer = Computer()
            player.opponent = computer
            computer.opponent = player
            if player.lives < 0:
                level = 1
                player = Player()
                computer = Computer()
                player.opponent = computer
                computer.opponent = player
        else:
            player = Player()
            computer = Computer()
            player.opponent = computer
            computer.opponent = player
            level += 1

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
