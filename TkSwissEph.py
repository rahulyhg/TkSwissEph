#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import os
import swisseph as swe
import tkinter as tk
from math import cos, sin, radians

swe.set_ephe_path(os.path.join(os.getcwd(), "Eph"))

root = tk.Tk()
root.title("")
root.configure(bg="white")
root.resizable(width=False, height=False)


def source_path(relative_path):
    import sys
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


if os.name == "nt":
    root.iconbitmap(source_path("TkSwissEph.ico"))

canvas = None
toplevel = None


def create_toplevel():
    global toplevel
    if toplevel is not None:
        toplevel.destroy()
    toplevel = tk.Toplevel()
    toplevel.resizable(width=False, height="False")
    toplevel.title("TkSwissEph")
    if os.name == "nt":
        toplevel.iconbitmap(source_path("TkSwissEph.ico"))
    return toplevel


def create_canvas(master):
    global canvas
    if canvas is not None:
        canvas.destroy()
    canvas = tk.Canvas(master=master, bg="white", width=1270, height=660)
    canvas.grid(row=0, column=0)
    return canvas


def create_label(*args, column, padx=1, bg="white", fg="black", row=0):
    for i, j in enumerate(args):
        label = tk.Label(master=root, text=j, bg=bg, fg=fg)
        label.grid(row=i + row, column=column, sticky="nw", padx=padx)
        yield label


def create_entry(n, column, row=0):
    for i in range(n):
        entry = tk.Entry(master=root, width=6)
        entry.grid(row=i + row, column=column)
        yield entry


label_names = "Year", "Month", "Day", "Hour", "Minute", "Latitude", "Longitude"
entry_label = {
    i: [j, k] for i, j, k in zip(
        label_names, create_entry(n=7, column=1, row=3), create_label(*label_names, column=0, row=3))
}

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
    "North Node": swe.TRUE_NODE,
    "Chiron": swe.CHIRON
}

ASPECT_SYMBOLS = {
    "Conjunction": "\u260C",
    "Semi-Sextile": "\u26BA",
    "Semi-Square": "\u2220",
    "Sextile": "\u26B9",
    "Quintile": "Q",
    "Square": "\u25A1",
    "Trine": "\u25B3",
    "Sesquiquadrate": "\u26BC",
    "BiQuintile": "bQ",
    "Quincunx": "\u26BB",
    "Opposite": "\u260D",
}

ENABLED_ASPECTS = {}
MIDPOINT = {}
FROM_WHICH_PLANET = {}
TO_WHICH_PLANET = {}
DAY_LIGHT_SAVE_TIME = {}


button = tk.Button(master=root, text="Generate Chart", bg="white",
                   activeforeground="black", activebackground="white")
button.grid(row=13, column=0, columnspan=4, pady=5)

select_aspect, = create_label("Select aspect(s), that you want,\n to be drawn", column=2, padx=25, fg="red")
select_midpoint, = create_label("Select midpoint(s), that you want,\n to be drawn", column=3, padx=25, fg="red")


def create_checkbutton(*args, column=2, dictionary, row=1):
    for i, j in enumerate(args):
        var = tk.StringVar()
        checkbutton = tk.Checkbutton(master=root, bg="white", text=j, activebackground="white",
                                     activeforeground="black", variable=var)
        var.set("0")
        dictionary[j] = [checkbutton, var]
        checkbutton.grid(row=i + row, column=column, sticky="nw", padx=25)


create_checkbutton(*list(ASPECT_SYMBOLS.keys()), column=2, dictionary=ENABLED_ASPECTS)
create_checkbutton("Midpoint", column=3, dictionary=MIDPOINT)
create_checkbutton("DST (on/off)", column=1, dictionary=DAY_LIGHT_SAVE_TIME, row=11)


def extend_midpoint_checkbutton():
    global label1, label2
    button.grid_forget()
    button.grid(row=13, column=0, columnspan=6, pady=5)
    if MIDPOINT["Midpoint"][1].get() == "1":
        label1, = create_label("Midpoints of a planet", column=4, padx=25, fg="red")
        label2, = create_label("Aspects to another planet", column=5, padx=25, fg="red")
        create_checkbutton(*list(PLANETS.keys()), column=4, dictionary=FROM_WHICH_PLANET)
        create_checkbutton(*list(PLANETS.keys()), column=5, dictionary=TO_WHICH_PLANET)
    else:
        label1.destroy()
        label2.destroy()
        for i in PLANETS:
            FROM_WHICH_PLANET[i][0].destroy()
            TO_WHICH_PLANET[i][0].destroy()


MIDPOINT["Midpoint"][0].configure(command=extend_midpoint_checkbutton)


def oval_object(x, y, r, dash=True):
    if dash is True:
        dash = (1, 10)
        canvas.create_oval(
            x - r,
            y - r,
            x + r,
            y + r,
            fill="white",
            width=2,
            dash=dash
        )
    else:
        canvas.create_oval(
            x - r,
            y - r,
            x + r,
            y + r,
            fill="white",
            width=2,
        )


def line_object(x1, y1, x2, y2, width=2, fill="black"):
    canvas.create_line(x1, y1, x2, y2, width=width, fill=fill)


def text_object(x, y, _text, width=0, font="Arial", fill="black"):
    canvas.create_text(x, y, text=_text, width=width, font=font, fill=fill)


class Chart:
    def __init__(self, year, month, day, hour, minute, longitude, latitude):
        self.year = year
        self.month = month
        self.day = day
        if DAY_LIGHT_SAVE_TIME["DST (on/off)"][1].get() == "1":
            self.hour = hour - 1
        else:
            self.hour = hour
        self.minute = minute
        self.longitude = longitude
        self.latitude = latitude

        self.SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                      "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        self.SIGN_SYMBOLS = ["\u2648", "\u2649", "\u264A", "\u264B", "\u264C", "\u264D",
                             "\u264E", "\u264F", "\u2650", "\u2651", "\u2652", "\u2653"]
        self.SIGN_COLORS = ["red", "green", "yellow", "blue"] * 3
        self._SIGN_SYMBOLS = {i: j for i, j in zip(self.SIGNS, self.SIGN_SYMBOLS)}
        self._SIGN_COLORS = {i: j for i, j in zip(self.SIGNS, self.SIGN_COLORS)}
        self.PLANETS = {i: j for i, j in PLANETS.items()}
        self.PLANET_SYMBOLS = {
            "Sun": "\u2299",
            "Moon": "\u263E",
            "Mercury": "\u263F",
            "Venus": "\u2640",
            "Mars": "\u2642",
            "Jupiter": "\u2643",
            "Saturn": "\u2644",
            "Uranus": "\u2645",
            "Neptune": "\u2646",
            "Pluto": "\u2647",
            "North Node": "\u260A",
            "Chiron": "\u26B7"
        }
        self.ASPECT_SYMBOLS = ASPECT_SYMBOLS
        self.ASPECT_SYMBOLS["Null"] = " "
        self.ASPECTS = {i: [] for i in self.PLANETS.keys()}
        self.MIDPOINTS = {}
        self.CONJUNCTION = []
        self.SEMI_SEXTILE = []
        self.SEMI_SQUARE = []
        self.SEXTILE = []
        self.QUINTILE = []
        self.SQUARE = []
        self.TRINE = []
        self.SESQUIQUADRATE = []
        self.BIQUINTILE = []
        self.QUINCUNX = []
        self.OPPOSITE = []
        self.NULL = []
        self.PLANET_DEGREES = []
        self.MIDPOINT_OF_HOUSES = []
        self.PLANET_INFO_FORMAT = []
        self.HOUSE_INFO_FORMAT = []

        self.draw_oval_object()
        self.draw_line_object()
        self.draw_houses()
        self.draw_signs()
        self.draw_house_numbers()
        self.draw_sign_symbols()
        self.draw_planets()
        self.draw_aspects()
        self.parse_aspects()
        self.new_order_of_the_aspects()
        self.draw_house_info()
        self.draw_planet_info()
        self.draw_aspect_info()
        self.draw_chart_info()
        self.draw_midpoints()

    @staticmethod
    def dd_to_dms(dd):
        degree = int(dd)
        minute = int((dd - degree) * 60)
        second = round(float((dd - degree - minute / 60) * 3600))
        return f"{degree}\u00b0 {minute}\' {second}\""

    @staticmethod
    def dms_to_dd(dms):
        dms = dms.replace("\u00b0", "").replace("\'", "").replace("\"", "")
        degree = int(dms.split(" ")[0])
        minute = float(dms.split(" ")[1]) / 60
        second = float(dms.split(" ")[2]) / 3600
        return degree + minute + second

    def utc_time(self):
        longitude = int(self.longitude)
        hour = float(self.hour)
        if longitude == 0:
            return hour
        elif longitude in range(1, 16):
            return hour - 1
        elif longitude in range(-16, -1):
            return hour + 1
        elif longitude in range(16, 31):
            return hour - 2
        elif longitude in range(-31, -16):
            return hour + 2
        elif longitude in range(31, 46):
            return hour - 3
        elif longitude in range(-46, -31):
            return hour + 3
        elif longitude in range(46, 61):
            return hour - 4
        elif longitude in range(-61, -46):
            return hour + 4
        elif longitude in range(61, 76):
            return hour - 5
        elif longitude in range(-76, -61):
            return hour + 5
        elif longitude in range(76, 91):
            return hour - 6
        elif longitude in range(-91, -76):
            return hour + 6
        elif longitude in range(91, 106):
            return hour - 7
        elif longitude in range(-106, -91):
            return hour + 7
        elif longitude in range(106, 121):
            return hour - 8
        elif longitude in range(-121, -106):
            return hour + 8
        elif longitude in range(121, 136):
            return hour - 9
        elif longitude in range(-136, -121):
            return hour + 9
        elif longitude in range(136, 151):
            return hour - 10
        elif longitude in range(-151, -136):
            return hour + 10
        elif longitude in range(151, 166):
            return hour - 11
        elif longitude in range(-166, -151):
            return hour + 11
        elif longitude in range(166, 181):
            return hour - 12
        elif longitude in range(-181, -166):
            return hour + 12

    def julday(self):
        jd = swe.julday(
            self.year, self.month, self.day, self.utc_time() + self.minute / 60)
        deltat = swe.deltat(jd)
        return round(jd + deltat, 6)

    def sidereal_time(self):
        longitude = str(self.longitude).split(".")
        longitude = " ".join(longitude)
        longitude += " 0"
        converted_geo_longitude = str(round(self.dms_to_dd(longitude) * 4, 2)).split(".")
        converted_geo_longitude = f"0\u00b0 {converted_geo_longitude[0]}' {converted_geo_longitude[1]}\""
        fraction = f"0\u00b0 0' {int((self.minute / 1440 + self.utc_time() / 24) * 236)}\""
        modify_utc = f"{int(self.utc_time())}\u00b0 {self.minute}\' 0\""
        jd = swe.sidtime(swe.julday(
            self.year, self.month, self.day, 0 + 0))
        return self.dd_to_dms(
            self.dms_to_dd(converted_geo_longitude) +
            self.dms_to_dd(fraction) +
            self.dms_to_dd(modify_utc) +
            jd
        )

    @staticmethod
    def convert_angle(angle):
        if 0 < angle < 30:
            return angle, "Aries"
        elif 30 < angle < 60:
            return angle - 30, "Taurus"
        elif 60 < angle < 90:
            return angle - 60, "Gemini"
        elif 90 < angle < 120:
            return angle - 90, "Cancer"
        elif 120 < angle < 150:
            return angle - 120, "Leo"
        elif 150 < angle < 180:
            return angle - 150, "Virgo"
        elif 180 < angle < 210:
            return angle - 180, "Libra"
        elif 210 < angle < 240:
            return angle - 210, "Scorpio"
        elif 240 < angle < 270:
            return angle - 240, "Sagittarius"
        elif 270 < angle < 300:
            return angle - 270, "Capricorn"
        elif 300 < angle < 330:
            return angle - 300, "Aquarius"
        elif 330 < angle < 360:
            return angle - 330, "Pisces"

    def planet_pos(self, planet):
        calc = self.convert_angle(swe.calc_ut(self.julday(), planet)[0])
        return self.dd_to_dms(calc[0]), calc[1]

    def append_house(self, house, i, j, name=""):
        if name == "":
            house.append((
                f"House {i + 1}",
                f"{self.dd_to_dms(self.convert_angle(j)[0])}",
                f"{self.convert_angle(j)[1]}"))
        else:
            house.append((
                f"{name}",
                f"{self.dd_to_dms(self.convert_angle(j)[0])}",
                f"{self.convert_angle(j)[1]}"))

    def house_cusps(self):
        houses = []
        asc = 0
        angle = []
        for i, j in enumerate(swe.houses(self.julday(), self.latitude, self.longitude)[0]):
            if i == 0:
                asc += j
            angle.append(j)
            if i + 1 == 1:
                self.append_house(houses, i, j, name="Asc")
            elif i + 1 == 4:
                self.append_house(houses, i, j, name="IC")
            elif i + 1 == 7:
                self.append_house(houses, i, j, name="Dsc")
            elif i + 1 == 10:
                self.append_house(houses, i, j, name="MC")
            else:
                self.append_house(houses, i, j)
        return houses, asc, angle

    def house_pos(self):
        return self.house_cusps()[2]

    def sign_pos(self):
        asc = self.house_cusps()[1]
        degree = self.house_cusps()[0][0][1].replace("'", "").replace('"', "").replace("\u00b0", "")
        end = 30 - self.dms_to_dd(degree) + asc
        start = end - 30
        signs = []
        for i, j in enumerate(self.house_cusps()[0]):
            signs.append(j[2])
        for i in self.SIGNS:
            if i not in signs:
                index_1 = self.SIGNS.index(i) + 1
                sign = self.SIGNS[index_1]
                index_2 = signs.index(sign)
                signs.insert(index_2, i)
        for i in signs:
            count = signs.count(i)
            if count > 1:
                signs.pop(signs.index(i, 1))
        _signs_ = []
        for i, j in enumerate(signs):
            _start = start + (i * 30)
            _end = end + (i * 30)
            if _start > 360:
                _start -= 360
            if _end > 360:
                _end -= 360
            _signs_.append(_start)
        return _signs_, signs

    @staticmethod
    def line_components(angle, r):
        x1, y1 = 550, 350
        x2 = x1 + (r * cos(radians(angle)))
        y2 = y1 - (r * sin(radians(angle)))
        return x1, y1, x2, y2

    def x_y(self, angle, r1, r2):
        x1, y1, x2, y2 = self.line_components(angle=angle, r=r1)
        _x1, _y1, _x2, _y2 = self.line_components(angle=angle, r=r2)
        return x2, y2, _x2, _y2

    @staticmethod
    def draw_oval_object(x=550, y=350):
        oval_object(x=x, y=y, r=260, dash=False)
        oval_object(x=x, y=y, r=210, dash=False)
        oval_object(x=x, y=y, r=165)
        oval_object(x=x, y=y, r=60, dash=False)

    @staticmethod
    def draw_line_object(x=900, y=1200):
        line_object(x1=x, y1=205, x2=y, y2=205, width=1)
        line_object(x1=x, y1=410, x2=y, y2=410, width=1)
        line_object(x1=x, y1=428, x2=x, y2=624, width=1)
        line_object(x1=x, y1=428 + (13 * 15), x2=x + 25 + (20 * 15), y2=428 + (13 * 15), width=1)

    def draw_houses(self):
        for i, j in enumerate(self.house_pos()):
            _degree = j - (self.house_pos()[0] - 180)
            if _degree < 0:
                _degree += 360
            elif _degree > 360:
                _degree -= 360
            self.MIDPOINT_OF_HOUSES.append(_degree)
            x1, y1, x2, y2 = self.x_y(angle=_degree, r1=60, r2=210)
            if i == 0 or i == 3 or i == 6 or i == 9:
                line_object(x1, y1, x2, y2, width=4)
            else:
                line_object(x1, y1, x2, y2, width=2)

    def draw_signs(self):
        sign_pos = self.sign_pos()[0]
        for i in sign_pos:
            _degree = i - (self.house_pos()[0] - sign_pos[1])
            if _degree > 360:
                _degree -= 360
            x1, y1, x2, y2 = self.x_y(angle=_degree, r1=210, r2=260)
            line_object(x1, y1, x2, y2, width=2)

    def draw_house_numbers(self):
        for i, j in enumerate(self.MIDPOINT_OF_HOUSES):
            if i == 11:
                midpoint = (self.MIDPOINT_OF_HOUSES[i] + self.MIDPOINT_OF_HOUSES[0]) / 2
            else:
                if self.MIDPOINT_OF_HOUSES[i] == 360:
                    midpoint = self.MIDPOINT_OF_HOUSES[i + 1] / 2
                else:
                    if self.MIDPOINT_OF_HOUSES[i + 1] == 0 or self.MIDPOINT_OF_HOUSES[i + 1] < 30:
                        midpoint = (self.MIDPOINT_OF_HOUSES[i] + self.MIDPOINT_OF_HOUSES[i + 1] + 360) / 2
                    else:
                        midpoint = (self.MIDPOINT_OF_HOUSES[i] + self.MIDPOINT_OF_HOUSES[i + 1]) / 2
            x1, y1, x2, y2 = self.x_y(angle=midpoint, r1=60, r2=110)
            x = (x1 + x2) / 2
            y = (y1 + y2) / 2
            text_object(x=x, y=y, _text=f"{i + 1}")

    def draw_sign_symbols(self):
        asc = self.house_cusps()[1]
        for i, j in enumerate(self.SIGNS):
            end = 30 - (asc % 30) + 180
            start = end - 30
            start += (30 * i)
            end += (30 * i)
            if start > 360:
                start -= 360
            if end > 360:
                end -= 360
            if start > 330:
                midpoint = (start + end + 360) / 2
            else:
                midpoint = (start + end) / 2
            if midpoint > 360:
                midpoint -= 360
            x1, y1, x2, y2 = self.x_y(angle=midpoint, r1=210, r2=260)
            x = (x1 + x2) / 2
            y = (y1 + y2) / 2
            text_object(x=x, y=y, _text=self._SIGN_SYMBOLS[self.sign_pos()[1][i]],
                        font="Arial 25", fill=self._SIGN_COLORS[self.sign_pos()[1][i]])

    def modify_text_object(self, planet_symbol, key, value, offset):
        x1, y1, x2, y2 = self.x_y(angle=value, r1=210, r2=175)
        x = ((x1 + x2) / 2) + offset
        y = ((y1 + y2) / 2) + offset
        if key == "Mars" or key == "Venus":
            if os.name == "posix":
                text_object(x=x, y=y, _text=f"{planet_symbol}", width=0, font="Arial 30")
            elif os.name == "nt":
                text_object(x=x, y=y, _text=f"{planet_symbol}", width=0, font="Arial 20")
        else:
            text_object(x=x, y=y, _text=f"{planet_symbol}", width=0, font="Arial 20")

    def draw_planets(self):
        count = 0
        planet_info_format = []
        house_info_format = []
        for key, value in self.PLANETS.items():
            planet = self.planet_pos(value)
            split_degree_1 = planet[0].split(" ")
            degree_1, minute_1, second_1 = split_degree_1
            planet_info = (
                self.PLANET_SYMBOLS[key],
                key,
                degree_1,
                minute_1,
                second_1,
                self._SIGN_SYMBOLS[planet[1]],
                planet[1]
            )
            planet_info_format.append(planet_info)
            split_degree_2 = self.house_cusps()[0][count][1].split(" ")
            degree_2, minute_2, second_2 = split_degree_2
            house_info = [
                self.house_cusps()[0][count][0],
                degree_2,
                minute_2,
                second_2,
                self._SIGN_SYMBOLS[self.house_cusps()[0][count][-1]],
                self.house_cusps()[0][count][-1]
            ]
            house_info_format.append(house_info)
            count += 1
            convert_planet_degree = self.dms_to_dd(
                self.planet_pos(value)[0].replace("'", "").replace('"', "").replace("\u00b0", ""))
            asc = self.house_cusps()[1]
            signs = []
            for i, j in enumerate(self.SIGNS):
                end = 30 - (asc % 30) + 180
                start = end - 30
                start += (30 * i)
                end += (30 * i)
                if start > 360:
                    start -= 360
                if end > 360:
                    end -= 360
                signs.append(start)
            planet_index = self.sign_pos()[1].index(planet[1])
            new_degree_of_planet = convert_planet_degree + signs[planet_index]
            self.PLANET_DEGREES.append(new_degree_of_planet)
        self.PLANET_INFO_FORMAT = planet_info_format
        self.HOUSE_INFO_FORMAT = house_info_format
        count1 = 0
        count2 = 0
        for i, j in zip(["Ascendant", "Medium Coeli"], ["Asc", "Mc"]):
            self.PLANETS[i] = 16 + count1
            self.PLANET_SYMBOLS[i] = j
            self.PLANET_DEGREES.append(self.MIDPOINT_OF_HOUSES[count2])
            count1 += 3
            count2 += 9
        planet_degrees = {i: j for i, j in zip(self.PLANETS, self.PLANET_DEGREES)}
        drawn_signs = []
        for key, value in planet_degrees.items():
            x1, y1, x2, y2 = self.x_y(angle=value, r1=210, r2=205)
            line_object(x1, y1, x2, y2, width=2, fill="red")
            for _key, _value in planet_degrees.items():
                aspect = value - _value
                if 0 < aspect < 4:
                    drawn_signs.append(key)
                    drawn_signs.append(_key)
                    self.modify_text_object(planet_symbol=self.PLANET_SYMBOLS[key],
                                            key=key, value=value, offset=6)
                elif -4 < aspect < 0:
                    self.modify_text_object(planet_symbol=self.PLANET_SYMBOLS[key],
                                            key=key, value=_value, offset=-6)
        drawn_signs = set(drawn_signs)
        for key, value in planet_degrees.items():
            if key not in drawn_signs:
                self.modify_text_object(planet_symbol=self.PLANET_SYMBOLS[key],
                                        key=key, value=value, offset=4)

    def create_aspect(self, planet_degrees, value, color, r1=160, r2=165):
        x1, y1, x2, y2 = self.x_y(angle=value, r1=r1, r2=r2)
        _x1, _y1, _x2, _y2 = self.x_y(angle=planet_degrees, r1=r1, r2=r2)
        line_object(x2, y2, _x2, _y2, width=2, fill=color)

    def if_enabled_aspects(self, planet_degrees, value, aspect, color):
        if ENABLED_ASPECTS[aspect][1].get() == "1":
            self.create_aspect(planet_degrees, value, color=color)

    def if_enabled_planets(self, _value, value, key, _key, planet_degrees):
        try:
            if FROM_WHICH_PLANET[key][1].get() == "1":
                for i in TO_WHICH_PLANET.keys():
                    if TO_WHICH_PLANET[i][1].get() == "1":
                        if _value < 30:
                            _value += 360
                        midpoint_aspect = (value + _value) / 2
                        diff = abs(planet_degrees[i] - midpoint_aspect)
                        self.MIDPOINTS[key, _key] = midpoint_aspect
                        self.select_aspect(diff, planet_degrees[i], midpoint_aspect, key, f"{key}/{_key}")
        except KeyError:
            pass

    def select_aspect(self, aspect, value, planet_degrees, key, _key):
        if 0 < aspect < 10 or 350 < aspect < 360:
            self.CONJUNCTION.append((key, self.ASPECT_SYMBOLS["Conjunction"], _key))
            self.if_enabled_aspects(planet_degrees, value, "Conjunction", "red")
        elif 28 < aspect < 32 or 328 < aspect < 332:
            self.SEMI_SEXTILE.append((key, self.ASPECT_SYMBOLS["Semi-Sextile"], _key))
            self.if_enabled_aspects(planet_degrees, value, "Semi-Sextile", "black")
        elif 43 < aspect < 47 or 313 < aspect < 347:
            self.SEMI_SQUARE.append((key, self.ASPECT_SYMBOLS["Semi-Square"], _key))
            self.if_enabled_aspects(planet_degrees, value, "Semi-Square", "black")
        elif 50 < aspect < 70 or 290 < aspect < 310:
            self.SEXTILE.append((key, self.ASPECT_SYMBOLS["Sextile"], _key))
            self.if_enabled_aspects(planet_degrees, value, "Sextile", "blue")
        elif 70 < aspect < 74 or 286 < aspect < 290:
            self.QUINTILE.append((key, self.ASPECT_SYMBOLS["Quintile"], _key))
            self.if_enabled_aspects(planet_degrees, value, "Quintile", "purple")
        elif 80 < aspect < 100 or 260 < aspect < 280:
            self.SQUARE.append((key, self.ASPECT_SYMBOLS["Square"], _key))
            self.if_enabled_aspects(planet_degrees, value, "Square", "red")
        elif 110 < aspect < 130 or 230 < aspect < 250:
            self.TRINE.append((key, self.ASPECT_SYMBOLS["Trine"], _key))
            self.if_enabled_aspects(planet_degrees, value, "Trine", "blue")
        elif 133 < aspect < 137 or 223 < aspect < 227:
            self.SESQUIQUADRATE.append((key, self.ASPECT_SYMBOLS["Sesquiquadrate"], _key))
            self.if_enabled_aspects(planet_degrees, value, "Sesquiquadrate", "orange")
        elif 142 < aspect < 146 or 202 < aspect < 206:
            self.BIQUINTILE.append((key, self.ASPECT_SYMBOLS["BiQuintile"], _key))
            self.if_enabled_aspects(planet_degrees, value, "BiQuintile", "gray")
        elif 147 < aspect < 153 or 207 < aspect < 213:
            self.QUINCUNX.append((key, self.ASPECT_SYMBOLS["Quincunx"], _key))
            self.if_enabled_aspects(planet_degrees, value, "Quincunx", "pink")
        elif 170 < aspect < 190:
            self.OPPOSITE.append((key, self.ASPECT_SYMBOLS["Opposite"], _key))
            self.if_enabled_aspects(planet_degrees, value, "Opposite", "red")
        else:
            self.NULL.append((key, self.ASPECT_SYMBOLS["Null"], _key))

    def draw_aspects(self):
        planet_degrees = {i: j for i, j in zip(self.PLANETS, self.PLANET_DEGREES)}
        for key, value in planet_degrees.items():
            for _key, _value in planet_degrees.items():
                aspect = abs(value - _value)
                if key != _key:
                    if MIDPOINT["Midpoint"][1].get() == "1":
                        self.if_enabled_planets(key=key, _key=_key, value=value, _value=_value,
                                                planet_degrees=planet_degrees)
                    else:
                        self.select_aspect(aspect, value, _value, key, _key)

    def draw_midpoints(self, offset=6):
        for i, j in self.MIDPOINTS.items():
            x1, y1, x2, y2 = self.x_y(angle=j, r1=280, r2=285)
            text_object(x=offset + (x1 + x2) / 2, y=offset + (y1 + y2) / 2,
                        _text=f"{self.PLANET_SYMBOLS[i[0]]}/{self.PLANET_SYMBOLS[i[1]]}")
            x1, y1, x2, y2 = self.x_y(angle=j, r1=260, r2=270)
            line_object(x1, y1, x2, y2, width=2, fill="red")

    def select_planet(self, i):
        for key, value in self.ASPECTS.items():
            if i[0] == key:
                value.append(i)

    def parse_aspects(self):
        for i in self.CONJUNCTION:
            self.select_planet(i)
        for i in self.SEMI_SEXTILE:
            self.select_planet(i)
        for i in self.SEMI_SQUARE:
            self.select_planet(i)
        for i in self.SEXTILE:
            self.select_planet(i)
        for i in self.QUINTILE:
            self.select_planet(i)
        for i in self.SQUARE:
            self.select_planet(i)
        for i in self.TRINE:
            self.select_planet(i)
        for i in self.SESQUIQUADRATE:
            self.select_planet(i)
        for i in self.BIQUINTILE:
            self.select_planet(i)
        for i in self.QUINCUNX:
            self.select_planet(i)
        for i in self.OPPOSITE:
            self.select_planet(i)
        for i in self.NULL:
            self.select_planet(i)

    def order_aspects(self):
        for planet in self.ASPECTS:
            planet_aspects = self.ASPECTS[planet]
            new_order = []
            save_aspects = {}
            for i, j in enumerate(planet_aspects):
                new_order.append(j[2])
                save_aspects[j[2]] = j[1]
            yield [(save_aspects[i], i) for i in self.PLANETS.keys() if i in new_order]

    def new_order_of_the_aspects(self):
        for i, j in zip(self.order_aspects(), self.ASPECTS):
            self.ASPECTS[j] = i
            aspect_list = []
            for m in i:
                try:
                    if list(self.ASPECTS.keys()).index(j) < list(self.ASPECTS.keys()).index(m[1]):
                        aspect_list.append(m[0])
                except ValueError:
                    aspect_list.append(m[0])
            self.ASPECTS[j] = aspect_list
        self.ASPECTS["Ascendant"] = []
        self.ASPECTS["Medium Coeli"] = []

    def modify_info(self, k, x, m, i, count1, count2):
        if k == self._SIGN_SYMBOLS["Aries"] or k == self._SIGN_SYMBOLS["Leo"] or \
                k == self._SIGN_SYMBOLS["Sagittarius"]:
            text_object(x=x + count1 + (m * 55), y=count2 + (i * 16), font="Arial 10", _text=k, fill="red")
        elif k == self._SIGN_SYMBOLS["Taurus"] or k == self._SIGN_SYMBOLS["Virgo"] or \
                k == self._SIGN_SYMBOLS["Capricorn"]:
            text_object(x=x + count1 + (m * 55), y=count2 + (i * 16), font="Arial 10", _text=k, fill="green")
        elif k == self._SIGN_SYMBOLS["Gemini"] or k == self._SIGN_SYMBOLS["Libra"] or \
                k == self._SIGN_SYMBOLS["Aquarius"]:
            text_object(x=x + count1 + (m * 55), y=count2 + (i * 16), font="Arial 10", _text=k, fill="yellow")
        elif k == self._SIGN_SYMBOLS["Cancer"] or k == self._SIGN_SYMBOLS["Scorpio"] or \
                k == self._SIGN_SYMBOLS["Pisces"]:
            text_object(x=x + count1 + (m * 55), y=count2 + (i * 16), font="Arial 10", _text=k, fill="blue")
        elif k in self.SIGNS or "\u00b0" in k or "'" in k or '"' in k or k in self.PLANETS:
            pass
        else:
            text_object(x=x + count1 + (m * 55), y=count2 + (i * 16), font="Arial 10", _text=k, fill="black")

    def draw_planet_info(self, x=900):
        planet_symbols = ""
        planets = ""
        degrees = ""
        minutes = ""
        seconds = ""
        sign_symbols = ""
        signs = ""
        for i, j in enumerate(self.PLANET_INFO_FORMAT):
            planet_symbols += f"{j[0]}\n"
            planets += f"{j[1]}\n"
            degrees += f"{j[2]}\n"
            minutes += f"{j[3]}\n"
            seconds += f"{j[4]}\n"
            sign_symbols += f"{j[5]}\n"
            signs += f"{j[6]}\n"
            for m, k in enumerate(j):
                if k == self.PLANET_SYMBOLS["Mars"] or k == self.PLANET_SYMBOLS["Venus"]:
                    if os.name == "posix":
                        text_object(x=x + 10 + (m * 60), y=15 + (i * 15), font="Arial 15", _text=k)
                    elif os.name == "nt":
                        text_object(x=x + 10 + (m * 60), y=15 + (i * 15), font="Arial 9", _text=k)
                else:
                    self.modify_info(k=k, x=x, m=m, i=i, count1=10, count2=15)
        text_object(x=x + 240, y=110, font="Arial 10", _text=signs)
        text_object(x=x + 60, y=110, font="Arial 10", _text=planets)
        text_object(x=x + 180, y=110, font="Arial 10", _text=seconds)
        text_object(x=x + 150, y=110, font="Arial 10", _text=minutes)
        text_object(x=x + 120, y=110, font="Arial 10", _text=degrees)

    def draw_house_info(self, x=900):
        houses = ""
        degrees = ""
        minutes = ""
        seconds = ""
        sign_symbols = ""
        signs = ""
        for i, j in enumerate(self.HOUSE_INFO_FORMAT):
            houses += f"{j[0]}\n"
            degrees += f"{j[1]}\n"
            minutes += f"{j[2]}\n"
            seconds += f"{j[3]}\n"
            sign_symbols += f"{j[4]}\n"
            signs += f"{j[5]}\n"
            for m, k in enumerate(j):
                if k == j[0]:
                    pass
                else:
                    self.modify_info(k=k, x=x, m=m, i=i, count1=65, count2=220)
        text_object(x=x + 30, y=315, font="Arial 10", _text=houses)
        text_object(x=x + 120, y=315, font="Arial 10", _text=degrees)
        text_object(x=x + 150, y=315, font="Arial 10", _text=minutes)
        text_object(x=x + 180, y=315, font="Arial 10", _text=seconds)
        text_object(x=x + 240, y=315, font="Arial 10", _text=signs)

    def draw_aspect_info(self, x=900):
        for i, j in enumerate(self.ASPECTS.items()):
            if i != len(self.ASPECTS.items()) - 1:
                line_object(x1=x + 25 + (i * 25), y1=428 + (i * 15), x2=x + 25 + (i * 25), y2=624, width=1)
                line_object(x1=x, y1=428 + (i * 15), x2=x + 25 + (i * 25), y2=428 + (i * 15), width=1)
            if j[0] == "Mars" or j[0] == "Venus":
                if os.name == "posix":
                    text_object(x=x + 15 + (i * 25), y=420 + (i * 15), _text=self.PLANET_SYMBOLS[j[0]], font="Arial 15")
                elif os.name == "nt":
                    text_object(x=x + 15 + (i * 25), y=420 + (i * 15), _text=self.PLANET_SYMBOLS[j[0]], font="Arial 10")
            else:
                text_object(x=x + 15 + (i * 25), y=420 + (i * 15), _text=self.PLANET_SYMBOLS[j[0]], font="Arial 10")
            for k, m in enumerate(j[1]):
                if m == self.ASPECT_SYMBOLS["Sextile"] or m == self.ASPECT_SYMBOLS["Trine"]:
                    text_object(x=x + 15 + (i * 25), y=420 + (i * 15) + ((k + 1) * 15), _text=m, font="Arial 10",
                                fill="blue")
                elif m == self.ASPECT_SYMBOLS["Conjunction"] or m == self.ASPECT_SYMBOLS["Square"] or \
                        m == self.ASPECT_SYMBOLS["Opposite"]:
                    text_object(x=x + 15 + (i * 25), y=420 + (i * 15) + ((k + 1) * 15), _text=m, font="Arial 10",
                                fill="red")
                elif m == self.ASPECT_SYMBOLS["Semi-Sextile"] or m == self.ASPECT_SYMBOLS["Quincunx"]:
                    text_object(x=x + 15 + (i * 25), y=420 + (i * 15) + ((k + 1) * 15), _text=m, font="Arial 10",
                                fill="green")
                else:
                    text_object(x=x + 15 + (i * 25), y=420 + (i * 15) + ((k + 1) * 15), _text=m, font="Arial 10")

    def draw_chart_info(self):
        chart_info_titles = "\n".join(
            [
                "Date:",
                "Time:",
                "Universal Time:",
                "Sidereal Time:",
                "Latitude:",
                "Longitude:",
            ]
        )
        chart_info_datas = "\n".join(
            [
                f"{self.day}.{self.month}.{self.year}",
                f"{self.hour}:{self.minute}",
                f"{int(self.utc_time())}:{self.minute}",
                f"""{self.sidereal_time().replace('"', '').replace("'", '').replace("°", "").replace(" ", ":")}""",
                f"{self.latitude}",
                f"{self.longitude}"
            ]
        )
        text_object(x=75, y=60, _text=chart_info_titles, font="Arial 10", fill="red")
        text_object(x=175, y=60, _text=chart_info_datas, font="Arial 10")


def on_press_button():
    global canvas, toplevel
    try:
        if not entry_label["Year"][0].get().isnumeric() or not \
                entry_label["Month"][0].get().isnumeric() or not \
                entry_label["Day"][0].get().isnumeric() or not \
                entry_label["Hour"][0].get().isnumeric() or not \
                entry_label["Minute"][0].get().isnumeric() or not \
                float(entry_label["Latitude"][0].get()) or not \
                float(entry_label["Longitude"][0].get()):
            pass
        else:
            toplevel = create_toplevel()
            canvas = create_canvas(master=toplevel)
            Chart(
                year=int(entry_label["Year"][0].get()),
                month=int(entry_label["Month"][0].get()),
                day=int(entry_label["Day"][0].get()),
                hour=int(entry_label["Hour"][0].get()),
                minute=int(entry_label["Minute"][0].get()),
                latitude=float(entry_label["Latitude"][0].get()),
                longitude=float(entry_label["Longitude"][0].get()),
            )
    except ValueError:
        pass


if __name__ == "__main__":
    button.configure(command=on_press_button)
    root.mainloop()
