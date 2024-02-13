from psychopy import core, event, visual, monitors
import os, random, datetime, pathlib, itertools

PRESENTATION_TIME = 5 # time during which targets are shown (NOTE: pair-condition gets double) in seconds
AMOUNT_TARGETS = 3 # amount targets to remember
TRIALS_PER_BLOCK = 25 # amount of trials within each block
LOGFILE_PATH = os.path.join(pathlib.Path(__file__).parent.absolute(), "results.csv")

class Experiment:
    def __init__(self):
        with open("fruits.txt", "r") as file:
            self.wordbank = file.read().splitlines()
        self.numberbank = [str(i) for i in range(10, 100) if i % 10]
        self.combinations = [f"{word}{' ' * (20 - len(word) - 2)}{number}" for word, number in itertools.product(self.wordbank, self.numberbank)]

        self.rand = random.Random()
        self.stopwatch = core.Clock()
        self.setup_window()
        self.menu_page()

    def setup_window(self):
        self.window = visual.Window(color = "#050505", fullscr = False, size=(1080, 720), monitor = "MainMonitor")

        self.background = visual.rect.Rect(self.window, size=3)
        self.background.draw()
        self.set_background_color("#050505")

        self.instructions = visual.TextStim(self.window, "", font = "Consolas")

        self.window.flip()

    def setup_monitor(self):
        monitors.Monitor("MainMonitor").save()

    def menu_page(self):
        self.set_background_color("#050505")
        self.set_instruction_text("EEG Recognition Task")
        self.window.flip()

        core.wait(1.5)

        self.get_ready()

    def get_ready(self):
        self.set_instruction_text("For each trial,\npress LEFT/RIGHT to indicate whether the item was in the list.\n\n" + "not in list: ←LEFT\n" + " was in list: RIGHT→" +  "\n\n" + "Press SPACE to proceed")
        self.window.flip()
        event.waitKeys(keyList = ["space"])[0]

        self.set_instruction_text("")
        self.window.flip()

        self.run_blocks()
        self.show_credits()

    def set_background_color(self, color):
        self.background.color = color
        self.background.draw()

    def set_instruction_text(self, text):
        self.instructions.text = text
        self.instructions.draw()

    def present_targets(self, presentation_duration):
        self.set_background_color("grey")
        target_delimiter = "\n\n"
        # target_delimiter = f"\n{'—' * 20}\n"
        self.set_instruction_text(target_delimiter.join(self.targets))
        self.window.flip()
        core.wait(presentation_duration)

    def present_trial(self, block, trial, item):
        self.set_instruction_text(item)
        self.window.flip()
        self.stopwatch.reset()
        response = "congruent" if event.waitKeys(keyList = ["left", "right"])[0] == "right" else "incongruent"
        response_time = self.stopwatch.getTime()
        self.log_result(
            block = block, 
            trial = trial, 
            response_time = response_time,
            target_response = "congruent" if item in self.targets else "incongruent",
            response = response,
        )

    def run_blocks(self):
        for stage, item_list in zip(("word", "number", "pair"), (self.wordbank, self.numberbank, self.combinations)):
            self.set_background_color("grey")
            self.set_instruction_text("Get ready")
            self.window.flip()
            core.wait(1)
            self.block(stage, item_list)

    def block(self, stage, items):
        self.targets = self.rand.sample(items, AMOUNT_TARGETS)
        self.selected_items = self.rand.sample(items, TRIALS_PER_BLOCK - AMOUNT_TARGETS) + self.targets
        self.rand.shuffle(self.selected_items)

        self.present_targets(PRESENTATION_TIME * 2 if stage == "pair" else PRESENTATION_TIME)

        for trial, item in enumerate(self.selected_items, start=1):
            self.present_trial(
                block = stage,
                trial = trial,
                item = item,
            )

    def show_credits(self):
        self.set_background_color("grey")
        self.set_instruction_text("This concludes the experiment.")
        self.window.flip()
        core.wait(2)

    def log_result(self, block, trial, response_time, target_response, response):
        if not os.path.isfile(LOGFILE_PATH):
            with open(LOGFILE_PATH, "w") as file:
                file.write("timestamp,block,trial,response_time,target_response,response")
        with open(LOGFILE_PATH, "a") as file:
            file.write(f"\n{datetime.datetime.now()},{block},{trial},{response_time},{target_response},{response}")

if __name__ == "__main__":
    print(f"[INITIATED] {datetime.datetime.now()}")
    Experiment()
    print(f"[CONCLUDED] {datetime.datetime.now()}")