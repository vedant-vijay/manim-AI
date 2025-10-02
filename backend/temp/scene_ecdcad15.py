from manim import *

class GeneratedScene(Scene):
    def construct(self):
        axes = Axes(
            x_range=[0, 4 * PI, PI / 2],
            y_range=[-1.5, 1.5, 1],
            x_length=10,
            y_length=6,
            axis_config={"include_tip": False},
        )
        self.add(axes)

        sine_wave = axes.plot(lambda x: np.sin(x), x_range=[0, 4 * PI], color=BLUE)
        cosine_wave = axes.plot(lambda x: np.cos(x), x_range=[0, 4 * PI], color=RED)

        self.play(Create(sine_wave), Create(cosine_wave))
        self.wait(2)
        self.play(FadeOut(sine_wave), FadeOut(cosine_wave))
        self.wait(1)