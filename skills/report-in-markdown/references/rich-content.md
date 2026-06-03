# Rich content: figures, math, tables

Load when writing markdown that contains figures, LaTeX math, or tables. Rules apply at every stage.

## Figures

### The attachments directory is a caller parameter

The target `attachments/` directory is supplied by the caller, not hard-coded in this skill. Common cases:

- Stage 1 task `## Results` → `attachments/` next to the task's `task.md` (superRA convention, see `task-system/references/planning.md` §Figure Embedding).
- Matured task results → `attachments/` next to the task's `task.md` unless the caller specifies another directory.
- Standalone report → `attachments/` next to the report file.

If the invoking skill did not specify a directory, default to `attachments/` next to the output file. Refer to the target as `ATTACH_DIR` in your head; substitute the actual path when embedding.

### Create the directory

```bash
mkdir -p "${ATTACH_DIR}"
```

### Materialize figures

Stage 1 typically *saves* figures directly into the task's `attachments/` directory (written there by the analysis script). No copying needed.

Permanent and standalone reports typically *copy* figures into a new attachments folder so the artifact is self-contained:

**PDF figures:** convert to PNG first, then save:

```bash
uv run --with pdf2image python -c "
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

Substitute `ATTACH_DIR` with the actual path for your context (see §The attachments directory is a caller parameter above).

Use a **descriptive caption** — not "Figure 1". The caption is the figure's documentation for readers who skim.

Cite the **original source path** beneath the embed so a future reader can regenerate the figure from the analysis script. The source path is the file the analysis script produced, not the copied version in `ATTACH_DIR`.


