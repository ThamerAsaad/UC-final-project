import pygame
import random
import os
from pygame import mixer

mixer.init()
pygame.init()

screen_width = 400 
screen_height = 600 




screen = pygame.display.set_mode((screen_width , screen_height))
pygame.display.set_caption('jumpy game')
clock = pygame.time.Clock()
FBS = 60

pygame.mixer.music.load('assets/music.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1,0.0)
jump_fx = pygame.mixer.Sound('assets/jump.mp3')
jump_fx.set_volume(0.6)
death_fx = pygame.mixer.Sound('assets/death.mp3')
death_fx.set_volume(0.6)


#Color
WHITE = (255,255,255)
BLACK = (0,0,0)
PANEL = (153 , 217 ,234)

#game var
scroll_thresh = 200
Gravity = 1
Max_platform = 10
scroll = 0
bg_scroll =0 
game_over = False
score = 0
fade_counter = 0
if os.path.exists('Score.txt'):
    with open ('Score.txt' , 'r') as file:
        high_score = int(file.read())
else:
    high_score = 0

#Font
font_small = pygame.font.SysFont('Lucida sans' , 20)
font_big = pygame.font.SysFont('Lucida sans' , 24)
#img for the game 
jumpy_image = pygame.image.load('assets/jump.png').convert_alpha()
bg_image = pygame.image.load('assets/bg.png').convert_alpha()
platform_image = pygame.image.load('assets/wood.png').convert_alpha()



def draw_text(text , font , text_col , x ,y ):
    img = font.render(text, True , text_col)
    screen.blit(img, (x,y))

def draw_panel():
    pygame.draw.rect(screen , PANEL , (0,0 , screen_width , 30 ))
    pygame.draw.line (screen , WHITE , (0,30) , (screen_width,30 ), 2)
    draw_text(f'SCORE: {score} ' , font_small ,WHITE , 0, 0 )

def draw_bg(scroll):
    screen.blit(bg_image , (0,0 + bg_scroll))
    screen.blit(bg_image , (0,-600 + bg_scroll))


#player class 
class Player():
    def __init__(self, x , y):
        self.image = pygame.transform.scale(jumpy_image, (45, 45))
        self.width = 25 
        self.height = 40 
        self.rect = pygame.Rect( 0 , 0 , self.width , self.height)
        self.rect.center = (x , y)
        self.vel_y = 0
        self.flip = False
    
    def move(self):
        scroll = 0 
        dx = 0
        dy = 0  
        
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            dx -= 10 
            self.flip = True
        if key[pygame.K_d]:
            dx += 10 
            self.flip = False

        self.vel_y += Gravity
        dy += self.vel_y

        #عدم السماح بخروج الاعب  من حدود الشاشة 
        if self.rect.left + dx <0 :
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right

        for platform in platform_group:
            if platform.rect.colliderect(self.rect.x , self.rect.y + dy , self.width , self.height):
                if self.rect.bottom < platform.rect.centery :
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        dy = 0 
                        self.vel_y = -20 
                        jump_fx.play()

        if self.rect.top <= scroll_thresh:
            if self.vel_y <0 :
                scroll  = -dy 


        self.rect.x += dx
        self.rect.y += dy +scroll

        return scroll


    def draw(self ):
        screen.blit(pygame.transform.flip(self.image , self.flip , False) ,(self.rect.x  - 12, self.rect.y -5 ))  
        # pygame.draw.rect(screen ,WHITE , self.rect ,2 )


class Platform(pygame.sprite.Sprite):
    def __init__(self,x , y , width , moving):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(platform_image , (width, 10 ))
        self.moving = moving
        self.move_counter = random.randint(0, 50)
        self.direction = random.choice([-1,1])
        self.speed = random.randint(1,2)
        self.rect = self.image.get_rect()
        self.rect.x = x 
        self.rect.y = y

    def update(self , scroll ):
        #movimg platform 
        if self.moving == True: 
            self.move_counter += 1
            self.rect.x += self.direction * self.speed

        if self.move_counter >=100 or self.rect.left <0 or self.rect.right > screen_width:
            self.direction *= -1
            self.move_counter = 0

        self.rect.y += scroll

        if self.rect.top > screen_height:
            self.kill()



jumpy = Player(screen_width // 2 , screen_height - 150 )

platform_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

platform = Platform(screen_width // 2  -50, screen_height -50 ,100 , False)
platform_group.add(platform)

#game loop 
run = True
while run: 
    clock.tick(FBS)

    if game_over == False:
        
        bg_scroll += scroll
        if bg_scroll >= 600:
            bg_scroll = 0
        draw_bg(bg_scroll)

        if len(platform_group)< Max_platform:
            p_w = random.randint(40,60)
            p_x = random.randint(0 , screen_width - p_w)
            p_y = platform.rect.y - random.randint(80, 120)
            p_type = random.randint(1,2)
            if p_type == 1 and score >800 :
                P_moving = True
            else:
                P_moving = False
            platform = Platform(p_x, p_y, p_w , P_moving)
            platform_group.add(platform)


        platform_group.update(scroll)

        

        if scroll > 0 :
            score += scroll 

        #line for high score
        pygame.draw.line(screen, WHITE , (0 , score - high_score + scroll_thresh), (screen_width , score - high_score + scroll_thresh) ,3 )
        draw_text('HIGH SCORE ', font_small , WHITE , screen_width - 130 , score - high_score + scroll_thresh)
        jumpy.draw()
        
        platform_group.draw(screen)
        draw_panel()

        scroll = jumpy.move()
        #check game over 
        if jumpy.rect.top > screen_height:
            game_over = True
            death_fx.play()
    else:
        if fade_counter < screen_width :
            fade_counter += 5
            for y in range(0,6 , 2):
                pygame.draw.rect(screen , BLACK, (0,y * 100, fade_counter , 100))
                pygame.draw.rect(screen , BLACK, (screen_width - fade_counter ,(y + 1 ) *100 , screen_width , 100 ))
        else:
            draw_text("GAME OVER!" , font_big , WHITE , 130 ,200)
            draw_text(f"SCORE : {score} " , font_big , WHITE , 130 ,250)
            draw_text('PRESS SPACE TO PLAY AGAIN' , font_big , WHITE , 40 ,300)
            #update high score 
            if score > high_score:
                high_score = score 
                with open('Score.txt' ,'w') as file:
                    file.write(str(high_score))
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:
                game_over = False
                score = 0 
                scroll = 0
                fade_counter = 0
                # reset player
                jumpy.rect.center = (screen_width // 2 , screen_height - 150 )
                # reset platform
                platform_group.empty()
                platform = Platform(screen_width // 2  -50, screen_height -50 ,100 ,False)
                platform_group.add(platform)           


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
    
        
pygame.quit()