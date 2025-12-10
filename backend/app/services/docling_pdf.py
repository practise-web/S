from docling.document_converter import DocumentConverter
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling_core.types.doc.document import PictureItem
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from pathlib import Path
from werkzeug.utils import secure_filename
import os

SAFE_BASE_DIR = Path("output").resolve()


def is_safe_path(base_dir: Path, path: Path) -> bool:
    """
    Check if `path` is strictly contained within `base_dir` after resolving both.
    """
    try:
        return path.is_relative_to(base_dir)
    except AttributeError:
        return str(path).startswith(str(base_dir))


def safe_filename(filename: str) -> str:
    # Only get the basename, remove any remaining path separators, keep ascii chars only
    return os.path.basename(filename).replace("/", "_").replace("\\", "_")


class ArixParse:
    def __init__(self, pdf_path: str):
        self.path = pdf_path

        accelerator_options = AcceleratorOptions(
            num_threads=8, device=AcceleratorDevice.CUDA
        )
        self.pipeline_options = PdfPipelineOptions()
        self.pipeline_options.accelerator_options = accelerator_options

        self.pipeline_options.do_ocr = False
        self.pipeline_options.do_table_structure = True
        self.pipeline_options.ocr_options.lang = ["eg"]
        self.pipeline_options.images_scale = 2.0
        self.pipeline_options.generate_page_images = False
        self.pipeline_options.generate_picture_images = True
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=self.pipeline_options)
            }
        )

    def parse(self):
        return self.converter.convert(self.path).document


def save_extracted_images(doc, output_folder: str):
    output_folder_name = safe_filename(output_folder)
    output_path = (SAFE_BASE_DIR / output_folder_name).resolve()

    if not is_safe_path(SAFE_BASE_DIR, output_path):
        raise ValueError(
            f"Security Warning: Attempted to save outside '{SAFE_BASE_DIR}'"
        )

    output_path.mkdir(parents=True, exist_ok=True)

    image_counter = 0

    for element, _ in doc.iterate_items():
        if isinstance(element, PictureItem):
            image_counter += 1
            # 1. Extract the image object
            image_obj = element.get_image(doc)

            if image_obj:
                # 2. Save it to disk
                filename = f"figure_{image_counter}.png"
                save_path = output_path / filename
                image_obj.save(save_path, "PNG")

                print(f"Saved: {save_path}")


def runPDF(pdf: str):
    doc = ArixParse(pdf_path=pdf).parse()

    fileName = secure_filename(Path(pdf).name)
    output_dir = (SAFE_BASE_DIR / fileName).resolve()
    if not output_dir.is_relative_to(SAFE_BASE_DIR):
        raise ValueError(
            f"Security Warning: Attempted to save outside '{SAFE_BASE_DIR}'"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "text.md", "w", encoding="utf-8") as f:
        f.write(doc.export_to_markdown())
    save_extracted_images(doc, str(output_dir / "extracted_images"))
