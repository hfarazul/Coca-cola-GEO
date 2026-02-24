#!/usr/bin/env python3
"""Generate the Technical Architecture diagram as a PNG."""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# Colors
BLUE_DARK = "#2B4C7E"
BLUE_MED = "#4472C4"
BLUE_ACCENT = "#5B9BD5"
WHITE = "#FFFFFF"
ORANGE = "#E07C3E"

fig, ax = plt.subplots(1, 1, figsize=(12, 15))
ax.set_xlim(0, 10)
ax.set_ylim(0, 13)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(WHITE)


def draw_box(x, y, w, h, title, subtitle=None, color=BLUE_MED):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.15",
        facecolor=color, edgecolor=BLUE_DARK, linewidth=2.0, zorder=2,
    )
    ax.add_patch(box)
    if subtitle:
        ax.text(x + w / 2, y + h * 0.62, title,
                ha="center", va="center", fontsize=18, fontweight="bold",
                color=WHITE, family="sans-serif", zorder=3)
        ax.text(x + w / 2, y + h * 0.3, subtitle,
                ha="center", va="center", fontsize=12,
                color=WHITE, alpha=0.9, family="sans-serif", zorder=3)
    else:
        ax.text(x + w / 2, y + h / 2, title,
                ha="center", va="center", fontsize=18, fontweight="bold",
                color=WHITE, family="sans-serif", zorder=3)


def draw_small_box(x, y, w, h, title, color=BLUE_ACCENT):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.1",
        facecolor=color, edgecolor=BLUE_DARK, linewidth=1.5, zorder=2,
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, title,
            ha="center", va="center", fontsize=14, fontweight="bold",
            color=WHITE, family="sans-serif", zorder=3)


def vertical_arrow(x, y_top, y_bottom):
    """Draw a straight downward arrow."""
    ax.plot([x, x], [y_top, y_bottom + 0.15], color=BLUE_DARK, lw=2.2, zorder=1)
    ax.plot(x, y_bottom + 0.05, marker="v", color=BLUE_DARK, markersize=10, zorder=1)


def fan_out(x_from, y_from, targets_x, y_to):
    """Draw horizontal bar from center then vertical drops to each target."""
    bar_y = (y_from + y_to) / 2 + 0.15
    # Vertical line from source down to bar
    ax.plot([x_from, x_from], [y_from, bar_y], color=BLUE_DARK, lw=2.2, zorder=1)
    # Horizontal bar spanning all targets
    ax.plot([min(targets_x), max(targets_x)], [bar_y, bar_y],
            color=BLUE_DARK, lw=2.2, zorder=1)
    # Vertical drops from bar to each target
    for tx in targets_x:
        ax.plot([tx, tx], [bar_y, y_to + 0.15], color=BLUE_DARK, lw=2.2, zorder=1)
        ax.plot(tx, y_to + 0.05, marker="v", color=BLUE_DARK, markersize=9, zorder=1)


def fan_in(sources_x, y_from, x_to, y_to):
    """Draw vertical lines up from sources to a bar, then down to target."""
    bar_y = (y_from + y_to) / 2 - 0.15
    # Vertical lines from each source up to bar
    for sx in sources_x:
        ax.plot([sx, sx], [y_from, bar_y], color=BLUE_DARK, lw=2.2, zorder=1)
    # Horizontal bar
    ax.plot([min(sources_x), max(sources_x)], [bar_y, bar_y],
            color=BLUE_DARK, lw=2.2, zorder=1)
    # Central drop from bar to target
    ax.plot([x_to, x_to], [bar_y, y_to + 0.15], color=BLUE_DARK, lw=2.2, zorder=1)
    ax.plot(x_to, y_to + 0.05, marker="v", color=BLUE_DARK, markersize=10, zorder=1)


# ============ LAYOUT ============

# Layer 1: Prompt Library
draw_box(2.5, 11.2, 5, 1.1,
         "Prompt Library",
         "100+ India-specific prompts  |  English + Vernacular")

# Arrow: Prompt Library → Query Engine
vertical_arrow(5, 11.2, 10.1)

# Layer 2: Parallel Query Engine
draw_box(2.5, 9.0, 5, 1.1,
         "Parallel Query Engine",
         "Async orchestrator  |  Per-provider rate limiting")

# Layer 3: Engine boxes
eng_y = 7.4
eng_h = 0.8
eng_w = 1.55
engines = [
    (0.35, "ChatGPT\nAPI"),
    (2.2,  "Claude\nAPI"),
    (4.05, "Gemini\nAPI"),
    (5.9,  "Perplexity\nAPI"),
    (7.75, "Google\nAI Overviews"),
]
for ex, label in engines:
    draw_small_box(ex, eng_y, eng_w, eng_h, label)

# Fan-out: Query Engine → 5 engine boxes
engine_centers = [ex + eng_w / 2 for ex, _ in engines]
fan_out(5, 9.0, engine_centers, eng_y + eng_h)

# Fan-in: 5 engine boxes → Extraction Pipeline
extract_y = 5.2
extract_h = 1.3
fan_in(engine_centers, eng_y, 5, extract_y + extract_h)

# Layer 4: Extraction Pipeline
draw_box(2.5, extract_y, 5, extract_h,
         "Extraction Pipeline",
         "Citation normalization  |  Brand detection & sentiment\n"
         "Position scoring  |  Competitor identification")

# Arrow: Extraction → PostgreSQL
vertical_arrow(5, extract_y, 4.3)

# Layer 5: PostgreSQL
pg_y = 3.2
draw_box(2.5, pg_y, 5, 1.1,
         "PostgreSQL Storage",
         "Runs, responses, citations, brand mentions, analyses",
         color=BLUE_DARK)

# Layer 6: Output boxes
out_y = 1.2
out_h = 0.9
out_w = 2.6
outputs = [
    (0.5,  "Scorecard\nDashboard (D7)"),
    (3.7,  "Content Gap\nAnalysis (D9)"),
    (6.9,  "Automated\nAlerts"),
]
for ox, label in outputs:
    draw_small_box(ox, out_y, out_w, out_h, label, color=ORANGE)

# Fan-out: PostgreSQL → 3 outputs
output_centers = [ox + out_w / 2 for ox, _ in outputs]
fan_out(5, pg_y, output_centers, out_y + out_h)

# Footer
ax.text(5, 0.4,
        "Built with: Python (async)  |  OpenAI / Anthropic / Google / Perplexity / SerpAPI  |  PostgreSQL",
        ha="center", va="center", fontsize=11, color="#666666",
        style="italic", family="sans-serif")

plt.tight_layout(pad=0.5)
out_path = "/Users/haquefarazul/Coke_GEO/coke-geo-tracker/docs/architecture.png"
fig.savefig(out_path, dpi=300, bbox_inches="tight", facecolor=WHITE)
print(f"Saved: {out_path}")
plt.close()
