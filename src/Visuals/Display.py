import tkinter as tk


class Displayable:

    def __init__(self, shortname="unknown"):

        self.shortname = shortname
        self.parent = None

    def draw(self):

        if self.parent is None:
            return

    def create(self, frame):

        self.parent = frame


class DisplayContent:

    def __init__(self, title="TITLE"):
        self.title = title

    def displayables(self) -> list[Displayable]:
        return []

    def options(self):
        return

    def update(self):
        for obj in self.displayables():
            obj.draw()


class Display:

    def __init__(self, content: DisplayContent):

        self.content = content

        # Initialize window and set fullscreen
        self.root = tk.Tk()
        self.root.title(content.title)
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

        self.root.withdraw()

        self.create_options_frame()
        self.create_display_grid()

    def create_display_grid(self):

        # graphics frame
        graphics_frame = tk.Frame(self.root)
        graphics_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        display_figures = self.content.displayables()
        if len(display_figures) == 0:
            return

        # create first display box (left box if there are multiple)
        main_width = 1
        if len(display_figures) > 1:
            main_width = 0.5

        main_graphics_box = tk.Frame(graphics_frame)
        main_graphics_box.place(
            relx=0, rely=0,
            relwidth=main_width, relheight=1)
        display_figures[0].create(main_graphics_box)

        if len(display_figures) > 1:

            minor_graphics_box = tk.Frame(graphics_frame)
            minor_graphics_box.place(
                relx=0.5, rely=0,
                relwidth=0.5, relheight=1)
            display_figures[1].create(minor_graphics_box)

        # # matplotlib figure in left box
        # self.fig = plt.figure()
        # self.ax = self.fig.add_subplot(1, 1, 1, projection='3d')
        # self.canvas = FigureCanvasTkAgg(self.fig, master=left_graphics_box)
        # self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        #
        # # matplotlib figure in right box
        # fig2 = plt.figure()
        # ax2 = fig2.add_subplot(1, 1, 1)
        # canvas2 = FigureCanvasTkAgg(fig2, master=right_graphics_box)
        # canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_options_frame(self):
        # options frame
        options_frame = tk.Frame(self.root, height=30)
        options_frame.pack(side=tk.TOP, fill=tk.X)
        options_frame.pack_propagate(False)

        # Options
        #
        # n-config
        self.n_spinbox = tk.Spinbox(
            options_frame,
            from_=10, to=50,
            command=self._on_n_changed)
        self.n_spinbox.bind("<Return>", lambda e: self._on_n_changed())
        self.n_spinbox.pack(side=tk.LEFT)
        #
        # toggles
        complement_var = tk.BooleanVar()
        tk.Checkbutton(
            options_frame,
            text="Complement",
            variable=complement_var).pack(side=tk.LEFT)
        #
        labels_var = tk.BooleanVar()
        tk.Checkbutton(
            options_frame,
            text="Prime Labels",
            variable=labels_var).pack(side=tk.LEFT)
        #
        tk.Button(options_frame, text="Cycle Layout").pack(side=tk.LEFT)

    def _on_n_changed(self):
        new_n = int(self.n_spinbox.get())

        self.obj.change_n(new_n)

        self.obj.draw(self.ax)
        self.canvas.draw_idle()

    def show(self):
        self.content.update()

        self.root.deiconify()
        self.root.state('zoomed')
        self.root.mainloop()