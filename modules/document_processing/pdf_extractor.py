"""
Smart PDF text extraction for academic papers and books.

Uses PyMuPDF with word-level extraction and gap-based column detection.
"""

import re
from collections import Counter


def extract_text_from_pdf(uploaded_file):
    """
    Extract clean, properly-ordered text from a PDF.
    Handles multi-column, headers, footers, page numbers.
    """
    try:
        import fitz
    except ImportError:
        raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")

    pdf_bytes = uploaded_file.read()
    uploaded_file.seek(0)

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    if doc.page_count == 0:
        return None

    all_pages_text = []
    header_candidates = []
    footer_candidates = []

    for page_num in range(doc.page_count):
        page = doc[page_num]
        page_height = page.rect.height
        page_width = page.rect.width

        header_limit = page_height * 0.08
        footer_limit = page_height * 0.92

        # Get word-level data
        words = page.get_text("words")

        if not words:
            continue

        header_words = []
        footer_words = []
        body_words = []

        for w in words:
            x0, y0, x1, y1 = w[0], w[1], w[2], w[3]

            if y0 < header_limit:
                header_words.append(w)
            elif y1 > footer_limit:
                footer_words.append(w)
            else:
                body_words.append(w)

        if header_words:
            h_text = " ".join(hw[4] for hw in sorted(header_words, key=lambda w: w[0]))
            header_candidates.append(h_text.strip())

        if footer_words:
            f_text = " ".join(fw[4] for fw in sorted(footer_words, key=lambda w: w[0]))
            footer_candidates.append(f_text.strip())

        if not body_words:
            continue

        page_text = _extract_with_columns(body_words, page_width)
        all_pages_text.append(page_text)

    doc.close()

    if not all_pages_text:
        return None

    raw_text = "\n\n".join(all_pages_text)

    # Remove repeating headers/footers
    total_pages = len(all_pages_text)
    min_repeats = max(2, int(total_pages * 0.4))

    for h_text, count in Counter(header_candidates).items():
        if count >= min_repeats and h_text:
            raw_text = raw_text.replace(h_text, "")

    for f_text, count in Counter(footer_candidates).items():
        if count >= min_repeats and f_text:
            raw_text = raw_text.replace(f_text, "")

    cleaned = _clean_pdf_text(raw_text)
    return cleaned if cleaned.strip() else None


def _extract_with_columns(body_words, page_width):
    """
    Core column extraction logic.

    Strategy:
    1. First determine if the page is multi-column by checking
       if there's a consistent vertical gap in x-positions
    2. If multi-column: split ALL words into left/right groups by x-position
    3. Within each group, sort by y then x to get reading order
    4. Read left group fully, then right group fully
    """
    if not body_words:
        return ""

    # Step 1: Detect columns by finding a vertical gap
    is_multi, split_x = _detect_column_gap(body_words, page_width)

    if not is_multi:
        # Single column — sort by y then x
        sorted_words = sorted(body_words, key=lambda w: (w[1], w[0]))
        return _words_to_text(sorted_words)

    # Step 2: Split words into left and right columns
    left_words = []
    right_words = []

    for w in body_words:
        word_center_x = (w[0] + w[2]) / 2

        if word_center_x < split_x:
            left_words.append(w)
        else:
            right_words.append(w)

    # Step 3: Sort each column by y then x
    left_words.sort(key=lambda w: (w[1], w[0]))
    right_words.sort(key=lambda w: (w[1], w[0]))

    # Step 4: Convert to text — left column fully, then right
    left_text = _words_to_text(left_words)
    right_text = _words_to_text(right_words)

    parts = []
    if left_text.strip():
        parts.append(left_text.strip())
    if right_text.strip():
        parts.append(right_text.strip())

    return " ".join(parts)


def _detect_column_gap(words, page_width):
    """
    Detect if there's a multi-column layout by finding a vertical gap.

    Looks at the x-positions of all words and checks if there's a
    significant gap (empty space) in the middle of the page where
    no words exist — that's the column gutter.

    Returns (is_multi_column, split_x_position)
    """
    if len(words) < 6:
        return False, 0

    # Collect all word x-ranges
    # Build a coverage map of x-positions
    x_min = min(w[0] for w in words)
    x_max = max(w[2] for w in words)
    total_x_range = x_max - x_min

    if total_x_range < 100:
        return False, 0

    # Create bins across the page width
    num_bins = 100
    bin_width = page_width / num_bins
    bins = [0] * num_bins

    for w in words:
        start_bin = max(0, int(w[0] / bin_width))
        end_bin = min(num_bins - 1, int(w[2] / bin_width))
        for b in range(start_bin, end_bin + 1):
            bins[b] += 1

    # Find the largest gap (consecutive empty or near-empty bins)
    # in the middle 60% of the page
    search_start = int(num_bins * 0.2)
    search_end = int(num_bins * 0.8)

    best_gap_start = -1
    best_gap_end = -1
    best_gap_size = 0

    current_gap_start = -1

    for i in range(search_start, search_end):
        if bins[i] <= 1:  # empty or nearly empty bin
            if current_gap_start == -1:
                current_gap_start = i
        else:
            if current_gap_start != -1:
                gap_size = i - current_gap_start
                if gap_size > best_gap_size:
                    best_gap_size = gap_size
                    best_gap_start = current_gap_start
                    best_gap_end = i
                current_gap_start = -1

    # Check last gap
    if current_gap_start != -1:
        gap_size = search_end - current_gap_start
        if gap_size > best_gap_size:
            best_gap_size = gap_size
            best_gap_start = current_gap_start
            best_gap_end = search_end

    # Gap must be at least 3% of page width to be a column gutter
    min_gap_bins = max(2, int(num_bins * 0.03))

    if best_gap_size >= min_gap_bins:
        split_x = (best_gap_start + best_gap_end) / 2 * bin_width

        # Verify: both sides need enough words
        left_count = sum(1 for w in words if (w[0] + w[2]) / 2 < split_x)
        right_count = sum(1 for w in words if (w[0] + w[2]) / 2 >= split_x)

        if left_count >= 5 and right_count >= 5:
            return True, split_x

    return False, 0


def _words_to_text(sorted_words):
    """
    Convert a sorted list of word tuples into readable text.
    Groups words into lines based on y-proximity,
    then merges lines into paragraphs.
    """
    if not sorted_words:
        return ""

    # Group into lines by y-position
    lines = []
    current_line = [sorted_words[0]]
    current_y = sorted_words[0][1]

    y_tolerance = 4  # pixels — words within this are same line

    for w in sorted_words[1:]:
        if abs(w[1] - current_y) <= y_tolerance:
            current_line.append(w)
        else:
            # Sort current line left to right
            current_line.sort(key=lambda w: w[0])
            line_text = " ".join(w[4] for w in current_line)
            lines.append(line_text)

            current_line = [w]
            current_y = w[1]

    # Last line
    if current_line:
        current_line.sort(key=lambda w: w[0])
        line_text = " ".join(w[4] for w in current_line)
        lines.append(line_text)

    # Merge lines into paragraphs
    return _merge_lines(lines)


def _merge_lines(lines):
    """Merge text lines, joining broken sentences."""
    if not lines:
        return ""

    merged = []
    buffer = ""

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if buffer:
                merged.append(buffer)
                buffer = ""
            continue

        if buffer:
            if buffer[-1] in '.!?:;")\u201d\u2019':
                merged.append(buffer)
                buffer = stripped
            else:
                buffer += " " + stripped
        else:
            buffer = stripped

    if buffer:
        merged.append(buffer)

    return " ".join(merged)


def _clean_pdf_text(text):
    """Clean extracted PDF text."""
    text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)
    text = re.sub(r'^\s*\d{1,4}\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'(?i)\s*pg\.?\s*\d+\s*', ' ', text)
    text = re.sub(r'(?i)\s*page\s+\d+(\s+of\s+\d+)?\s*', ' ', text)
    text = re.sub(r'(?i)^\s*©.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()