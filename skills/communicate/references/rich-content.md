# Figures

Load when writing markdown that contains figures. Rules apply at every stage.

## The attachments directory (`ATTACH_DIR`)

The caller supplies the target `attachments/` directory — substitute the actual path when embedding. No caller value: default to `attachments/` next to the output file:

- Task `## Results` → next to the task's `task.md` (see `task-tree/references/task-file-contract.md` §Figure Embedding).
- Matured task results → next to the task's `task.md`.
- Standalone report → next to the report file.

### Create the directory

```bash
mkdir -p "${ATTACH_DIR}"
```

### Materialize figures

Task figures are written directly into the task's `attachments/` by the analysis script — no copying. Permanent and standalone reports copy figures into a new attachments folder so the artifact is self-contained:

**PDF figures:** convert to PNG first, then save:

```bash
uv run --no-project --with pdf2image python -c "
from pdf2image import convert_from_path
images = convert_from_path('path/to/figure.pdf')
images[0].save('${ATTACH_DIR}/description.png')
"
```

**PNG / JPG / other raster:** copy directly:

```bash
cp path/to/figure.png "${ATTACH_DIR}/description.png"
```

### Embed

```markdown
![Descriptive caption](ATTACH_DIR/description.png)

Source: [Original](relative/path/to/original/figure.pdf)
```

Use a **descriptive caption**, not "Figure 1" — it is the figure's documentation for skimmers.

Cite the **original source path** beneath the embed — the file the analysis script produced, not the copy in `ATTACH_DIR` — so a future reader can regenerate the figure.
