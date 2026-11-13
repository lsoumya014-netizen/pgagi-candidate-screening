import { useState } from 'react';
import Head from 'next/head';

export default function Home() {
  const [step, setStep] = useState(1);
  const [candidate, setCandidate] = useState({ name: 'Soumya L', email: 'lsoumya014@gmail.com', role: 'backend_engineer' });
  const [session, setSession] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [answer, setAnswer] = useState('');
  const [evalResult, setEvalResult] = useState(null);
  const [summary, setSummary] = useState(null);

  const startInterview = async (e) => {
    e.preventDefault();
    const res = await fetch('http://localhost:8000/api/interview/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        candidate_name: candidate.name,
        email: candidate.email,
        target_role: candidate.role,
        resume_text: "Python, FastAPI, SQL, Docker, RAG"
      })
    });
    const data = await res.json();
    setSession(data.session_id);
    setCurrentQuestion(data);
    setStep(2);
  };

  const submitAnswer = async (e) => {
    e.preventDefault();
    const res = await fetch('http://localhost:8000/api/interview/answer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: session,
        question_id: currentQuestion.question_id,
        answer_text: answer
      })
    });
    const data = await res.json();
    setEvalResult(data.evaluation);
    if (data.is_completed) {
      loadSummary();
    }
  };

  const nextQuestion = async () => {
    setEvalResult(null);
    setAnswer('');
    const res = await fetch(`http://localhost:8000/api/interview/question/${session}`);
    const nextQ = await res.json();
    setCurrentQuestion(nextQ);
  };

  const loadSummary = async () => {
    const res = await fetch(`http://localhost:8000/api/reports/summary/${session}`);
    const data = await res.json();
    setSummary(data);
    setStep(3);
  };

  return (
    <div style={{ background: '#0b0f19', color: '#f8fafc', minHeight: '100vh', padding: '40px 20px', fontFamily: 'sans-serif' }}>
      <Head>
        <title>PG-AGI | AI-Powered Screening System (Next.js)</title>
      </Head>
      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #263554', paddingBottom: '20px', marginBottom: '30px' }}>
          <h1 style={{ fontSize: '24px', fontWeight: 800 }}>PG-AGI Screening System</h1>
          <span style={{ background: '#10b98122', color: '#10b981', padding: '6px 14px', borderRadius: '20px', fontSize: '13px' }}>● RAG Active</span>
        </header>

        {step === 1 && (
          <form onSubmit={startInterview} style={{ background: '#182238', padding: '30px', borderRadius: '16px', border: '1px solid #263554' }}>
            <h2 style={{ marginBottom: '15px' }}>Candidate Setup & Role Selection</h2>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', fontSize: '13px', marginBottom: '6px' }}>Candidate Name</label>
              <input value={candidate.name} onChange={(e) => setCandidate({...candidate, name: e.target.value})} style={{ width: '100%', padding: '10px', background: '#131c2e', border: '1px solid #263554', color: '#fff', borderRadius: '8px' }} />
            </div>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', fontSize: '13px', marginBottom: '6px' }}>Target Role</label>
              <select value={candidate.role} onChange={(e) => setCandidate({...candidate, role: e.target.value})} style={{ width: '100%', padding: '10px', background: '#131c2e', border: '1px solid #263554', color: '#fff', borderRadius: '8px' }}>
                <option value="backend_engineer">Backend Engineering</option>
                <option value="ai_ml_engineer">AI / Machine Learning Engineer</option>
                <option value="data_science_ml">Data Science / Applied ML</option>
              </select>
            </div>
            <button type="submit" style={{ background: '#6366f1', color: '#fff', padding: '12px 24px', borderRadius: '8px', border: 'none', fontWeight: 700, cursor: 'pointer' }}>Start Technical Interview</button>
          </form>
        )}

        {step === 2 && currentQuestion && (
          <div style={{ background: '#182238', padding: '30px', borderRadius: '16px', border: '1px solid #263554' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '15px' }}>
              <span style={{ color: '#6366f1', fontWeight: 700 }}>Question {currentQuestion.question_number} of {currentQuestion.total_questions}</span>
              <span style={{ background: '#10b98122', color: '#10b981', padding: '4px 10px', borderRadius: '12px', fontSize: '12px' }}>{currentQuestion.topic}</span>
            </div>
            <div style={{ background: '#0b0f19', padding: '12px', borderRadius: '8px', fontSize: '12px', color: '#94a3b8', marginBottom: '15px' }}>
              📚 Grounded Reference: {currentQuestion.grounded_context}
            </div>
            <h3 style={{ fontSize: '17px', lineHeight: '1.5', marginBottom: '20px' }}>{currentQuestion.question_text}</h3>
            <form onSubmit={submitAnswer}>
              <textarea value={answer} onChange={(e) => setAnswer(e.target.value)} disabled={!!evalResult} rows={6} placeholder="Type your technical answer here..." style={{ width: '100%', padding: '12px', background: '#131c2e', border: '1px solid #263554', color: '#fff', borderRadius: '8px', marginBottom: '15px' }} required />
              {!evalResult ? (
                <button type="submit" style={{ background: '#6366f1', color: '#fff', padding: '10px 20px', borderRadius: '8px', border: 'none', fontWeight: 700, cursor: 'pointer' }}>Submit Answer</button>
              ) : (
                <div>
                  <div style={{ background: '#10b98115', border: '1px solid #10b98144', padding: '15px', borderRadius: '8px', marginBottom: '15px' }}>
                    <strong style={{ color: '#10b981' }}>Score: {evalResult.score}/10</strong>
                    <p style={{ marginTop: '5px' }}>{evalResult.feedback}</p>
                  </div>
                  <button type="button" onClick={step === 3 ? null : nextQuestion} style={{ background: '#10b981', color: '#fff', padding: '10px 20px', borderRadius: '8px', border: 'none', fontWeight: 700, cursor: 'pointer' }}>Next Question ➔</button>
                </div>
              )}
            </form>
          </div>
        )}

        {step === 3 && summary && (
          <div style={{ background: '#182238', padding: '30px', borderRadius: '16px', border: '1px solid #263554' }}>
            <h2 style={{ fontSize: '24px' }}>Interview Scorecard: {summary.overall_score} / 10 ({summary.percentage}%)</h2>
            <p style={{ color: '#10b981', fontWeight: 700, margin: '10px 0 20px' }}>Recommendation: {summary.hiring_recommendation}</p>
            <p style={{ background: '#131c2e', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>{summary.summary_report}</p>
            <button onClick={() => setStep(1)} style={{ background: '#263554', color: '#fff', padding: '10px 20px', borderRadius: '8px', border: 'none', cursor: 'pointer' }}>↺ Restart</button>
          </div>
        )}
      </div>
    </div>
  );
}
