"""
HTML report generator for exploratory test results.
"""

import time
from pathlib import Path
from typing import Optional, Union

REPORT_CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       max-width: 960px; margin: 0 auto; padding: 20px; background: #0F0F23; color: #E0E0E0; }
h1 { color: #6C5CE7; border-bottom: 2px solid #6C5CE7; padding-bottom: 8px; }
h2 { color: #A29BFE; margin-top: 32px; }
.summary-box { background: #16163A; border-radius: 12px; padding: 20px; margin: 16px 0;
               border: 1px solid rgba(255,255,255,0.06); }
.summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px; }
.stat { text-align: center; padding: 12px; background: rgba(108,92,231,0.1); border-radius: 8px; }
.stat-value { font-size: 28px; font-weight: bold; color: #6C5CE7; }
.stat-label { font-size: 12px; color: #888; margin-top: 4px; }
.step { background: #16163A; border-radius: 8px; margin: 12px 0; padding: 16px;
        border: 1px solid rgba(255,255,255,0.06); }
.step-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.step-num { font-weight: bold; color: #A29BFE; }
.step-action { color: #FD79A8; font-weight: 500; }
.step-reason { color: #888; font-size: 14px; }
.step-screen { color: #FFC048; font-size: 13px; }
.screenshot { max-width: 100%; max-height: 400px; border-radius: 8px; margin-top: 8px;
              cursor: pointer; border: 1px solid rgba(255,255,255,0.08); }
.screenshot-thumb { max-width: 200px; max-height: 350px; border-radius: 6px;
                    border: 1px solid rgba(255,255,255,0.08); cursor: pointer; }
.crash-badge { display: inline-block; background: #E74C3C; color: white; padding: 2px 8px;
               border-radius: 4px; font-size: 11px; font-weight: bold; }
.step-success { color: #2ECC71; }
.step-fail { color: #E74C3C; }
.crash-list { margin: 16px 0; }
.crash-item { background: rgba(231,76,60,0.1); border-left: 3px solid #E74C3C;
              padding: 12px; margin: 8px 0; border-radius: 0 6px 6px 0;
              font-family: monospace; font-size: 12px; white-space: pre-wrap; word-break: break-all; }
.gallery { display: flex; flex-wrap: wrap; gap: 12px; margin: 16px 0; }
.screens-covered { display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0; }
.screen-chip { background: rgba(108,92,231,0.2); color: #A29BFE; padding: 4px 12px;
               border-radius: 16px; font-size: 13px; border: 1px solid rgba(108,92,231,0.3); }
.finding { background: rgba(255,192,72,0.1); border-left: 3px solid #FFC048;
           padding: 12px; margin: 8px 0; border-radius: 0 6px 6px 0; }
"""


def generate_report(result: dict, output_dir: Union[str, Path] = "assets/reports") -> Path:
    """Generate an HTML report from the runner result. Returns the file path."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"report_{timestamp}.html"

    mission = result.get("mission", "Unknown")
    duration = result.get("duration_seconds", 0)
    steps = result.get("steps", 0)
    screens = result.get("screens_visited", [])
    crashes = result.get("crashes", {})
    total_events = crashes.get("total_events", 0)
    history = result.get("history", [])

    duration_min = duration / 60
    duration_str = f"{int(duration_min)}m {int(duration % 60)}s" if duration_min >= 1 else f"{int(duration)}s"

    # Build crash summary
    crash_html = ""
    if total_events > 0:
        crash_html = '<div class="crash-list">'
        for ev in crashes.get("events", []):
            crash_html += f'<div class="crash-item">[{ev["type"]}] {ev["log"]}</div>'
        crash_html += "</div>"

    # Build step timeline
    steps_html = ""
    for step in history:
        step_num = step.get("step", "?")
        action = step.get("action", {})
        a_type = action.get("type", "?")
        a_reason = action.get("reason", "")
        screen = step.get("screen", "?")
        success = step.get("result", {}).get("success", True)
        has_crash = len(step.get("crashes", [])) > 0
        screenshot = step.get("screenshot", "")

        status_icon = "✅" if success else "❌"
        crash_badge = '<span class="crash-badge">CRASH</span>' if has_crash else ""

        # Build action detail
        action_detail = ""
        if a_type == "tap":
            action_detail = f"({action.get('x', '?')}, {action.get('y', '?')})"
        elif a_type == "text":
            action_detail = f"'{action.get('text', '')}'"
        elif a_type == "swipe":
            action_detail = f"({action.get('x1', '?')},{action.get('y1', '?')})→({action.get('x2', '?')},{action.get('y2', '?')})"
        elif a_type == "wait":
            action_detail = f"{action.get('ms', '?')}ms"

        # Use just the filename with correct relative path from reports/ to screenshots/
        ss_html = ""
        if screenshot:
            ss_html = f'<br><a href="../screenshots/{Path(screenshot).name}" target="_blank"><img src="../screenshots/{Path(screenshot).name}" class="screenshot-thumb" alt="Step {step_num}"></a>'

        steps_html += f"""
        <div class="step">
            <div class="step-header">
                <span>
                    <span class="step-num">Step {step_num}</span>
                    <span class="step-screen">[{screen}]</span>
                </span>
                <span>
                    {crash_badge}
                    <span class="{'step-success' if success else 'step-fail'}">{status_icon}</span>
                </span>
            </div>
            <div class="step-action">{a_type} {action_detail}</div>
            <div class="step-reason">{a_reason}</div>
            {ss_html}
        </div>
        """

    # Build findings
    findings_html = ""
    done_action = None
    for step in history:
        if step.get("action", {}).get("type") == "done":
            done_action = step["action"]
            break
    if done_action and done_action.get("findings"):
        for f in done_action["findings"]:
            findings_html += f'<div class="finding">🔍 {f}</div>'

    screens_chips = "".join(f'<span class="screen-chip">{s}</span>' for s in screens)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Exploratory Test Report — {mission}</title>
<style>{REPORT_CSS}</style>
</head>
<body>
<h1>🧪 Exploratory Test Report</h1>
<p style="color:#888;">Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}</p>

<div class="summary-box">
    <h2>📊 Summary</h2>
    <div class="summary-grid">
        <div class="stat"><div class="stat-value">{mission}</div><div class="stat-label">Mission</div></div>
        <div class="stat"><div class="stat-value">{duration_str}</div><div class="stat-label">Duration</div></div>
        <div class="stat"><div class="stat-value">{steps}</div><div class="stat-label">Steps</div></div>
        <div class="stat"><div class="stat-value" style="color:{'#E74C3C' if total_events > 0 else '#2ECC71'}">{total_events}</div><div class="stat-label">Crashes/Anomalies</div></div>
    </div>
</div>

<div class="summary-box">
    <h2>📱 Screens Covered</h2>
    <div class="screens-covered">
        {screens_chips if screens_chips else '<span style="color:#888;">No screen data</span>'}
    </div>
</div>

{findings_html if findings_html else ''}

<h2>🚨 Crashes & Anomalies</h2>
{crash_html if crash_html else '<div class="summary-box" style="text-align:center;color:#2ECC71;">✅ No crashes or anomalies detected</div>'}

<h2>📋 Step Timeline</h2>
{steps_html}

<script>
// Click screenshot to view full size
document.querySelectorAll('.screenshot-thumb').forEach(img => {{
    img.addEventListener('click', () => {{
        window.open(img.src, '_blank');
    }});
}});
</script>
</body>
</html>"""

    report_path.write_text(html, encoding="utf-8")
    print(f"📄 Report saved: {report_path}")
    return report_path
