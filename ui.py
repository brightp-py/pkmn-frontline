from functools import lru_cache

import pygame
pygame.init()

class Button:

    def __init__(self, image, on_click=None):
        """Create a Button object that can be clicked to run a function.

        Parameters:

            image    - Pygame Surface object.

            on_click - Function to be run when this button is clicked.
        """
        self._orig_image = image
        self._image = image
        self._on_click = on_click

        self._x, self._y = 0, 0
        self._w, self._h = self._image.get_size()
    
    def check_pressed(self, mouse_pos):
        """Run this button's function if the mouse position lies within it.
        
        Parameters:
            mouse_pos - (x, y) of cursor position.
        
        Return True if mouse_pos lies in this Button's rect. False otherwise.
        """
        x, y = mouse_pos
        if self._x <= x and x <= self._x + self._w and \
           self._y <= y and y <= self._y + self._h:
            if self._on_click is not None:
                self._on_click()
            return True
        return False
    
    def render(self, screen, rect):
        """Draw this button on the screen, stretched to fit the given rect.

        Parameters:

            screen - Pygame Surface to draw on.

            rect   - (x, y, w, h) of coords/area to use up.
        """
        x, y, w, h = rect
        if w != self._w or h != self._h:
            self._w = w
            self._h = h
            try:
                self._image = pygame.transform.smoothscale(self._orig_image,
                                                           (w, h))
            except ValueError:
                self._image = pygame.transform.scale(self._orig_image, (w, h))
        self._x, self._y = x, y
        screen.blit(self._image, (x, y))


class TextBox:
    font = pygame.font.Font("assets/font/PokemonGB-RAeo.ttf", 14)
    title_font = pygame.font.Font("assets/font/PokemonGB-RAeo.ttf", 24)
    bg = (255, 255, 255)
    fg = (0, 0, 0)
    line_spacing = 8

    def __init__(self, text):
        """Create a text box that contains and wraps text."""
        self._text = text
        self._rect = (0, 0, 0, 0)
    
    @lru_cache(16)
    def _generate_text_img(self, size, text, do_title=True):
        """Create the white-background text image.
        
        Parameters:
            rect - (w, h) defining white background.
        """
        w, h = size
        surface = pygame.Surface((w, h))
        surface.fill(TextBox.bg)
        font_height = TextBox.font.size("Tg")[1]
        title_height = TextBox.title_font.size("Tg")[1]

        x = 5
        w -= 10
        y = 5

        while text:
            if text[0] == '\n':
                y += font_height + TextBox.line_spacing
                text = text[1:]
                continue

            i = 1
            if y + font_height > h:
                break
            while TextBox.font.size(text[:i])[0] < w and i < len(text):
                i += 1
            if '\n' in text[:i]:
                i = text.find('\n', 0, i) + 1
            elif i < len(text):
                i = text.rfind(' ', 0, i) + 1
            if do_title:
                line = TextBox.title_font.render(text[:i], True, TextBox.fg,
                                                 TextBox.bg)
                surface.blit(line, (x, y))
                y += title_height + TextBox.line_spacing
                do_title = False
            else:
                
                line = TextBox.font.render(text[:i], True, TextBox.fg,
                                           TextBox.bg)
                surface.blit(line, (x, y))
                y += font_height + TextBox.line_spacing
            text = text[i:]
        
        return surface
    
    def set_text(self, text):
        """Set the text attribute."""
        self._text = text
    
    def render(self, screen, rect):
        """Draw this text box onto another Pygame Surface.

        Parameters:
        
            screen - Pygame Surface to draw onto.
        
            rect   - (x, y, w, h) defining white background.
        """
        image = self._generate_text_img(rect[2:], self._text)
        screen.blit(image, rect[:2])
        pygame.draw.rect(screen, TextBox.fg, rect, width=3)
        self._rect = rect
    
    def contains(self, point):
        """Return true if point (x, y) lies in this (x, y, w, h)."""
        x0, y0 = point
        x, y, w, h = self._rect
        return x <= x0 and x0 <= x + w and y <= y0 and y0 <= y + h
