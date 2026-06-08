import os
import socket

import streamlit as st


st.set_page_config(page_title="HPC Streamlit Smoke Test")

st.title("HPC Streamlit Smoke Test")
st.write("This app is intentionally tiny so it can be reviewed before launch.")

st.subheader("Runtime")
st.write(
    {
        "host": socket.gethostname(),
        "job_id": os.environ.get("SLURM_JOB_ID", "local"),
        "cpus_per_task": os.environ.get("SLURM_CPUS_PER_TASK", "unknown"),
        "working_directory": os.getcwd(),
    }
)

st.subheader("Checklist")
st.checkbox("I am running inside a scheduled allocation.")
st.checkbox("I will close the tunnel and cancel the job when finished.")
