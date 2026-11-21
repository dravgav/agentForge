# Design: Simple Calculator App

## 1) Goal

Build a small calculator application in a single-directory Python project using **Gradio** for the UI and a backend Python module for arithmetic logic. The app should support basic operations and be easy to test.

---

## 2) Scope

### Required features
- Input for two numbers
- Support for basic operations:
  - addition
  - subtraction
  - multiplication
  - division
- Display the result in the UI
- Handle invalid input gracefully
- Handle division by zero gracefully
- Provide unit tests for the backend logic

### Non-goals
- No persistent storage
- No user accounts/authentication
- No history/logging UI
- No advanced scientific functions

---

## 3) File Layout

All files live in the same directory.

- `calculator_backend.py`
- `app.py`
- `test_calculator_backend.py`

---

## 4) Module Design

## 4.1 `calculator_backend.py`

This module contains all pure calculation logic and input validation.  
Keep it UI-agnostic so it can be tested independently.

### Responsibilities
- Parse and validate inputs
- Perform arithmetic operations
- Raise clear exceptions for invalid cases
- Return results in a simple, predictable format

### Constants
- `ALLOWED_OPERATIONS: tuple[str, ...]`

### Exceptions
Use built-in exceptions where possible:
- `ValueError` for invalid operation or invalid numeric input
- `ZeroDivisionError` for division by zero

### Functions

#### `parse_number(value: str | int | float) -> float`
- Convert input to a float
- Raise `ValueError` if input cannot be parsed

#### `calculate(num1: str | int | float, num2: str | int | float, operation: str) -> float`
- Perform the requested arithmetic operation
- Supported `operation` values:
  - `"add"`
  - `"subtract"`
  - `"multiply"`
  - `"divide"`
- Raise:
  - `ValueError` if operation is unsupported
  - `ZeroDivisionError` if dividing by zero

#### `format_result(result: float) -> str`
- Convert the numeric result to a display string
- Keep formatting simple and stable for UI display

---

## 5) Frontend Design

## 5.1 `app.py`

This module builds the Gradio interface and connects UI events to backend functions.

### Responsibilities
- Create the calculator UI
- Capture inputs from the user
- Call backend logic
- Show result or error messages
- Launch the app

### Gradio 6 API guidance for the frontend engineer

Use the modern **`gr.Blocks()`** app structure.

Key points:
- Prefer `gr.Blocks()` for layout composition.
- Use standard input components such as:
  - `gr.Textbox` for numeric entry if you want flexible input handling
  - or `gr.Number` if you want numeric-only input
- Use `gr.Button` for triggering calculation
- Use `gr.Markdown` or `gr.Textbox` for result display
- Event wiring should use component events like:
  - `button.click(...)`
- Keep callback functions simple and pure where possible
- Use `demo.launch()` to start the app
- If you need public sharing, use `demo.launch(share=True)` only if required
- Avoid assuming older-style `Interface` patterns unless necessary

Since the app is simple, a `Blocks` layout is the safest design choice.

### UI layout
- Title/header
- Two number inputs
- Operation selector
- Calculate button
- Output area for result/errors
- Optional clear/reset button

### UI behavior
- On clicking “Calculate”:
  - collect `num1`, `num2`, and `operation`
  - call backend `calculate(...)`
  - format and display the result
- If validation fails:
  - display a friendly error message
- Clear button:
  - reset inputs and output

### Functions

#### `build_app() -> gr.Blocks`
- Create and return the configured Gradio app

#### `handle_calculate(num1: str, num2: str, operation: str) -> str`
- Call backend calculator logic
- Return a user-facing message string
- Catch exceptions and return readable error messages

#### `handle_clear() -> tuple`
- Return cleared values for all input and output components
- Exact tuple shape should match the components being reset

#### `main() -> None`
- Build the app and launch it

### Suggested component structure
- `gr.Markdown("## Simple Calculator")`
- `gr.Textbox(label="First number")`
- `gr.Textbox(label="Second number")`
- `gr.Dropdown(choices=[...], label="Operation")`
- `gr.Button("Calculate")`
- `gr.Button("Clear")`
- `gr.Textbox(label="Result", interactive=False)`

### Event wiring
- `calculate_button.click(fn=handle_calculate, inputs=[...], outputs=[...])`
- `clear_button.click(fn=handle_clear, inputs=[], outputs=[...])`

---

## 6) Backend / Frontend Contract

The frontend must call the backend with these values:
- `num1`: string from UI
- `num2`: string from UI
- `operation`: one of `"add"`, `"subtract"`, `"multiply"`, `"divide"`

The backend returns:
- a numeric result from `calculate(...)`

The frontend converts this into:
- a display string such as `"Result: 12.5"`

If an error occurs:
- the frontend returns a user-friendly string such as:
  - `"Error: invalid number input"`
  - `"Error: division by zero"`
  - `"Error: unsupported operation"`

---

## 7) Test Design

## 7.1 `test_calculator_backend.py`

This module contains unit tests for backend logic only.  
Do not test Gradio UI behavior here.

### Responsibilities
- Verify each arithmetic operation
- Verify parsing behavior
- Verify error handling
- Ensure backend is deterministic and easy to trust

### Suggested test cases

#### Parsing
- valid integer string
- valid float string
- invalid string input

#### Operations
- addition
- subtraction
- multiplication
- division
- division with non-integer result

#### Error handling
- unsupported operation
- division by zero
- invalid numeric input

### Test function signatures

#### `test_parse_number_with_integer_string() -> None`
#### `test_parse_number_with_float_string() -> None`
#### `test_parse_number_with_invalid_string() -> None`
#### `test_calculate_addition() -> None`
#### `test_calculate_subtraction() -> None`
#### `test_calculate_multiplication() -> None`
#### `test_calculate_division() -> None`
#### `test_calculate_division_by_zero() -> None`
#### `test_calculate_with_unsupported_operation() -> None`

---

## 8) Engineer Assignments

## 8.1 backend_engineer

### Deliverables
Implement `calculator_backend.py`

### Work items
- Define allowed operations
- Implement `parse_number(...)`
- Implement `calculate(...)`
- Implement `format_result(...)`
- Ensure exceptions are raised consistently
- Keep the module UI-independent

### Acceptance criteria
- All arithmetic operations work correctly
- Invalid inputs raise clear exceptions
- Backend can be imported by frontend and tests without side effects

---

## 8.2 frontend_engineer

### Deliverables
Implement `app.py`

### Work items
- Build Gradio UI using `gr.Blocks`
- Wire calculate and clear actions
- Use backend functions for all computation
- Return user-friendly error messages
- Provide `main()` and app launch flow

### Gradio 6 API guidance
- Use `gr.Blocks()` rather than legacy layout styles
- Use `component.click(...)` for button actions
- Prefer explicit `inputs=[...]` and `outputs=[...]`
- Use `demo.launch()` to run locally
- Keep callback signatures aligned with component values

### Acceptance criteria
- App opens successfully
- User can input numbers and select operation
- Result displays correctly
- Invalid input is handled gracefully
- Clear button resets the form

---

## 8.3 test_engineer

### Deliverables
Implement `test_calculator_backend.py`

### Work items
- Write unit tests for backend parsing and arithmetic
- Include positive and negative cases
- Verify exception behavior
- Keep tests fast and isolated

### Acceptance criteria
- Tests cover all supported operations
- Tests fail when backend behavior is incorrect
- No dependency on Gradio UI

---

## 9) Function Signatures Summary

## `calculator_backend.py`
- `parse_number(value: str | int | float) -> float`
- `calculate(num1: str | int | float, num2: str | int | float, operation: str) -> float`
- `format_result(result: float) -> str`

## `app.py`
- `build_app() -> gr.Blocks`
- `handle_calculate(num1: str, num2: str, operation: str) -> str`
- `handle_clear() -> tuple`
- `main() -> None`

## `test_calculator_backend.py`
- `test_parse_number_with_integer_string() -> None`
- `test_parse_number_with_float_string() -> None`
- `test_parse_number_with_invalid_string() -> None`
- `test_calculate_addition() -> None`
- `test_calculate_subtraction() -> None`
- `test_calculate_multiplication() -> None`
- `test_calculate_division() -> None`
- `test_calculate_division_by_zero() -> None`
- `test_calculate_with_unsupported_operation() -> None`

---

## 10) Implementation Notes

- Keep backend functions pure and simple.
- The frontend should not reimplement arithmetic.
- Use friendly messages in the UI, but keep exceptions precise in the backend.
- Since all files are in one directory, import directly by module name:
  - `from calculator_backend import calculate, format_result`
- Avoid circular imports:
  - backend should not import frontend
- Use stable labels and operation values so tests and UI stay aligned.

---

## 11) Definition of Done

The work is complete when:
- The calculator app launches successfully
- All four basic operations work
- Invalid input is handled cleanly
- Division by zero is handled cleanly
- Backend unit tests pass
- The code is organized into the three files above