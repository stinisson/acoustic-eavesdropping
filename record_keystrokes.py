from time import sleep

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

pygame.init()
pygame.display.set_caption('Record keystrokes')

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500
COLORS = {'GREEN': (75, 192, 192), 'BLUE': (54, 162, 235)}

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
font = pygame.font.Font(pygame.font.get_default_font(), 28)

infoText = font.render("Press enter to begin recording", True, COLORS['GREEN'], COLORS['BLUE'])
textRect = infoText.get_rect()
textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

recordText = font.render('Recording - press escape to stop recording', True, COLORS['GREEN'], COLORS['BLUE'])
recordTextRect = recordText.get_rect()
recordTextRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

stopText = font.render('Recording ended', True, COLORS['GREEN'], COLORS['BLUE'])
stopTextRect = stopText.get_rect()
stopTextRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)


def save_to_file(key_strokes, time_string):
    df = pd.DataFrame(key_strokes)
    df.to_csv(f"output/{time_string}.csv")


key_presses = []
recording_start_timestamp = None
running = True
recording_started = False
audio_recording = Audio()
while running:

    for event in pygame.event.get():

        if (event.type == KEYDOWN and event.key == K_ESCAPE) or event.type == pygame.QUIT:
            if recording_started:
                time_string = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S.%f")
                save_to_file(key_presses, time_string)
                audio_recording.stop_recording(time_string)
            running = False

        elif event.type in (KEYDOWN, KEYUP) and event.key == K_RETURN:
            if not recording_started:
                infoText = recordText
                textRect = recordTextRect
                sleep(0.5)
                audio_recording.start_recording()
                recording_start_timestamp = datetime.datetime.now().timestamp()
                recording_started = True

        elif event.type == KEYUP and recording_started:
            ts = datetime.datetime.now().timestamp() - recording_start_timestamp
            key_presses.append({"timestamp": ts, "key": pygame.key.name(event.key), "direction": "up"})

        elif event.type == KEYDOWN and recording_started:
            # keydown_offset = -0.15  # compensate delay between real keypress and recorded keypress
            ts = datetime.datetime.now().timestamp() - recording_start_timestamp  # + keydown_offset
            key_presses.append({"timestamp": ts, "key": pygame.key.name(event.key), "direction": "down"})

    screen.fill(COLORS['BLUE'])
    screen.blit(infoText, textRect)

    pygame.display.flip()

pygame.quit()
