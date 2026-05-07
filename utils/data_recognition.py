from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from PIL import Image, ImageFilter, ImageOps

try:
	import pytesseract
except ImportError:  # pragma: no cover - handled at runtime for missing optional dependency
	pytesseract = None


def _cluster_positions(values: list[float], tolerance: int) -> list[float]:
	if not values:
		return []

	centers = [values[0]]
	for value in values[1:]:
		if abs(value - centers[-1]) <= tolerance:
			centers[-1] = (centers[-1] + value) / 2
		else:
			centers.append(value)
	return centers


def _nearest_cluster(value: float, clusters: list[float]) -> int:
	return min(range(len(clusters)), key=lambda idx: abs(clusters[idx] - value))


def _make_unique_headers(raw_headers: list[str]) -> list[str]:
	seen: dict[str, int] = {}
	headers: list[str] = []

	for idx, value in enumerate(raw_headers, start=1):
		header = (value or "").strip() or f"column_{idx}"
		count = seen.get(header, 0) + 1
		seen[header] = count
		headers.append(header if count == 1 else f"{header}_{count}")

	return headers


def _prepare_image_for_ocr(image: Image.Image) -> Image.Image:
	gray = ImageOps.grayscale(image)
	denoised = gray.filter(ImageFilter.MedianFilter(size=3))
	enhanced = ImageOps.autocontrast(denoised)
	# Binary threshold usually improves OCR on scanned forms and screenshots.
	return enhanced.point(lambda x: 0 if x < 160 else 255, mode="1")


def _tokens_to_dataframe(tokens: list[dict[str, Any]], row_tolerance: int, col_tolerance: int) -> pd.DataFrame:
	if not tokens:
		return pd.DataFrame()

	row_positions = sorted(token["top"] + token["height"] / 2 for token in tokens)
	col_positions = sorted(token["left"] + token["width"] / 2 for token in tokens)

	row_centers = _cluster_positions(row_positions, tolerance=row_tolerance)
	col_centers = _cluster_positions(col_positions, tolerance=col_tolerance)

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
		return pd.DataFrame()

	columns = [f"column_{idx + 1}" for idx in range(len(rows[0]))]
	return pd.DataFrame(rows, columns=columns)


def _show_ocr_not_available_error() -> None:
	"""Display a user-friendly error message when OCR is not available."""
	try:
		import streamlit as st
		st.error(
			"❌ OCR feature is not available.\n\n"
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
	error_msg = f"⚠️ OCR processing failed: {str(error)}\n\nPlease check your image and try again."
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
	if pytesseract is None:
		_show_ocr_not_available_error()
		return pd.DataFrame()
	ocr_engine = pytesseract

	path = Path(image_path)
	if not path.exists():
		raise FileNotFoundError(f"Image file was not found: {path}")
	if path.suffix.lower() != ".png":
		raise ValueError(f"Expected a .png file, got: {path.name}")

	if tesseract_cmd:
		ocr_engine.pytesseract.tesseract_cmd = tesseract_cmd

	try:
		with Image.open(path) as image:
			prepared_image = _prepare_image_for_ocr(image)

		ocr_result = ocr_engine.image_to_data(
			prepared_image,
			lang=lang,
			output_type=ocr_engine.Output.DICT,
			config="--psm 6",
		)
	except Exception as e:
		_show_ocr_error(e)
		return pd.DataFrame()

	tokens: list[dict[str, Any]] = []
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

	dataframe = _tokens_to_dataframe(tokens, row_tolerance=row_tolerance, col_tolerance=col_tolerance)
	if dataframe.empty or not use_first_row_as_header:
		return dataframe

	headers = _make_unique_headers(dataframe.iloc[0].fillna("").astype(str).tolist())
	return dataframe.iloc[1:].reset_index(drop=True).set_axis(headers, axis=1)
