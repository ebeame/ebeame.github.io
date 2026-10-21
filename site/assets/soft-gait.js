/* Original procedural artwork inspired by the author's millipede robot footage. */
(() => {
  const canvas = document.querySelector('#soft-gait');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  const button = document.querySelector('.gait-toggle');
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let paused = motion.matches;
  let visible = true;
  let time = 0;
  let last = 0;
  let frame = 0;
  let ratio = 1;
  const tau = Math.PI * 2;
  const sceneWidth = 640;
  const sceneHeight = 430;
  const robotScale = 1.35;
  const bodyLength = 195 * robotScale;
  // One period of an invisible S-curve, joined smoothly across the canvas edges.
  const route = [];
  let routeLength = 0;
  for (let i = 0; i <= 960; i++) {
    const u = i / 960;
    const p = {x: sceneWidth * u, y: sceneHeight / 2 + 82 * Math.sin(u * tau)};
    if (i) routeLength += Math.hypot(p.x - route[i - 1].x, p.y - route[i - 1].y);
    route.push({...p, distance: routeLength});
  }

  function onRoute(distance) {
    const period = Math.floor(distance / routeLength);
    distance -= period * routeLength;
    let low = 0, high = route.length - 1;
    while (low + 1 < high) {
      const middle = (low + high) >> 1;
      if (route[middle].distance < distance) low = middle;
      else high = middle;
    }
    const a = route[low], b = route[high];
    const amount = (distance - a.distance) / (b.distance - a.distance);
    const length = Math.hypot(b.x - a.x, b.y - a.y);
    return {x: a.x + (b.x - a.x) * amount + period * sceneWidth, y: a.y + (b.y - a.y) * amount,
      tx: (b.x - a.x) / length, ty: (b.y - a.y) / length};
  }

  // Build each flexible appendage as a tapered ribbon, not a hinged rigid leg.
  function ribbon(points, width, fill) {
    const left = [], right = [];
    points.forEach((p, i) => {
      const before = points[Math.max(0, i - 1)];
      const after = points[Math.min(points.length - 1, i + 1)];
      const dx = after.x - before.x, dy = after.y - before.y;
      const length = Math.hypot(dx, dy) || 1;
      const half = width(i / (points.length - 1)) / 2;
      left.push({x: p.x - dy / length * half, y: p.y + dx / length * half});
      right.push({x: p.x + dy / length * half, y: p.y - dx / length * half});
    });
    ctx.beginPath();
    ctx.moveTo(left[0].x, left[0].y);
    left.slice(1).forEach(p => ctx.lineTo(p.x, p.y));
    right.reverse().forEach(p => ctx.lineTo(p.x, p.y));
    ctx.closePath();
    ctx.fillStyle = fill;
    ctx.fill();
  }

  function center(u, t) {
    const head = (300 + t * 36) % routeLength;
    const p = onRoute(head - (1 - u) * bodyLength);
    const wave = 2.4 * robotScale * Math.sin(u * tau * 0.85 - t * 1.4);
    return {...p, x: p.x - p.ty * wave, y: p.y + p.tx * wave};
  }

  function drawRobot(t, offset) {
    ctx.save();
    ctx.translate(offset, 0);

    const legs = [];
    for (let i = 0; i < 15; i++) {
      const u = 0.045 + i / 14 * 0.91;
      const root = center(u, t);
      for (const side of [-1, 1]) {
        // Neighbouring legs are phase shifted, producing the observed wave-like gait.
        const phase = t * 2.5 - i * 0.54 + (side === 1 ? 0.55 : 0);
        const swing = Math.sin(phase);
        const bend = Math.cos(phase);
        const reach = 28 + 7 * Math.sin(u * Math.PI);
        const points = [];
        for (let j = 0; j <= 30; j++) {
          const s = j / 30;
          const curl = Math.sin(s * Math.PI / 2);
          const along = ((-14 + 12 * swing) * s + (7 + 5 * bend) * s * s * s) * robotScale;
          const across = side * (3 + reach * curl - 4 * bend * Math.sin(s * Math.PI)) * robotScale;
          points.push({x: root.x + root.tx * along - root.ty * across,
            y: root.y + root.ty * along + root.tx * across});
        }
        legs.push({points, side, root});
      }
    }

    // Soft, short shadows beneath each moving leg.
    ctx.save();
    ctx.translate(2 * robotScale, 4 * robotScale);
    ctx.filter = `blur(${2 * robotScale}px)`;
    legs.forEach(leg => ribbon(leg.points, s => 4 * robotScale * (1 - s * 0.76), 'rgba(28,66,54,.14)'));
    ctx.restore();

    legs.forEach(({points, root, side}) => {
      const tip = points[points.length - 1];
      const shade = ctx.createLinearGradient(root.x, root.y, tip.x, tip.y);
      shade.addColorStop(0, '#265a4d');
      shade.addColorStop(0.25, '#588c78');
      shade.addColorStop(0.62, '#9fb9a5');
      shade.addColorStop(1, '#3d7260');
      ribbon(points, s => 4.2 * robotScale * (1 - s * 0.78), shade);
      ctx.beginPath();
      points.forEach((p, i) => i ? ctx.lineTo(p.x - 0.7 * robotScale, p.y - 0.8 * robotScale) : ctx.moveTo(p.x - 0.7 * robotScale, p.y - 0.8 * robotScale));
      ctx.strokeStyle = 'rgba(248,255,240,.4)';
      ctx.lineWidth = 0.5 * robotScale;
      ctx.stroke();
    });

    const body = Array.from({length: 101}, (_, i) => center(i / 100, t));
    const middle = center(0.5, t);
    const bodyShade = ctx.createLinearGradient(middle.x + middle.ty * 7 * robotScale, middle.y - middle.tx * 7 * robotScale,
      middle.x - middle.ty * 7 * robotScale, middle.y + middle.tx * 7 * robotScale);
    bodyShade.addColorStop(0, '#99b7a0');
    bodyShade.addColorStop(0.24, '#487e66');
    bodyShade.addColorStop(0.58, '#174e3f');
    bodyShade.addColorStop(1, '#0d342c');
    ribbon(body, s => (8 * Math.pow(Math.sin(Math.PI * s), 0.2) + 0.7) * robotScale, bodyShade);

    // Delicate segment seams and a continuous dorsal highlight reveal the flexure.
    for (let i = 0; i < 30; i++) {
      const u = 0.025 + i / 29 * 0.95;
      const p = center(u, t);
      const half = 3.6 * robotScale * Math.pow(Math.sin(Math.PI * u), 0.2);
      ctx.beginPath();
      ctx.moveTo(p.x + p.ty * half, p.y - p.tx * half);
      ctx.quadraticCurveTo(p.x + p.tx * robotScale, p.y + p.ty * robotScale, p.x - p.ty * half, p.y + p.tx * half);
      ctx.strokeStyle = 'rgba(219,239,213,.22)';
      ctx.lineWidth = 0.65 * robotScale;
      ctx.stroke();
    }
    ctx.beginPath();
    body.forEach((p, i) => i ? ctx.lineTo(p.x + p.ty * 1.2 * robotScale, p.y - p.tx * 1.2 * robotScale) : ctx.moveTo(p.x + p.ty * 1.2 * robotScale, p.y - p.tx * 1.2 * robotScale));
    ctx.strokeStyle = 'rgba(212,230,196,.48)';
    ctx.lineWidth = robotScale;
    ctx.stroke();
    ctx.restore();
  }

  function draw(t) {
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.clearRect(0, 0, sceneWidth, sceneHeight);
    const headDistance = (300 + t * 36) % routeLength;
    const head = onRoute(headDistance);
    const tail = onRoute(headDistance - bodyLength);
    // Render translated copies of the same continuous body. At a boundary,
    // the head enters at left while the matching tail is still leaving at right.
    for (const offset of [-sceneWidth, 0, sceneWidth]) {
      if (head.x + offset < -60 * robotScale || tail.x + offset > sceneWidth + 60 * robotScale) continue;
      drawRobot(t, offset);
    }
    // Feather the artwork itself into the page, leaving the pause control crisp.
    ctx.save();
    ctx.globalCompositeOperation = 'destination-in';
    const horizontal = ctx.createLinearGradient(0, 0, sceneWidth, 0);
    horizontal.addColorStop(0, 'rgba(0,0,0,0)');
    horizontal.addColorStop(0.085, '#000');
    horizontal.addColorStop(0.915, '#000');
    horizontal.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = horizontal;
    ctx.fillRect(0, 0, sceneWidth, sceneHeight);
    const vertical = ctx.createLinearGradient(0, 0, 0, sceneHeight);
    vertical.addColorStop(0, 'rgba(0,0,0,0)');
    vertical.addColorStop(0.065, '#000');
    vertical.addColorStop(0.935, '#000');
    vertical.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = vertical;
    ctx.fillRect(0, 0, sceneWidth, sceneHeight);
    ctx.restore();
  }

  function tick(stamp) {
    frame = 0;
    if (paused || !visible || document.hidden) { last = 0; return; }
    if (last) time += Math.min((stamp - last) / 1000, 0.05);
    last = stamp;
    draw(time);
    frame = requestAnimationFrame(tick);
  }
  function sync() {
    cancelAnimationFrame(frame);
    frame = 0;
    last = 0;
    button.hidden = false;
    button.textContent = paused ? 'Play animation' : 'Pause animation';
    button.setAttribute('aria-pressed', String(paused));
    if (!paused && visible && !document.hidden) frame = requestAnimationFrame(tick);
  }
  function resize() {
    ratio = Math.min(window.devicePixelRatio || 1, 2) * Math.max(canvas.clientWidth / 640, 0.5);
    canvas.width = Math.round(sceneWidth * ratio);
    canvas.height = Math.round(sceneHeight * ratio);
    draw(time);
  }
  button.addEventListener('click', () => { paused = !paused; sync(); });
  motion.addEventListener('change', event => { paused = event.matches; sync(); });
  document.addEventListener('visibilitychange', sync);
  const observer = new IntersectionObserver(entries => { visible = entries[0].isIntersecting; sync(); });
  observer.observe(canvas);
  new ResizeObserver(resize).observe(canvas);
  resize();
  sync();
})();
