import pygame

class Tooltip:
    def __init__(self, font, text=""):
        self.font = font
        self.text = ""
        self.visible = False
        self.position = (0, 0)
        self.set_text(text)
        self.background_color = (0, 0, 0)
        self.text_color = (255, 255, 255)
        self.padding = 5

    def set_text(self, text):
        self.text = str(text)
        if self.text:
            words = self.text.split()
            self.lines = []
            current_line = []
            current_width = 0
            
            for word in words:
                word_surface = self.font.render(word + " ", True, self.text_color)
                word_width = word_surface.get_width()
                
                if current_width + word_width > 200:  # Max width
                    self.lines.append(" ".join(current_line))
                    current_line = [word]
                    current_width = word_width
                else:
                    current_line.append(word)
                    current_width += word_width
            
            if current_line:
                self.lines.append(" ".join(current_line))
        else:
            self.lines = []

    def show(self, position):
        self.visible = True
        self.position = position

    def hide(self):
        self.visible = False

    def draw(self, surface):
        if not self.visible or not self.text:
            return

        # Calculate total height
        line_height = self.font.get_linesize()
        total_height = len(self.lines) * line_height + 2 * self.padding

        # Calculate max width
        max_width = max([self.font.size(line)[0] for line in self.lines]) + 2 * self.padding

        # Draw background
        background_rect = pygame.Rect(self.position[0], self.position[1], max_width, total_height)
        pygame.draw.rect(surface, self.background_color, background_rect)
        pygame.draw.rect(surface, self.text_color, background_rect, 1)

        # Draw text
        y = self.position[1] + self.padding
        for line in self.lines:
            text_surface = self.font.render(line, True, self.text_color)
            surface.blit(text_surface, (self.position[0] + self.padding, y))
            y += line_height 