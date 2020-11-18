from builtins import object
from psychopy import visual, event
from psychopy.visual import Window
from psychopy.visual import TextBox2

import pytest

# cd psychopy/psychopy
# py.test -k textbox --cov-report term-missing --cov visual/textbox

@pytest.mark.textbox
class Test_textbox(object):
    def setup_class(self):
        self.win = Window([128,128], pos=[50,50], allowGUI=False, autoLog=False)

    def teardown_class(self):
        self.win.close()

    def test_unicode(self):
        textbox = TextBox2(self.win, "", "Arial")
        text = ""
        for encoding in ['utf-8', 'utf-16']:
            for asDecimal in range(143859):
                # Add each unicode character to the data file
                try:
                    chr(asDecimal).encode(encoding)
                except UnicodeEncodeError:
                    # Skip if not a valid unicode
                    continue
                text += chr(asDecimal)

            # Set textbox
            textbox.text = text
            textbox.draw()

    def test_basic(self):
        pass

    def test_something(self):
        # to-do: test visual display, char position, etc
        pass
