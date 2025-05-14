import pygame

class PauseMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 36)
        self.options = ["Resume Game", "Save and Exit", "Quit to Main Menu"]
        self.selected = 0
        self.result = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self.result = self.options[self.selected]

    def update(self):
        pass

    def draw(self):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))

        title = self.font.render("Paused", True, (255, 255, 0))
        self.screen.blit(title, (450, 150))

        y = 250
        for i, option in enumerate(self.options):
            color = (255, 255, 255) if i != self.selected else (0, 255, 0)
            text = self.font.render(option, True, color)
            self.screen.blit(text, (400, y))
            y += 50

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        while self.result is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                self.handle_event(event)

            self.update()
            self.draw()
            clock.tick(30)

        return self.result
