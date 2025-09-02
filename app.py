import streamlit as st
import os
import sys
import tempfile
import zipfile
from io import BytesIO
import re

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.diff_viewer.diff_viewer import CodeDiffViewer
from src.parser.airflow_parser import AirflowDagParser
from src.graph.graph_builder import GraphBuilder
from src.graph.dot_generator import DotGenerator
from src.optimiser.optimiser import Optimiser

def main():
    st.title("Airflow Optimiser")

    st.header("Upload Airflow DAGs and Code")
    uploaded_files = st.file_uploader("Upload your Airflow DAGs and Python code (zip file or individual files)", accept_multiple_files=True, key="main_codebase")

    if uploaded_files:
        if "code_contents" not in st.session_state:
            st.session_state.code_contents = {}
        if "optimized_code" not in st.session_state:
            st.session_state.optimized_code = {}
        if "show_diff_opt" not in st.session_state:
            st.session_state.show_diff_opt = {}
        if "dags" not in st.session_state:
            st.session_state.dags = []

        if not st.session_state.code_contents:
            for uploaded_file in uploaded_files:
                try:
                    content = uploaded_file.getvalue().decode("utf-8")
                    st.session_state.code_contents[uploaded_file.name] = content
                except UnicodeDecodeError:
                    st.session_state.code_contents[uploaded_file.name] = "This file is not a UTF-8 encoded text file."

        st.header("Optimisation Suggestions")
        if st.button("Analyse and Optimise"):
            with st.spinner("Analyzing code for optimizations..."):
                st.session_state.dags = []
                st.session_state.optimized_code = {}
                all_parsed_data = {"nodes": [], "edges": []}
                for file_name, original_code in st.session_state.code_contents.items():
                    if file_name.endswith(".py"):
                        try:
                            parser = AirflowDagParser(original_code)
                            dags = parser.parse()
                            st.session_state.dags.extend(dags)
                            optimiser = Optimiser(original_code)
                            st.session_state.optimized_code[file_name] = optimiser.suggest_optimisations()
                            for dag in dags:
                                all_parsed_data["nodes"].append({"id": dag['dag_id'], "type": "dag", "name": dag['dag_id']})
                                for task in dag['tasks']:
                                    all_parsed_data["nodes"].append({"id": task['task_id'], "type": "task", "name": task['task_id']})
                                    all_parsed_data["edges"].append({"source": dag['dag_id'], "target": task['task_id'], "type": "CONTAINS"})
                                    for dependency in task['dependencies']:
                                        all_parsed_data["edges"].append({"source": task['task_id'], "target": dependency, "type": "DEPENDS_ON"})
                        except Exception as e:
                            st.warning(f"Could not parse {file_name}: {e}")
                
                graph_builder = GraphBuilder()
                code_graph = graph_builder.build_graph(all_parsed_data)
                st.session_state.code_graph = code_graph


        if st.session_state.get("dags"):
            st.header("Detected DAGs")
            for dag in st.session_state.dags:
                st.write(f"- {dag['dag_id']}")

        if st.session_state.get("code_graph"):
            st.header("DAGs Graph")
            dot_generator = DotGenerator()
            dot_string = dot_generator.generate_dot(st.session_state.code_graph)
            st.graphviz_chart(dot_string)

        if st.session_state.get("optimized_code"):
            for file_name, optimized_code in st.session_state.optimized_code.items():
                st.subheader(f"Optimized Code for {file_name}:")
                st.text_area("Original Code", st.session_state.code_contents[file_name], height=300, key=f"original_opt_{file_name}")
                st.text_area("Optimized Code", optimized_code, height=300, key=f"optimized_{file_name}")
                if st.button(f"Show Diff for {file_name}", key=f"opt_{file_name}"):
                    st.session_state.show_diff_opt[file_name] = not st.session_state.show_diff_opt.get(file_name, False)

                if st.session_state.show_diff_opt.get(file_name, False):
                    original_code = st.session_state.code_contents[file_name]
                    diff_viewer = CodeDiffViewer(original_code, optimized_code)
                    diff_viewer.show_diff()

if __name__ == "__main__":
    main()
