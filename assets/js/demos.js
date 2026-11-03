/* Expandable demos: load on demand, preserve playback state, and fit their content. */
(() => {
  const frames = [...document.querySelectorAll('.anim-embed iframe')];

  function send(frame, type, extra = {}) {
    if (!frame.getAttribute('src') || !frame.contentWindow) return;
    frame.contentWindow.postMessage({ type, ...extra }, location.origin);
  }

  function sync(panel, frame) {
    if (panel.open && !frame.getAttribute('src') && frame.dataset.demoSrc) {
      const source = new URL(frame.dataset.demoSrc, location.href);
      if (source.origin === location.origin) frame.src = source.href;
    }
    send(frame, 'demo-visibility', { active: panel.open });
    if (panel.open) send(frame, 'demo-measure');
  }

  frames.forEach((frame) => {
    const panel = frame.closest('details.demo-panel');
    frame.addEventListener('load', () => {
      if (panel) sync(panel, frame);
      else send(frame, 'demo-measure');
    });
    if (!panel) return;
    panel.addEventListener('toggle', () => sync(panel, frame));
    sync(panel, frame);
  });

  addEventListener('message', (event) => {
    if (event.origin !== location.origin || event.data?.type !== 'anim-height') return;
    const h = event.data.h;
    if (!Number.isFinite(h) || h < 100 || h > 4096) return;
    const frame = frames.find((candidate) => candidate.contentWindow === event.source);
    if (!frame) return;
    const panel = frame.closest('details.demo-panel');
    if (panel && !panel.open) return;
    const height = `${Math.ceil(h)}px`;
    if (frame.style.height !== height) frame.style.height = height;
  });

  // A link to an individual demo should reveal it before the browser scrolls to it.
  function revealLinkedDemo() {
    const target = document.getElementById(location.hash.slice(1));
    const panel = target?.closest('details.demo-panel');
    if (panel) panel.open = true;
  }
  addEventListener('hashchange', revealLinkedDemo);
  revealLinkedDemo();
})();
