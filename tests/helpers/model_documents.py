from abc import ABC, abstractmethod
from typing import Self
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import FreeText


# A generic page container to test whether functions that shuffle around pages work properly
class ModelDocument(ABC):
    @classmethod
    @abstractmethod
    def New(cls, contents: list[str]) -> Self:
        pass

    @classmethod
    @abstractmethod
    def Read(cls, source: str|Path) -> Self:
        pass

    @abstractmethod
    def save(self, path: str|Path):
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        pass

    @abstractmethod
    def __eq__(self, other: Self) -> bool:
        pass


class ModelPDF(ModelDocument):
    def __init__(self, contents: list[str]):
        self.contents = [str(content) for content in contents]

    @classmethod
    def New(cls, contents: list[str]) -> Self:
        return ModelPDF(contents)

    @classmethod
    def Read(cls, path: str|Path) -> Self:
        reader = PdfReader(path)

        contents = []
        for page in reader.pages:
            if "/Annots" not in page:
                continue

            annots = page["/Annots"]
            if len(annots) == 0:
                continue

            annot = annots[0].get_object()
            subtype = annot["/Subtype"]
            if subtype != "/FreeText":
                continue

            contents.append(annot["/Contents"])

        return ModelPDF(contents)

    def save(self, path: str|Path):
        writer = PdfWriter()
        for i, content in enumerate(self.contents):
            writer.add_blank_page(width = 100, height = 100)

            writer.add_annotation(
                page_number = i,
                annotation = FreeText(
                    text = content,
                    rect = (0, 0, 100, 100)
                )
            )

        writer.write(path)

    def is_empty(self) -> bool:
        return len(self.contents) == 0

    def __eq__(self, other: Self) -> bool:
        if not isinstance(other, ModelPDF):
            other = ModelPDF(other)

        if self.is_empty() and other.is_empty():
            return True

        return all([
            content == other_content
            for content, other_content in zip(self.contents, other.contents)
        ])

    def __repr__(self):
        return ",".join(self.contents)
