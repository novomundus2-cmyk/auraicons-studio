"""Exercise the note-agent image dependencies offline with synthetic data."""

import contextlib
import io
import unittest

import note_agent
from matplotlib.figure import Figure
from PIL import Image


class NoteAgentEnvironmentTests(unittest.TestCase):
    def test_entry_point_and_image_roundtrip(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            note_agent.main()
        self.assertIn("Hello from note-agent!", output.getvalue())

        figure = Figure()
        axis = figure.subplots()
        try:
            axis.plot([0, 1, 2], [0, 1, 4])
            buffer = io.BytesIO()
            figure.savefig(buffer, format="png")
            buffer.seek(0)
            with Image.open(buffer, formats=["PNG"]) as image:
                image.load()
                self.assertEqual(image.format, "PNG")
                self.assertGreater(image.width, 0)
                self.assertGreater(image.height, 0)
        finally:
            figure.clear()


if __name__ == "__main__":
    unittest.main()
