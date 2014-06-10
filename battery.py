#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2014, Alexandre Vicenzi
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# * Neither the name of the {organization} nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import pyinotify
import pygame
import pygame.locals
import sys

# GCW button mappings
BUTTON_DPAD_UP        = pygame.locals.K_UP
BUTTON_DPAD_DOWN      = pygame.locals.K_DOWN
BUTTON_DPAD_LEFT      = pygame.locals.K_LEFT
BUTTON_DPAD_RIGHT     = pygame.locals.K_RIGHT
BUTTON_A              = pygame.locals.K_LCTRL
BUTTON_B              = pygame.locals.K_LALT
BUTTON_X              = pygame.locals.K_SPACE
BUTTON_Y              = pygame.locals.K_LSHIFT
BUTTON_START          = pygame.locals.K_RETURN
BUTTON_SELECT         = pygame.locals.K_ESCAPE
BUTTON_LEFT_SHOULDER  = pygame.locals.K_TAB
BUTTON_RIGHT_SHOULDER = pygame.locals.K_BACKSPACE
BUTTON_HOLD           = pygame.locals.K_PAUSE

COLOR_RED    = (255, 0, 0)
COLOR_YELLOW = (230, 255, 0)
COLOR_GREEN  = (0, 255, 0)
COLOR_BLACK  = (0, 0, 0)
COLOR_WHITE  = (255, 255, 255)

STATUS     = 'POWER_SUPPLY_STATUS'
HEALTH     = 'POWER_SUPPLY_HEALTH'
CAPACITY   = 'POWER_SUPPLY_CAPACITY'

FPS = 1

GCW_BATTERY_FILE = '/sys/class/power_supply/battery/uevent'

def log(msg):
    sys.stderr.write('%s\n' % msg)

def parse_file():
    try:
        f = open(GCW_BATTERY_FILE, 'r')
    except Exception as e:
        log(e)
        return None

    lines = f.readlines()
    data = {}

    for l in lines:
        items = l.replace('\n', '').split('=')
        key = items[0]
        value = items[1] if len(items) else None
        data[key] = value

    return data

class HandleEvent(pyinotify.ProcessEvent):

    def my_init(self, func):
        self.func = func

    def process_default(self, event):
        if self.func and callable(self.func):
            self.func()

class App:

    def __init__(self):
        log('Starting GCW Battery...')

        self.capacity = None
        self.status = None
        self.health = None

        self._update()

        # Configure pygame.
        pygame.init()
        self.screen = pygame.display.set_mode((320, 240))
        pygame.display.set_caption('GCW Battery')
        pygame.mouse.set_visible(0)

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()

        self.clock = pygame.time.Clock()

        # Configure notifier.
        wm = pyinotify.WatchManager()
        wm.add_watch(GCW_BATTERY_FILE, pyinotify.IN_MODIFY | pyinotify.IN_ACCESS, self._update)
        self.notifier = pyinotify.ThreadedNotifier(wm)

    def _update(self, event=None):
        log('Updating battery info...')
        f = parse_file()
        self.capacity = f.get(CAPACITY)
        self.status = f.get(STATUS)
        self.health = f.get(HEALTH)

    def loop(self):
        self.notifier.start()

        while 1:
            # Handle input events
            for event in pygame.event.get():
                if event.type == pygame.locals.QUIT or\
                   (event.type == pygame.locals.KEYDOWN and event.key == pygame.locals.K_ESCAPE) or\
                   (event.type == pygame.locals.KEYDOWN and event.key == BUTTON_START):
                    self.notifier.stop()
                    log('Ending GCW Battery.')
                    return 0

            self._draw()

            self.clock.tick(FPS)

    def _draw(self):
        # TODO:
        # A better way is use a layer to dispaly text.
        # So we don't need to redraw all screen.

        self.background.fill(COLOR_BLACK)

        if self.capacity != None:
            c = float(self.capacity)

            if c > 0:
                color = COLOR_GREEN if c > 65 else (COLOR_YELLOW if c > 25 else COLOR_RED)
                size = 160 - ((120 * c) / 100)
                size_c = size if size > 60 else 60

                # Battery body
                pygame.draw.polygon(self.background, color, ((120, size_c), (120, 160), (200, 160), (200, size_c)))

                if size >= 40 and size <= 60:
                    # Battery connector
                    pygame.draw.polygon(self.background, color, ((140, size), (140, 60), (180, 60), (180, size)))

        border_width = 3

        # pygame.draw.lines(Surface, color, closed, pointlist, width=1) -> Rect
        # (x , y)

        # Left
        pygame.draw.lines(self.background, COLOR_WHITE, False, [(120, 60), (120, 160)], border_width)
        # Right
        pygame.draw.lines(self.background, COLOR_WHITE, False, [(200, 60), (200, 160)], border_width)
        # Bottom
        pygame.draw.lines(self.background, COLOR_WHITE, False, [(120, 160), (200, 160)], border_width)
        # Top
        pygame.draw.lines(self.background, COLOR_WHITE, False, [(120, 60), (140, 60)], border_width)
        pygame.draw.lines(self.background, COLOR_WHITE, False, [(180, 60), (200, 60)], border_width)
        # Left
        pygame.draw.lines(self.background, COLOR_WHITE, False, [(140, 60), (140, 40)], border_width)
        # Right
        pygame.draw.lines(self.background, COLOR_WHITE, False, [(180, 60), (180, 40)], border_width)
        # Bottom
        pygame.draw.lines(self.background, COLOR_WHITE, False, [(140, 40), (180, 40)], border_width)

        if pygame.font:
            font36 = pygame.font.SysFont("Monospace", 36) or pygame.font.Font(None, 36)
            font28 = pygame.font.SysFont("Monospace", 28) or pygame.font.Font(None, 28)

            if self.capacity != None:
                capacity = str(self.capacity) + '%'

                text = font36.render(capacity, 1, COLOR_WHITE)
                pos = text.get_rect(centerx=160, centery=110)
                self.background.blit(text, pos)

                if self.status:
                    status = 'Status: ' + self.status
                    text = font28.render(status, 1, COLOR_WHITE)
                    pos = text.get_rect(centerx=160, centery=185)
                    self.background.blit(text, pos)

                if self.health:
                    health = 'Health: ' + self.health
                    text = font28.render(health, 1, COLOR_WHITE)
                    pos = text.get_rect(centerx=160, centery=220)
                    self.background.blit(text, pos)
            else:
                font = pygame.font.SysFont("Monospace", 18) or pygame.font.Font(None, 18)
                text = font.render("Error: Can't load battery status", 1, COLOR_WHITE)
                pos = text.get_rect(centerx=160, centery=110)
                self.background.blit(text, pos)

        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

if __name__ == '__main__':
    sys.exit(App().loop())

