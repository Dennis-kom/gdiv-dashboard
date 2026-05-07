"""Test fallback behavior when pytesseract is not available."""
from pathlib import Path
import sys
from unittest.mock import patch


def test_fallback_with_missing_pytesseract_non_streamlit():
    """Test that fallback shows error message when pytesseract is missing (non-Streamlit context)."""
    # Mock pytesseract as None to simulate missing dependency
    with patch("utils.data_recognition.pytesseract", None):
        from utils.data_recognition import pic_to_table

        # Should return empty DataFrame and print error (not raise)
        result = pic_to_table("dummy.png")
        assert result.empty, "Should return empty DataFrame when pytesseract is missing"
        print("✓ Test passed: Non-Streamlit fallback works (returns empty DataFrame without crashing)")


def test_fallback_output_structure():
    """Test that the fallback produces valid output."""
    with patch("utils.data_recognition.pytesseract", None):
        from utils.data_recognition import pic_to_table
        import pandas as pd

        result = pic_to_table("test.png")
        assert isinstance(result, pd.DataFrame), "Should return a DataFrame instance"
        assert result.empty, "Fallback DataFrame should be empty"
        print("✓ Test passed: Fallback returns valid empty DataFrame")


if __name__ == "__main__":
    test_fallback_with_missing_pytesseract_non_streamlit()
    test_fallback_output_structure()
    print("\n✓ All fallback tests passed!")

