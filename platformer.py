import pygame
import sys
import time
from collections import deque
from vosk import Model, KaldiRecognizer
import pyaudio
import json
import threading

# =========================
# CONFIG
# =========================
WIDTH, HEIGHT = 800, 600
PLAYER_SIZE = (50, 50)

PLAYER_SPEED = 2
JUMP_POWER = 15
GRAVITY = 0.5
MOVE_DURATION = 0.5
COMMAND_DELAY = 0.1

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Platforms
PLATFORMS = [
    pygame.Rect(0, HEIGHT - 40, WIDTH, 40),
    pygame.Rect(200, 450, 200, 20),
    pygame.Rect(500, 350, 200, 20),
    pygame.Rect(350, 250, 150, 20),
]


# =========================
# HELPERS
# =========================
def check_collision(rect, platforms):
    for platform in platforms:
        if rect.colliderect(platform):
            return platform
    return None


class Movement:
    def __init__(self, direction, start_time, duration):
        self.direction = direction
        self.start_time = start_time
        self.duration = duration

    def is_active(self, now):
        return (now - self.start_time) < self.duration


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, *PLAYER_SIZE)
        self.vel_x = 0
        self.vel_y = 0
        self.current_movement = None

    def update(self, now):
        if self.current_movement and self.current_movement.is_active(now):
            self.vel_x = self.current_movement.direction
        else:
            self.vel_x = 0
            self.current_movement = None

        self.vel_y += GRAVITY
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Bounds
        self.rect.x = max(0, min(self.rect.x, WIDTH - PLAYER_SIZE[0]))
        if self.rect.y > HEIGHT - PLAYER_SIZE[1]:
            self.rect.y = HEIGHT - PLAYER_SIZE[1]
            self.vel_y = 0

    def jump(self, platforms):
        if check_collision(self.rect.move(0, 1), platforms):
            self.vel_y = -JUMP_POWER

    def land_on(self, platform):
        if self.vel_y > 0:
            self.rect.bottom = platform.top
            self.vel_y = 0


# =========================
# VOICE RECOGNITION (VOSK)
# =========================
command_queue = deque()

last_partial = ""
last_time = 0
cooldown = 0.5

def voice_listener():
    global last_partial, last_time

    model = Model("model-small")
    rec = KaldiRecognizer(model, 16000, '["left right jump"]')

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1,
                    rate=16000, input=True, frames_per_buffer=800)
    stream.start_stream()

    while True:
        data = stream.read(800, exception_on_overflow=False)
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            words = result.get("text", "").split()[1:]
            for w in words:
                if w in ["left", "right", "jump"]:
                    command_queue.append((w, time.time()))
                    print("Final Command:", w)

        else:
            partial = json.loads(rec.PartialResult())
            word = partial.get("partial", "").strip()
            now = time.time()

            if word in ["left", "right", "jump"]:
                if word != last_partial or (now - last_time) > cooldown:
                    if word != "jump" or (now - last_time) > cooldown + 1:
                        command_queue.append((word, now))
                        print("Instant Partial Command:", word)
                        last_partial = word
                        last_time = now
                    


# =========================
# MAIN GAME
# =========================
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Smooth Platformer (Vosk)")
    clock = pygame.time.Clock()

    player = Player(100, HEIGHT - PLAYER_SIZE[1] - 50)

    threading.Thread(target=voice_listener, daemon=True).start()

    command_timer = 0

    while True:
        now = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if command_queue and now - command_timer >= COMMAND_DELAY:
            cmd, _ = command_queue.popleft()
            command_timer = now
            if cmd == "left":
                player.current_movement = Movement(-PLAYER_SPEED, now, MOVE_DURATION)
            elif cmd == "right":
                player.current_movement = Movement(PLAYER_SPEED, now, MOVE_DURATION)
            elif cmd == "jump":
                player.jump(PLATFORMS)

        player.update(now)
        platform = check_collision(player.rect, PLATFORMS)
        if platform:
            player.land_on(platform)

        screen.fill(WHITE)
        for plat in PLATFORMS:
            pygame.draw.rect(screen, GREEN, plat)
        pygame.draw.rect(screen, BLUE, player.rect)
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
