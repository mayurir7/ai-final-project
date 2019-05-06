from kivy.lang import Builder
from kivy.base import runTouchApp

KV = '''
#:import DropShadow effectwidget.DropShadowEffect
<T@Label>:
    size_hint_x: None
    width: self.texture_size[0]
<S@Slider>:
    orientation: 'horizontal'
    Label:
        pos: root.pos
        text: str(root.value)
BoxLayout:
    FloatLayout:
        Widget:
            bgr: bgr.value
            bgb: bgb.value
            bgg: bgg.value
            bga: bga.value
            canvas.before:
                Color:
                    rgba: self.bgr or 0, self.bgg or 0, self.bgb or 0, self.bga or 0
                Rectangle:
                    pos: self.pos
                    size: self.size
        EffectWidget:
            id: effect
            drop_shadow: DropShadow()
            effects: [self.drop_shadow]
            Label:
                text: ti.text
                font_size: font_size.value
                color: [r.value, g.value, b.value, a.value]
    GridLayout:
        cols: 2
        T:
            text: 'text'
        TextInput:
            id: ti
            text: 'Test'
        T:
            text: 'font_size'
        S:
            id: font_size
            min: 10
            max: 500
        T:
            text: 'color_r'
        S:
            id: r
            min: 0
            max: 1
        T:
            text: 'color_g'
        S:
            id: g
            min: 0
            max: 1
        T:
            text: 'color_b'
        S:
            id: b
            min: 0
            max: 1
        T:
            text: 'color_a'
        S:
            id: a
            min: 0
            max: 1
        T:
            text: 'offset_x'
        S:
            min: -100
            max: 100
            step: 1
            on_value: effect.drop_shadow.offset[0] = self.value
        T:
            text: 'offset_y'
        S:
            min: -100
            max: 100
            step: 1
            on_value: effect.drop_shadow.offset[1] = self.value
        T:
            text: 'radius'
        S:
            min: 1
            max: 10
            on_value: effect.drop_shadow.radius = self.value
        T:
            text: 'sampling'
        S:
            min: 1
            max: 10
            on_value: effect.drop_shadow.sampling = self.value
        T:
            text: 'tint_r'
        S:
            min: 0
            max: 1
            on_value: effect.drop_shadow.tint[0] = self.value
        T:
            text: 'tint_g'
        S:
            min: 0
            max: 1
            on_value: effect.drop_shadow.tint[1] = self.value
        T:
            text: 'tint_b'
        S:
            min: 0
            max: 1
            on_value: effect.drop_shadow.tint[2] = self.value
        T:
            text: 'tint_a'
        S:
            min: 0
            max: 1
            on_value: effect.drop_shadow.tint[3] = self.value
        T:
            text: 'bgr'
        S:
            id: bgr
            min: 0
            max: 1
        T:
            text: 'bgg'
        S:
            id: bgg
            min: 0
            max: 1
        T:
            text: 'bgb'
        S:
            id: bgb
            min: 0
            max: 1
        T:
            text: 'bga'
        S:
            id: bga
            min: 0
            max: 1
'''

runTouchApp(Builder.load_string(KV))