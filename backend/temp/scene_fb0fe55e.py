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
        sine_wave = axes.plot(lambda x: np.sin(x), x_range=[0, 4 * PI])
        cosine_wave = axes.plot(lambda x: np.cos(x), x_range=[0, 4 * PI], color=YELLOW)

        self.play(Create(axes), run_time=1)
        self.play(Create(sine_wave), run_time=2)
        self.play(Create(cosine_wave), run_time=2)
        self.wait(0.5)
        self.play(FadeOut(sine_wave), FadeOut(cosine_wave), run_time=1)
        self.play(FadeOut(axes), run_time=1)