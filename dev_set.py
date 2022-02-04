from configparser import ConfigParser


class Configuration:
    def __init__(self):
        config = ConfigParser()
        config.read("config.ini")
        self.frameRate = float(config.get("device", "frameRate"))
        self.exposureTime = float(config.get("device", "exposureTime"))
        self.gain = float(config.get("device", "gain"))
        self.line = config.get("device", "line")
        self.lineSource = config.get("device", "lineSource")

        self.image_format = config.get("image", "image_format")

        # Coordinates in Pixels of left upper corner of the snippet
        # As (x, y) starting from left upper corner of the original image
        self.snippet_position = (
            int(config.get("image", "snippet_position_x")),
            int(config.get("image", "snippet_position_y")),
        )

        # Size of the snippet in vertical (x-direction) and horizontal (y-direction) direction
        self.snippet_size = (
            int(config.get("image", "snippet_size_x")),
            int(config.get("image", "snippet_size_y")),
        )

    def box(self):
        """
        Builds a usable box to make the snippet and draw
        a rectangle in the original image where the snippet is cut out
        e.g. ImageDraw.draw.rectangle(Configuration.box(), outline="green", widht=2)
        """
        return (
            self.snippet_position[0],
            self.snippet_position[1],
            self.snippet_position[0] + self.snippet_size[0],
            self.snippet_position[1] + self.snippet_size[1],
        )
