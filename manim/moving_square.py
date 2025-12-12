from manim import *

class MovingSquare(Scene):
    def construct(self):
        # Create a blue square
        square = Square(color=BLUE)

        # Show the square being drawn
        self.play(Create(square))

        # Move the square to the right
        self.play(square.animate.shift(RIGHT * 2))

        # Rotate the square
        self.play(Rotate(square, angle=PI / 4))

        # Keep the final frame on screen for a bit
        self.wait(1)
