# Figure design rules derived from the research-group guides

Use this reference when planning, assembling, or auditing scientific figures.

## Figure planning

1. Build the paper skeleton before polishing figures.
2. Assign one central idea to each figure.
3. Give each figure an internal working title and 1–2 sentences explaining its role in the paper.
4. Sketch a block diagram of the panels before producing publication-quality plots.
5. Choose the graphs that communicate the point most clearly, including to readers outside the immediate subfield.
6. Make the most important panel visually dominant.
7. For multi-panel figures, arrange panels to create an obvious reading flow.
8. When two panels must be compared, make the difference visible immediately.
9. Test early layouts with people who did not work on the project; their confusion is evidence that the figure needs revision.

## Figure 1

Figure 1 should usually communicate the central idea, physical system, phenomenon, or conceptual mechanism. It should orient the reader before specialized quantitative results appear.

## Typography and labels

- Use a readable sans-serif font.
- Use the largest font that comfortably fits the final-size figure.
- Keep font family and size hierarchy consistent across the entire paper.
- Use italics only for mathematical variables.
- Axis labels must contain a quantity/name, not only a unit.
- Put ticks outside the axes.
- Prefer direct labels on curves where practical.
- Keep legends visually subordinate to the data.
- Avoid title case for ordinary labels and annotations.

## Color

- Use distinctive colors for data that must be differentiated.
- Reuse the same semantic color assignments across figures when possible.
- Avoid harsh pure RGB colors when a flatter/broken palette gives better visual balance.
- For heat maps, use perceptually sensible colormaps such as viridis, plasma, inferno, or magma unless the science requires another mapping.
- Never let color be the only carrier of a crucial distinction if the target output may be printed or viewed with color-vision limitations; add line style, marker, annotation, or layout cues when needed.

## Visual noise

- Avoid gridlines unless repeated precise visual reading is essential.
- Leave some whitespace between subfigures even if axes are shared.
- Remove decorations that do not encode information.
- Keep panel lettering and annotation style consistent.

## Vector-first workflow

For line plots, schematics, labels, and other graphics that benefit from infinite scaling, prefer vector formats such as SVG, PDF, EPS, or EMF when the production environment supports them.

A robust workflow is:

1. Save computational output/data separately from plotting code.
2. Produce clean graph elements from the scientific plotting environment.
3. Assemble the final multi-panel figure in an editable layout/graphics environment when that improves control over typography and alignment.
4. Export in a vector format when possible.
5. Inspect the final manuscript PDF at high zoom and at final print size.

## Figure captions

Start every caption with an informative short title. Then explain:

- what each panel shows;
- what encodings/colors/lines mean;
- the minimum method/context needed to interpret the panel;
- the scientific takeaway.

The figure itself should remain understandable without forcing the reader to repeatedly consult the caption.
