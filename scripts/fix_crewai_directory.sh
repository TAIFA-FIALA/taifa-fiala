[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "taifa_etl"
version = "0.1.0"
authors = [
  { name = "Your Name", email = "your.email@example.com" },
]
description = "TAIFA CrewAI Enhanced ETL Pipeline"
readme = "README.md"
requires-python = ">=3.9"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
dependencies = [
    "crewai>=0.28.0",
    "langchain>=0.0.335",
    "langchain-openai>=0.0.2",
    "schedule>=1.2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.3.1",
]

[project.urls]
"Homepage" = "https://github.com/your-repo-url"
"Bug Tracker" = "https://github.com/your-repo-url/issues"

[tool.crewai]
config-file = "config.yaml"