from manim import *

class GeneratedScene(Scene):
    def construct(self):
        title = Text("Pythagorean Theorem", font_size=48)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        
        # Create right triangle
        triangle = Polygon(
            [-2, -1, 0], [2, -1, 0], [2, 1, 0],
            color=WHITE
        )
        
        # Labels
        a_label = MathTex("a").next_to(triangle, LEFT)
        b_label = MathTex("b").next_to(triangle, DOWN)
        c_label = MathTex("c").next_to(triangle, UR)
        
        formula = MathTex("a^2 + b^2 = c^2").to_edge(DOWN)
        
        self.play(Create(triangle))
        self.play(Write(a_label), Write(b_label), Write(c_label))
        self.wait(1)
        self.play(Write(formula))
        self.wait(2)
        self.play(FadeOut(Group(triangle, a_label, b_label, c_label, formula, title)))