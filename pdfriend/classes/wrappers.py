import pypdf
from typing import Self
from PIL import Image

class PDFWrapper:
    def __init__(self, pages: list[pypdf.PageObject] = None):
        self.pages = [] if pages is None else pages

    @classmethod
    def Read(cls, filename: str):
        pdf = pypdf.PdfReader(filename)

        return PDFWrapper(pages=list(pdf.pages))
    
    def len(self):
        return len(self.pages)

    def rotate_page(self, page_idx: int, angle: float) -> Self:
        rotation = pypdf.Transformation.rotate(angle)

        self.pages[page_idx].add_transformation(rotation)

        return self

    def pop_page(self, page_idx: int) -> pypdf.PageObject:
        return self.pages.pop(page_idx)

    def merge_with(self, other: Self) -> Self:
        self.pages.extend(other.pages)

        return self

    def invert(self) -> Self:
        self.pages = self.pages[::-1]

        return self

    # def interlace(self, other: Self) -> Self:
    #     return PDFWrapper()

    def write(self, filename: str):
        writer = pypdf.PdfWriter()

        for page in self.pages:
            writer.add_page(page)

        writer.write(filename)


def convert_to_rgb(img_rgba: Image.Image):
    try:
        img_rgba.load()
        _, _, _, alpha = img_rgba.split()

        img_rgb = Image.new("RGB", img_rgba.size, (255, 255, 255))
        img_rgb.paste(img_rgba, mask=alpha)

        return img_rgb
    except (IndexError, ValueError):
        return img_rgba


class ImageWrapper:
    def __init__(self, images: list[Image.Image]):
        self.images = [convert_to_rgb(image) for image in images]

    @classmethod
    def FromFiles(cls, filenames: list[str]) -> Self:
        return ImageWrapper([Image.open(filename) for filename in filenames])

    def equalize_widths(self):
        max_width = max([image.size[0] for image in self.images])

        for i, image in enumerate(self.images):
            width, height = image.size

            scale = max_width / width

            self.images[i] = image.resize((max_width, int(height * scale)))

    def write(self, outfile: str, quality: int | float):
        self.images[0].save(
            outfile,
            "PDF",
            optimize=True,
            quality=int(quality),
            save_all=True,
            append_images=self.images[1:],
        )
