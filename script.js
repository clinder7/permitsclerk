const modal = document.getElementById('flowModal');
const form = document.getElementById('permitForm');
const steps = [...document.querySelectorAll('.form-step')];
const nextButton = document.getElementById('nextButton');
const backButton = document.getElementById('backButton');
const submitButton = document.getElementById('submitButton');
const progressBar = document.getElementById('progressBar');
const stepLabel = document.getElementById('stepLabel');
const progressPercent = document.getElementById('progressPercent');
const successState = document.getElementById('successState');
let currentStep = 1;

function openFlow(){
  modal.classList.add('open');
  modal.setAttribute('aria-hidden','false');
  document.body.style.overflow='hidden';
}
function closeFlow(){
  modal.classList.remove('open');
  modal.setAttribute('aria-hidden','true');
  document.body.style.overflow='';
}
function showStep(step){
  currentStep = step;
  steps.forEach(s => s.classList.toggle('active', Number(s.dataset.step) === step));
  const pct = step * 20;
  progressBar.style.width = `${pct}%`;
  stepLabel.textContent = `Step ${step} of 5`;
  progressPercent.textContent = `${pct}%`;
  backButton.style.visibility = step === 1 ? 'hidden' : 'visible';
  nextButton.style.display = step === 5 ? 'none' : 'inline-block';
  submitButton.style.display = step === 5 ? 'inline-block' : 'none';
  document.querySelector('.flow-shell').scrollTo({top:0,behavior:'smooth'});
}
function validateCurrentStep(){
  const active = steps[currentStep-1];
  const fields = [...active.querySelectorAll('input,select')];
  for(const field of fields){
    if(!field.checkValidity()){
      field.reportValidity();
      return false;
    }
  }
  return true;
}

document.querySelectorAll('.open-flow').forEach(el => el.addEventListener('click', openFlow));
document.querySelectorAll('.close-flow').forEach(el => el.addEventListener('click', closeFlow));
nextButton.addEventListener('click', () => { if(validateCurrentStep() && currentStep < 5) showStep(currentStep + 1); });
backButton.addEventListener('click', () => { if(currentStep > 1) showStep(currentStep - 1); });
form.addEventListener('submit', (e) => {
  e.preventDefault();
  if(!validateCurrentStep()) return;
  form.style.display='none';
  document.querySelector('.progress-wrap').style.display='none';
  successState.classList.add('show');
});
document.addEventListener('keydown', e => { if(e.key === 'Escape') closeFlow(); });
showStep(1);
