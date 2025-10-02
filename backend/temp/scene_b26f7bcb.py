from manim import *

class GeneratedScene(Scene):
    def construct(self):
        title = Text("Shape Transformation", font_size=48)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        
        circle = Circle(radius=1.5, color=BLUE, fill_opacity=0.5)
        square = Square(side_length=3, color=RED, fill_opacity=0.5)
        
        self.play(Create(circle))
        self.wait(1)
        self.play(Transform(circle, square), run_time=2)
        self.wait(1)
        self.play(FadeOut(circle), FadeOut(title))