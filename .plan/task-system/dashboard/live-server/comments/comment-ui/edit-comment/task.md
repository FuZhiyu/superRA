---
title: "Add comment editing support"
status: not-started
review_status: ~
integration_status: ~
depends_on:  []
tags: []
created: 2026-05-25
updated: 2026-05-25
---

## Objective

Allow users to edit existing comments in-place. Add an Edit button alongside Resolve/Delete on each comment. Clicking Edit replaces the comment body with an editable textarea pre-filled with the current text, with Save/Cancel controls. On save, PATCH the comment body via the API and re-render the thread (comment #2).

## Results

