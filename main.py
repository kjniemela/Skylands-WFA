from time import time
import sys
import os
try:
    import pygame
except ModuleNotFoundError:
    print("ModuleNotFoundError: Pygame module could not be found.")
    if input("Install pygame [y/n]? ").lower() == "y":
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
        import pygame
    else:
        exit()

if len(sys.argv) > 1:
    save_file = sys.argv[1]
else:
    save_file = None

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

VERSION_MAJOR = 0
VERSION_MINOR = 1
VERSION_PATCH = 7
    
pygame.display.init()
islandIcon = pygame.image.load(resource_path('assets/icon.png'))
pygame.display.set_icon(islandIcon)

window = pygame.display.set_mode((960, 720), pygame.RESIZABLE)
win = pygame.Surface((480, 360))

pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))

pygame.display.set_caption("Skylands %d.%d.%d" % (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH))

asciiIcon = """                   
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

menuXOffset = 0

#MENU
sky = pygame.image.load(resource_path('assets/sky.png')).convert_alpha()
menuIsland = pygame.image.load(resource_path('assets/menu.png')).convert()
loading = pygame.image.load(resource_path('assets/loading.png'))
playText = pygame.image.load(resource_path('assets/play.png'))

bg = pygame.transform.scale(sky, (480, 360))
menu = pygame.transform.scale(menuIsland, (480, 360))
pl = playText

win.blit(bg, (0, 0))
win.blit(menu, (menuXOffset, 0))
win.blit(loading, (15, 660))
pygame.display.update()

###TEXTURES###
#PLAY MENU
playMenu = pygame.image.load(resource_path('assets/playMenu2.png'))
creditsSlide = pygame.image.load(resource_path('assets/credits.png'))

#PAUSE MENU
button1 = pygame.image.load(resource_path('assets/button1.png'))
button2 = pygame.image.load(resource_path('assets/button2.png'))

#HUD
HUD = pygame.image.load(resource_path('assets/HUD.png'))
HUD_back = pygame.image.load(resource_path('assets/HUD back.png'))

#ITEMS
STBRight = pygame.image.load(resource_path('assets/STB Mk1.png'))
STBLeft = pygame.transform.flip(STBRight, False, True)

items = {1: {
        'stb': STBRight
    }, -1: {
        'stb': STBLeft
        }}

from player import *
from level import *
loadPlayerTextures()
loadLevelTextures()
loadEntityTextures(items)

cursor = pygame.image.load(resource_path('assets/cursor.png'))
##############

###SOUND###
vol = 0.25
playMusic = True

pygame.mixer.pre_init(44100, -16, 4, 512)
pygame.mixer.init()
if playMusic:
    pygame.mixer.init()
    menuMusic = pygame.mixer.Sound(resource_path("assets/The Light - The Album Leaf.wav"))
    gameMusic = pygame.mixer.Sound(resource_path("assets/music.ogg"))
    gameMusic.set_volume(0.4*vol)
    menuMusic.set_volume(1*vol)

GDFSER_shoot = pygame.mixer.Sound(resource_path("assets/GDFSER-fire2.wav"))
GDFSER_shoot.set_volume(1*vol)

loadEntitySounds(vol)
###########

###FONTS###
pygame.font.init()
fonts = {
    "gemCount": pygame.font.Font(pygame.font.match_font('arial', bold=1), 16),
    "buttonText": pygame.font.Font(pygame.font.match_font('arial', bold=1), 24),
    "controlsText": pygame.font.Font(pygame.font.match_font('arial', bold=1), 20),
    "achievementTitle": pygame.font.Font(pygame.font.match_font('inkfree'), 15),
    "achievementSubt": pygame.font.Font(pygame.font.match_font('inkfree'), 6),
    }
###########

###FADE###
class Fade:
    def __init__(self, fadeWhite, fadeBlack):
        self.fadeWhite = fadeWhite
        self.fadeBlack = fadeBlack
        self.alpha = 0
        self.active = False
        self.color = "black"
        self.speed = 1
        self.next_state = ""
        self.fading = True
    def fade_white(self, speed, next_state):
        self.color = "white"
        self.speed = speed
        self.next_state = next_state
        self.active = True
        self.fading = True
    def fade_black(self, speed, next_state):
        self.color = "black"
        self.speed = speed
        self.next_state = next_state
        self.active = True
        self.fading = True
    def draw_static(self, win, alpha):
        if self.color == "white":
            self.fadeWhite.set_alpha(alpha)
            win.blit(self.fadeWhite, (0,0))
        elif self.color == "black":
            self.fadeBlack.set_alpha(alpha)
            win.blit(self.fadeBlack, (0,0))
    def draw(self, win):
        global gameState
        
        if self.active:
            if self.color == "white":
                self.fadeWhite.set_alpha(self.alpha)
                win.blit(self.fadeWhite, (0,0))
            elif self.color == "black":
                self.fadeBlack.set_alpha(self.alpha)
                win.blit(self.fadeBlack, (0,0))
            if self.fading:
                if self.alpha < 255:
                    self.alpha += self.speed
                else:
                    self.fading = False
                    gameState = self.next_state
            else:
                if self.alpha > 0:
                    self.alpha -= self.speed
                else:
                    self.active = False

fade = Fade(pygame.image.load(resource_path('assets/fadeWhite.png')).convert(),\
            pygame.image.load(resource_path('assets/fadeBlack.png')).convert())
##########

clock = pygame.time.Clock()
creditsY = 0

controlsDisplayPage = 0
lastControl = ""
controlsList = [
    [#page 1
        [['A', "Walk Left"], ['S', "Sneak"]],#column 1
        [['W', "Jump"], ['Space', "Shoot"]],#column 2
        [['D', "Walk Right"], ['', ""], ['P', "Pause"]] #column 3
    ],
    [#page 2
        [['B', "Debug Mode"]],#column 1
        [['F', "Toggle Flight"]],#column 2
        [['T', "Reset Level"]] #column 3
    ]
]
keyMap = {
    'W': pygame.K_w,
    'A': pygame.K_a,
    'S': pygame.K_s,
    'D': pygame.K_d,
    'Space': pygame.K_SPACE,
    'B': pygame.K_b,
    'F': pygame.K_f,
    'T': pygame.K_t,
    'P': pygame.K_p,
}
controlsMap = {}
def updateControlsMap():
    global controlsMap
    controlsMap = {
        "left": keyMap[controlsList[0][0][0][0]],
        "up": keyMap[controlsList[0][1][0][0]],
        "right": keyMap[controlsList[0][2][0][0]],
        "fire": keyMap[controlsList[0][1][1][0]],
        "sneak": keyMap[controlsList[0][0][1][0]],
        "pause": keyMap[controlsList[0][2][2][0]],
        "debug": keyMap[controlsList[1][0][0][0]],
        "fly": keyMap[controlsList[1][1][0][0]],
        "reset": keyMap[controlsList[1][2][0][0]],
    }
updateControlsMap()

selCol = -1
selRow = 0

def drawGameWindow():
    global gameState
    global player
    global fonts
    global creditsY
    global selCol
    global selRow

    zoom = 1 #make global or smth later

    if gameState == "mainMenu" or gameState == "fade":
        if gameState == "fade":
            win.blit(bg, (0, 0))
        win.blit(menu, (0, 0))
        if gameState == "mainMenu":
            win.blit(pl, (176, 306))
    elif gameState == "playMenu":
        win.blit(playMenu, (0, 0))
        win.blit(cursor, (mouseX-8,mouseY-8))
    elif gameState == "credits":
        win.fill((251, 251, 254))
        win.blit(creditsSlide, (0, min(creditsY, 0)))
        creditsY -= 1
        if creditsY < -1440:
            fade.fade_white(6, "playMenu")
    elif gameState == "inGame":
        win.fill((240, 240, 255))
        level.draw(camX, camY, win, mouseX, mouseY, winW, winH)
        player.draw(camX, camY, win, mouseX, mouseY, winW, winH)
        level.draw_overlays(camX, camY, win, mouseX, mouseY, winW, winH)

        win.blit(HUD_back, (293, 28))
        drawHUD(win, player, fonts)
        win.blit(HUD, (0, 0))

        level.achievement_handler.draw(win, level, fonts)

        win.blit(cursor, (mouseX-8,mouseY-8))
    elif gameState == "paused":
        win.fill((240, 240, 255))

        win.blit(HUD_back, (293, 28))
        drawHUD(win, player, fonts)
        win.blit(HUD, (0, 0))

        fade.color = "black"
        fade.draw_static(win, 200)

        win.blit(button2, (140, 100))
        win.blit(button2, (140, 150))
        win.blit(button2, (140, 200))
        resumeText = fonts["buttonText"].render("Resume", True, (170, 170, 190), (130, 132, 130))
        settingsText = fonts["buttonText"].render("Settings", True, (170, 170, 190), (130, 132, 130))
        controlsText = fonts["buttonText"].render("Controls", True, (170, 170, 190), (130, 132, 130))
        win.blit(resumeText, (194, 106))
        win.blit(settingsText, (193, 156))
        win.blit(controlsText, (191, 206))

        win.blit(cursor, (mouseX-8,mouseY-8))
    elif gameState == "settings":
        win.fill((80, 80, 80))

        #win.blit(HUD_back, (293, 28))
        #drawHUD(win, player, fonts)
        #win.blit(HUD, (0, 0))

        #fade.color = "black"
        #fade.draw_static(win, 200)

        win.blit(button1, (10, 300))
        win.blit(button1, (172, 300))
        win.blit(button1, (334, 300))
        #win.blit(button2, (140, 150))
        returnText = fonts["buttonText"].render("Return", True, (200, 200, 220), (130, 132, 130))
        nextText = fonts["buttonText"].render("Next ->", True, (200, 200, 220), (130, 132, 130))
        prevText = fonts["buttonText"].render("<- Prev", True, (200, 200, 220), (130, 132, 130))
        win.blit(returnText, (202, 306))
        win.blit(nextText, (334+((136-fonts["buttonText"].size("Next ->")[0])/2), 306))
        win.blit(prevText, (10+((136-fonts["buttonText"].size("<- Prev")[0])/2), 306))

        for i in range(3):
            for j in range(3):
                try:
                    string1 = controlsList[controlsDisplayPage][j][i][1]
                    text1 = fonts["controlsText"].render(string1, True, (170, 170, 190), (80, 80, 80))
                    win.blit(text1, ((10+(162*j))+((136-fonts["controlsText"].size(string1)[0])/2), 16+(i*80)))
                    
                    string1 = controlsList[controlsDisplayPage][j][i][0]
                    win.blit(button1, (10+(162*j), 40+(i*80)))
                    if j == selCol and i == selRow:
                        text1 = fonts["buttonText"].render(string1, True, (230, 230, 190), (130, 132, 130))
                    else:
                        text1 = fonts["buttonText"].render(string1, True, (200, 200, 220), (130, 132, 130))
                    win.blit(text1, ((10+(162*j))+((136-fonts["buttonText"].size(string1)[0])/2), 46+(i*80)))
                except IndexError:
                    pass

        win.blit(cursor, (mouseX-8,mouseY-8))

    fade.draw(win)
    window.blit(pygame.transform.scale(win, (winW*zoom, winH*zoom)), (menuXOffset-(winW*(0.5*(zoom-1))),-(winW*(0.5*(zoom-1)))))
    pygame.display.update()

def controlsScreen(nextState):
    global run
    global keys
    global held
    global gameState
    global mouseX
    global mouseY
    global player
    global level
    global menuXOffset
    global winW
    global winH
    global controlsList
    global controlsDisplayPage
    global selCol
    global selRow

    controls = True
    selCol = -1
    selRow = 0

    gameState = "settings"
    while run and controls:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if not save_file == None:
                    player.save()
                run = False
            if event.type == pygame.MOUSEMOTION:
                mouseX, mouseY = event.pos
                mouseX -= menuXOffset
                mouseX *= 480/winW
                mouseY *= 360/winH
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouseX, mouseY = event.pos
                    mouseX -= menuXOffset
                    mouseX *= 480/winW
                    mouseY *= 360/winH
##                    if mouseY>318 and mouseX<42:
##                        pause = False
                    if 300<mouseY<340:
                        if 172<mouseX<308:
                            controls = False
                        elif 10<mouseX<146:
                            controlsDisplayPage = (controlsDisplayPage-1)%len(controlsList)
                        elif 334<mouseX<470:
                            controlsDisplayPage = (controlsDisplayPage+1)%len(controlsList)
                    for col in range(3):
                        if 10+(162*col)<mouseX<146+(162*col):
                            for row in range(3):
                                if 40+(row*80)<mouseY<80+(row*80):
                                    try:
                                        selCol = col
                                        selRow = row
                                    except IndexError:
                                        pass
            if event.type == pygame.VIDEORESIZE:
                winW, winH = int(480*(event.h/360)), event.h
                surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                #bg = pygame.transform.scale(sky, (event.w, event.h))
                #menu = pygame.transform.scale(menuIsland, (480, 360))
                pl = pygame.transform.scale(playText, (int(255*(event.h/720)), int(event.h/18)))
                menuXOffset = int(event.w/2) - int(960*(event.h/720)/2)
                
        held = keys
        keys = pygame.key.get_pressed()

        if True in keys and selCol > -1:
            k = keys.index(True)
            lastControl = controlsList[controlsDisplayPage][selCol][selRow][0]
            controlsList[controlsDisplayPage][selCol][selRow][0] = pygame.key.name(k).capitalize()
            try:
                updateControlsMap()
            except KeyError:
                controlsList[controlsDisplayPage][selCol][selRow][0] = lastControl
            selCol = -1

        drawGameWindow()

##        pygame.display.set_caption("Skylands %d.%d.%d    FPS: %d X: %d Y: %d ~ %d %d ~ %d %d"\
##                               % (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH,
##                                  FPS, player.x, player.y, camX+mouseX, camY-mouseY, mouseX, mouseY))
    
    gameState = nextState

def pauseScreen(nextState):
    global run
    global keys
    global held
    global gameState
    global mouseX
    global mouseY
    global player
    global level
    global menuXOffset
    global winW
    global winH

    pause = True

    gameState = "paused"
    while run and pause:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if not save_file == None:
                    player.save()
                run = False
            if event.type == pygame.MOUSEMOTION:
                mouseX, mouseY = event.pos
                mouseX -= menuXOffset
                mouseX *= 480/winW
                mouseY *= 360/winH
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouseX, mouseY = event.pos
                    mouseX -= menuXOffset
                    mouseX *= 480/winW
                    mouseY *= 360/winH
##                    if mouseY>318 and mouseX<42:
##                        pause = False
                    if 140<mouseX<340:
                        if 100<mouseY<140:
                            pause = False
                        if 150<mouseY<190:
                            pass
                        if 200<mouseY<240:
                            controlsScreen("paused")
            if event.type == pygame.VIDEORESIZE:
                winW, winH = int(480*(event.h/360)), event.h
                surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                #bg = pygame.transform.scale(sky, (event.w, event.h))
                #menu = pygame.transform.scale(menuIsland, (480, 360))
                pl = pygame.transform.scale(playText, (int(255*(event.h/720)), int(event.h/18)))
                menuXOffset = int(event.w/2) - int(960*(event.h/720)/2)
                
        held = keys
        keys = pygame.key.get_pressed()

        if keys[controlsMap["pause"]] and not held[controlsMap["pause"]]:
            break

        drawGameWindow()

##        pygame.display.set_caption("Skylands %d.%d.%d    FPS: %d X: %d Y: %d ~ %d %d ~ %d %d"\
##                               % (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH,
##                                  FPS, player.x, player.y, camX+mouseX, camY-mouseY, mouseX, mouseY))
    
    gameState = nextState

print(asciiIcon)
print("Skylands: Worlds from Above v%d.%d.%d" % (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH))

player = Player(125, 25, save_file)
level = Level("lab", player)

run = True
runMenu = True
gameState = "mainMenu"
mouseX, mouseY = 0, 0
camX, camY = ((player.x+5)-(480/2)), ((player.y+20)+(360/2))
winW, winH = 500, 480
fpst = time()
fps = 0
FPS = 60
fly = False
held = {}
keys = pygame.key.get_pressed()

if playMusic:
    curChannel = menuMusic.play(-1)

    while run and runMenu:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEMOTION:
                mouseX, mouseY = event.pos
                mouseX -= menuXOffset
                mouseX *= 480/winW
                mouseY *= 360/winH
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouseX, mouseY = event.pos
                    mouseX -= menuXOffset
                    mouseX *= 480/winW
                    mouseY *= 360/winH
                    #print(mouseX, mouseY)
                    if gameState == "playMenu":
                        if mouseY<32 and 375<mouseX<470:
                            runMenu = False
                        if 47<mouseY<77 and 375<mouseX<470:
                            #LOAD
                            pass
                        if 125<mouseY<155 and 375<mouseX<470:
                            #SETTINGS
                            controlsScreen("playMenu")
                        if 310<mouseY<348 and 377<mouseX<465:
                            fade.fade_white(6, "mainMenu")
                        if 310<mouseY<348 and 16<mouseX<100:
                            creditsY = 40
                            fade.fade_white(6, "credits")
            if event.type == pygame.VIDEORESIZE:
                winW, winH = int(480*(event.h/360)), event.h
                surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                bg = pygame.transform.scale(sky, (event.w, event.h))
                menu = pygame.transform.scale(menuIsland, (480, 360))
                pl = pygame.transform.scale(playText, (127, 20))
                menuXOffset = int(event.w/2) - int(480*(event.h/360)/2)

        keys = pygame.key.get_pressed()

        if gameState == "mainMenu":
            if keys[pygame.K_SPACE]:
                fade.fade_white(6, "playMenu")

        drawGameWindow()
    if playMusic:
        menuMusic.fadeout(1000)
    fade.fade_black(6, "inGame")
else:
    gameState = "inGame"

currentlyPlaying = None

def startMusic(music):
    global currentlyPlaying
    global curChannel
    if curChannel.get_busy() and not music == currentlyPlaying:
        curChannel = music.play(-1)
        currentlyPlaying = music
    elif not curChannel.get_busy():
        curChannel = music.play(-1)
        currentlyPlaying = music

while run:
    clock.tick(60)
    if playMusic:
        startMusic(gameMusic)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if not save_file == None:
                player.save()
            run = False
        if event.type == pygame.MOUSEMOTION:
            mouseX, mouseY = event.pos
            mouseX -= menuXOffset
            mouseX *= 480/winW
            mouseY *= 360/winH
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouseX, mouseY = event.pos
                mouseX -= menuXOffset
                mouseX *= 480/winW
                mouseY *= 360/winH
                if mouseY>318 and mouseX<42:
                    pauseScreen("inGame")
        if event.type == pygame.VIDEORESIZE:
            winW, winH = int(480*(event.h/360)), event.h
            surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            #bg = pygame.transform.scale(sky, (event.w, event.h))
            #menu = pygame.transform.scale(menuIsland, (480, 360))
            pl = pygame.transform.scale(playText, (int(255*(event.h/720)), int(event.h/18)))
            menuXOffset = int(event.w/2) - int(960*(event.h/720)/2)

    held = keys
    keys = pygame.key.get_pressed()

    if keys[controlsMap["pause"]] and not held[controlsMap["pause"]]:
        pauseScreen("inGame")

    player.x += player.xVel
    player.y += player.yVel
    
    if keys[pygame.K_x]:
        player.width = 30
        player.xOffset = 5
    else:
        player.xOffset = 0
        player.width = 40

    player.get_touching(level)

    if keys[controlsMap["left"]]:
        player.xVel -= 2
        player.walkFrame += player.facing*-1
        #player.facing = -1
    if keys[controlsMap["right"]]:
        player.xVel += 2
        player.walkFrame += player.facing
        #player.facing = 1

    player.xVel *= 0.6
    if abs(player.xVel) < 0.01:
        player.xVel = 0
    if player.falling and not fly:
        player.yVel -= level.gravity
        
    if fly:
        if keys[controlsMap["up"]]:
            player.yVel = 5
        elif keys[controlsMap["sneak"]]:
            player.yVel = -5
        elif not  keys[pygame.K_g]:
            player.yVel *= 0.9
    else:
        if keys[controlsMap["up"]] and player.touchingPlatform and player.jumping == 0:
            player.jumping = 1
            player.yVel += 10
        elif player.touchingPlatform:
            if keys[controlsMap["sneak"]]:
                player.heightHead = 0
            else:
                player.heightHead = 18
        
    if keys[controlsMap["fly"]] and not held[controlsMap["fly"]]:
        if not fly:
            player.yVel += 5
            fly = True
        else:
            fly = False

    if keys[controlsMap["debug"]] and not held[controlsMap["debug"]]:
        level.debugMode = not level.debugMode
        
    if keys[controlsMap["reset"]]:
        level = Level(level.src, player)
    if keys[controlsMap["fire"]] and player.gunCooldown == 0:
        GDFSER_shoot.play()
        bulletspeed = 20
        level.projectiles.append(Bullet(player.gunX, -player.gunY, player.rightArm+(player.rightHand*player.facing), bulletspeed, player))
        player.gunCooldown = 30

    if player.gunCooldown > 0:
        player.gunCooldown -= 1

    if player.y < -2000:
        player.hp = 0

    if player.hp <= 0:
        player.kill()
        level.achievement_handler.trigger("StillAlive")

    camX += (((player.x+5)-(480/2))-camX)*0.2
    camY += (((player.y+20)+(360/2))-camY)*0.2

    drawGameWindow()
    
    fps += 1
    if time() - fpst > 1:
        fpst = time()
        FPS = fps
        fps = 0
##    pygame.display.set_caption("Skylands %d.%d.%d    FPS: %d X: %d Y: %d ~ %d %d ~ %d %d"\
##                               % (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH,
##                                  FPS, player.x, player.y, camX+mouseX, camY-mouseY, mouseX, mouseY))

pygame.quit()
