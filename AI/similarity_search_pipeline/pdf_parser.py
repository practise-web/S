from langchain_community.document_loaders import PyPDFLoader
from docling.document_converter import DocumentConverter
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling_core.types.doc.document import PictureItem
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from pathlib import Path

class ArixParse:
    def __init__(self, pdf_path: str):
        self.path =  pdf_path

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


def parsePDF(path:str, outputdir, withImages = False):
    """ takes PDF file path and returns PDF parsed pages text with metadata"""
    llm_loader = PyPDFLoader(path)
    pages = llm_loader.load_and_split()
    
    if withImages:
        doc = ArixParse(pdf_path=path).parse()
        images_path = Path(outputdir) / "images"
        images_path.mkdir(exist_ok=True)

        image_counter = 0
        for element, level in doc.iterate_items():
            if isinstance(element, PictureItem):
                image_counter += 1
                img = element.get_image(doc)
                if img:
                    img_path = images_path / f"figure_{image_counter}.png"
                    img.save(img_path, "PNG")
    return pages
