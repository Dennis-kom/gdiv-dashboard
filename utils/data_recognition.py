from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd
from PIL import Image, ImageFilter, ImageOps

try:
	import pytesseract
except ImportError:  # pragma: no cover - handled at runtime for missing optional dependency
	pytesseract = None


LOG_DIR = Path(__file__).resolve().parents[1] / "logging"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)
if not logger.handlers:
	file_handler = logging.FileHandler(LOG_DIR / "data_recognition.log", encoding="utf-8")
	file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
	logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
logger.propagate = False


def _cluster_positions(values: list[float], tolerance: int) -> list[float]:
	logger.info(" > LOG:: Enter _cluster_positions with %d values and tolerance=%d", len(values), tolerance)
	if not values:
		logger.info(" > LOG:: _cluster_positions received no values")
		return []

	centers = [values[0]]
	for value in values[1:]:
		if abs(value - centers[-1]) <= tolerance:
			centers[-1] = (centers[-1] + value) / 2
		else:
			centers.append(value)
	logger.info(" > LOG:: _cluster_positions produced %d centers", len(centers))
	return centers


def _nearest_cluster(value: float, clusters: list[float]) -> int:
	idx = min(range(len(clusters)), key=lambda idx: abs(clusters[idx] - value))
	logger.info(" > LOG:: _nearest_cluster selected index=%d", idx)
	return idx


def _make_unique_headers(raw_headers: list[str]) -> list[str]:
	logger.info(" > LOG:: Enter _make_unique_headers with %d headers", len(raw_headers))
	seen: dict[str, int] = {}
	headers: list[str] = []

	for idx, value in enumerate(raw_headers, start=1):
		header = (value or "").strip() or f"column_{idx}"
		count = seen.get(header, 0) + 1
		seen[header] = count
		headers.append(header if count == 1 else f"{header}_{count}")

	logger.info(" > LOG:: _make_unique_headers completed")
	return headers


def _prepare_image_for_ocr(image: Image.Image) -> Image.Image:
	logger.info(" > LOG:: Start image preprocessing")
	gray = ImageOps.grayscale(image)
	denoised = gray.filter(ImageFilter.MedianFilter(size=3))
	enhanced = ImageOps.autocontrast(denoised)
	# Binary threshold usually improves OCR on scanned forms and screenshots.
	result = enhanced.point(lambda x: 0 if x < 160 else 255, mode="1")
	logger.info(" > LOG:: Image preprocessing completed")
	return result


def _tokens_to_dataframe(tokens: list[dict[str, Any]], row_tolerance: int, col_tolerance: int) -> pd.DataFrame:
	logger.info(
		" > LOG:: Enter _tokens_to_dataframe with tokens=%d row_tolerance=%d col_tolerance=%d",
		len(tokens),
		row_tolerance,
		col_tolerance,
	)
	if not tokens:
		logger.info(" > LOG:: No tokens available, returning empty DataFrame")
		return pd.DataFrame()

	row_positions = sorted(token["top"] + token["height"] / 2 for token in tokens)
	col_positions = sorted(token["left"] + token["width"] / 2 for token in tokens)

	row_centers = _cluster_positions(row_positions, tolerance=row_tolerance)
	col_centers = _cluster_positions(col_positions, tolerance=col_tolerance)
	logger.info(" > LOG:: Calculated row_centers=%d col_centers=%d", len(row_centers), len(col_centers))

	grid: dict[int, dict[int, list[tuple[int, str]]]] = {}
	for token in tokens:
		row_idx = _nearest_cluster(token["top"] + token["height"] / 2, row_centers)
		col_idx = _nearest_cluster(token["left"] + token["width"] / 2, col_centers)
		grid.setdefault(row_idx, {}).setdefault(col_idx, []).append((token["left"], token["text"]))

	rows: list[list[str]] = []
	for row_idx in sorted(grid):
		row: list[str] = []
		for col_idx in range(len(col_centers)):
			cell_tokens = sorted(grid[row_idx].get(col_idx, []), key=lambda item: item[0])
			row.append(" ".join(text for _, text in cell_tokens).strip())
		rows.append(row)

	while rows and not any(rows[-1]):
		rows.pop()

	if not rows:
		logger.info(" > LOG:: Rows are empty after cleanup, returning empty DataFrame")
		return pd.DataFrame()

	columns = [f"column_{idx + 1}" for idx in range(len(rows[0]))]
	df = pd.DataFrame(rows, columns=columns)
	logger.info(" > LOG:: _tokens_to_dataframe created DataFrame shape=%s", df.shape)
	return df


def _show_ocr_not_available_error() -> None:
	"""Display a user-friendly error message when OCR is not available."""
	logger.info(" > LOG:: OCR dependency is not available")
	try:
		import streamlit as st
		st.error(
			"OCR feature is not available.\n\n"
			"To enable PNG-to-table conversion:\n"
			"1. Install pytesseract: `pip install pytesseract`\n"
			"2. Install Tesseract OCR binary from: "
			"https://github.com/UB-Mannheim/tesseract/wiki\n"
			"3. Restart your application."
		)
	except ImportError:
		print(
			"ERROR: OCR feature is not available.\n"
			"To enable PNG-to-table conversion:\n"
			"1. Install pytesseract: pip install pytesseract\n"
			"2. Install Tesseract OCR binary from: "
			"https://github.com/UB-Mannheim/tesseract/wiki\n"
			"3. Restart your application."
		)


def _show_ocr_error(error: Exception) -> None:
	"""Display a user-friendly error message when OCR processing fails."""
	logger.info(" > LOG:: OCR processing raised exception: %s", str(error))
	error_msg = f"OCR processing failed: {str(error)}\n\nPlease check your image and try again."
	try:
		import streamlit as st
		st.warning(error_msg)
	except ImportError:
		print(f"WARNING: {error_msg}")



def pic_to_table(
	image_path: str | Path,
	*,
	lang: str = "eng+heb",
	min_confidence: int = 30,
	row_tolerance: int = 14,
	col_tolerance: int = 40,
	use_first_row_as_header: bool = True,
	tesseract_cmd: str | None = None,
) -> pd.DataFrame:
	"""Convert a PNG image containing a table into a pandas DataFrame using OCR."""
	logger.info(" > LOG:: Start pic_to_table")
	if pytesseract is None:
		_show_ocr_not_available_error()
		logger.info(" > LOG:: Returning empty DataFrame because pytesseract is missing")
		return pd.DataFrame()
	ocr_engine = pytesseract

	path = Path(image_path)
	logger.info(" > LOG:: Resolved image path: %s", path)
	if not path.exists():
		logger.info(" > LOG:: Image file does not exist")
		raise FileNotFoundError(f"Image file was not found: {path}")
	if path.suffix.lower() != ".png":
		logger.info(" > LOG:: Invalid image extension: %s", path.suffix)
		raise ValueError(f"Expected a .png file, got: {path.name}")

	if tesseract_cmd:
		logger.info(" > LOG:: Applying custom tesseract_cmd")
		ocr_engine.pytesseract.tesseract_cmd = tesseract_cmd

	try:
		logger.info(" > LOG:: Opening image file")
		with Image.open(path) as image:
			prepared_image = _prepare_image_for_ocr(image)

		logger.info(" > LOG:: Running OCR image_to_data")
		ocr_result = ocr_engine.image_to_data(
			prepared_image,
			lang=lang,
			output_type=ocr_engine.Output.DICT,
			config="--psm 6",
		)
		logger.info(" > LOG:: OCR completed successfully")
	except Exception as e:
		_show_ocr_error(e)
		logger.info(" > LOG:: Returning empty DataFrame after OCR failure")
		return pd.DataFrame()

	tokens: list[dict[str, Any]] = []
	logger.info(" > LOG:: Parsing OCR output tokens")
	for idx, text in enumerate(ocr_result.get("text", [])):
		cleaned = (text or "").strip()
		if not cleaned:
			continue

		confidence_raw = str(ocr_result.get("conf", ["-1"])[idx]).strip()
		confidence = int(float(confidence_raw)) if confidence_raw not in {"", "-1"} else -1
		if confidence < min_confidence:
			continue

		tokens.append(
			{
				"text": cleaned,
				"left": int(ocr_result["left"][idx]),
				"top": int(ocr_result["top"][idx]),
				"width": int(ocr_result["width"][idx]),
				"height": int(ocr_result["height"][idx]),
			}
		)
	logger.info(" > LOG:: Filtered token count=%d", len(tokens))

	dataframe = _tokens_to_dataframe(tokens, row_tolerance=row_tolerance, col_tolerance=col_tolerance)
	if dataframe.empty or not use_first_row_as_header:
		logger.info(" > LOG:: Returning DataFrame without header promotion; shape=%s", dataframe.shape)
		return dataframe

	headers = _make_unique_headers(dataframe.iloc[0].fillna("").astype(str).tolist())
	result = dataframe.iloc[1:].reset_index(drop=True).set_axis(headers, axis=1)
	logger.info(" > LOG:: Returning DataFrame with headers; shape=%s", result.shape)
	return result
