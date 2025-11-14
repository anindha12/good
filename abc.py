import random
import pygame

pygame.init()

class Button:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.width = image.get_width()
        self.height = image.get_height()

    def clicked(self, pos):
        return self.x < pos[0] < self.x + self.width and self.y < pos[1] < self.y + self.height

class RPSGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((960, 640))
        pygame.display.set_caption("Rock Paper Scissors")

        # Load images
        self.bg = pygame.image.load("background.jpg")
        self.r_btn_img = pygame.image.load("r_button.png").convert_alpha()
        self.p_btn_img = pygame.image.load("p_button.png").convert_alpha()
        self.s_btn_img = pygame.image.load("s_button.png").convert_alpha()

        self.choose_rock = pygame.image.load("rock.png").convert_alpha()
        self.choose_paper = pygame.image.load("paper.png").convert_alpha()
        self.choose_scissors = pygame.image.load("scissors.png").convert_alpha()

        # Create button objects with image sizes
        self.rock_button = Button(20, 500, self.r_btn_img)
        self.paper_button = Button(330, 500, self.p_btn_img)
        self.scissors_button = Button(640, 500, self.s_btn_img)

        self.font = pygame.font.Font(None, 60)
        self.player_option = None
        self.pc_random_choice = None
        self.player_score = 0
        self.pc_score = 0

        self.draw_buttons()
        self.draw_scores()
        pygame.display.update()

    def draw_buttons(self):
        self.screen.blit(self.bg, (0, 0))
        self.screen.blit(self.r_btn_img, (self.rock_button.x, self.rock_button.y))
        self.screen.blit(self.p_btn_img, (self.paper_button.x, self.paper_button.y))
        self.screen.blit(self.s_btn_img, (self.scissors_button.x, self.scissors_button.y))

    def player_choice(self, pos):
        if self.rock_button.clicked(pos):
            self.player_option = 'rock'
            self.screen.blit(self.choose_rock, (120, 200))
        elif self.paper_button.clicked(pos):
            self.player_option = 'paper'
            self.screen.blit(self.choose_paper, (120, 200))
        elif self.scissors_button.clicked(pos):
            self.player_option = 'scissors'
            self.screen.blit(self.choose_scissors, (120, 200))
        # Debug click
        print(f"Player chose: {self.player_option}")
        return self.player_option

    def computer_choice(self):
        self.pc_random_choice = random.choice(['rock', 'paper', 'scissors'])
        if self.pc_random_choice == 'rock':
            self.screen.blit(self.choose_rock, (600, 200))
        elif self.pc_random_choice == 'paper':
            self.screen.blit(self.choose_paper, (600, 200))
        else:
            self.screen.blit(self.choose_scissors, (600, 200))

    def check_winner(self):
        pl = self.player_option
        pc = self.pc_random_choice
        if not pl or not pc:
            return None
        if pl == pc:
            return "Draw"
        elif (pl == 'rock' and pc == 'scissors') or \
             (pl == 'paper' and pc == 'rock') or \
             (pl == 'scissors' and pc == 'paper'):
            self.player_score += 1
            return "Player Wins!"
        else:
            self.pc_score += 1
            return "Computer Wins!"

    def draw_scores(self):
        player_text = self.font.render(f"Player: {self.player_score}", True, (255, 255, 255))
        pc_text = self.font.render(f"Computer: {self.pc_score}", True, (255, 255, 255))
        self.screen.blit(player_text, (50, 50))
        self.screen.blit(pc_text, (650, 50))

    def run(self):
        running = True
        while running:
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    # Draw buttons first
                    self.draw_buttons()
                    self.player_choice(pos)
                    self.computer_choice()
                    result = self.check_winner()
                    if result:
                        result_text = self.font.render(result, True, (255, 255, 0))
                        self.screen.blit(result_text, (350, 400))
                    self.draw_scores()

if __name__ == "__main__":
    game = RPSGame()
    game.run()
    pygame.quit()
