import { useEffect, useRef } from "react";

// Drifting particle field on a 2D canvas, written to follow the usage snippet the owner supplied.
// Implemented: particleColors, particleCount, particleSpread, speed, particleBaseSize, glow, twinkle, sizeRandomness,
// shape (circle | square), moveParticlesOnHover with hoverEffect "parallax", particleHoverFactor, clickBurst, intro,
// opacity, disableRotation. Accepted and ignored: depthOfField, connections, connectionDistance, hoverRadius, drift,
// driftSpeed, alphaParticles, cameraDistance, variation, lightMode.
//
// Cost model: the field is a few hundred sprites drawn with drawImage, so a frame is cheap, but it still animates
// continuously; with prefers-reduced-motion it draws once and stops.
const MAX_PIXEL_RATIO = 2;
const RESIZE_DEBOUNCE_MS = 150;
const SPRITE_SIZE = 64;
const BURST_RADIUS = 320;
const BURST_STRENGTH = 7;
const BURST_DECAY = 0.93;
const INTRO_MS = 1200;
const PARALLAX_REACH_PX = 36;
const PARALLAX_EASE = 0.06;

const hexToRgb = (hex) => {
  const value = parseInt(hex.replace("#", ""), 16);
  return [(value >> 16) & 255, (value >> 8) & 255, value & 255];
};

// One soft round sprite per colour, so drawing a particle is a single drawImage.
function makeSprite(color, glow, shape) {
  const sprite = document.createElement("canvas");
  sprite.width = sprite.height = SPRITE_SIZE;
  const context = sprite.getContext("2d");
  const [r, g, b] = hexToRgb(color);
  const middle = SPRITE_SIZE / 2;
  if (glow > 0) {
    const halo = context.createRadialGradient(middle, middle, 0, middle, middle, middle);
    halo.addColorStop(0, `rgba(${r},${g},${b},${0.55 * glow})`);
    halo.addColorStop(1, `rgba(${r},${g},${b},0)`);
    context.fillStyle = halo;
    context.fillRect(0, 0, SPRITE_SIZE, SPRITE_SIZE);
  }
  context.fillStyle = `rgb(${r},${g},${b})`;
  const core = middle * 0.3;
  if (shape === "square") context.fillRect(middle - core, middle - core, core * 2, core * 2);
  else { context.beginPath(); context.arc(middle, middle, core, 0, Math.PI * 2); context.fill(); }
  return sprite;
}

export default function Particles({
  particleColors = ["#ffffff"], particleCount = 200, particleSpread = 10, speed = 0.1, particleBaseSize = 100,
  glow = 0.5, twinkle = 0.3, moveParticlesOnHover = true, hoverEffect = "parallax", sizeRandomness = 1, shape = "circle",
  particleHoverFactor = 1, disableRotation = false, opacity = 1, clickBurst = true, intro = true,
}) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const sprites = particleColors.map((color) => makeSprite(color, glow, shape));
    const hover = moveParticlesOnHover && hoverEffect === "parallax" && !reduceMotion;
    const burstEnabled = clickBurst && !reduceMotion;
    const spread = Math.max(0.2, particleSpread / 10);
    const count = particleCount;
    const x = new Float32Array(count);
    const y = new Float32Array(count);
    const depth = new Float32Array(count);
    const size = new Float32Array(count);
    const phase = new Float32Array(count);
    const pick = new Uint8Array(count);
    const burstX = new Float32Array(count);
    const burstY = new Float32Array(count);
    const burstVx = new Float32Array(count);
    const burstVy = new Float32Array(count);
    for (let i = 0; i < count; i++) {
      x[i] = (Math.random() * 2 - 1) * spread;
      y[i] = (Math.random() * 2 - 1) * spread;
      depth[i] = Math.random();
      size[i] = (particleBaseSize / 100) * (1 + (Math.random() - 0.5) * sizeRandomness);
      phase[i] = Math.random() * Math.PI * 2;
      pick[i] = Math.floor(Math.random() * sprites.length);
    }
    const pointer = { x: 0, y: 0 };
    const eased = { x: 0, y: 0 };
    let width = 0;
    let height = 0;
    let angle = 0;
    let last = performance.now();
    const started = last;
    let frame = 0;
    let resizeTimer = 0;
    let bursting = false;

    const layout = () => {
      const rect = canvas.getBoundingClientRect();
      if (rect.width === width && rect.height === height) return false;
      width = rect.width;
      height = rect.height;
      const ratio = Math.min(window.devicePixelRatio || 1, MAX_PIXEL_RATIO);
      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round(height * ratio);
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
      return true;
    };

    const draw = (now) => {
      const dt = Math.min(64, now - last);
      last = now;
      const introProgress = intro && !reduceMotion ? Math.min(1, (now - started) / INTRO_MS) : 1;
      if (!reduceMotion && !disableRotation) angle += speed * 0.00006 * dt;
      eased.x += (pointer.x - eased.x) * PARALLAX_EASE;
      eased.y += (pointer.y - eased.y) * PARALLAX_EASE;
      const cos = Math.cos(angle);
      const sin = Math.sin(angle);
      const centerX = width / 2;
      const centerY = height / 2;
      const reachX = Math.max(width, height) / 2;
      const time = now / 1000;
      context.clearRect(0, 0, width, height);
      let burstActive = false;
      for (let i = 0; i < count; i++) {
        const rotatedX = x[i] * cos - y[i] * sin;
        const rotatedY = x[i] * sin + y[i] * cos;
        const parallax = depth[i] * PARALLAX_REACH_PX * particleHoverFactor;
        if (bursting) {
          burstX[i] += burstVx[i]; burstY[i] += burstVy[i];
          burstVx[i] *= BURST_DECAY; burstVy[i] *= BURST_DECAY;
          if (Math.abs(burstVx[i]) > 0.05 || Math.abs(burstVy[i]) > 0.05) burstActive = true;
          burstX[i] *= 0.985; burstY[i] *= 0.985;
        }
        const px = centerX + rotatedX * reachX - (hover ? eased.x * parallax : 0) + burstX[i];
        const py = centerY + rotatedY * reachX - (hover ? eased.y * parallax : 0) + burstY[i];
        if (px < -20 || py < -20 || px > width + 20 || py > height + 20) continue;
        const flicker = reduceMotion ? 1 : 1 - twinkle * (0.5 + 0.5 * Math.sin(time * (0.8 + depth[i]) * 2 + phase[i]));
        const alpha = opacity * introProgress * (0.35 + 0.65 * depth[i]) * flicker;
        const radius = SPRITE_SIZE * 0.5 * size[i] * (0.35 + 0.5 * depth[i]) * (0.4 + 0.6 * introProgress);
        context.globalAlpha = alpha;
        context.drawImage(sprites[pick[i]], px - radius, py - radius, radius * 2, radius * 2);
      }
      context.globalAlpha = 1;
      bursting = burstActive;
    };

    const tick = (now) => { draw(now); frame = requestAnimationFrame(tick); };
    const onMove = (event) => {
      pointer.x = (event.clientX / width) * 2 - 1;
      pointer.y = (event.clientY / height) * 2 - 1;
    };
    const onClick = (event) => {
      for (let i = 0; i < count; i++) {
        const px = centerFor(i).x - event.clientX;
        const py = centerFor(i).y - event.clientY;
        const distance = Math.hypot(px, py);
        if (distance < BURST_RADIUS) {
          const push = (1 - distance / BURST_RADIUS) * BURST_STRENGTH * (0.4 + 0.6 * depth[i]);
          burstVx[i] += (px / (distance || 1)) * push;
          burstVy[i] += (py / (distance || 1)) * push;
        }
      }
      bursting = true;
    };
    const centerFor = (i) => {
      const cos = Math.cos(angle); const sin = Math.sin(angle);
      const reach = Math.max(width, height) / 2;
      return { x: width / 2 + (x[i] * cos - y[i] * sin) * reach + burstX[i], y: height / 2 + (x[i] * sin + y[i] * cos) * reach + burstY[i] };
    };
    const onResize = () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => { if (layout() && reduceMotion) draw(performance.now()); }, RESIZE_DEBOUNCE_MS);
    };

    layout();
    if (reduceMotion) draw(started);
    else frame = requestAnimationFrame(tick);
    window.addEventListener("resize", onResize);
    if (hover) window.addEventListener("pointermove", onMove);
    if (burstEnabled) window.addEventListener("pointerdown", onClick);
    return () => {
      cancelAnimationFrame(frame);
      clearTimeout(resizeTimer);
      window.removeEventListener("resize", onResize);
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerdown", onClick);
    };
  }, [particleColors.join(), particleCount, particleSpread, speed, particleBaseSize, glow, twinkle, moveParticlesOnHover, hoverEffect, sizeRandomness, shape, particleHoverFactor, disableRotation, opacity, clickBurst, intro]);

  return <canvas ref={canvasRef} className="bg-canvas" aria-hidden="true" />;
}
