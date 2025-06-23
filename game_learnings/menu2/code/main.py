from button import Button
from settings import *

class Game:
  def __init__(self):
    pygame.init()
    self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Main Menu")

    self.game_paused = False
    self.menu_state = "main"
    self.running = True
    self.clock = pygame.time.Clock()
    self.font = pygame.font.Font(None, 40)
    
    self.load_menu_images()
    self.draw_menu_images()
              
  def load_menu_images(self):
    self.resume_img = pygame.image.load(join('code','images','button_resume.png')).convert_alpha()
    self.options_img = pygame.image.load(join('code','images','button_options.png')).convert_alpha()
    self.quit_img = pygame.image.load(join('code','images','button_quit.png')).convert_alpha()
    self.video_img = pygame.image.load(join('code','images','button_video.png')).convert_alpha()
    self.audio_img = pygame.image.load(join('code','images','button_audio.png')).convert_alpha()
    self.keys_img = pygame.image.load(join('code','images','button_keys.png')).convert_alpha()
    self.back_img = pygame.image.load(join('code','images','button_back.png')).convert_alpha()

  def draw_menu_images(self):
    self.resume_button = Button(304, 125, self.resume_img, 1)
    self.options_button = Button(297, 250, self.options_img, 1)
    self.quit_button = Button(336, 375, self.quit_img, 1)
    self.video_button = Button(226, 75, self.video_img, 1)
    self.audio_button = Button(225, 200, self.audio_img, 1)
    self.keys_button = Button(246, 325, self.keys_img, 1)
    self.back_button = Button(332, 450, self.back_img, 1)

  def draw_text(self, text, text_col, x, y):
    img = self.font.render(text, True, text_col)
    self.screen.blit(img, (x, y))

  def run(self):
    while self.running:
      dt = self.clock.tick() / 1000
      
      for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_ESCAPE:
            self.game_paused = True
        if event.type == pygame.QUIT:
          self.running = False
          
      self.screen.fill('black')

      #check if game is paused
      if self.game_paused == True:
        #check menu state
        if self.menu_state == "main":
          #draw pause screen buttons
          if self.resume_button.draw(self.screen):
            self.game_paused = False
          if self.options_button.draw(self.screen):
            self.menu_state = "options"
          if self.quit_button.draw(self.screen):
            self.running = False
        #check if the options menu is open
        if self.menu_state == "options":
          #draw the different options buttons
          if self.video_button.draw(self.screen):
            print("Video Settings")
          if self.audio_button.draw(self.screen):
            print("Audio Settings")
          if self.keys_button.draw(self.screen):
            print("Change Key Bindings")
          if self.back_button.draw(self.screen):
            self.menu_state = "main"
      else:
        self.draw_text("Press Esc to pause", TEXT_COL, SCREEN_WIDTH/2 - 150, SCREEN_HEIGHT/2 - 20)

      pygame.display.update()
            
    pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
