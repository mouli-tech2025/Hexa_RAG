from pathlib import Path

from pypdf import PdfReader

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

# FAA handbooks/ADs are typically digitally published with a native text
# layer, not scanned images - OCR (RapidOCR) is ~50-100x slower and adds
# risk of misreads on text that's already perfect. Try fast text-layer
# extraction first; only fall back to OCR (loud, not silent) if a PDF
# turns out to actually be a scanned image with no usable text layer.
_no_ocr_options = PdfPipelineOptions(do_ocr=False)
_converter_no_ocr = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=_no_ocr_options)}
)

_ocr_options = PdfPipelineOptions(do_ocr=True)
_converter_ocr = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=_ocr_options)}
)

# Below this many non-whitespace chars, treat native extraction as having
# failed to find a text layer (i.e. the PDF is probably a scanned image).
_MIN_EXTRACTED_CHARS = 50

# Empirically found: a single DocumentConverter.convert() call on this
# Docling version/install starts throwing std::bad_alloc (a native
# allocator failure, not overall system RAM exhaustion - process RSS was
# only ~365MB when it first failed) after ~11 pages of work within that
# one call, regardless of which absolute page it starts on. 8 pages per
# call was tested clean across multiple consecutive batches. If this is
# revisited on a different Docling version/install, re-run the same
# page-count probe before assuming 8 is still safe.
_PAGE_BATCH_SIZE = 8


def _convert_in_batches(converter: DocumentConverter, path: Path) -> str:
    total_pages = len(PdfReader(str(path)).pages)

    batch_texts = []
    for start in range(1, total_pages + 1, _PAGE_BATCH_SIZE):
        end = min(start + _PAGE_BATCH_SIZE - 1, total_pages)
        result = converter.convert(str(path), page_range=(start, end))
        batch_texts.append(result.document.export_to_markdown())

    return "\n\n".join(batch_texts)


def extract_faa_doc(file_path: str) -> str:
    path = Path(file_path)

    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8")

    text = _convert_in_batches(_converter_no_ocr, path)

    if len(text.strip()) < _MIN_EXTRACTED_CHARS:
        print(
            f"[stage_2_docling] '{path.name}': native text-layer extraction yielded only "
            f"{len(text.strip())} chars - falling back to OCR (likely a scanned PDF)."
        )
        text = _convert_in_batches(_converter_ocr, path)

    return text
