import shutil
from typing import Self
from helpers.model_documents import ModelPDF
from pathlib import Path


class FileManager:
    def __init__(self, files: list[str|Path]):
        self.files = [Path(file) for file in files]

    @classmethod
    def New(cls):
        result = cls.__new__(cls)
        result.files = []
        return result

    def register(self, file: str|Path) -> Self:
        self.files.append(Path(file))
        return self

    def delete_all(self):
        for file in self.files:
            if file.is_file():
                file.unlink()
            elif file.is_dir():
                shutil.rmtree(file)

    def new_pdf(self, file: str|Path, pages: list[int]) -> ModelPDF:
        result = ModelPDF.New(pages)
        result.save(file)
        self.register(file)
        return result

    def read_pdf(self, file: str|Path) -> ModelPDF:
        self.register(file)
        return ModelPDF.Read(file)
