"""Gradio frontend for the simple calculator app."""

from __future__ import annotations

import gradio as gr

from calculator_backend import calculate, format_result

ALLOWED_OPERATIONS = ["add", "subtract", "multiply", "divide"]


CSS = """
:root {
  --calc-accent: #209dd7;
  --calc-accent-2: #753991;
  --calc-warm: #ecad0a;
  --calc-surface: rgba(255, 255, 255, 0.78);
  --calc-surface-strong: rgba(255, 255, 255, 0.92);
  --calc-border: rgba(117, 57, 145, 0.18);
  --calc-text: #1f2937;
  --calc-muted: #6b7280;
}
@media (prefers-color-scheme: dark) {
  :root {
    --calc-surface: rgba(18, 24, 38, 0.72);
    --calc-surface-strong: rgba(18, 24, 38, 0.9);
    --calc-border: rgba(236, 173, 10, 0.2);
    --calc-text: #f3f4f6;
    --calc-muted: #9ca3af;
  }
}
#calc-shell {
  max-width: 860px;
  margin: 0 auto;
}
#calc-hero {
  border: 1px solid var(--calc-border);
  background: linear-gradient(135deg, color-mix(in srgb, var(--calc-accent) 16%, transparent), color-mix(in srgb, var(--calc-accent-2) 12%, transparent)), var(--calc-surface);
  border-radius: 24px;
  padding: 28px;
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(14px);
}
#calc-title h1 {
  margin: 0;
  font-size: 2rem;
  line-height: 1.1;
  color: var(--calc-text);
}
#calc-subtitle p {
  margin: 10px 0 0;
  color: var(--calc-muted);
}
.calc-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--calc-warm) 14%, transparent);
  color: var(--calc-text);
  border: 1px solid color-mix(in srgb, var(--calc-warm) 35%, transparent);
  font-weight: 600;
  font-size: 0.92rem;
}
.calc-card {
  border: 1px solid var(--calc-border);
  background: var(--calc-surface-strong);
  border-radius: 20px;
  padding: 22px;
}
button.primary {
  background: linear-gradient(135deg, var(--calc-accent), var(--calc-accent-2)) !important;
  border: none !important;
  color: white !important;
}
"""


def handle_calculate(num1: str, num2: str, operation: str) -> str:
    """Calculate and return a user-friendly message."""
    try:
        result = calculate(num1, num2, operation)
        return f"Result: {format_result(result)}"
    except ValueError as exc:
        return f"Error: {exc}"
    except ZeroDivisionError as exc:
        return f"Error: {exc}"


def handle_clear() -> tuple[str, str, str, str]:
    """Clear all input and output fields."""
    return "", "", "add", ""


def build_app() -> gr.Blocks:
    """Create and return the Gradio Blocks app."""
    with gr.Blocks() as demo:
        with gr.Column(elem_id="calc-shell"):
            with gr.Group(elem_id="calc-hero"):
                gr.HTML(
                    """
                    <div id="calc-title">
                      <h1>Simple Calculator</h1>
                    </div>
                    <div id="calc-subtitle">
                      <p>A polished Gradio demo for fast arithmetic: add, subtract, multiply, and divide.</p>
                    </div>
                    <div style="margin-top: 14px;">
                      <span class="calc-pill">Fast · Friendly · Tested</span>
                    </div>
                    """
                )

                with gr.Row():
                    with gr.Column(scale=2, elem_classes=["calc-card"]):
                        gr.Markdown("### Inputs")
                        with gr.Row():
                            num1 = gr.Textbox(label="First number", placeholder="e.g. 12.5")
                            num2 = gr.Textbox(label="Second number", placeholder="e.g. 3")
                        operation = gr.Dropdown(
                            choices=ALLOWED_OPERATIONS,
                            value="add",
                            label="Operation",
                        )
                        with gr.Row():
                            calculate_button = gr.Button("Calculate", variant="primary")
                            clear_button = gr.Button("Clear")

                    with gr.Column(scale=1, elem_classes=["calc-card"]):
                        gr.Markdown("### Result")
                        result = gr.Textbox(label="Output", interactive=False, lines=3)
                        gr.Markdown(
                            "Use the operation menu to choose how the two values should be combined."
                        )

        calculate_button.click(
            fn=handle_calculate,
            inputs=[num1, num2, operation],
            outputs=[result],
        )
        clear_button.click(
            fn=handle_clear,
            inputs=[],
            outputs=[num1, num2, operation, result],
        )

    demo.css = CSS
    demo.theme = gr.themes.Soft()
    return demo


def main() -> None:
    demo = build_app()
    demo.launch()


if __name__ == "__main__":
    main()
