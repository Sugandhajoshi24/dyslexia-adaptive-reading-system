"""
Bionic Reading Mode — Multilingual.
Bolds the first portion of each word for faster reading.
Works with Latin, Devanagari, and Tamil scripts.

Segmentation separator (·) is preserved:
- stripped temporarily for cluster analysis
- reinserted after bionic bold is applied
- this ensures segmentation + bionic work together correctly
"""

import re

BIONIC_BOLD_RATIO = 0.4

# Devanagari marks
DEVA_MARKS = set('ािीुूृॄेैोौंःँ़ॅॉ')

# Tamil marks
TAMIL_MARKS = set('ாிீுூெேைொோௌஂஃ')

ALL_MARKS = DEVA_MARKS | TAMIL_MARKS

# Segmentation separator used by hindi_segmenter and tamil_segmenter
SEGMENTATION_SEP = '·'


def apply_bionic_reading(text, bold_ratio=None):
    """
    Apply bionic reading formatting to plain text.
    Used when only bionic is enabled (no highlighting).
    Preserves existing HTML tags.
    """
    if bold_ratio is None:
        bold_ratio = BIONIC_BOLD_RATIO

    parts = re.split(r'(<[^>]+>)', text)

    result = []
    for part in parts:
        if part.startswith('<'):
            result.append(part)
        else:
            result.append(_bionic_segment(part, bold_ratio))

    return ''.join(result)


def _bionic_segment(segment, bold_ratio):
    """Apply bionic formatting to a plain text segment."""
    if not segment.strip():
        return segment

    words = segment.split(' ')
    processed = []

    for word in words:
        if not word or not any(_is_letter(c) for c in word):
            processed.append(word)
            continue
        processed.append(_bionic_word(word, bold_ratio))

    return ' '.join(processed)


def _is_letter(c):
    """Check if character is a letter in any supported script."""
    if c.isalpha():
        return True
    if '\u0900' <= c <= '\u097F':
        return True
    if '\u0B80' <= c <= '\u0BFF':
        return True
    return False


def _is_indic(c):
    """Check if character is from an Indic script."""
    return ('\u0900' <= c <= '\u097F') or ('\u0B80' <= c <= '\u0BFF')


def _is_indic_consonant(c):
    """Check if character is a Devanagari or Tamil consonant."""
    if '\u0915' <= c <= '\u0939':
        return True
    if '\u0B95' <= c <= '\u0BB9':
        return True
    return False


def _bionic_word(word, bold_ratio):
    """
    Apply bionic to a single word token.
    Exported so processor.py can use it per-word inside
    highlight_difficult_words.

    Detects script and routes to correct handler.
    Segmentation separators (·) are preserved by each handler.
    """
    has_indic = any(_is_indic(c) for c in word)

    if has_indic:
        return _bionic_indic_word(word, bold_ratio)
    else:
        return _bionic_latin_word(word, bold_ratio)


def _bionic_latin_word(word, bold_ratio):
    """Bionic for Latin script."""
    match = re.match(
        r'^([^a-zA-Z]*)'
        r'([a-zA-Z][a-zA-Z\-]*[a-zA-Z]|[a-zA-Z])'
        r'([^a-zA-Z]*)$',
        word
    )

    if not match:
        return word

    prefix = match.group(1)
    core = match.group(2)
    suffix = match.group(3)

    if len(core) <= 1:
        return prefix + "<b>" + core + "</b>" + suffix

    bold_len = max(1, int(len(core) * bold_ratio + 0.5))
    if bold_len >= len(core):
        bold_len = len(core) - 1
    bold_len = max(1, bold_len)

    return (
        prefix
        + "<b>" + core[:bold_len] + "</b>"
        + core[bold_len:]
        + suffix
    )


def _bionic_indic_word(word, bold_ratio):
    """
    Bionic for Indic scripts (Devanagari and Tamil).

    Segmentation separators (·) are handled carefully:
    1. Detect if word contains segmentation separators
    2. Strip them temporarily for accurate cluster analysis
    3. Apply bionic bold split on clean core
    4. Reinsert separators proportionally after bold boundary

    This preserves segmentation when bionic + segmentation
    are both enabled simultaneously.
    """
    # Detect if this word was segmented (contains · separators)
    has_segmentation = SEGMENTATION_SEP in word

    # Work on clean version (no separators) for bionic analysis
    clean_word = word.replace(SEGMENTATION_SEP, '')

    match = re.match(
        r'^([^\u0900-\u097F\u0B80-\u0BFF]*)'
        r'([\u0900-\u097F\u0B80-\u0BFF]+)'
        r'([^\u0900-\u097F\u0B80-\u0BFF]*)$',
        clean_word
    )

    if not match:
        # Cannot parse — return original word unchanged
        return word

    prefix = match.group(1)
    core = match.group(2)
    suffix = match.group(3)

    clusters = _get_indic_clusters(core)

    if not clusters:
        return word

    # Single cluster — bold the whole thing
    if len(clusters) == 1:
        if has_segmentation:
            # Reinsert separators around the bolded single cluster
            return prefix + "<b>" + _reinsert_separators(word, core) + "</b>" + suffix
        return prefix + "<b>" + core + "</b>" + suffix

    bold_count = max(1, int(len(clusters) * bold_ratio + 0.5))
    if bold_count >= len(clusters):
        bold_count = len(clusters) - 1
    bold_count = max(1, bold_count)

    bold_part = ''.join(clusters[:bold_count])
    rest_part = ''.join(clusters[bold_count:])

    if has_segmentation:
        # Reinsert separators into bold and rest parts separately
        bold_part_with_sep = _reinsert_separators_partial(
            word, bold_part, is_bold_section=True
        )
        rest_part_with_sep = _reinsert_separators_partial(
            word, rest_part, is_bold_section=False
        )
        return (
            prefix
            + "<b>" + bold_part_with_sep + "</b>"
            + rest_part_with_sep
            + suffix
        )

    return (
        prefix
        + "<b>" + bold_part + "</b>"
        + rest_part
        + suffix
    )


def _reinsert_separators(original_word, core):
    """
    Reinsert segmentation separators into a single-cluster bolded word.
    Used when the entire core is bolded.
    """
    # Return the core portion of the original word with separators
    clean = original_word.replace(SEGMENTATION_SEP, '')
    core_start = clean.find(core)
    if core_start == -1:
        return core

    # Reconstruct original with separators in the core range
    result = []
    clean_idx = 0
    for ch in original_word:
        if ch == SEGMENTATION_SEP:
            result.append(ch)
        else:
            if core_start <= clean_idx < core_start + len(core):
                result.append(ch)
            clean_idx += 1

    return ''.join(result)


def _reinsert_separators_partial(original_word, part_text, is_bold_section):
    """
    Reinsert segmentation separators into bold or rest section.

    Strategy:
    - Split original word on separators to get segments
    - Count how many Indic chars are in bold_part vs rest_part
    - Assign separator-delimited chunks accordingly
    - Rejoin with separators

    This is approximate but visually correct for display.
    """
    if SEGMENTATION_SEP not in original_word:
        return part_text

    # Get the segments from the original segmented word
    # Strip any non-Indic prefix/suffix first
    indic_only = re.sub(
        r'^[^\u0900-\u097F\u0B80-\u0BFF]*'
        r'|[^\u0900-\u097F\u0B80-\u0BFF]*$',
        '',
        original_word
    )
    segments = indic_only.split(SEGMENTATION_SEP)

    if not segments:
        return part_text

    # Count Indic chars in the target part
    target_len = len(part_text)

    # Accumulate segments until we reach the target length
    accumulated = []
    char_count = 0

    if is_bold_section:
        for seg in segments:
            seg_len = len(seg)
            if char_count + seg_len <= target_len:
                accumulated.append(seg)
                char_count += seg_len
            else:
                break
        return SEGMENTATION_SEP.join(accumulated) if accumulated else part_text
    else:
        # Rest section — skip segments that belong to bold section
        # Count total bold chars first (everything before rest)
        total = sum(len(s) for s in segments)
        rest_len = len(part_text)
        bold_len = total - rest_len

        skipped = 0
        rest_segs = []
        for seg in segments:
            if skipped < bold_len:
                skipped += len(seg)
            else:
                rest_segs.append(seg)

        return SEGMENTATION_SEP.join(rest_segs) if rest_segs else part_text


def _get_indic_clusters(text):
    """Break Indic text into visual clusters (aksharas)."""
    if not text:
        return []

    clusters = []
    i = 0
    n = len(text)

    while i < n:
        cluster = text[i]
        i += 1

        while i < n:
            ch = text[i]

            if ch in ALL_MARKS:
                cluster += ch
                i += 1
                continue

            if ch == '\u094D' or ch == '\u0BCD':
                if i + 1 < n and _is_indic_consonant(text[i + 1]):
                    cluster += ch + text[i + 1]
                    i += 2
                    continue
                else:
                    cluster += ch
                    i += 1
                    continue

            break

        clusters.append(cluster)

    return clusters