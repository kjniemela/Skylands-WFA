from utils import *
from window import controller

class Player:
    def __init__(self, x, y, save_file=None):
        self.save_file = save_file
        self.spawnpoint = (x, y)
        self.xOffset = 0
        self.width = 40
        self.lastXOffset = 0
        self.lastWidth = 0
        self.heightHead = 18
        self.heightBody = 48
        self.walkFrame = 0
        self.facing = 1
        self.touchingPlatform = False
        self.falling = True
        self.jumping = 0
        self.walljump = False
        self.sneaking = False
        self.wallJumpTime = 0
        self.gunX = 0
        self.gunY = 0
        self.level = None
        self.rightArm = 0
        self.leftArm = 0
        self.rightHand = 0
        self.leftHand = 0
        self.gunCooldown = 0
        self.reloadSpeed = 2
        self.reload = True
        self.gunPower = 40
        self.maxPower = 240
        self.power = 0
        self.aim = 0
        self.quest = "B116"
        self.drawHUD = True
        if save_file == None:
            self.x = x
            self.y = y
            self.xVel = 0
            self.yVel = 0

            self.gems = 0
            
            self.hp = 10
            self.maxHp = 10
        else:
            self.load(self.save_file)
    def set_spawn(self, x, y):
        self.x = x
        self.y = y
        self.spawnpoint = (x, y)
    def load(self, save_file):
        with open(save_file) as f:
            data = f.read().split('\n')
        print(data)
        self.x = float(data[1])
        self.y = float(data[2])
        self.xVel = float(data[3])
        self.yVel = float(data[4])
        #self.gunCooldown = int(data[5])
        self.gems = int(data[6])
        self.hp = int(data[7])
        self.maxHp = int(data[8])
    def save(self):
        with open(self.save_file, mode='w') as f:
            data = [
                str("SAVENAME"),
                str(self.x),
                str(self.y),
                str(self.xVel),
                str(self.yVel),
                str(self.gunCooldown),
                str(self.gems),
                str(self.hp),
                str(self.maxHp),
                ]
            f.write('\n'.join(data))

    def update(self):
        pass

    def draw(self, playerdata, camX, camY):

        win = controller.win
        mouseX, mouseY = controller.mouse_pos
        winW, winH = controller.win_size

        if not self.level == None:
            if self.level.debugMode:
                pygame.draw.rect(win, (0, 0, 0),
                                 ((self.x+self.xOffset)-camX, -((self.y+self.heightHead)-camY),
                                  self.width, self.heightHead+self.heightBody))
        head_rot = -math.degrees(math.atan2(mouseY-(180+24), mouseX-(240+16)))
        head_rot_left = ((360+(head_rot))%360)-180#math.degrees(math.atan2(mouseY-(180+15), 240-mouseX))
        self.aim = head_rot
        
        if abs(head_rot)> 90:
            self.facing = -1
        else:
            self.facing = 1
        
        if self.walkFrame + 1 >= 32:
            self.walkFrame = 0
        if self.walkFrame < 0:
            self.walkFrame = 30

        if (self.walkFrame == 10 or self.walkFrame == 25) and self.touchingPlatform:
            controller.sound_ctrl.play_sound(controller.sounds["step%i"%(randint(1, 3))])

        for i in playerdata:
            try:
                self.drawPlayer(playerdata[i][0], playerdata[i][1], -1 if abs(playerdata[i][2])> 90 else 1, playerdata[i][2], camX, camY, win, mouseX, mouseY, winW, winH)
            except IndexError:
                print(playerdata[i])
            
        self.drawPlayer(self.x, self.y, self.facing, head_rot, camX, camY)
    def drawPlayer(self, x, y, facing, head_rot, camX, camY):

        win = controller.win
        player_textures = controller.player_textures
        # mouseX, mouseY = controller.mouse_pos
        # winW, winH = controller.win_size

        head_rot_left = ((360+(head_rot))%360)-180
        self.rightArm = head_rot-(15*facing)#(Sin((time()+1)*40)*10)-90-(5*self.facing)#
        self.leftArm = (Sin(time()*40)*10)-90-(5*facing)
        self.rightHand = 15
        self.leftHand = 10

        #arm position is a bit buggy
        
        if facing == -1:
            blitRotateCenter(win, player_textures["arm_far"][-1], self.rightArm, (x-(3),-y-(2)), (camX,camY))
            handX = (x-(8))+(Cos(-self.rightArm)*(11))
            handY = (-y-(0))+(Sin(-self.rightArm)*(11))
            self.gunX = (handX+(8))+(Cos(-(self.rightArm-self.rightHand))*(15))
            self.gunY = handY+(Sin(-(self.rightArm-self.rightHand))*(16))
            blitRotateCenter(win, player_textures["hand_far"][-1], self.rightArm-self.rightHand, (handX,handY), (camX,camY))
            blitRotateCenter(win, controller.items["GDFSER"][-1], self.rightArm-self.rightHand, (self.gunX,self.gunY), (camX,camY))
        elif facing == 1:
            blitRotateCenter(win, player_textures["arm_far"][1], self.leftArm, (x+(15),-y-(2)), (camX,camY))
            handX = (x+(11))+(Cos(-self.leftArm)*(11))
            handY = (-y-(0))+(Sin(-self.leftArm)*(11))
            blitRotateCenter(win, player_textures["hand_far"][1], self.leftArm+self.leftHand, (handX,handY), (camX,camY))

        if self.sneaking:
            win.blit(player_textures["sneak"][facing], (x-camX+3,-(y-camY)) if self.facing < 0 else (x-camX-7,-(y-camY)))
        else:
            if abs(self.xVel) > 0:
                win.blit(player_textures["walk"][facing][self.walkFrame//4], (x-camX,-(y-camY)))
            else:
                win.blit(player_textures["idle"][facing], (x-camX,-(y-camY)))

        if facing == -1:
            blitRotateCenter(win, player_textures["head"][-1], min(max(head_rot_left, -45), 45), (x,-y-(20)), (camX,camY))
        elif facing == 1:
            blitRotateCenter(win, player_textures["head"][1], min(max(head_rot, -45), 45), (x,-y-(20)), (camX,camY))

        if facing == -1:
            blitRotateCenter(win, player_textures["arm_near"][-1], -self.leftArm, (x+17,-y-0), (camX,camY))
            handX = (x+(12))-(Cos(-self.leftArm)*(11))
            handY = (-y-(0))+(Sin(-self.leftArm)*(11))
            blitRotateCenter(win, player_textures["hand_near"][-1], -self.leftArm-self.leftHand, (handX,handY), (camX,camY))
        elif facing == 1:
            blitRotateCenter(win, player_textures["arm_near"][1], self.rightArm, (x-2,-y-(2)), (camX,camY))
            handX = (x-(8))+(Cos(-self.rightArm)*(11))
            handY = (-y-(0))+(Sin(-self.rightArm)*(11))
            self.gunX = (handX+(8))+(Cos(-(self.rightArm+self.rightHand))*(15))
            self.gunY = handY+(Sin(-(self.rightArm+self.rightHand))*(16))
            blitRotateCenter(win, controller.items["GDFSER"][1], self.rightArm+self.rightHand, (self.gunX,self.gunY), (camX,camY))
            blitRotateCenter(win, player_textures["hand_near"][1], self.rightArm+self.rightHand, (handX,handY), (camX,camY))

    def damage(self, dmg, src, knockback=(0,0)):
        """
        0: fall damage - 1: melee damage
        """
        controller.sound_ctrl.play_sound(controller.sounds["hurt"])
        self.hp -= dmg
        self.xVel += knockback[0]
        self.yVel += knockback[1]

    def kill(self):
        level = self.level
        self.__init__(*self.spawnpoint, self.save_file)
        self.level = level

    def check_inside(self, x, y):
        if self.x<x and self.x+(self.width)>x and self.y+(self.heightHead)>y and self.y-(self.heightBody)<y:
            return (True, (self.x+(self.width/2))-x, self.y-y)
        else:
            return (False, 0, 0)

    def get_colliding_platform(self, platform, down):
        x3 = platform.x-((platform.w/2)*Cos(-platform.d))+((platform.h/2)*Sin(-platform.d))
        y3 = platform.y+((platform.h/2)*Cos(-platform.d))+((platform.w/2)*Sin(-platform.d))
        x4 = platform.x+((platform.w/2)*Cos(-platform.d))+((platform.h/2)*Sin(-platform.d))
        y4 = platform.y+((platform.h/2)*Cos(-platform.d))-((platform.w/2)*Sin(-platform.d))
        return self.get_colliding_lines(x3, y3, x4, y4, platform.d)

    def get_colliding_lines(self, x3, y3, x4, y4, d, down=True):
        if ((d+180)%360)-180 > 0:
            col1 = line_collision((self.x+self.width+self.xOffset, self.y+(self.heightHead),
                                   self.x+self.width+self.xOffset, self.y-(self.heightBody)),
                             (x3, y3, x4, y4))
            if not col1[0]:
                col1 = line_collision((self.x+self.xOffset, self.y+(self.heightHead),
                                       self.x+self.xOffset, self.y-(self.heightBody)),
                             (x3, y3, x4, y4))  
        else:
            col1 = line_collision((self.x+self.xOffset, self.y+(self.heightHead),
                                   self.x+self.xOffset, self.y-(self.heightBody)),
                             (x3, y3, x4, y4))
            if not col1[0]:
                col1 = line_collision((self.x+self.width+self.xOffset, self.y+(self.heightHead),
                                       self.x+self.width+self.xOffset, self.y-(self.heightBody)),
                             (x3, y3, x4, y4))
        col2 = line_collision((self.x+self.xOffset, self.y-(self.heightBody),
                               self.x+self.width+self.xOffset, self.y-(self.heightBody)),
                             (x3, y3, x4, y4))
        
        #blitRotateCenter(self.win, headRight, 0, (x3, -y3), (camX,camY))
        #blitRotateCenter(self.win, headRight, 0, (x4, -y4), (camX,camY))
        #pygame.draw.aaline(self.win, (111, 255, 239, 0.5), (x3-camX, -(y3-camY)), (x4-camX, -(y4-camY)))
        if col1[0]:
            self.touchingPlatform = True
            #blitRotateCenter(self.win, headRight, 0, (col[1],-col[2]), (camX,camY))
            self.downTouching = col1[2]-(self.y-(self.heightBody))
        if col2[0]:
            self.touchingPlatform = True
            #blitRotateCenter(self.win, headRight, 0, (col2[1],-col2[2]), (camX,camY))
            if ((d+180)%360)-180 > 0:
                self.rightTouching = (self.x+self.width+self.xOffset)-col2[1]
            else:
                self.leftTouching = col2[1]-self.x
        return col1[0] if down else col2[0]

    def get_touching(self, level, controlsMap, xOld, yOld):
        self.rightTouching = 0
        self.leftTouching = 0
        self.upTouching = 0
        self.downTouching = 0
        self.falling = True
        self.touchingPlatform = False
        xChange = self.xVel
        yChange = self.yVel

        for platform in level.platforms:
            if platform.d == 0:
                if self.x+self.xOffset<platform.x+(platform.w/2) and\
                self.x+(self.width+self.xOffset)>platform.x-(platform.w/2) and\
                self.y+(self.heightHead)>platform.y-(platform.h/2) and\
                self.y-(self.heightBody)<platform.y+(platform.h/2):
                    self.touchingPlatform = True
                    self.rightTouching = (self.x+(self.width+self.xOffset))-(platform.x-(platform.w/2))
                    self.leftTouching = (platform.x+(platform.w/2))-(self.x+self.xOffset)
                    self.upTouching = (self.y+(self.heightHead))-(platform.y-(platform.h/2))
                    self.downTouching = (platform.y+(platform.h/2))-(self.y-(self.heightBody))
                    if self.downTouching > 0 and self.downTouching <= -(yChange-2):
                        if self.yVel < -5:
                            controller.sound_ctrl.play_sound(controller.sounds["land"])
                        if self.yVel < -20:
                            dmg = math.ceil((abs(self.yVel)-11)/8)
                            self.yVel = 0
                            self.damage(dmg, 0) #FALL DAMAGE
                        else:
                            self.yVel = 0
                        self.y += math.ceil(self.downTouching)-1
                        self.jumping = 0
                        self.falling = False
                    if self.upTouching > 0 and self.upTouching <= yChange:
                        self.yVel = 0
                        self.y -= math.ceil(self.upTouching)
                        #self.yChange -= math.ceil(self.upTouching)
                    if self.downTouching > 1 and self.rightTouching > 0 and self.rightTouching <= self.xVel+((self.xOffset+self.width)-(self.lastXOffset+self.lastWidth)): #this needs to be the relative xVel between the player and the platform
                        self.xVel = 0
                        self.x -= math.ceil(self.rightTouching)
                        if self.downTouching < 6:
                            self.y += self.downTouching
                        if controlsMap["left"] and (not self.walljump or self.wallJumpTime > 40):
                            self.xVel = -4
                            self.yVel = 10
                            self.walljump = True
                            self.falling = True
                            self.wallJumpTime = 0
##                    elif self.downTouching > 1 and self.rightTouching > 0 and self.rightTouching <= self.xVel+((self.xOffset+self.width)-(self.lastXOffset+self.lastWidth)):
##                        self.xVel = 0
##                        self.xOffset = self.lastXOffset
##                        self.width = self.lastWidth
                    if self.downTouching > 1 and self.leftTouching > 0 and self.leftTouching <= (-self.xVel)+(self.lastXOffset-self.xOffset): #this needs to be the relative xVel between the player and the platform
                        self.xVel = 0
                        self.x += math.ceil(self.leftTouching)
                        if self.downTouching < 6:
                            self.y += self.downTouching
                        if controlsMap["right"] and (not self.walljump or self.wallJumpTime > 40):
                            self.xVel = 4
                            self.yVel = 10
                            self.walljump = True
                            self.falling = True                  
                            self.wallJumpTime = 0
##                    elif self.downTouching > 1 and self.leftTouching > 0 and self.leftTouching <= (-self.xVel)+(self.lastXOffset-self.xOffset):
##                        self.xVel = 0
##                        self.xOffset = self.lastXOffset
            else:
                if self.get_colliding_platform(platform, True):
                    if self.downTouching > 0:
                        if self.yVel < -20:
                            dmg = math.ceil((abs(self.yVel)-11)/8)
                            self.yVel = 0
                            self.damage(dmg, 0) #FALL DAMAGE
                        else:
                            self.yVel += 0
                        self.y += self.downTouching-1
                        self.jumping = 0
                        self.falling = False
                xVel = self.xVel
                self.x += xVel
                if self.get_colliding_platform(platform, False):
                    if self.downTouching > 0 and self.leftTouching > 0:
                        if self.downTouching < 6:
                            self.y += self.downTouching
                        else:
                            self.x += math.ceil(self.leftTouching)
                    if self.downTouching > 0 and self.rightTouching > 0:
                        if self.downTouching < 6:
                            self.y += self.downTouching
                        else:
                            self.x -= math.ceil(self.rightTouching)
                self.x -= xVel
        self.lastXOffset = self.xOffset
        self.lastWidth = self.width

class Bullet:
    def __init__(self, x, y, d, speed, owner):
        self.x = x
        self.y = y
        self.d = d
        self.owner = owner
        self.xVel = (Cos(d)*(speed))#+owner.xVel
        self.yVel = (Sin(d)*(speed))#+owner.yVel
        self.speed = speed
        self.age = 0

    def update(self):
        self.x += self.xVel
        self.y += self.yVel
        self.age += 1
        #self.yVel -= 1

        return 0 < self.age < 100

    def check_forward(self, pr, platform):
        if (
            self.x + (self.xVel*pr) < platform.x + (platform.w/2) and
            self.x + (self.xVel*pr) > platform.x - (platform.w/2) and
            self.y + (self.yVel*pr) > platform.y - (platform.h/2) and
            self.y + (self.yVel*pr) < platform.y + (platform.h/2)
        ):
            return True
        else:
            return False

    def get_touching(self, level):
        self.touchingPlatform = False
        self.rightTouching = 0
        self.leftTouching = 0
        self.upTouching = 0
        self.downTouching = 0

        for platform in level.platforms:
            if platform.d == 0:
                if (
                    self.x < platform.x + (platform.w/2) and
                    self.x > platform.x - (platform.w/2) and
                    self.y > platform.y - (platform.h/2) and
                    self.y < platform.y + (platform.h/2)
                ):
                    return True
                elif distance(self.x, self.y, platform.x, platform.y)<=max(platform.w,platform.h):
                    pr = -1

                    while abs(pr*self.speed)>2:
                        pr *= 0.9

                        if self.check_forward(pr, platform):
                            return True
            else:
                x3 = platform.x - ((platform.w/2) * Cos(-platform.d)) + ((platform.h/2) * Sin(-platform.d))
                y3 = platform.y + ((platform.h/2) * Cos(-platform.d)) + ((platform.w/2) * Sin(-platform.d))
                x4 = platform.x + ((platform.w/2) * Cos(-platform.d)) + ((platform.h/2) * Sin(-platform.d))
                y4 = platform.y + ((platform.h/2) * Cos(-platform.d)) - ((platform.w/2) * Sin(-platform.d))
                col = line_collision((self.x, self.y, self.x-self.xVel, self.y-self.yVel),
                                     (x3, y3, x4, y4))
                if col[0]:
                    return True

        for entity in level.entities:
            if not entity == self.owner:
                hit, xD, yD = entity.check_inside(self.x, self.y)
                if hit:
                    #print(hit, xD, yD)
                    entity.damage(1, 2, (self.xVel*0.2, self.yVel*0.2 + 1))
                    return True
        if not level.player == self.owner:
            hit, xD, yD = level.player.check_inside(self.x, self.y)
            if hit:
                level.player.damage(1, 2, (self.xVel*1, self.yVel*1 + 1))
                return True
        return False