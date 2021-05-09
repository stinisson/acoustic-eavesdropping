import pandas as pd
import datetime
import pygame

from pygame.locals import (
    K_ESCAPE,
    K_RETURN,
    KEYDOWN,
    KEYUP
)

from record_audio import Audio
from train import audio_to_image

pygame.init()
pygame.display.set_caption('Record keystrokes')

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500
COLORS = {'GREEN': (75, 192, 192), 'BLUE': (54, 162, 235)}

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
font = pygame.font.Font(pygame.font.get_default_font(), 28)

infoText = font.render('Write letters a-z', True, COLORS['GREEN'], COLORS['BLUE'])
recordTextRect = infoText.get_rect()
recordTextRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)

recordText = font.render('Recording - press escape to stop recording', True, COLORS['GREEN'], COLORS['BLUE'])
recordTextRect = recordText.get_rect()
recordTextRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

audio_recording = Audio()
audio_recording.start_recording()
running = True
while running:

    for event in pygame.event.get():

        if (event.type == KEYDOWN and event.key == K_ESCAPE) or event.type == pygame.QUIT:
            audio_recording.stop_recording()
            running = False

        elif event.type == KEYUP:
            key_name = pygame.key.name(event.key)
            if key_name in 'abcdefghjijklmnopqrstuvxyz':
                time_string = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S.%f")
                if audio_recording.save_keystroke(key_name, time_string):
                    directory = "output/" + key_name + "/"
                    audio_file_path = directory + time_string + ".wav"
                    image_file_path = directory + time_string + ".png"
                    audio_to_image(audio_file_path, image_file_path)
                    print("Saved", key_name)
                else:
                    print("Too short")

    screen.fill(COLORS['BLUE'])
    #screen.blit(infoText, textRect)
    pygame.display.flip()

pygame.quit()
