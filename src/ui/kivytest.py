from kivy.app import App
#kivy.require("1.10.0")
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.core.text import LabelBase
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.uix.dropdown import DropDown
from kivy.input.providers import mouse
from kivy.properties import BoundedNumericProperty, NumericProperty, StringProperty, ReferenceListProperty, ListProperty,BooleanProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.elevationbehavior import RectangularElevationBehavior
from theming import ThemableBehavior, ThemeManager
from kivy.metrics import dp
from kivy.uix.widget import Widget
import matplotlib.pyplot as plt
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.font_manager as fm
from matplotlib.dates import (DateFormatter, AutoDateLocator, drange)
import numpy as np
import datetime
from matplotlib import rcParams

# do some black magic to import from parent folder
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from predict_sources import PredictSources

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

segoeui = fm.FontProperties(fname='fonts/SEGOEUI.TTF')
segoeuil = fm.FontProperties(fname='fonts/segoeuil.ttf')
gothaml = fm.FontProperties(fname='fonts/Gotham Light Regular.otf')
avenir1 = fm.FontProperties(fname='fonts/Avenir1.otf')
avenir2 = fm.FontProperties(fname='fonts/Avenir2.otf')
avenir3 = fm.FontProperties(fname='fonts/Avenir3.otf')
rcParams.update({'figure.autolayout': True})

LabelBase.register(name="Gotham",
    fn_regular= "fonts/Gotham Light Regular.otf"
    )

LabelBase.register(name="GothamBook",
    fn_regular= "fonts/GothamBook.ttf"
    )

LabelBase.register(name="GothamB",
    fn_regular= "fonts/Gotham-Bold.otf"
    )

LabelBase.register(name="GothamM",
    fn_regular= "fonts/GothamMedium.ttf"
    )

LabelBase.register(name="Avenir3",
    fn_regular= "fonts/Avenir3.otf"
    )

LabelBase.register(name="Avenir2",
    fn_regular= "fonts/Avenir2.otf"
    )

LabelBase.register(name="SegoeL",
    fn_regular= "fonts/segoeuil.ttf"
    )

LabelBase.register(name="Segoe",
    fn_regular= "fonts/SEGOEUI.TTF"
    )

class HoverBehavior(object):
    hovered = BooleanProperty(False)
    border_point= ObjectProperty(None)

    def __init__(self, **kwargs):
        self.register_event_type('on_enter')
        self.register_event_type('on_leave')
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(HoverBehavior, self).__init__(**kwargs)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return # do proceed if I'm not displayed <=> If have no parent
        pos = args[1]
        #Next line to_widget allow to compensate for relative layout
        inside = self.collide_point(*self.to_widget(*pos))
        if self.hovered == inside:
            #We have already done what was needed
            return
        self.border_point = pos
        self.hovered = inside
        if inside:
            self.dispatch('on_enter')
        else:
            self.dispatch('on_leave')

    def on_enter(self):
        pass

    def on_leave(self):
        pass

Factory.register('HoverBehavior', HoverBehavior)

class StartScreen(Screen):
    pass

class MainScreen(Screen):
    c1 = StringProperty("#2a2a2a")
    c2 = StringProperty("#232323")
    c3 = StringProperty("#111111")
    c4 = StringProperty("#c0c0c0")
    c5 = StringProperty("#c00000")
    c6 = StringProperty("#30b023")
    c7 = StringProperty("#3e3e3e")
    wc = StringProperty("#ffffff")
    sc = StringProperty("#ffc600")
    hc = StringProperty("#21a5f0")

    date_str = StringProperty()
    time = StringProperty()
    cloud_cover = StringProperty()
    temp = NumericProperty()
    wind_speed = NumericProperty()
    energy_gain = ListProperty()
    energy_loss = ListProperty()
    energy_levels = ListProperty()
    total_gain = NumericProperty()
    total_loss = NumericProperty()
    sum_total_energy_needed = NumericProperty()
    sum_net_energy = ListProperty()
    sum_energy_used = ListProperty()
    sum_energy_saved = NumericProperty()

    def __init__(self, **kwargs):
        self.dropdown = CustomDropDown()
        self.dropdown.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', x))
        super(MainScreen, self).__init__(**kwargs)
        
        # get prediction class
        self.predicter = PredictSources(path_to_data="../../data/10monthsV2.txt", path_to_energy="../../data/2018load.csv")
        
        # properties that do not change
        self.capacity = self.predicter.startingEnergyLevel
        print self.capacity
        self.dates_to_indices()

        # TODO: calculate these numbers
        self.sum_total_energy_needed = 70000
        self.sum_net_energy = [0.0, 10.0, 0.0]
        self.sum_energy_used = [25.0, 150.0, 50.0, 69875.0]
        self.sum_energy_saved = 225
        
        # initialize properties        
        first = self.predicter.result[0][0] 
        self.on_date_time_change(first.month, first.day, first.year, first.hour)

    def on_pre_enter(self, *args):
        # handle graph stuff

        plt.style.use('dark_background')
        
        loc = AutoDateLocator()
        formatter = DateFormatter('%m-%d-%y')
        date1 = datetime.date(2018, 1, 1)
        date2 = datetime.date(2019, 1, 1)
        delta = datetime.timedelta(days=7)
        dates = drange(date1, date2, delta)
        s = np.random.rand(len(dates))  # make up some random y values

        fig, ax = plt.subplots()
        
        ax.xaxis.set_major_locator(loc)
        ax.xaxis.set_major_formatter(formatter)
        ax.set_facecolor('#232323')
        fig.patch.set_facecolor('#2a2a2a')
        plt.plot_date(dates, s, linestyle='solid', marker='None', color='#38ff38', linewidth=1)
        plt.ylabel('Efficiency', fontproperties=avenir3,fontsize=10)
        plt.xlabel('Date', fontproperties=avenir3,fontsize=10)
        plt.yticks(fontproperties=segoeui, fontsize=8)
        plt.xticks(fontproperties=segoeui, fontsize=7)
        plt.grid(color='#686868', linestyle=':', linewidth=.5)
        self.ids.test.add_widget(FigureCanvasKivyAgg(plt.gcf()))

    def dates_to_indices(self):
        mapping = {}
        for index in range(len(self.predicter.result)):
            raw_data = self.predicter.result[index][0]
            mapping[tuple((raw_data.month, raw_data.day, raw_data.year, raw_data.hour))] = index
        self.indices = mapping

    def update_date_time(self, month, day, year, hour, minute):
        self.date = datetime.datetime(year, month, day, hour, minute)
        self.date_str = self.date.strftime("%B %d, %Y")
        self.time = self.date.strftime("%H:%M")

    def percentage(self, array):
        array = list(array)
        for index in range(len(self.capacity)):
            array[index] = array[index] / self.capacity[index] * 100.0
        return array

    def on_date_time_change(self, month, day, year, hour):
        # updates the text labels based on the prediction for that date/time
        entry = self.predicter.result[self.indices[(month, day, year, hour)]]
        self.update_date_time(month, day, year, hour, entry[0].minute)
        self.temp = entry[0].temperature
        self.cloud_cover = entry[0].sunForecast
        self.wind_speed = entry[0].windSpeed * 2.237
        self.temperature = entry[0].temperature
        self.energy_gain = self.percentage(entry[1])
        self.energy_loss = self.percentage(entry[2])
        self.energy_levels = self.percentage(entry[3])
        self.total_gain = sum(entry[1]) / sum(self.capacity) * 100.0
        self.total_loss = sum(entry[2]) / sum(self.capacity) * 100.0

    def on_leave(self, *args):
        self.ids.test.remove_widget(self.ids.test.children[0])

    def click_file(self):
        self.dropdown.open(self)

class CustomDropDown(DropDown):
    pass

class HoverButton(Button, HoverBehavior):
    def on_enter(self, *args):
        pass

    def on_leave(self, *args):
        pass

class FirstKivy(App):
    Builder.load_file("dropdown.kv")
    def build(self):
        Window.borderless = True
        Window.size = (800, 650)
        return Builder.load_file("layout2.kv")

if __name__ == "__main__":
    FirstKivy().run()
    
