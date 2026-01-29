from docling.document_converter import DocumentConverter
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling_core.types.doc.document import PictureItem
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from pathlib import Path
from werkzeug.utils import secure_filename
import os
import logging

logger = logging.getLogger("app.services.docling")
SAFE_BASE_DIR = Path("output").resolve()


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
        self.pipeline_options.ocr_options.lang = ["en"]
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



def parse_pdf(pdf: str):
    doc = ArixParse(pdf_path=pdf).parse()

    fileName = secure_filename(Path(pdf).name)
    output_dir = (SAFE_BASE_DIR / fileName).resolve()
    if not output_dir.is_relative_to(SAFE_BASE_DIR):
        logging.error(
            f"Security Warning: Attempted to save outside '{SAFE_BASE_DIR}'"
        )
        raise ValueError(
            f"Security Warning: Attempted to save outside '{SAFE_BASE_DIR}'"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "text.md", "w", encoding="utf-8") as f:
        f.write(doc.export_to_markdown())
    
    # Save extracted images
    images_path = (output_dir / "extracted_images").resolve()
    images_path.mkdir(parents=True, exist_ok=True)
    image_counter = 0
    for element, _ in doc.iterate_items():
        if isinstance(element, PictureItem):
            image_counter += 1
            # 1. Extract the image object
            image_obj = element.get_image(doc)

            if image_obj:
                # 2. Save it to disk
                filename = f"figure_{image_counter}.png"
                save_path = images_path / filename
                image_obj.save(save_path, "PNG")

                logger.debug(f"Saved extracted image to: {save_path}")
    logger.info(f"Document parsed and saved to: {output_dir}")
