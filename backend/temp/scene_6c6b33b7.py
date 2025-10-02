from manim import *
import numpy as np

class GeneratedScene(Scene):
    def construct(self):
        title = Text("Trigonometric Functions", font_size=40)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-2, 2, 1],
            axis_config={"color": GREY},
            x_length=8,
            y_length=4,
        )
        
        sine_graph = axes.plot(lambda x: np.sin(x), color=RED, x_range=[-4, 4])
        cosine_graph = axes.plot(lambda x: np.cos(x), color=BLUE, x_range=[-4, 4])
        
        sine_label = MathTex(r"y = \sin(x)", color=RED).to_edge(RIGHT).shift(UP)
        cosine_label = MathTex(r"y = \cos(x)", color=BLUE).to_edge(RIGHT)
        
        self.play(Create(axes))
        self.play(Create(sine_graph), Write(sine_label))
        self.wait(1)
        self.play(Create(cosine_graph), Write(cosine_label))
        self.wait(2)
        self.play(*[FadeOut(obj) for obj in [axes, sine_graph, cosine_graph, 
                                              sine_label, cosine_label, title]])