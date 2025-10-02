from manim import *
import numpy as np

class GeneratedScene(Scene):
    def construct(self):
        title = Text("Sine and Cosine Waves", font_size=40)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-2, 2, 1],
            axis_config={"color": BLUE},
        )
        
        sine_graph = axes.plot(lambda x: np.sin(2*x), color=RED)
        cosine_graph = axes.plot(lambda x: np.cos(2*x), color=GREEN)
        
        sine_label = MathTex(r"\sin(2x)", color=RED).next_to(axes, RIGHT)
        cosine_label = MathTex(r"\cos(2x)", color=GREEN).next_to(sine_label, DOWN)
        
        self.play(Create(axes))
        self.play(Create(sine_graph), Write(sine_label))
        self.wait(1)
        self.play(Transform(sine_graph, cosine_graph), 
                  Transform(sine_label, cosine_label))
        self.wait(2)
        self.play(FadeOut(Group(axes, sine_graph, sine_label, title)))