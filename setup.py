from setuptools import find_packages, setup


setup(
    name="hpc-skill-hub",
    version="0.4.0",
    description="Open registry of validated, reusable skills for HPC workflows.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    package_dir={"": "src"},
    packages=find_packages("src"),
    package_data={
        "hpc_skill_hub": [
            "data/registry/*.json",
            "data/integrations/*.json",
            "data/security/*.json",
        ]
    },
    extras_require={
        "mcp": ["mcp>=1.27,<2; python_version >= '3.10'"]
    },
    entry_points={
        "console_scripts": [
            "hpc-skill=hpc_skill_hub.cli:main",
            "hpc-skill-mcp=hpc_skill_hub.mcp_server:main",
        ]
    },
)
