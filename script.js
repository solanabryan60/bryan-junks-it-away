"use strict";
const calculator = document.querySelector('#calculator');
if (calculator) {
 const update = () => {
  const data = new FormData(calculator);
  const load = Number(data.get('load'));
  const kind = data.get('kind');
  const extras = data.getAll('extra');
  const special = kind === 'Heavy / construction materials' || extras.includes('Heavy / special disposal');
  const names = {150:'Small pickup',250:'¼ truck',400:'½ truck',550:'¾ truck',700:'Full truck'};
  document.querySelector('#estimate').textContent = special ? 'In-person quote' : '$' + load + (load === 150 ? '+' : '');
  document.querySelector('#estimate-caption').textContent = names[load] + ' · ' + kind;
  document.querySelector('#adjustment').textContent = special ? 'Heavy materials and special disposal need an individual assessment. Standard load prices do not cover these items.' : (extras.length || !['Curbside / driveway','Garage / ground level'].includes(data.get('access')) ? 'Access and handling may change your final price. Bryan will assess these details in person.' : 'Based on standard household junk and straightforward access.');
  const params = new URLSearchParams({load:String(load),kind,access:data.get('access'),extras:extras.join(', ')});
  document.querySelector('#schedule-estimate').href = 'schedule.html?' + params;
 };
 calculator.addEventListener('change',update);
 calculator.addEventListener('reset',()=>setTimeout(update,0));
 calculator.addEventListener('submit',event=>event.preventDefault());
 update();
}
