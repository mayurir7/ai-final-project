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
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
import matplotlib.pyplot as plt
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.font_manager as fm
from matplotlib.dates import (DateFormatter, AutoDateLocator, drange)
import numpy as np
import datetime
from matplotlib import rcParams
import pickle
from kivy.uix.modalview import ModalView
import calendar
from datetime import date
import datetime
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock

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
    
    def show_load(self, load):
	self.loadsave = LoadSave()
        self.loadsave.show_load(load)
    
    def load_predictions(self, path, filename):
        self.manager.get_screen('main').predicter = self.loadsave.load_predictions(path, filename)
        self.manager.get_screen('main').on_predict()
        self.manager.current = 'main'

    def load_predicter(self, path, filename):
        self.manager.get_screen('main').predicter = self.loadsave.load_predicter(path, filename)
        self.manager.get_screen('main').on_predict()
        self.manager.current = 'main'

class LoadSave(FloatLayout):
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)
    to_save = None

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self, load):
        content = LoadDialog(load=load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load_predicter(self, path, filename):
        filename = os.path.join(path, filename[0])
        predicter = PredictSources(path_to_data=filename, path_to_energy="../../data/2018load.csv")
	predicter.prediction()
        self.dismiss_popup()
	return predicter

    def load_predictions(self, path, filename):
	filename = os.path.join(path, filename[0])
	predicter = PredictSources(path_to_energy="../../data/2018load.csv")
	predicter.result = pickle.load(open(filename))
	self.dismiss_popup()
	return predicter

    def save(self, path, filename):
        filename = os.path.join(path, filename)
	with open(filename, 'wb') as f:
	    pickle.dump(self.to_save, f)
        self.dismiss_popup()

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    path = os.getcwd()

class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    path = os.getcwd()

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
    previous_date = ObjectProperty()
    
    def __init__(self, **kwargs):
        self.dropdown = CustomDropDown()
        self.dropdown.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', x))
        super(MainScreen, self).__init__(**kwargs)
        
        # initialize all fields with empty data
        self.predicter = None
        self.capacity = [0.0, 0.0, 0.0]
        self.sum_net_energy = [0.0, 0.0, 0.0]
        self.sum_total_energy_needed = 0.0
        self.sum_energy_used = [0.0, 0.0, 0.0, 0.0]
        self.sum_energy_saved = 0.0
        self.update_date_time(1, 1, 2019, 0, 0)
        self.temp = 0.0
        self.cloud_cover = ""
        self.wind_speed = 0.0
        self.energy_gain = [0.0, 0.0, 0.0]
        self.energy_loss = [0.0, 0.0, 0.0]
        self.energy_levels = [0.0, 0.0, 0.0]
        self.total_gain = 0.0
        self.total_loss = 0.0

    def set_previous_date(self, date_obj):
        self.previous_date = date_obj
        self.on_date_time_change(date_obj.month, date_obj.day, date_obj.year, 4)

    def show_example_date_picker(self):
        pd = self.previous_date
        # pass first and last date into date picker
        fdate = self.predicter.result[0][0]
        ldate = self.predicter.result[len(self.predicter.result) - 1][0]
        mindate = datetime.date(fdate.year, fdate.month, fdate.day)
        maxdate = datetime.date(ldate.year, ldate.month, ldate.day)
        try:
            # make date picker that starts on currently selected date
            DatePicker(self.set_previous_date,
                            pd.year, pd.month, pd.day,
                            maxdate, mindate).open()
        except AttributeError:
            # make date picker that starts on first date in data
            DatePicker(self.set_previous_date,
                            fdate.year, fdate.month, fdate.day, maxdate, mindate).open()

    def on_predict(self):
        """
        This method should run once we have a PredictSources
        instance that has read in the provided file
        and predicted for the entire provided timespan
        """
        # properties that do not change
        self.capacity = self.predicter.capacity
        self.dates_to_indices()

        # calculate statistics over total time period
        self.sum_net_energy = [round(i, 3) for i in self.predicter.result[len(self.predicter.result) - 1][3]]

        self.sum_total_energy_needed = 0
        self.sum_energy_used = [0.0, 0.0, 0.0, 0.0]
        self.sum_energy_saved = 0
        self.max_gain = [0.0, 0.0, 0.0]
        self.max_loss = [0.0, 0.0, 0.0]
        self.max_cap = [0.0, 0.0, 0.0]
        for tuple in self.predicter.result:
            # nested bc sum_energy_used is longer than all others
            for idx in range(len(self.sum_energy_used) - 1):
                self.sum_energy_used[idx] += tuple[2][idx]
            # calculate coal used, energy needed, energy saved
            self.sum_energy_used[3] += tuple[4] - sum(tuple[2])
            self.sum_total_energy_needed += tuple[4]
            self.sum_energy_saved += sum(tuple[2])
            
            # find maxes
            self.max_gain = [max(tuple[3][i], self.max_gain[i]) for i in range(len(self.max_gain))]
            self.max_loss = [max(tuple[3][i], self.max_loss[i]) for i in range(len(self.max_loss))]
            self.max_cap = [max(tuple[3][i], self.max_cap[i]) for i in range(len(self.max_cap))]

        self.sum_total_energy_needed = round(self.sum_total_energy_needed / 10000000, 3)
        self.sum_energy_saved = round(self.sum_energy_saved / 1000, 3)
        self.sum_energy_used = [round(i / 1000.0, 3) for i in self.sum_energy_used]

        # initialize dynamic hourly properties
        first = self.predicter.result[0][0] 
        self.on_date_time_change(first.month, first.day, first.year, first.hour)

        # initialize graph
        self.graph_setup()

    def graph_setup(self, *args):
        """
        Handle graph setup
        """
        
        plt.style.use('dark_background')

        loc = AutoDateLocator()
        formatter = DateFormatter('%m-%d-%y\n%H:%M')
        dates = []
        s = []
        for idx in range(0, len(self.predicter.result), 24):
            date = self.predicter.result[idx]
            dates.append(datetime.datetime(date[0].year, date[0].month, date[0].day, date[0].hour, date[0].minute))
            s.append(round(sum(date[2]) / date[4] * 100))
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
        """
        Takes all of the dates over the predicter's
        range of data and maps them to indices
        into the predicter's results array for
        easier access later
        """
        mapping = {}
        for index in range(len(self.predicter.result)):
            raw_data = self.predicter.result[index][0]
            mapping[tuple((raw_data.month, raw_data.day, raw_data.year, raw_data.hour))] = index
        self.indices = mapping

    def update_date_time(self, month, day, year, hour, minute):
        """
        Given a date and time, converts to strings
        for easier display on UI
        """
        self.date = datetime.datetime(year, month, day, hour, minute)
        self.date_str = self.date.strftime("%B %d, %Y")
        self.time = self.date.strftime("%H:%M")

    def percentage(self, array, total):
        """
        Given an array, turns into percentages
        """
        array = list(array)
        for index in range(len(self.capacity)):
            array[index] = min(round(array[index] / total[index] * 100.0, 2), 100.0)
        return array

    def on_date_time_change(self, month, day, year, hour):
        """
        Given a date and time, updates all text labels
        in day report to match the data for that date
        and time
        """
        #TODO: delete this line
        #month = random.randint(1, 5)
        #day = random.randint(1, 30)
        #year = 2018
        #hour = random.randint(0, 23)
        # TODO: end delete

        entry = self.predicter.result[self.indices[(month, day, year, hour)]]
        self.update_date_time(month, day, year, hour, entry[0].minute)
        self.temp = entry[0].temperature
        self.cloud_cover = entry[0].sunForecast
        self.wind_speed = entry[0].windSpeed * 2.237
        self.temperature = entry[0].temperature
        self.energy_gain = self.percentage(entry[1], self.max_gain)
        self.energy_loss = self.percentage(entry[2], self.max_loss)
        self.energy_levels = self.percentage(entry[3], self.max_cap)
        self.total_gain = sum(entry[1]) / sum(self.max_gain) * 100.0
        self.total_loss = sum(entry[2]) / sum(self.max_loss) * 100.0

    def on_leave(self, *args):
        self.ids.test.remove_widget(self.ids.test.children[0])

    # Methods to deal with File menu and its options

    def click_file(self):
        self.dropdown.open(self)
    
    def save_plan(self):
        """
        Callback method called when 'Save Plan'
        option clicked in File menu
        """
        self.loadsave = LoadSave()
	self.loadsave.to_save = self.predicter.result
	self.loadsave.show_save()

    def load_predictions(self, path, filename):
        """
        Wrapper method that uses LoadSave to load
        a pre-calculated set of predictions and then
        re-calculate numbers to show on main screen
        """
        self.predicter = self.loadsave.load_predictions(path, filename)
        self.on_predict()
        #self.dropdown.close(self)

    def open_plan(self):
	"""
        Callback method called when 'Open Plan'
        option clicked on file menu
        """
        self.loadsave = LoadSave()
	self.loadsave.show_load(self.load_predictions)

    def load_predicter(self, path, filename):
        """
        Wrapper method that loads weather data, makes
        new set of predictions, and re-calculates
        numbers to display
        """
        self.predicter = self.loadsave.load_predicter(path, filename)
        self.on_predict()

    def new_plan(self):
	"""
        Callback method called when 'New Plan' option
        selected on File menu
        """
        self.loadsave = LoadSave()
	self.loadsave.show_load(self.load_predicter)

class CustomDropDown(DropDown):
    pass

class HoverButton(Button, HoverBehavior):
    def on_enter(self, *args):
        pass

    def on_leave(self, *args):
        pass



class DaySelector(AnchorLayout):
    shown = BooleanProperty(False)

    def __init__(self, parent):
        super(DaySelector, self).__init__()
        self.parent_class = parent
        self.parent_class.add_widget(self, index=7)
        self.selected_widget = None
        Window.bind(on_resize=self.move_resize)

    def update(self):
        parent = self.parent_class
        if parent.sel_month == parent.month and parent.sel_year == parent.year:
            self.shown = True
        else:
            self.shown = False

    def set_widget(self, widget):
        self.selected_widget = widget
        self.pos = widget.pos
        self.move_resize(do_again=True)
        self.update()

    def move_resize(self, window=None, width=None, height=None, do_again=True):
        self.pos = self.selected_widget.pos
        if do_again:
            Clock.schedule_once(lambda x: self.move_resize(do_again=False), 0.01)


class DayButton(ButtonBehavior, AnchorLayout):
    text = StringProperty()
    owner = ObjectProperty()
    is_today = BooleanProperty(False)
    is_selected = BooleanProperty(False)

    def on_release(self):
        self.owner.set_selected_widget(self)


class WeekdayLabel(Label):
    pass


class DatePicker(FloatLayout, ModalView):
    _sel_day_widget = ObjectProperty()
    cal_list = None
    cal_layout = ObjectProperty()
    sel_year = NumericProperty()
    sel_month = NumericProperty()
    sel_day = NumericProperty()
    day = NumericProperty()
    month = NumericProperty()
    year = NumericProperty()
    today = date.today()
    callback = ObjectProperty()
    background_color = ListProperty([0, 0, 0, 0.7])

    class SetDateError(Exception):
        pass

    def __init__(self, callback, year, month, day,
                 maxdate, mindate, firstweekday=0,
                 **kwargs):
        self.callback = callback
        self.cal = calendar.Calendar(firstweekday)
        self.sel_year = year
        self.sel_month = month
        self.sel_day = day
        self.month = self.sel_month
        self.year = self.sel_year
        self.day = self.sel_day
        self.maxdate = maxdate
        self.mindate = mindate
        super(DatePicker, self).__init__(**kwargs)
        self.selector = DaySelector(parent=self)
        self.generate_cal_widgets()
        self.update_cal_matrix(self.sel_year, self.sel_month)
        self.set_month_day(self.sel_day)
        self.selector.update()
        

    def ok_click(self):
        self.callback(date(self.sel_year, self.sel_month, self.sel_day))
        self.dismiss()

    def fmt_lbl_date(self, year, month, day):
        d = datetime.date(int(year), int(month), int(day))
        separator = ' '
        print d.strftime('%a,').capitalize() + separator + d.strftime(
            '%b').capitalize() + ' ' + str(day).lstrip('0')
        return d.strftime('%a,').capitalize() + separator + d.strftime(
            '%b').capitalize() + ' ' + str(day).lstrip('0')

    def set_date(self, year, month, day):
        try:
            date(year, month, day)
        except Exception as e:
            print(e)
            if str(e) == "day is out of range for month":
                raise self.SetDateError(" Day %s day is out of range for month %s" % (day, month))
            elif str(e) == "month must be in 1..12":
                raise self.SetDateError("Month must be between 1 and 12, got %s" % month)
            elif str(e) == "year is out of range":
                raise self.SetDateError("Year must be between %s and %s, got %s" %
                                        (datetime.MINYEAR, datetime.MAXYEAR, year))
        else:
            self.sel_year = year
            self.sel_month = month
            self.sel_day = day
            self.month = self.sel_month
            self.year = self.sel_year
            self.day = self.sel_day
            self.update_cal_matrix(self.sel_year, self.sel_month)
            self.set_month_day(self.sel_day)
            self.selector.update()

    def set_selected_widget(self, widget):
        if self._sel_day_widget:
            self._sel_day_widget.is_selected = False
        widget.is_selected = True
        self.sel_month = int(self.month)
        self.sel_year = int(self.year)
        self.sel_day = int(widget.text)
        self._sel_day_widget = widget
        self.selector.set_widget(widget)

    def set_month_day(self, day):
        for idx in range(len(self.cal_list)):
            if str(day) == str(self.cal_list[idx].text):
                self._sel_day_widget = self.cal_list[idx]
                self.sel_day = int(self.cal_list[idx].text)
                if self._sel_day_widget:
                    self._sel_day_widget.is_selected = False
                self._sel_day_widget = self.cal_list[idx]
                self.cal_list[idx].is_selected = True
                self.selector.set_widget(self.cal_list[idx])

    def update_cal_matrix(self, year, month):
        try:
            dates = [x for x in self.cal.itermonthdates(year, month)]
        except ValueError as e:
            if str(e) == "year is out of range":
                pass
        else:
            self.year = year
            self.month = month
            for idx in range(len(self.cal_list)):
                if idx >= len(dates) or dates[idx].month != month:
                    self.cal_list[idx].disabled = True
                    self.cal_list[idx].text = ''
                else:
                    self.cal_list[idx].disabled = False
                    self.cal_list[idx].text = str(dates[idx].day)
                    self.cal_list[idx].is_today = dates[idx] == self.today
            self.selector.update()

    def generate_cal_widgets(self):
        cal_list = []
        for i in calendar.day_abbr:
            self.cal_layout.add_widget(WeekdayLabel(text=i[0].upper()))
        for i in range(6 * 7):  # 6 weeks, 7 days a week
            db = DayButton(owner=self)
            cal_list.append(db)
            self.cal_layout.add_widget(db)
        self.cal_list = cal_list

    def change_month(self, operation):
        op = 1 if operation is 'next' else -1
        sl, sy = self.month, self.year
        m = 12 if sl + op == 0 else 1 if sl + op == 13 else sl + op
        y = sy - 1 if sl + op == 0 else sy + 1 if sl + op == 13 else sy
        if datetime.date(y, m, 1) > self.maxdate or datetime.date(y, m, 28) < self.mindate:
            y = sy
            m = sl
        self.update_cal_matrix(y, m)

class FirstKivy(App):

    def build(self):
        Builder.load_file("testlayout.kv")
        Builder.load_file("dropdown.kv")
        Window.borderless = True
        Window.size = (800, 650)
        return Builder.load_file("layout2.kv")

if __name__ == "__main__":
    FirstKivy().run()

