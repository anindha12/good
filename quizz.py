import pygame
import sys
import random
import html
import urllib.request
import json

pygame.init()


class Button:
    def __init__(self, x, y, w, h, text, font, bg=(50, 50, 50), fg=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.bg = bg
        self.fg = fg

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg, self.rect, border_radius=8)
        txt = self.font.render(self.text, True, self.fg)
        txt_rect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, txt_rect)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


class QuizGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((960, 640))
        pygame.display.set_caption("Quiz Game")
        self.clock = pygame.time.Clock()

        # Reduced font sizes so question/answer text appears smaller
        self.font_q = pygame.font.Font(None, 36)
        self.font_opt = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)

        # Local fallback question bank (used if API not chosen or fetch fails)
        self.local_bank = [
            {"q": "What is the capital of France?", "opts": ["Berlin", "Madrid", "Paris", "Rome"], "a": 2},
            {"q": "Which number is prime?", "opts": ["4", "6", "9", "7"], "a": 3},
            {"q": "Which language is this program written in?", "opts": ["Java", "C++", "Python", "Ruby"], "a": 2},
        ]

        # Questions will be set after startup choice (API or Local)
        self.questions = None
        self.score = 0
        self.index = 0
        self.selected = None
        self.answered = False

        # Buttons for options will be created once questions are set
        self.option_buttons = []
        self.next_button = Button(380, 520, 200, 50, "Next", self.font_small, bg=(20, 120, 20))

        # Startup selection UI
        self.startup_msg = "Choose question source"
        self.api_button = Button(260, 260, 180, 60, "Use API", self.font_opt, bg=(40, 100, 200))
        self.local_button = Button(520, 260, 180, 60, "Use Local", self.font_opt, bg=(80, 80, 80))
        self.fetch_error = None

    def update_buttons(self):
        self.option_buttons = []
        q = self.questions[self.index]
        start_x = 100
        start_y = 220
        w = 760
        h = 60
        gap = 20
        for i, opt in enumerate(q['opts']):
            btn = Button(start_x, start_y + i * (h + gap), w, h, opt, self.font_opt, bg=(70, 70, 70))
            self.option_buttons.append(btn)

    def fetch_questions_from_api(self, amount=5):
        """Fetches multiple-choice questions from OpenTDB using urllib
        and returns a list of dicts in the format: { 'q': str, 'opts': [..], 'a': index }.
        Returns None on failure so caller can fallback to local questions."""
        url = f"https://opentdb.com/api.php?amount={amount}&type=multiple"
        # Prefer requests if available (faster/friendlier); otherwise use urllib
        try:
            import requests
        except Exception:
            requests = None

        try:
            if requests:
                resp = requests.get(url, timeout=6)
                resp.raise_for_status()
                data = resp.json()
            else:
                with urllib.request.urlopen(url, timeout=6) as resp:
                    raw = resp.read()
                data = json.loads(raw.decode('utf-8'))

            if data.get('response_code') != 0:
                msg = "OpenTDB returned no questions (response_code != 0)"
                print(msg)
                try:
                    self.fetch_error = msg
                except Exception:
                    pass
                return None

            out = []
            for item in data.get('results', []):
                question = html.unescape(item.get('question', ''))
                correct = html.unescape(item.get('correct_answer', ''))
                incorrect = [html.unescape(i) for i in item.get('incorrect_answers', [])]
                opts = incorrect + [correct]
                random.shuffle(opts)
                a_index = opts.index(correct)
                out.append({'q': question, 'opts': opts, 'a': a_index})
            if out:
                print(f"Fetched {len(out)} questions from OpenTDB")
                return out
            return None
        except Exception as e:
            msg = f"Failed fetching questions from OpenTDB: {e}"
            print(msg)
            # store a human-readable error for the startup UI to show
            try:
                self.fetch_error = msg
            except Exception:
                pass
            return None

    def draw(self):
        # If questions not yet chosen, show startup screen
        if self.questions is None:
            self.draw_startup()
            return
        self.screen.fill((30, 30, 40))

        # Draw header and score
        header = self.font_q.render(f"Question {self.index + 1} / {len(self.questions)}", True, (255, 255, 255))
        self.screen.blit(header, (30, 20))
        score_txt = self.font_small.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_txt, (800, 30))

        # Draw question
        qtxt = self.font_q.render(self.questions[self.index]['q'], True, (220, 220, 220))
        self.screen.blit(qtxt, (80, 120))

        # Draw options
        for i, btn in enumerate(self.option_buttons):
            # Highlight selected or show correct/incorrect after answering
            if self.answered:
                correct_idx = self.questions[self.index]['a']
                if i == correct_idx:
                    btn.bg = (20, 120, 20)
                elif self.selected == i and i != correct_idx:
                    btn.bg = (160, 40, 40)
                else:
                    btn.bg = (70, 70, 70)
            else:
                # Reset to default when not answered
                btn.bg = (70, 70, 70)
            btn.draw(self.screen)

        # Draw next button only after answering
        if self.answered:
            self.next_button.draw(self.screen)

        # If answered, show feedback text
        if self.answered:
            correct_idx = self.questions[self.index]['a']
            if self.selected == correct_idx:
                fb = self.font_q.render("Correct!", True, (200, 230, 200))
            else:
                correct_text = self.questions[self.index]['opts'][correct_idx]
                fb = self.font_q.render(f"Wrong! Answer: {correct_text}", True, (250, 200, 200))
            fb_rect = fb.get_rect(center=(480, 470))
            self.screen.blit(fb, fb_rect)

    def handle_click(self, pos):
        # If still on startup, delegate
        if self.questions is None:
            self.handle_startup_click(pos)
            return
        if not self.answered:
            for i, btn in enumerate(self.option_buttons):
                if btn.clicked(pos):
                    self.selected = i
                    self.answered = True
                    # check correctness
                    if i == self.questions[self.index]['a']:
                        self.score += 1
                    print(f"Selected option {i}, correct = {self.questions[self.index]['a']}")
                    break
        else:
            if self.next_button.clicked(pos):
                # move to next question or finish
                self.index += 1
                if self.index >= len(self.questions):
                    self.show_final()
                else:
                    self.selected = None
                    self.answered = False
                    self.update_buttons()

    def show_final(self):
        # Show final score screen and exit after user closes
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    running = False
            self.screen.fill((15, 15, 30))
            txt = self.font_q.render(f"Final Score: {self.score} / {len(self.questions)}", True, (255, 255, 255))
            sub = self.font_small.render("Click anywhere or close window to quit", True, (180, 180, 180))
            self.screen.blit(txt, txt.get_rect(center=(480, 260)))
            self.screen.blit(sub, sub.get_rect(center=(480, 320)))
            pygame.display.update()
            self.clock.tick(30)
        pygame.quit()
        sys.exit()

    # ---------- Startup UI ----------
    def draw_startup(self):
        self.screen.fill((18, 18, 30))
        title = self.font_q.render(self.startup_msg, True, (240, 240, 240))
        self.screen.blit(title, title.get_rect(center=(480, 160)))

        # Buttons
        self.api_button.draw(self.screen)
        self.local_button.draw(self.screen)

        # Show fetch error if present
        if self.fetch_error:
            err = self.font_small.render(self.fetch_error, True, (240, 100, 100))
            self.screen.blit(err, err.get_rect(center=(480, 360)))

    def handle_startup_click(self, pos):
        if self.api_button.clicked(pos):
            # Try to fetch questions from API
            self.fetch_error = None
            fetched = self.fetch_questions_from_api(amount=5)
            if fetched:
                self.questions = fetched
                self.index = 0
                self.score = 0
                self.selected = None
                self.answered = False
                self.update_buttons()
            else:
                self.fetch_error = "Failed to fetch from API. Check network."
        elif self.local_button.clicked(pos):
            self.questions = list(self.local_bank)
            self.index = 0
            self.score = 0
            self.selected = None
            self.answered = False
            self.update_buttons()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    self.handle_click(pos)

            self.draw()
            pygame.display.update()
            self.clock.tick(30)

        pygame.quit()


if __name__ == '__main__':
    game = QuizGame()
    game.run()
