from manim import *
import numpy as np
from PIL import Image  # <-- New import to load the image file


class SimpleConvolution(Scene):
    def construct(self):
        # 1) Load mario.png as grayscale and normalize to [0, 1]
        #    Make sure mario.png is in the same folder as this script.
        img = Image.open("mario.png").convert("L")  # "L" = grayscale

        # Optional: downscale the image so the grid is not huge.
        # You can change (32, 32) or comment this out if your image is already small.
        img = img.resize((32, 32), resample=Image.NEAREST)

        image = np.array(img, dtype=float) / 255.0  # values in [0, 1]

        # 2) Define a simple 3x3 box blur kernel
        kernel = np.ones((3, 3), dtype=float) / 9.0

        # 3) Compute the convolution (same size, with padding)
        conv = self.convolve_same(image, kernel)

        # 4) Create grids for original and convolved image
        original_grid = self.grid_from_array(image)
        conv_grid = self.grid_from_array(conv)
        # Start with convolved image invisible
        for cell in conv_grid:
            cell.set_fill(opacity=0.0)

        # Put original on the left, convolved on the right
        group = VGroup(original_grid, conv_grid).arrange(RIGHT, buff=2.0)
        self.add(group)

        # 5) Add labels
        original_label = Text("Original", font_size=32).next_to(original_grid, UP)
        conv_label = Text("Convolved", font_size=32).next_to(conv_grid, UP)
        self.play(Write(original_label), Write(conv_label))

        # 6) Create a 3x3 "kernel highlight" that will move across the original image
        kernel_highlight = self.create_kernel_highlight(original_grid, kernel.shape)
        self.add(kernel_highlight)

        # 7) Animate the kernel running across the image
        rows, cols = image.shape
        original_cells = original_grid.submobjects
        conv_cells = conv_grid.submobjects

        # Helper to map (row, col) -> flat index in the VGroup
        def idx(r, c):
            return r * cols + c

        # Reveal pixels one by one in row-major order
        for r in range(rows):
            for c in range(cols):
                target_index = idx(r, c)

                # Move kernel highlight to the corresponding original cell
                self.play(
                    kernel_highlight.animate.move_to(original_cells[target_index]),
                    run_time=0.03,  # a bit faster for bigger images
                )

                # Compute the color for the convolved value and fade it in
                val = np.clip(conv[r, c], 0.0, 1.0)
                color = rgb_to_color([val, val, val])

                self.play(
                    conv_cells[target_index].animate.set_fill(color, opacity=1.0),
                    run_time=0.02,
                )

        self.wait(1)

    # ---------- Helper methods ----------

    def convolve_same(self, image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """
        Manual 2D convolution with 'same' output size and zero padding.
        image: 2D array (H, W)
        kernel: 2D array (kh, kw)
        """
        H, W = image.shape
        kh, kw = kernel.shape
        pad_h = kh // 2
        pad_w = kw // 2

        # Pad image with zeros around the border
        padded = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode="constant", constant_values=0.0)

        output = np.zeros_like(image, dtype=float)

        for i in range(H):
            for j in range(W):
                region = padded[i:i + kh, j:j + kw]
                output[i, j] = np.sum(region * kernel)

        # Clip to [0, 1] just to be safe
        return np.clip(output, 0.0, 1.0)

    def grid_from_array(self, array: np.ndarray) -> VGroup:
        """
        Turn a 2D array of values in [0,1] into a grid of squares with grayscale colors.
        """
        H, W = array.shape
        grid = VGroup()

        for i in range(H):
            for j in range(W):
                val = float(array[i, j])
                val = np.clip(val, 0.0, 1.0)
                color = rgb_to_color([val, val, val])

                sq = Square()
                sq.set_fill(color, opacity=1.0)
                sq.set_stroke(WHITE, width=0.5)
                grid.add(sq)

        # Arrange cells into HxW grid
        grid.arrange_in_grid(rows=H, cols=W, buff=0)
        grid.set_height(4.0)  # scale for visibility

        return grid

    def create_kernel_highlight(self, original_grid: VGroup, kernel_shape) -> VGroup:
        """
        Create a kh x kw group of semi-transparent squares that represents the kernel region.
        It will be moved around over the original grid.
        """
        kh, kw = kernel_shape
        example_cell = original_grid[0]

        cells = VGroup()
        for _ in range(kh * kw):
            sq = Square(side_length=example_cell.width)
            sq.set_fill(color=BLUE, opacity=0.15)
            sq.set_stroke(color=BLUE, width=2.0)
            cells.add(sq)

        cells.arrange_in_grid(rows=kh, cols=kw, buff=0)
        cells.move_to(example_cell)

        return cells
