from utils import *
from sound import SoundController
from fade import Fade

ascii_icon = """                   
         %%%%@  *@@@            
      *##################       
    ######################(     
 ###########################@###
  ,,,,,,,##########,,,*,,,,,&,,#
   ,,,,,,,,,,,,#,,,,,,,,,,,,%,, 
     ,,,,,,,,,,,,,,,,,,,,,,,%,  
      ,,,,,,,,,,,,,,,,,,,,,,#   
      .,,,,,,,,,,,,,,,,,,,,,(   
        ,,,,,,,,,,,,,,,,,,, @   
           ,,,,,,,,,,,,,,.  @   
            .,  ,,,,,,,,,   @   
                ,,,,,,,,    @   
                  ,,,,          
                   , .     
"""

## Constants
DISPLAY_WIDTH, DISPLAY_HEIGHT = 480, 360

class WindowController:
    def __init__(self):
        self.textures = {}
        self.items = {
            1: {},
            -1: {}
        }

        self.mouse_pos = (0, 0)
        self.menu_offsets = (0, 0)
        self.win_size = (DISPLAY_WIDTH * 2, DISPLAY_HEIGHT * 2)
        self.setup_window()

        ## Display Loading Screen
        self.intro_credits = self.load_texture("assets/intro.png")
        loading_text = self.load_texture("assets/loading.png")
        self.win.blit(self.intro_credits, (0, 0))
        self.win.blit(loading_text, (374, 330))
        self.draw(self.win_size, self.menu_offsets)

        self.setup_sound()
        self.setup_textures()
        self.setup_fonts()

    def cl_intro(self):
        print(ascii_icon)
        print("Skylands: Worlds from Above v%d.%d.%d" % self.version)

    def draw(self, size, offset):
        pygame.transform.scale(self.win, size, self.win2)
        self.window.blit(self.win2, offset)
        pygame.display.update()

    def load_item(self, name, path):
        texture_right = self.load_texture(path)
        texture_left = pygame.transform.flip(texture_right, False, True)
        self.items[1][name] = texture_right
        self.items[-1][name] = texture_left

    def load_texture(self, path):
        return pygame.image.load(resource_path(path))

    def set_version(self, major, minor, patch):
        self.version = major, minor, patch
        pygame.display.set_caption("Skylands %d.%d.%d" % self.version)

    def set_player(self, player):
        self.player = player

    def setup_window(self):
        ## Set up pygame window
        pygame.display.init()
        self.island_icon = pygame.image.load(resource_path("assets/icon.png"))
        pygame.display.set_icon(self.island_icon)

        ## TODO: find better names for these
        self.window = pygame.display.set_mode(self.win_size, pygame.RESIZABLE)
        self.win = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.win2 = pygame.Surface(self.win_size)

        pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))

    def setup_sound(self):
        ## Try to create sound controller
        try:
            self.sound_ctrl = SoundController()
        except pygame.error:
            self.sound_ctrl = None
        
        if self.sound_ctrl:
            ## TODO OBS: these should indicate to the controller that they are music files and not sound effects!
            self.menu_music_start = self.sound_ctrl.load_music("assets/music/Skylands Theme Start.ogg")
            self.menu_music = self.sound_ctrl.load_music("assets/music/Skylands Theme Loop.ogg")

        self.sounds = {
            "player_shoot": self.sound_ctrl.load_sound("assets/sounds/GDFSER1.wav"),
            "stb_shoot": self.sound_ctrl.load_sound("assets/sounds/GDFSER2.wav"),
            "step1": self.sound_ctrl.load_sound("assets/sounds/step1.wav"),
            "step2": self.sound_ctrl.load_sound("assets/sounds/step2.wav"),
            "step3": self.sound_ctrl.load_sound("assets/sounds/step3.wav"),
            "land": self.sound_ctrl.load_sound("assets/sounds/land.wav"),
            "hurt": self.sound_ctrl.load_sound("assets/sounds/hurt.wav"),
            "pickup": self.sound_ctrl.load_sound("assets/sounds/gem.wav"),
            "alert": self.sound_ctrl.load_sound("assets/sounds/alert.wav"),
            "click": self.sound_ctrl.load_sound("assets/sounds/click.wav"),
            "door_open": self.sound_ctrl.load_sound("assets/sounds/door_open.wav"),
            "door_close": self.sound_ctrl.load_sound("assets/sounds/door_close.wav"),
            "powerup": self.sound_ctrl.load_sound("assets/sounds/powerup.wav"),
            "hum": self.sound_ctrl.load_sound("assets/sounds/hum.wav"),
            "button": self.sound_ctrl.load_sound("assets/sounds/button.wav"),
        }

    def setup_textures(self):
        self.play_text = self.load_texture("assets/play.png")
        self.sky = pygame.transform.scale( self.load_texture('assets/sky.png').convert_alpha() , (480, 360))
        self.menu_island = pygame.transform.scale( self.load_texture('assets/menu.png').convert() , (480, 360))

        ## PLAY MENU
        self.play_menu = self.load_texture("assets/playMenu.png")
        self.credits_slide = self.load_texture("assets/credits.png")

        ## PAUSE MENU
        self.button1 = self.load_texture("assets/button1.png")
        self.button2 = self.load_texture("assets/button2.png")

        ## HUD
        self.hud = self.load_texture("assets/HUD.png")
        self.hud_back = self.load_texture("assets/HUD back.png")

        ## ITEMS
        self.load_item("stb", "assets/STB Mk1.png")

        ## Cursor
        self.cursor = self.load_texture("assets/cursor.png")

        ## Fade Screen
        self.fade = Fade(
            self.load_texture("assets/fadeWhite.png").convert(),
            self.load_texture("assets/fadeBlack.png").convert()
        )

    def setup_fonts(self):
        pygame.font.init()
        self.fonts = {
            "gemCount": pygame.font.Font(pygame.font.match_font("arial", bold=1), 16),
            "buttonText": pygame.font.Font(pygame.font.match_font("arial", bold=1), 24),
            "controlsText": pygame.font.Font(pygame.font.match_font("arial", bold=1), 20),
            "achievementTitle": pygame.font.Font(pygame.font.match_font("inkfree"), 15),
            "achievementSubt": pygame.font.Font(pygame.font.match_font("inkfree"), 6),
        }

    def render_view(self, view):
        if view == None:
            return False

        ## TODO FIXME
        zoom = 1

        view.render()

        self.win.blit(self.cursor, (self.mouse_pos[0] - 8, self.mouse_pos[1] - 8))

        self.fade.draw(self.win)
        # pygame.transform.scale(self.win, self.win_size, self.win2)
        self.draw(self.win_size, self.menu_offsets)
        self.window.blit(
            self.win2, 
            (
                self.menu_offsets[0] - ( self.win_size[0] * ( 0.5 * (zoom - 1))),
                self.menu_offsets[1] - ( self.win_size[0] * ( 0.5 * (zoom - 1))),
            ),
        )
        pygame.display.update()