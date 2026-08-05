# Diagram Baseline

Every heavy architecture includes a checkable diagram. Mermaid is sufficient when it clearly
shows the complete relationship. Use a self-contained HTML file with inline SVG when the system
has multiple trust boundaries, lifecycle flows, or a publication-quality diagram is useful.

## Required Content

- All architecture modules and their unique responsibilities.
- Directed data or control-flow arrows with readable labels.
- Trust, deployment, runtime, and manual-Gate boundaries.
- Parallel lanes and hard dependencies.
- Failure or rollback flow where it changes ownership.
- A legend or direct semantic labels; do not rely on color alone.

## HTML Contract

A self-contained diagram has `lang`, UTF-8, viewport, a title, and an outer capture container. The
inline SVG uses `role="img"`, `aria-labelledby`, `<title>`, `<desc>`, and a viewBox. Use plain SVG
shapes and text; avoid `foreignObject`, remote images, and event handlers in SVG. If export scripts
are included, pin their versions and integrity values.

## Visual Gate

Open the real file in a browser. Check desktop width, intended mobile behavior, page overflow,
crossing or reversed arrows, text clipping, legend placement, long labels, and dark/light contrast
as applicable. A screenshot alone is not a Gate unless the browser geometry and source file were
also inspected. Record the tested viewport and actual result.
