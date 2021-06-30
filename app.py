import cv2
import numpy as np
from MathRect import MathRect


def click_event(event, x, y, flags, param):
    global is_selecting, rectangle_start, rectangle_end, frame, toggle_menu
    for idx, eq in enumerate(math_equations):
        toggle_menu[idx] = 1 if eq.is_pt_in((x, y)) else 0
    if event == cv2.EVENT_LBUTTONDOWN:
        the_click_is_not_for_rect = False
        for idx, eq in enumerate(math_equations):
            if eq.is_pt_in((x, y)):
                toggle_menu[idx] = 2
                the_click_is_not_for_rect = True
        if not the_click_is_not_for_rect:
            rectangle_start = [x, y]
            is_selecting = True
    elif event == cv2.EVENT_MOUSEMOVE:
        if is_selecting:
            rectangle_end = [x, y]
    elif event == cv2.EVENT_LBUTTONUP:
        if is_selecting:
            math_equations.append(MathRect(rectangle_start, rectangle_end, frame[rectangle_start[1]: rectangle_end[1], rectangle_start[0]: rectangle_end[0]], is_simple=is_simple))
            toggle_menu.append(0)
            rectangle_start, rectangle_end = None, None
            is_selecting = False


math_equations = []
toggle_menu = []
is_selecting = False
rectangle_start = None
rectangle_end = None
frame = canvas = None

video_path = './photos/video_plot_eq.mp4'
is_simple = False
cam = cv2.VideoCapture(video_path)
cv2.namedWindow("Output", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Output", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.setMouseCallback("Output", click_event)

while True:
    if not is_selecting:
        ret, frame = cam.read()
        canvas = frame.copy()
        for eq, tog in zip(math_equations, toggle_menu):
            init_coord = eq.init_coord
            end_coord = eq.end_coord
            cv2.rectangle(canvas, init_coord, end_coord, (0, 255, 0) if tog == 0 else (255, 0, 0), 5)
            if tog == 1:
                cv2.putText(canvas, eq.text, (init_coord[0], init_coord[1] - 10), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
            elif tog == 2:
                whiteboard = (np.ones((500, 500, 3)) * 255).astype('uint8')
                cv2.putText(whiteboard, eq.text, (15, 55), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)
                cv2.putText(whiteboard, "Solution:", (15, 125), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
                cv2.putText(whiteboard, eq.sol_form, (15, 160), cv2.FONT_HERSHEY_SIMPLEX, 1., (0, 0, 0), 2)
                if not eq.is_simple:
                    plot_image = eq.plot_image
                    plot_image = cv2.resize(plot_image, (500, 300))
                    whiteboard[-plot_image.shape[0]:, :] = plot_image
                whiteboard = cv2.copyMakeBorder(whiteboard, top=10, bottom=10, left=10, right=10, borderType=cv2.BORDER_CONSTANT, value=[100, 100, 100])
                canvas[init_coord[1]: init_coord[1]+whiteboard.shape[0], end_coord[0]: end_coord[0]+whiteboard.shape[1]] = whiteboard
        cv2.imshow("Output", canvas)
    else:
        black = np.zeros_like(frame)
        darker_frame = cv2.addWeighted(frame, 0.4, black, 0.6, 1)
        if rectangle_start is not None and rectangle_end is not None:
            cut = frame[rectangle_start[1]: rectangle_end[1], rectangle_start[0]: rectangle_end[0]]
            darker_frame[rectangle_start[1]: rectangle_end[1], rectangle_start[0]: rectangle_end[0]] = cut
        cv2.imshow("Output", darker_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cv2.destroyAllWindows()
cam.release()
