from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from kivy.lang import Builder

class Graph(BoxLayout):
    graph = ObjectProperty()


class MyApp(App):

    def build(self):
        plt.plot([1, 23, 2, 4])
        plt.ylabel('some numbers')

        self.root.ids.dest.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        return Builder.load_file("layout3.kv")

MyApp().run()
