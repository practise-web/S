from docling.document_converter import DocumentConverter
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling_core.types.doc.document import PictureItem
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions
)
from pathlib import Path


class ArixParse:
    def __init__(self, pdf_path: str):
        self.path = pdf_path
        
        accelerator_options = AcceleratorOptions(
            num_threads=8,
            device=AcceleratorDevice.CUDA 
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
    output_path = Path(output_folder)
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
    fileName = Path(pdf).name
    output_dir = Path("output") / fileName
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(f"output/{fileName}/text.md", "w", encoding="utf-8") as f:
        f.write(doc.export_to_markdown())
    save_extracted_images(doc, str(output_dir / "extracted_images"))

