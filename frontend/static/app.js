// State Management
let currentSessionId = null;
let currentQuestionId = null;
let currentQuestionNumber = 1;
let totalQuestions = 5;

// DOM Elements
const dropzone = document.getElementById('dropzone');
const resumeFileInput = document.getElementById('resumeFileInput');
const selectedFileName = document.getElementById('selectedFileName');
const resumeRawText = document.getElementById('resumeRawText');
const candidateNameInput = document.getElementById('candidateName');
const candidateEmailInput = document.getElementById('candidateEmail');
const targetRoleSelect = document.getElementById('targetRole');
const parseResumeBtn = document.getElementById('parseResumeBtn');
const parsedSkillsContainer = document.getElementById('parsedSkillsContainer');
const skillsPillBox = document.getElementById('skillsPillBox');

const stage1 = document.getElementById('stage1-container');
const stage2 = document.getElementById('stage2-container');
const stage3 = document.getElementById('stage3-container');

const candidateEntryForm = document.getElementById('candidateEntryForm');
const answerSubmitForm = document.getElementById('answerSubmitForm');
const candidateAnswerText = document.getElementById('candidateAnswerText');
const submitAnswerBtn = document.getElementById('submitAnswerBtn');
const nextQuestionBtn = document.getElementById('nextQuestionBtn');

const interviewProgressFill = document.getElementById('interviewProgressFill');
const questionCounterText = document.getElementById('questionCounterText');
const topicBadge = document.getElementById('topicBadge');
const difficultyBadge = document.getElementById('difficultyBadge');
const groundedContextText = document.getElementById('groundedContextText');
const questionPromptText = document.getElementById('questionPromptText');
const evalFeedbackBox = document.getElementById('evalFeedbackBox');
const feedbackScoreBadge = document.getElementById('feedbackScoreBadge');
const feedbackDetailText = document.getElementById('feedbackDetailText');
const feedbackConceptsList = document.getElementById('feedbackConceptsList');

// File Upload Handlers
dropzone.addEventListener('click', () => resumeFileInput.click());

dropzone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropzone.style.borderColor = 'var(--accent-primary)';
});

dropzone.addEventListener('dragleave', () => {
  dropzone.style.borderColor = 'var(--border-color)';
});

dropzone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropzone.style.borderColor = 'var(--border-color)';
  if (e.dataTransfer.files.length) {
    handleFileUpload(e.dataTransfer.files[0]);
  }
});

resumeFileInput.addEventListener('change', () => {
  if (resumeFileInput.files.length) {
    handleFileUpload(resumeFileInput.files[0]);
  }
});

async function handleFileUpload(file) {
  selectedFileName.textContent = `Selected: ${file.name} (${Math.round(file.size / 1024)} KB)`;
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const res = await fetch('/api/interview/parse-resume', {
      method: 'POST',
      body: formData
    });
    if (res.ok) {
      const data = await res.json();
      displayParsedSkills(data);
    }
  } catch (err) {
    console.error('Error parsing resume:', err);
  }
}

parseResumeBtn.addEventListener('click', async () => {
  const text = resumeRawText.value.trim();
  if (!text) {
    alert('Please paste resume text or select a PDF first.');
    return;
  }
  const formData = new FormData();
  formData.append('raw_text', text);
  
  try {
    const res = await fetch('/api/interview/parse-resume', {
      method: 'POST',
      body: formData
    });
    if (res.ok) {
      const data = await res.json();
      displayParsedSkills(data);
    }
  } catch (err) {
    console.error('Error parsing text:', err);
  }
});

function displayParsedSkills(data) {
  if (data.name && data.name !== 'Candidate') candidateNameInput.value = data.name;
  if (data.email) candidateEmailInput.value = data.email;
  
  skillsPillBox.innerHTML = '';
  if (data.skills && data.skills.length > 0) {
    data.skills.forEach(skill => {
      const pill = document.createElement('span');
      pill.className = 'skill-pill';
      pill.textContent = skill;
      skillsPillBox.appendChild(pill);
    });
    parsedSkillsContainer.style.display = 'block';
  }
}

// Start Interview
candidateEntryForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const candidateName = candidateNameInput.value.trim();
  const email = candidateEmailInput.value.trim();
  const targetRole = targetRoleSelect.value;
  const resumeText = resumeRawText.value.trim();
  
  const startBtn = document.getElementById('startInterviewBtn');
  startBtn.disabled = true;
  startBtn.textContent = 'Initializing Knowledge Retrieval...';
  
  try {
    const res = await fetch('/api/interview/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        candidate_name: candidateName,
        email: email,
        target_role: targetRole,
        resume_text: resumeText
      })
    });
    
    if (!res.ok) throw new Error('Failed to start interview');
    const questionData = await res.json();
    
    currentSessionId = questionData.session_id;
    renderQuestion(questionData);
    
    stage1.style.display = 'none';
    stage2.style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } catch (err) {
    alert('Failed to initialize screening session: ' + err.message);
  } finally {
    startBtn.disabled = false;
    startBtn.textContent = '🚀 Start Technical Interview';
  }
});

function renderQuestion(q) {
  currentQuestionId = q.question_id;
  currentQuestionNumber = q.question_number;
  totalQuestions = q.total_questions;
  
  questionCounterText.textContent = `${q.question_number} of ${q.total_questions}`;
  interviewProgressFill.style.width = `${(q.question_number / q.total_questions) * 100}%`;
  topicBadge.textContent = q.topic;
  difficultyBadge.textContent = q.difficulty;
  groundedContextText.textContent = q.grounded_context;
  questionPromptText.textContent = q.question_text;
  
  candidateAnswerText.value = '';
  candidateAnswerText.disabled = false;
  submitAnswerBtn.style.display = 'inline-flex';
  nextQuestionBtn.style.display = 'none';
  evalFeedbackBox.style.display = 'none';
  candidateAnswerText.focus();
}

// Submit Answer
answerSubmitForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const answer = candidateAnswerText.value.trim();
  if (!answer) return;
  
  submitAnswerBtn.disabled = true;
  submitAnswerBtn.textContent = 'Evaluating response...';
  
  try {
    const res = await fetch('/api/interview/answer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: currentSessionId,
        question_id: currentQuestionId,
        answer_text: answer
      })
    });
    
    if (!res.ok) throw new Error('Evaluation request failed');
    const data = await res.json();
    
    const ev = data.evaluation;
    candidateAnswerText.disabled = true;
    submitAnswerBtn.style.display = 'none';
    
    // Display feedback
    feedbackScoreBadge.textContent = `Score: ${ev.score}/10`;
    feedbackDetailText.textContent = ev.feedback;
    
    let conceptsHtml = '';
    if (ev.key_concepts_covered && ev.key_concepts_covered.length > 0) {
      conceptsHtml += `<strong>Concepts Covered:</strong> ${ev.key_concepts_covered.join(', ')} `;
    }
    if (ev.missing_concepts && ev.missing_concepts.length > 0) {
      conceptsHtml += `<br><strong>Key Context Areas:</strong> ${ev.missing_concepts.join(', ')}`;
    }
    feedbackConceptsList.innerHTML = conceptsHtml;
    evalFeedbackBox.style.display = 'block';
    
    if (data.is_completed) {
      nextQuestionBtn.textContent = 'View Final Scorecard & Report ➔';
    } else {
      nextQuestionBtn.textContent = 'Proceed to Next Question ➔';
    }
    nextQuestionBtn.style.display = 'inline-flex';
  } catch (err) {
    alert('Error submitting answer: ' + err.message);
    submitAnswerBtn.disabled = false;
    submitAnswerBtn.textContent = 'Submit Answer';
  }
});

// Proceed to Next Question or Final Summary
nextQuestionBtn.addEventListener('click', async () => {
  if (currentQuestionNumber >= totalQuestions) {
    loadFinalScorecard();
  } else {
    try {
      const res = await fetch(`/api/interview/question/${currentSessionId}`);
      if (!res.ok) throw new Error('Failed to fetch next question');
      const nextQ = await res.json();
      renderQuestion(nextQ);
    } catch (err) {
      alert('Error loading next question: ' + err.message);
    }
  }
});

// Load Final Scorecard
async function loadFinalScorecard() {
  try {
    const res = await fetch(`/api/reports/summary/${currentSessionId}`);
    if (!res.ok) throw new Error('Failed to load summary scorecard');
    const data = await res.json();
    
    document.getElementById('scorecardCandidateName').textContent = data.candidate_name;
    document.getElementById('scorecardRoleText').textContent = data.target_role.replace(/_/g, ' ').toUpperCase() + ' TRACK';
    document.getElementById('finalScoreDisplay').innerHTML = `${data.overall_score}<span style="font-size: 20px; color: var(--text-muted);">/10</span>`;
    document.getElementById('recommendationBadge').textContent = data.hiring_recommendation;
    document.getElementById('executiveSummaryText').textContent = data.summary_report;
    
    // Strengths
    const strengthsUl = document.getElementById('strengthsList');
    strengthsUl.innerHTML = '';
    data.strengths.forEach(s => {
      const li = document.createElement('li');
      li.textContent = s;
      strengthsUl.appendChild(li);
    });
    
    // Growth Areas
    const improveUl = document.getElementById('improvementsList');
    improveUl.innerHTML = '';
    data.areas_for_improvement.forEach(i => {
      const li = document.createElement('li');
      li.textContent = i;
      improveUl.appendChild(li);
    });
    
    // Breakdown
    const breakdownBox = document.getElementById('breakdownContainer');
    breakdownBox.innerHTML = '';
    data.evaluations.forEach((ev, idx) => {
      const div = document.createElement('div');
      div.className = 'breakdown-item';
      div.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <strong style="color: var(--accent-primary);">Question ${idx + 1}</strong>
          <span style="font-weight: 700; color: ${ev.score >= 7 ? 'var(--accent-emerald)' : 'var(--accent-amber)'};">${ev.score}/10</span>
        </div>
        <p style="font-weight: 600; font-size: 14px; margin-bottom: 8px;">${ev.question_text}</p>
        <p style="font-size: 13px; color: #cbd5e1; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 6px; margin-bottom: 8px;"><em>"${ev.candidate_answer}"</em></p>
        <p style="font-size: 12px; color: var(--text-muted);">${ev.feedback}</p>
      `;
      breakdownBox.appendChild(div);
    });
    
    stage2.style.display = 'none';
    stage3.style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } catch (err) {
    alert('Error loading scorecard: ' + err.message);
  }
}

// Export JSON
document.getElementById('exportReportBtn').addEventListener('click', () => {
  if (currentSessionId) {
    window.location.href = `/api/reports/export/${currentSessionId}`;
  }
});

// Restart Screening
document.getElementById('restartScreeningBtn').addEventListener('click', () => {
  stage3.style.display = 'none';
  stage1.style.display = 'block';
  window.scrollTo({ top: 0, behavior: 'smooth' });
});
