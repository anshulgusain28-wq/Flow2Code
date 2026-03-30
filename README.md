# Flow2Code

**Flow2Code** is a visual programming language compiler that bridges the gap between flowchart design and executable code. It allows users to create logic visually using a drag-and-drop interface and instantly compile it into Python or C++ code.

---

## 🚀 What is this project?

Flow2Code is a desktop application designed to help students, beginners, and prototypers understand programming logic without getting bogged down by syntax errors. By visually constructing algorithms using standard flowchart symbols, users can see the direct correlation between their logical design and the actual code implementation in multiple languages.

## ⚙️ How it works

1.  **Visual Editor**: Users drag and drop shapes (Start, Process, Decision, Input, Output, End) onto a canvas.
2.  **Connections**: Nodes are connected to define the flow of execution.
3.  **Internal Representation**: The application builds an internal directed graph (AST) representing the logic.
4.  **Compilation Process**:
    *   **AST Construction**: The visual nodes and connections are parsed into an Abstract Syntax Tree.
    *   **Semantic Analysis**: The graph is checked for logical errors (e.g., disconnected nodes, missing start/end).
    *   **Code Generation**: The valid graph is traversed to generate equivalent code in the selected target language (Python or C++).

## 🛠️ Tech Stack

*   **Language**: Python 3.10+
*   **GUI Framework**: Tkinter (Standard Python GUI)
*   **Graph Processing**: NetworkX (For graph data structures and traversal)
*   **OS Support**: Windows (Primary), macOS, Linux

## 🎯 Problem Solved

Learning to code often involves two simultaneous struggles: understanding **logic** and mastering **syntax**. Flow2Code isolates the logic component, allowing users to:
*   Visualize algorithms before writing a single line of code.
*   Debug logic visually.
*   Learn how control structures (loops, if-else) translate between visual flows and text-based code.
*   Prototype algorithms quickly without syntax overhead.

## 🏗️ System Architecture

The project follows a modular architecture separating the UI from the compiler logic:

### 1. Frontend (`src/ui`)
*   **Editor (`editor.py`)**: Manages the canvas, event handling (clicks, drags), and the main application loop.
*   **Toolbar (`toolbar.py`)**: Provides tools for selecting shapes and managing application state (Run, Clear, connect).
*   **Shapes (`shapes.py`)**: Defines the visual appearance and properties of flowchart nodes (Start, Process, etc.).

### 2. Backend / Compiler (`src/compiler`)
*   **AST Builder (`ast_builder.py`)**: Converts the raw UI shape objects and connection lines into a structured NetworkX graph.
*   **Semantic Analyzer (`semantic.py`)**: Validates the graph for logical correctness before code generation.
*   **Code Generator (`generator.py`)**: Traverses the graph to produce syntactically correct source code in the target language.

### 3. Entry Point
*   **`main.py`**: Initializes the application context and launches the UI.

## 📦 Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/Flow2Code.git
    cd Flow2Code
    ```

2.  **Create a virtual environment** (Optional but recommended):
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ Usage

1.  Run the application:
    ```bash
    python src/main.py
    ```
2.  **Drag** shapes from the toolbar to the canvas.
3.  **Double-click** shapes to edit their content (e.g., variable names, conditions).
4.  Select the **Arrow Tool** to connect nodes.
5.  Click **"Convert to Code"** or select a language from the dropdown to see the generated code.

---
*Built with ❤️ for the coding community.*
