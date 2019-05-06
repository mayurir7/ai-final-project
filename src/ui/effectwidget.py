from kivy.uix.effectwidget import EffectBase
from kivy.properties import NumericProperty, ReferenceListProperty, ListProperty,BooleanProperty, ObjectProperty
effect_drop_shadow = '''
#define M_PI 3.1415926535897932384626433832795
vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords) {{
    vec2 coords2;
    float x, y;
    float radius, sampling, surface;
    vec4 tint, shadow;
    coords2 = coords + vec2({offset_x:f}, {offset_y:f}) ;
    radius = {radius:f};
    sampling = {sampling:f};
    tint = vec4({r:f}, {g:f}, {b:f}, {a:f});
    if (color.a >= .99)
        return color;
    surface = (sampling * M_PI * radius * radius) / 2.;
    shadow = vec4(0., 0., 0., 0.);
    for (x = -radius; x < radius; x += sampling)
        for (y = -radius; y < radius; y += sampling)
            if (length(vec2(x, y)) <= radius)
                shadow += texture2D(
                    texture,
                    vec2(coords2.x + x, coords2.y + y) / resolution
                    ).a * tint / surface;
    return color + shadow * (shadow.a - color.a);
}}
'''

class DropShadowEffect(EffectBase):
    '''Add DropShadow to the input.'''
    offset = ListProperty([0, 0])
    tint = ListProperty([0, 0, 0, 1])
    radius = NumericProperty(1)
    sampling = NumericProperty(1)

    def __init__(self, *args, **kwargs):
        super(DropShadowEffect, self).__init__(*args, **kwargs)
        self.fbind('offset', self.do_glsl)
        self.fbind('tint', self.do_glsl)
        self.fbind('radius', self.do_glsl)
        self.fbind('sampling', self.do_glsl)
        self.do_glsl()

    def on_size(self, *args):
        self.do_glsl()

    def do_glsl(self, *args):
        self.glsl = effect_drop_shadow.format(
            offset_x=self.offset[0],
            offset_y=self.offset[1],
            radius=self.radius,
            sampling=self.sampling,
            r=self.tint[0],
            g=self.tint[1],
            b=self.tint[2],
            a=self.tint[3],
        )