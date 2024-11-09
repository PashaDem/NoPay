import logging
import re
from pathlib import Path

from PIL import Image

from parsing_utils.errors import NoRegistrationSignError

logger = logging.getLogger(__name__)
PARSING_PATTERN = r"Рег\.знак:.*?\)\."


def parse_image_text(local_filename: str | Path) -> str:
    import pyocr
    import pyocr.builders

    tools = pyocr.get_available_tools()
    tool = tools[0]  # using tesseract

    img = Image.open(local_filename)

    text_from_image = tool.image_to_string(
        img, builder=pyocr.builders.TextBuilder(), lang="rus"
    )
    cleaned_text = "".join(text_from_image.splitlines())

    match = re.search(PARSING_PATTERN, cleaned_text)
    if not match:
        logger.error("Не удалось распознать регистрационный знак.")
        raise NoRegistrationSignError

    return match.group()
