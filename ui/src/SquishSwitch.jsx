import { useState } from "react";

/**
 * A two-state pill switch. Both options sit in the track and stay visible; a thumb slides under the active one.
 * The thumb travels on a spring and squashes and stretches on the way (transform only, so it stays smooth).
 *
 * Props: checked, onChange(next), label (accessible name), startContent / endContent (shown for the off / on side),
 * width, height, radius, stretch (thumb width in px at the peak of the stretch), speed (0-100, higher is faster),
 * hoverScale, colorDuration (ms), disabled, trackColor / trackOnColor, thumbColor / thumbOnColor,
 * activeColor (content on the thumb), idleColor (content on the track).
 * Reduced motion removes the movement and keeps the colour change (see styles.css).
 */
export default function SquishSwitch({
  checked, onChange, label, startContent, endContent, width = 76, height = 38, radius = height / 2, stretch = height + 2, speed = 50,
  hoverScale = 1.04, colorDuration = 320, disabled = false, trackColor, trackOnColor = trackColor, thumbColor, thumbOnColor = thumbColor,
  activeColor, idleColor,
}) {
  const [pulse, setPulse] = useState(0);
  const pad = Math.round(height * 0.11);
  const base = height - pad * 2;
  const travel = width - pad * 2 - base;
  const duration = Math.round(640 - Math.min(100, Math.max(0, speed)) * 4);

  function toggle() {
    if (disabled) return;
    setPulse((count) => count + 1);
    onChange(!checked);
  }

  const style = {
    width, height, borderRadius: radius, background: checked ? trackOnColor : trackColor,
    "--pad": `${pad}px`, "--base": `${base}px`, "--travel": `${travel}px`, "--duration": `${duration}ms`, "--color-duration": `${colorDuration}ms`,
    "--hover-scale": hoverScale, "--peak": Math.max(1, stretch / base).toFixed(3), "--active": activeColor, "--idle": idleColor,
  };
  return (
    <button type="button" role="switch" aria-checked={checked} aria-label={label} disabled={disabled} onClick={toggle} className="squish" style={style}>
      <span className="squish-thumb" style={{ transform: `translateX(${checked ? travel : 0}px)` }}>
        <span className="squish-shape" data-run={pulse > 0} key={pulse} style={{ "--origin": checked ? "left center" : "right center", borderRadius: radius, background: checked ? thumbOnColor : thumbColor }} />
      </span>
      <span className="squish-slot" data-active={!checked} aria-hidden="true">{startContent}</span>
      <span className="squish-slot" data-active={checked} aria-hidden="true">{endContent}</span>
    </button>
  );
}
