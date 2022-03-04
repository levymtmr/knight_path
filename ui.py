import pygame

class UI:

    def __init__(self, surface) -> None:
        
        self.display_surface = surface

        # health
        self.health_bar = pygame.image.load('./graphics/ui/health_bar.png').convert_alpha()
        self.health_bar_topleft = (54, 39)
        self.bar_max_width = 152
        self.bar_height = 4

        # coins
        self.coin_bank = pygame.image.load('./graphics/ui/coin.png').convert_alpha()
        self.coin_bank_rect = self.coin_bank.get_rect(topleft = (50, 61))

        # font
        self.font = pygame.font.Font('./graphics/ui/ARCADEPI.TTF', 30)

    def show_health(self, current_health, full_health):
        self.display_surface.blit(self.health_bar, (20, 10))
        current_health_radio = current_health / full_health
        current_bar_health = self.bar_max_width * current_health_radio
        health_bar_rect = pygame.Rect(self.health_bar_topleft, (current_bar_health, self.bar_height))
        pygame.draw.rect(self.display_surface, '#dc4949', health_bar_rect)


    def show_coins_bank(self, amount):
        self.display_surface.blit(self.coin_bank, self.coin_bank_rect)
        coin_amount_surface = self.font.render(str(amount), False, '#33323d')
        coin_amount_rect = coin_amount_surface.get_rect(midleft = (self.coin_bank_rect.right + 4, self.coin_bank_rect.centery))
        self.display_surface.blit(coin_amount_surface, coin_amount_rect)