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

FPS = 30

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

def main():
    log('Starting GCW Battery...')
    pygame.init()
    screen = pygame.display.set_mode((320, 240))
    pygame.display.set_caption('GCW Battery')
    pygame.mouse.set_visible(0)

    background = pygame.Surface(screen.get_size())
    background = background.convert()

    clock = pygame.time.Clock()

    while 1:
        clock.tick(FPS)

        # Handle input events
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT or\
               (event.type == pygame.locals.KEYDOWN and event.key == pygame.locals.K_ESCAPE) or\
               (event.type == pygame.locals.KEYDOWN and event.key == BUTTON_START):
                log('Ending GCW Battery.')
                return

        background.fill(COLOR_BLACK)

        battery = parse_file()

        if battery:

            # TODO:
            # A better way is use a layer to dispaly text.
            # So we don't need to redraw all screen.

            capacity = battery.get(CAPACITY)

            if capacity != None:
                c = float(capacity)

                if c > 0:
                    color = COLOR_GREEN if c > 65 else (COLOR_YELLOW if c > 25 else COLOR_RED)
                    size = 160 - ((120 * c) / 100)
                    size_c = size if size > 60 else 60

                    # Battery body
                    pygame.draw.polygon(background, color, ((120, size_c), (120, 160), (200, 160), (200, size_c)))

                    if size >= 40 and size <= 60:
                        # Battery connector
                        pygame.draw.polygon(background, color, ((140, size), (140, 60), (180, 60), (180, size)))

            border_width = 3

            # pygame.draw.lines(Surface, color, closed, pointlist, width=1) -> Rect
            # (x , y)

            # Left
            pygame.draw.lines(background, COLOR_WHITE, False, [(120, 60), (120, 160)], border_width)
            # Right
            pygame.draw.lines(background, COLOR_WHITE, False, [(200, 60), (200, 160)], border_width)
            # Bottom
            pygame.draw.lines(background, COLOR_WHITE, False, [(120, 160), (200, 160)], border_width)
            # Top
            pygame.draw.lines(background, COLOR_WHITE, False, [(120, 60), (140, 60)], border_width)
            pygame.draw.lines(background, COLOR_WHITE, False, [(180, 60), (200, 60)], border_width)
            # Left
            pygame.draw.lines(background, COLOR_WHITE, False, [(140, 60), (140, 40)], border_width)
            # Right
            pygame.draw.lines(background, COLOR_WHITE, False, [(180, 60), (180, 40)], border_width)
            # Bottom
            pygame.draw.lines(background, COLOR_WHITE, False, [(140, 40), (180, 40)], border_width)

        if pygame.font:
            font = pygame.font.SysFont("Monospace", 36)

            if not font:
                log("Can't load Monospace font.")
                font = pygame.font.Font(None, 36)

            if battery:
                capacity = str(capacity) + '%' if capacity != None else 'Unknown'

                text = font.render(capacity, 1, COLOR_WHITE)
                pos = text.get_rect(centerx=160, centery=110)
                background.blit(text, pos)

                status = battery.get(STATUS)

                if status:
                    status = 'Status: ' + status
                    text = font.render(status, 1, COLOR_WHITE)
                    pos = text.get_rect(centerx=160, centery=185)
                    background.blit(text, pos)

                health = battery.get(HEALTH)

                if health:
                    health = 'Health: ' + health
                    text = font.render(health, 1, COLOR_WHITE)
                    pos = text.get_rect(centerx=160, centery=220)
                    background.blit(text, pos)
            else:
                font = pygame.font.Font(None, 18)
                text = font.render("Error: Can't load battery status", 1, COLOR_WHITE)
                pos = text.get_rect(centerx=160, centery=110)
                background.blit(text, pos)

        screen.blit(background, (0, 0))
        pygame.display.flip()

if __name__ == '__main__':
    main()

