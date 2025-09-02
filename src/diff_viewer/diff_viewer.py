import difflib
import streamlit as st

class CodeDiffViewer:
    def __init__(self, original_code, optimized_code):
        self.original_code = original_code
        self.optimized_code = optimized_code

    def show_diff(self):
        diff = difflib.unified_diff(
            self.original_code.splitlines(keepends=True),
            self.optimized_code.splitlines(keepends=True),
            fromfile='original',
            tofile='optimized',
        )
        st.code(''.join(diff), language='diff')