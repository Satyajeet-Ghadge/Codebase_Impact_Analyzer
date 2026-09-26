Codebase Impact Analyzer

A Python-based developer productivity tool that analyzes the impact of code changes in a repository.

It uses Python AST analysis and Git history to identify which files, functions, and tests may be affected by a change. It also calculates an impact score and risk level for the change.

Problem Statement

When a developer changes a function or file in a large codebase, it can be difficult to determine:

Which files depend on the changed code?

Which functions may be affected?

Which tests should be reviewed or executed?

How deep the impact propagates through the codebase?

How risky is the change?

Manually finding these dependencies becomes difficult as a project grows.

Solution

Codebase Impact Analyzer builds dependency information from the source code and combines it with Git changes.

The analyzer:

Scans the repository for Python files.

Parses Python code using the AST module.

Builds a file dependency graph.

Builds a function dependency graph.

Reads Git changes from the working tree, a commit, or a commit range.

Detects the exact functions changed using Git diff line ranges and AST function boundaries.

Finds potentially affected files and functions.

Identifies potentially affected tests.

Calculates impact metrics.

Produces an impact score and risk level.

Supports text and JSON output.

Supports CI usage with configurable failure thresholds.

Features

Repository Analysis

Recursive Python file scanning

AST-based source-code analysis

Import detection

Function and class detection

Function-call extraction

Dependency Analysis

File dependency graph using NetworkX

Function dependency analysis

Direct and indirect impact detection

Maximum dependency depth calculation

Git Integration

Supports analysis of:

Current working-tree changes

A specific Git commit

A Git commit range

Example:

python main.py --repo sample_project

python main.py --repo sample_project --commit HEAD

python main.py --repo sample_project --base HEAD~1 --head HEAD

Exact Changed Function Detection

The analyzer uses Git diff line ranges together with AST function boundaries to determine which functions were actually modified.

For example, if only login() changed:

Changed Functions:
  sample_project/auth.py::login

Test Impact

The analyzer identifies tests that may be affected by changed code.

Example:

Potentially Affected Tests:
  sample_project/tests/test_auth.py

Impact Scoring

The analyzer calculates a score using:

Directly affected files

Indirectly affected files

Affected functions

Affected tests

Maximum dependency depth

Risk levels are classified as:

LOW
MEDIUM
HIGH

Output Formats

Text output:

python main.py --repo sample_project

JSON output:

python main.py --repo sample_project --format json

CI Mode

The analyzer can be used in CI pipelines to fail when the calculated risk reaches a configured threshold.

Example:

python main.py --repo sample_project --ci --fail-on high

Architecture

                 Repository
                     |
                     v
              File Scanner
                     |
                     v
                AST Parser
                /         \
               /           \
              v             v
      File Dependency   Function Dependency
           Graph              Graph
              \              /
               \            /
                v          v
                  Git Changes
                       |
                       v
                 Impact Analysis
                /       |        \
               v        v         v
             Files   Functions   Tests
                \       |        /
                 \      |       /
                  v     v      v
                  Impact Metrics
                       |
                       v
                  Risk Analysis
                       |
                       v
                CLI / JSON / CI

Project Structure

Codebase_Impact_Analyzer/
│
├── .github/
│   └── workflows/
│       └── impact-analyzer.yml
│
├── analyzer/
│   ├── __init__.py
│   ├── change_detector.py
│   ├── code_model.py
│   ├── dependency.py
│   ├── function_graph.py
│   ├── function_impact.py
│   ├── git_analyzer.py
│   ├── graph.py
│   ├── impact_analyzer.py
│   ├── parser.py
│   ├── report.py
│   ├── risk_analyzer.py
│   ├── scanner.py
│   ├── snapshot.py
│   └── test_analyzer.py
│
├── sample_project/
│   └── Git submodule containing the sample repository
│
├── main.py
├── requirements.txt
├── .gitignore
├── .gitmodules
└── README.md

Technologies Used

Python

Abstract Syntax Tree (AST)

NetworkX

Git

Git diff

unittest

GitHub Actions

Installation

Clone the repository:

git clone https://github.com/Satyajeet-Ghadge/Codebase_Impact_Analyzer.git
cd Codebase_Impact_Analyzer

Initialize the sample-project submodule:

git submodule update --init --recursive

Create a virtual environment:

Windows

python -m venv venv
venv\Scripts\activate

Linux / macOS

python3 -m venv venv
source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Usage

Analyze the working tree

python main.py --repo sample_project

Analyze a specific commit

python main.py --repo sample_project --commit HEAD

Analyze a commit range

python main.py --repo sample_project --base HEAD~1 --head HEAD

JSON output

python main.py --repo sample_project --format json

CI mode

python main.py --repo sample_project --ci

CI with risk threshold

python main.py --repo sample_project --ci --fail-on high

Example Output

CODEBASE IMPACT ANALYZER

Changes
  Modified: auth.py

Impact of: auth.py

Potentially Affected Files:
  sample_project/main.py

Changed Functions:
  sample_project/auth.py::login

Potentially Affected Functions:
  sample_project/main.py::main

Potentially Affected Tests:
  sample_project/tests/test_auth.py

Impact Summary
  Files affected: 1
  Functions affected: 1
  Public functions: 1
  Tests affected: 1
  Maximum depth: 1
  Direct files: 1
  Indirect files: 0
  Impact Score: 8
  Risk Level: MEDIUM

Testing

Run the project tests with:

python -m unittest discover -s sample_project/tests -t sample_project -p "test*.py" -v

The project also contains analyzer tests covering Git analysis, impact scoring, risk classification, dependency impact, public functions, reports, and Git snapshots.

GitHub Actions

The project includes a GitHub Actions workflow under:

.github/workflows/impact-analyzer.yml

The workflow is intended to automatically run the analyzer/tests when changes are pushed to GitHub.

Current Scope

The current implementation focuses on Python repositories.

The analyzer currently uses static AST-based analysis and Git information. It does not execute the target application's business logic to determine runtime dependencies.

Future Improvements

Possible future extensions include:

Support for additional programming languages

Better handling of deleted functions

More precise rename analysis

Dependency graph visualization

Result caching for large repositories

Pull request comments with impact reports

Web dashboard

More advanced semantic dependency analysis

Author

Satyajeet Ghadge

GitHub:

https://github.com/Satyajeet-Ghadge