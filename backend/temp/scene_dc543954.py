from manim import *

class GeneratedScene(Scene):
    def construct(self):
        input_layer = VGroup(
            Circle(radius=0.2, color=BLUE),
            Circle(radius=0.2, color=BLUE),
            Circle(radius=0.2, color=BLUE)
        ).arrange(RIGHT, buff=0.5).shift(LEFT * 4)

        hidden_layer1 = VGroup(
            Circle(radius=0.2, color=BLUE),
            Circle(radius=0.2, color=BLUE),
            Circle(radius=0.2, color=BLUE),
            Circle(radius=0.2, color=BLUE)
        ).arrange(RIGHT, buff=0.5).shift(UP * 0.5)

        hidden_layer2 = VGroup(
            Circle(radius=0.2, color=BLUE),
            Circle(radius=0.2, color=BLUE),
            Circle(radius=0.2, color=BLUE)
        ).arrange(RIGHT, buff=0.5).shift(DOWN * 0.5)

        output_layer = VGroup(
            Circle(radius=0.2, color=BLUE),
            Circle(radius=0.2, color=BLUE)
        ).arrange(RIGHT, buff=0.5).shift(RIGHT * 4)

        self.play(Create(input_layer), Create(hidden_layer1), Create(hidden_layer2), Create(output_layer))

        signal1 = Dot(color=YELLOW, radius=0.05)
        self.add(signal1)
        self.play(MoveAlongPath(signal1, input_layer[0].get_center() + RIGHT * 0.2), run_time=0.5)
        self.play(MoveAlongPath(signal1, hidden_layer1[0].get_center() + LEFT * 0.2), run_time=0.5)
        self.play(MoveAlongPath(signal1, hidden_layer2[0].get_center() + LEFT * 0.2), run_time=0.5)
        self.play(MoveAlongPath(signal1, output_layer[0].get_center() + LEFT * 0.2), run_time=0.5)

        signal2 = Dot(color=YELLOW, radius=0.05)
        self.add(signal2)
        self.play(MoveAlongPath(signal2, input_layer[1].get_center() + RIGHT * 0.2), run_time=0.5)
        self.play(MoveAlongPath(signal2, hidden_layer1[1].get_center() + LEFT * 0.2), run_time=0.5)
        self.play(MoveAlongPath(signal2, hidden_layer2[1].get_center() + LEFT * 0.2), run_time=0.5)
        self.play(MoveAlongPath(signal2, output_layer[1].get_center() + LEFT * 0.2), run_time=0.5)

        self.wait(1)
        self.play(FadeOut(input_layer), FadeOut(hidden_layer1), FadeOut(hidden_layer2), FadeOut(output_layer), FadeOut(signal1), FadeOut(signal2))