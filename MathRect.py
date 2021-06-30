import uuid

import numpy as np
import pytesseract
from sympy import Symbol, Eq, solve, plotting, simplify
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


correct_dict = {'—': '-', 'T': '7', 'a': 'x', '?': '^2', 'I': '2', 'r': 'x'}
correct_op = ['*', '-', '+', '/', '=']


class MathRect:
    def __init__(self, init_coord, end_coord, image, is_simple):
        self.is_simple = is_simple
        self.init_coord = init_coord
        self.end_coord = end_coord
        self.image = image
        self.id = str(uuid.uuid4())
        self.text = pytesseract.image_to_string(image[:, :, ::-1]).rstrip()
        self.text = self._correct_text(self.text)
        if self.is_simple:
            self.unknown = self._get_unknown(self.text)

        self.equation = self._format_text(self.text)

        x = Symbol('x')
        if not is_simple:
            y = Symbol('y')
            f = Eq(eval(self.equation[0]), eval(self.equation[1]))
            self.sol = solve(f, y)
            self.sol_form = str(simplify(self.sol[0]))

            x = np.linspace(-100, 100, 1000)
            fig = Figure()
            canvas = FigureCanvas(fig)
            ax = fig.gca()
            ax.margins(x=0.1, y=0.1)
            ax.set_title(self.sol_form + ' = y')
            ax.plot(x, eval(self.sol_form))
            ax.grid()
            canvas.draw()
            self.plot_image = np.frombuffer(canvas.tostring_rgb(), dtype='uint8')
            size = fig.get_size_inches() * fig.dpi
            self.plot_image = self.plot_image.reshape((int(size[1]), int(size[0]), 3))
            self.sol_form = str(simplify(self.sol[0])) + ' = y'
        else:
            f = Eq(eval(self.equation[0]), eval(self.equation[1]))
            self.sol = solve(f, x)
            self.sol_form = 'x = ' + str(self.sol)

    def is_pt_in(self, pt):
        return self.init_coord[0] <= pt[0] <= self.end_coord[0] and self.init_coord[1] <= pt[1] <= self.end_coord[1]

    @staticmethod
    def _get_unknown(text):
        unknown = ''
        for c in text:
            if c in correct_op or c.isdigit():
                continue
            if unknown == '':
                unknown = c
                continue
            if c != unknown:
                print("Something is wrong...", unknown, c)
        return unknown

    @staticmethod
    def _correct_text(text):
        new_text = ""
        for c in text:
            v = correct_dict.get(c)
            if v is None:
                new_text += c
            else:
                new_text += v
        return new_text.replace(' ', '')

    def _format_text(self, text):
        if self.is_simple:
            text = text.replace(self.unknown, 'x')
        text = text.replace('^', '**')
        unknown_idx = [i for i in range(len(text)) if text.startswith('x', i)]
        idx_offset = 0
        for idx in unknown_idx:
            idx += idx_offset
            if idx == 0 or text[idx-1] in correct_op:
                continue
            text = text[:idx] + '*' + text[idx:]
            idx_offset += 1
        if not self.is_simple:
            unknown_idx = [i for i in range(len(text)) if text.startswith('y', i)]
            idx_offset = 0
            for idx in unknown_idx:
                idx += idx_offset
                if idx == 0 or text[idx - 1] in correct_op:
                    continue
                text = text[:idx] + '*' + text[idx:]
                idx_offset += 1
        return text.split('=')


if __name__ == '__main__':
    m = MathRect(None, None, None, is_simple=False)
