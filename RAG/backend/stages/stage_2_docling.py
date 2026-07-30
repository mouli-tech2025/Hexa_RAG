from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from pypdf import PdfReader

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.exceptions import ConversionError

""" FAA handbooks/ADs are typically digitally published with a native text
layer, not scanned images - OCR (RapidOCR) is ~50-100x slower and adds
 risk of misreads on text that's already perfect. Try fast text-layer
 extraction first; only fall back to OCR (loud, not silent) if a PDF
 turns out to actually be a scanned image with no usable text layer."""
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

""" Empirically found: a single DocumentConverter.convert() call on this
 Docling version/install can throw std::bad_alloc (a native allocator
 failure, not overall system RAM exhaustion) after roughly ~11 pages of
 work within that one call. This appears to be non-deterministic (a real
 25-page PDF failed on different, varying pages across repeated runs at
 batch size 8 - not always the same page), so even 8 pages per call is
 not consistently safe. Dropped to 4 as a larger safety margin. If this
 is revisited on a different Docling version/install, re-run the same
page-count probe before assuming 4 is still safe - and regardless of
 batch size, per-page failures are now detected and surfaced (see below)
rather than assumed away """
_PAGE_BATCH_SIZE = 4

"""If more than this fraction of a document's pages fail extraction, the
result is unmistakably incomplete - print a loud warning rather than
letting a partial document silently look like a full success."""
_FAILURE_WARNING_THRESHOLD = 0.10


@dataclass
class ExtractionResult:
    text: str
    total_pages: int
    failed_pages: List[int] = field(default_factory=list)

    @property
    def succeeded_pages(self) -> int:
        return self.total_pages - len(self.failed_pages)


def _convert_in_batches(converter: DocumentConverter, path: Path) -> ExtractionResult:
    total_pages = len(PdfReader(str(path)).pages)

    batch_texts = []
    failed_pages: List[int] = []

    for start in range(1, total_pages + 1, _PAGE_BATCH_SIZE):
        end = min(start + _PAGE_BATCH_SIZE - 1, total_pages)
        try:
            result = converter.convert(str(path), page_range=(start, end))
        except (ConversionError, Exception) as exc:
            # Some PDFs have corrupt/encrypted streams that Docling can't
            # parse at all for a given batch — record as failed pages and
            # continue instead of crashing the whole ingestion run.
            print(
                f"[stage_2_docling] ERROR: '{path.name}' pages {start}-{end} "
                f"batch conversion failed: {exc!s:.150}"
            )
            for page_no in range(start, end + 1):
                failed_pages.append(page_no)
            continue

        batch_texts.append(result.document.export_to_markdown())

        # Docling can silently drop pages within a batch on internal
        # failures (e.g. std::bad_alloc) without raising a Python
        # exception - result.status becomes PARTIAL_SUCCESS/FAILURE and
        # result.pages simply won't contain the missing page numbers.
        # Detect that here instead of assuming every requested page made
        # it into the result.
        succeeded_page_nos = {p.page_no for p in result.pages}
        for page_no in range(start, end + 1):
            if page_no in succeeded_page_nos:
                continue
            failed_pages.append(page_no)
            error_messages = [e.error_message for e in result.errors if e.page_no == page_no]
            detail = f" - {error_messages[0][:150]}" if error_messages else ""
            print(f"[stage_2_docling] ERROR: '{path.name}' page {page_no} failed extraction{detail}")

    text = "\n\n".join(batch_texts)
    return ExtractionResult(text=text, total_pages=total_pages, failed_pages=failed_pages)


def extract_faa_doc(file_path: str) -> ExtractionResult:
    path = Path(file_path)

    if path.suffix.lower() == ".txt":
        text = path.read_text(encoding="utf-8")
        return ExtractionResult(text=text, total_pages=1, failed_pages=[])

    extraction = _convert_in_batches(_converter_no_ocr, path)

    # Only attempt OCR fallback when:
    #   1. Native extraction yielded almost no text (likely a scanned PDF), AND
    #   2. The page failure rate is low (< 30%) — a high failure rate indicates a
    #      corrupt/encrypted PDF, not a scanned one. OCR cannot fix stream-level
    #      corruption, so retrying wastes minutes for the same result.
    _CORRUPT_PAGE_THRESHOLD = 0.30
    page_fail_rate = (
        len(extraction.failed_pages) / extraction.total_pages
        if extraction.total_pages
        else 0.0
    )
    if len(extraction.text.strip()) < _MIN_EXTRACTED_CHARS and page_fail_rate < _CORRUPT_PAGE_THRESHOLD:
        print(
            f"[stage_2_docling] '{path.name}': native text-layer extraction yielded only "
            f"{len(extraction.text.strip())} chars - falling back to OCR (likely a scanned PDF)."
        )
        extraction = _convert_in_batches(_converter_ocr, path)
    elif len(extraction.text.strip()) < _MIN_EXTRACTED_CHARS and page_fail_rate >= _CORRUPT_PAGE_THRESHOLD:
        print(
            f"[stage_2_docling] '{path.name}': {len(extraction.failed_pages)}/{extraction.total_pages} "
            f"pages failed ({page_fail_rate:.0%}) — likely corrupt/encrypted PDF, skipping OCR fallback."
        )

    if extraction.total_pages and len(extraction.failed_pages) / extraction.total_pages > _FAILURE_WARNING_THRESHOLD:
        print(
            f"WARNING: {path.name} - {len(extraction.failed_pages)} of {extraction.total_pages} "
            f"pages failed extraction, content is incomplete"
        )

    return extraction
