"""
audio.py
---------------------------------
AI Gesture Experience

Audio Manager

Author: Shane
"""

import pygame
import os


class AudioManager:

    def __init__(self):

        pygame.mixer.init()

        self.sounds = {}

        self.load_sounds()

    def load_sounds(self):

        sound_folder = "assets/sounds"

        files = {
            "click": "click.wav",
            "success": "success.wav",
            "boxing": "boxing.mp3",
            "victory": "victory.mp3",
            "error": "error.wav"
        }

        for name, file in files.items():

            path = os.path.join(sound_folder, file)

            if os.path.exists(path):

                self.sounds[name] = pygame.mixer.Sound(path)

    def play(self, name):

        if name in self.sounds:

            self.sounds[name].play()

    def stop_all(self):

        pygame.mixer.stop()

    def play_music(self, file):

        path = os.path.join("assets/sounds", file)

        if os.path.exists(path):

            pygame.mixer.music.load(path)
            pygame.mixer.music.play()

    def stop_music(self):

        pygame.mixer.music.stop()