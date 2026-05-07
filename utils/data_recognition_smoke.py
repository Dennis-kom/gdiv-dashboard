from utils.data_recognition import _make_unique_headers, _tokens_to_dataframe


def run_smoke() -> None:
    # Synthetic OCR output to validate table reconstruction logic without OCR binary.
    tokens = [
        {"text": "name", "left": 10, "top": 10, "width": 30, "height": 10},
        {"text": "score", "left": 120, "top": 10, "width": 35, "height": 10},
        {"text": "Alice", "left": 10, "top": 35, "width": 30, "height": 10},
        {"text": "95", "left": 120, "top": 35, "width": 15, "height": 10},
    ]

    df = _tokens_to_dataframe(tokens, row_tolerance=12, col_tolerance=35)
    headers = _make_unique_headers(df.iloc[0].tolist())
    df = df.iloc[1:].reset_index(drop=True).set_axis(headers, axis=1)

    assert list(df.columns) == ["name", "score"]
    assert df.iloc[0].to_dict() == {"name": "Alice", "score": "95"}
    print("Smoke test passed")


if __name__ == "__main__":
    run_smoke()

