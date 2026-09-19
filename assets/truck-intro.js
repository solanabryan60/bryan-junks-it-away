(() => {
  const scene = document.querySelector('.truck-intro');
  if (!scene) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let queued = false;
  const render = () => {
    queued = false;
    const span = scene.offsetHeight - innerHeight;
    const progress = reduced.matches ? 1 : Math.min(1, Math.max(0, -scene.getBoundingClientRect().top / Math.max(1, span)));
    const door = Math.min(1, progress / .86);
    scene.style.setProperty('--door', door.toFixed(4));
    scene.style.setProperty('--reveal', Math.min(1, progress / .65).toFixed(4));
    const behind = scene.querySelector('.truck-welcome');
    behind.inert = !reduced.matches && door < .82;
    scene.querySelector('.truck-scroll-text').textContent = door > .95 ? 'More room. More possibilities.' : 'Scroll to make room';
  };
  const update = () => { if (!queued) { queued = true; requestAnimationFrame(render); } };
  scene.classList.add('motion-ready');
  addEventListener('scroll', update, {passive:true});
  addEventListener('resize', update, {passive:true});
  reduced.addEventListener('change', update);
  render();
})();
