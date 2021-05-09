import datetime
import pygame
import numpy as np
from fastai.data.all import *
from fastai.vision.all import *
from fastai.vision import *

from pygame.locals import (
    K_ESCAPE,
    K_RETURN,
    KEYDOWN,
    KEYUP
)

from record_audio import Audio
from train import audio_to_image


def label_func(fname):
    return str(fname).split("\\")[1]


model = load_learner('export.pkl')


def predict(filepath):
    im = PILImage.create(filepath)
    predicted = model.predict(im)
    return predicted[0]


def evesdrop():
    pygame.init()
    pygame.display.set_caption('Record keystrokes')

    SCREEN_WIDTH = 700
    SCREEN_HEIGHT = 500
    COLORS = {'GREEN': (75, 192, 192), 'BLUE': (54, 162, 235), 'ORANGE': (222, 200, 180), 'RED': (210, 99, 132)}

    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    font = pygame.font.Font(pygame.font.get_default_font(), 28)

    infoText = font.render('EVESDROPPING', True, COLORS['BLUE'], COLORS['GREEN'])
    textRec = infoText.get_rect()
    textRec.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.2)

    # recordText = font.render('Recording - press escape to stop recording', True, COLORS['GREEN'], COLORS['BLUE'])
    # recordTextRect = recordText.get_rect()
    # recordTextRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    keyText = font.render("You entered: ", True, COLORS['ORANGE'], COLORS['GREEN'])
    keyRec = keyText.get_rect()
    keyRec.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.4)

    predText = font.render("Predicted: ", True, COLORS['ORANGE'], COLORS['GREEN'])
    predRec = predText.get_rect()
    predRec.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.5)

    messText = font.render("Secret message: ", True, COLORS['RED'], COLORS['GREEN'])
    messRec = messText.get_rect()
    messRec.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.7)

    secText = font.render("", True, COLORS['RED'], COLORS['GREEN'])
    secRec = secText.get_rect()
    secRec.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.8)

    message = ""

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
                if event.key == pygame.K_SPACE:
                    message += " "
                    secText = font.render(f'{message}', True, COLORS['RED'], COLORS['GREEN'])
                    secRec = secText.get_rect()
                    secRec.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.8)

                if key_name in 'abcdefghjijklmnopqrstuvxyz':
                    time_string = datetime.now().strftime("%Y_%m_%d_%H%M%S.%f")
                    if audio_recording.save_keystroke(key_name, time_string):
                        try:
                            directory = "output/" + key_name + "/"
                            audio_file_path = directory + time_string + ".wav"
                            image_file_path = directory + time_string + ".png"
                            audio_to_image(audio_file_path, image_file_path)

                            print("\nPrinted: ", key_name)
                            keyText = font.render(f'You entered: {key_name}', True, COLORS['ORANGE'], COLORS['GREEN'])

                            predicted_key = predict(image_file_path)
                            print("Predicted: ", predicted_key)
                            predText = font.render(f'Predicted: {predicted_key}', True, COLORS['ORANGE'], COLORS['GREEN'])

                            message += predicted_key
                            messText = font.render(f'Secret message:', True, COLORS['RED'], COLORS['GREEN'])
                            secText = font.render(f'{message}', True, COLORS['RED'], COLORS['GREEN'])
                            secRec = secText.get_rect()
                            secRec.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.8)

                        except:
                            print("Try again")

                    else:
                        print("Too short")

        screen.fill(COLORS['GREEN'])
        screen.blit(infoText, textRec)
        screen.blit(keyText, keyRec)
        screen.blit(predText, predRec)
        screen.blit(messText, messRec)
        screen.blit(secText, secRec)


        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    evesdrop()
