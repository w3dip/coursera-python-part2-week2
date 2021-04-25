#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
import random
import math

SCREEN_DIM = (800, 600)


class Vec2d:
    def __init__(self, point):
        x, y = point
        self.x = x
        self.y = y

    def __add__(self, other):
        """возвращает сумму двух векторов"""
        return Vec2d((self.x + other.x, self.y + other.y))

    def __sub__(self, other):
        """"возвращает разность двух векторов"""
        return Vec2d((self.x - other.x, self.y - other.y))

    def __mul__(self, k):
        """возвращает произведение вектора на число"""
        return Vec2d((self.x * k, self.y * k))

    @staticmethod
    def len(a):
        """возвращает длину вектора"""
        return math.sqrt(a.x * a.x + a.y * a.y)

    def int_pair(self):
        return int(self.x), int(self.y)

    def __str__(self):
        return "X = " + str(self.x) + " Y = " + str(self.y)


class Polyline:
    def __init__(self):
        self.points = []
        self.speeds = []
        self.steps = 35

    def add_point_and_speed(self, point, speed):
        self.points.append(point)
        self.speeds.append(speed)

    def del_point_and_speed(self):
        del self.points[-1]
        del self.speeds[-1]

    def set_points(self):
        """функция перерасчета координат опорных точек"""
        for p in range(len(self.points)):
            self.points[p] = self.points[p] + self.speeds[p]
            if self.points[p].x > SCREEN_DIM[0] or self.points[p].x < 0:
                self.speeds[p] = Vec2d((-self.speeds[p].x, self.speeds[p].y))
            if self.points[p].y > SCREEN_DIM[1] or self.points[p].y < 0:
                self.speeds[p] = Vec2d((self.speeds[p].x, -self.speeds[p].y))

    def inc_step(self):
        self.steps += 1

    def dec_step(self):
        self.steps -= 1 if self.steps > 1 else 0

    def inc_speed(self):
        for speed in self.speeds:
            speed.x *= 2
            speed.y *= 2
        self.set_points()

    def dec_speed(self):
        for speed in self.speeds:
            speed.x /= 2
            speed.y /= 2
        self.set_points()

    def draw_help(self):
        """функция отрисовки экрана справки программы"""
        gameDisplay.fill((50, 50, 50))
        font1 = pygame.font.SysFont("courier", 24)
        font2 = pygame.font.SysFont("serif", 24)
        data = []
        data.append(["F1", "Show Help"])
        data.append(["R", "Restart"])
        data.append(["P", "Pause/Play"])
        data.append(["Num+", "More points"])
        data.append(["Num-", "Less points"])
        data.append(["I", "Increase speed"])
        data.append(["D", "Decrease speed"])
        data.append(["A", "Add polyline"])
        data.append(["Right", "Click right button to remove last point"])
        data.append(["", ""])
        data.append([str(self.steps), "Current points"])

        pygame.draw.lines(gameDisplay, (255, 50, 50, 255), True, [
            (0, 0), (800, 0), (800, 600), (0, 600)], 5)
        for i, text in enumerate(data):
            gameDisplay.blit(font1.render(
                text[0], True, (128, 128, 255)), (100, 100 + 30 * i))
            gameDisplay.blit(font2.render(
                text[1], True, (128, 128, 255)), (200, 100 + 30 * i))

    @staticmethod
    def draw_points(points, style="points", width=3, color=(255, 255, 255)):
        """функция отрисовки точек на экране"""
        if style == "line":
            for p_n in range(-1, len(points) - 1):
                pygame.draw.line(gameDisplay, color,
                                 points[p_n].int_pair(),
                                 points[p_n + 1].int_pair(), width)

        elif style == "points":
            for p in points:
                pygame.draw.circle(gameDisplay, color,
                                   p.int_pair(), width)


class Knot(Polyline):
    def __init__(self, curve_koef = 1.0):
        super().__init__()
        self.knot_points = []
        self.curve_koef = curve_koef

    def add_point_and_speed(self, point, speed):
        super().add_point_and_speed(point, speed)
        self.knot_points = self.get_knot(self.points, self.steps)

    def set_points(self):
        super().set_points()
        self.knot_points = self.get_knot(self.points, self.steps)

    def get_knot(self, points, count):
        if len(points) < 3:
            return []
        res = []
        for i in range(-2, len(points) - 2):
            ptn = []
            ptn.append((points[i] + points[i + 1]) * 0.5)
            ptn.append(points[i + 1])
            ptn.append((points[i + 1] + points[i + 2]) * 0.5)

            res.extend(self.get_points(ptn, count))
        return res

    def get_points(self, base_points, count):
        alpha = (1 / count) * self.curve_koef
        res = []
        for i in range(count):
            res.append(self.get_point(base_points, i * alpha))
        return res

    def get_point(self, points, alpha, deg=None):
        if deg is None:
            deg = len(points) - 1
        if deg == 0:
            return points[0]
        return (points[deg] * alpha) + (self.get_point(points, alpha, deg - 1) * (1 - alpha))


if __name__ == "__main__":
    pygame.init()
    gameDisplay = pygame.display.set_mode(SCREEN_DIM)
    pygame.display.set_caption("MyScreenSaver")

    working = True
    polylines = []
    polyline = Knot()
    polylines.append(polyline)
    show_help = False
    pause = True

    hue = 0
    color = pygame.Color(0)

    while working:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                working = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    working = False
                if event.key == pygame.K_r:
                    polylines = []
                    polyline = Knot()
                    polylines.append(polyline)
                if event.key == pygame.K_p:
                    pause = not pause
                if event.key == pygame.K_KP_PLUS:
                    polyline.inc_step()
                if event.key == pygame.K_F1:
                    show_help = not show_help
                if event.key == pygame.K_KP_MINUS:
                    polyline.dec_step()

                if event.key == pygame.K_i:
                    for polyline in polylines:
                        polyline.inc_speed()

                if event.key == pygame.K_d:
                    for polyline in polylines:
                        polyline.dec_speed()

                if event.key == pygame.K_a:
                    last_polyline = polylines[0]
                    new_polyline = Knot(random.random())
                    new_polyline.points = last_polyline.points
                    new_polyline.speeds = last_polyline.speeds
                    new_polyline.knot_points = new_polyline.get_knot(new_polyline.points, new_polyline.steps)
                    polylines.append(new_polyline)

            if event.type == pygame.MOUSEBUTTONDOWN:
                for polyline in polylines:
                    if event.button == 1:
                        polyline.add_point_and_speed(Vec2d(event.pos), Vec2d((random.random() * 2, random.random() * 2)))
                    if event.button == 3:
                        polyline.del_point_and_speed()

        gameDisplay.fill((0, 0, 0))
        hue = (hue + 1) % 360
        color.hsla = (hue, 100, 50, 100)
        for polyline in polylines:
            polyline.draw_points(polyline.points)
            polyline.draw_points(polyline.knot_points, "line", 3, color)
            if not pause:
                polyline.set_points()
            if show_help:
                polyline.draw_help()

        pygame.display.flip()

    pygame.display.quit()
    pygame.quit()
    exit(0)
