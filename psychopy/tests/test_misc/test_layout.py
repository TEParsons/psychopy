import numpy
from psychopy import layout, visual


class TestVector:
    def setup(self):
        self.win = visual.Window(size=(128, 64), monitor="testMonitor")

    def teardown(self):
        self.win.close()
        del self.win

    def test_shorthand(self):
        """
        Test that units shorthand functions as intended
        """
        cases = [
            # Basic test for each shorthand
            {"inval": "1px", "inunits": "pix", "outval": 1, "outunits": "pix"},
            {"inval": "1cm", "inunits": "cm", "outval": 1, "outunits": "cm"},
            {"inval": "1h", "inunits": "height", "outval": 1, "outunits": "height"},
            {"inval": "1n", "inunits": "norm", "outval": 1, "outunits": "norm"},
            {"inval": "1d", "inunits": "deg", "outval": 1, "outunits": "deg"},
            # Value types
            {"inval": "1.5px", "inunits": "pix", "outval": 1.5, "outunits": "pix"},
            {"inval": "Nonepx", "inunits": "pix", "outval": None, "outunits": "pix"},
            # Cross-unit override
            {"inval": "Nonepx", "inunits": "norm", "outval": None, "outunits": "pix"},
            {"inval": "Nonen", "inunits": "pix", "outval": None, "outunits": "norm"},
        ]

        for case in cases:
            # Check pure shorthand parsing function
            val, units = layout.interpretShorthand(case['inval'])
            assert val == case['outval'], (
                f"{case['inval']} should give {case['outval']}, but instead gave {val}.")
            assert units == case['outunits'], (
                f"{case['inval']} should give units {case['outunits']}, but instead gave {units}.")
            # Create Vector object from given string and units
            actual = layout.Vector(case['inval'], units=case['inunits'], win=self.win)
            # Create target vector
            target = layout.Vector(case['outval'], units=case['outunits'], win=self.win)
            # Check vector objects are the same value
            assert actual == target

    def test_values(self):
        """
        Check that Vector objects with various values return as intended in a variety of unit spaces.
        """
        # List of objects with their intended values in various spaces
        cases = [
            # (1, 1) height
            (layout.Vector((1, 1), 'height', self.win),
             {'pix': (64, 64), 'height': (1, 1), 'norm': (1, 2), 'cm': (1.875, 1.875)}),
            # (1, 1) norm
            (layout.Vector((1, 1), 'norm', self.win),
             {'pix': (64, 32), 'height': (1, 0.5), 'norm': (1, 1), 'cm': (1.875, 0.9375)}),
            # (1, 1) pix
            (layout.Vector((1, 1), 'pix', self.win),
             {'pix': (1, 1), 'height': (1/64, 1/64), 'norm': (1/64, 1/32), 'cm': (1.875/64, 1.875/64)}),
            # (1, 1) cm
            (layout.Vector((1, 1), 'cm', self.win),
             {'pix': (64/1.875, 64/1.875), 'height': (1/1.875, 1/1.875), 'norm': (1/1.875, 1/0.9375), 'cm': (1, 1)}),
            # Check ratio of pt to cm
            (layout.Vector(1, 'pt', self.win),
             {'pt': 1, 'cm': 0.03527778}),
            # Negative values
            (layout.Vector((-1, -1), 'height', self.win),
             {'pix': (-64, -64), 'height': (-1, -1), 'norm': (-1, -2), 'cm': (-1.875, -1.875)}),
        ]

        # Check that each object returns the correct value in each space specified
        for obj, ans in cases:
            for space in ans:
                # Convert both value and answer to numpy arrays and round to 5dp
                val = numpy.array(getattr(obj, space)).round(5)
                thisAns = numpy.array(ans[space]).round(5)
                # Check that they match
                assert (val == thisAns).all(), (
                    f"Vector of {obj._requested} in {obj._requestedUnits} should return {ans[space]} in {space} units, "
                    f"but instead returned {val}"
                )
