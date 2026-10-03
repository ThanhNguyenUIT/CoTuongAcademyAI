import { useEffect, useMemo, useRef, useState } from 'react';
import LearningDashboard from './LearningDashboard';
import { localLearnerId, newLearningId, submitLearningAttempt, type AttemptReceipt } from './learningApi';

type Line = { id: string; label: string; moves_iccs: string[]; review_status: string; version: string };
type PositionNode = { position_key: string; fen: string; side_to_move: 'r' | 'b'; incoming_lines: string[] };
type Edge = { from_position_key: string; move_iccs: string; to_position_key: string; line_ids: string[] };
type Annotation = { id: string; claim: string; source_refs: string[]; review_status: string; version: string };
type Step = { id: string; title: string; body: string; moves_iccs: string[]; annotation_ids: string[] };
type Choice = { id: string; text: string; move_iccs: string; feedback: string; correct: boolean; counterplay: string; counterplay_moves_iccs: string[] };
type Exercise = { id: string; fen: string; question: string; skill_tags: string[]; rubric: string[]; hint_ladder: string[]; choices: Choice[] };
type TutorEvidence = { ref: string; kind: string; review_status?: string | null; version?: string | null; engine_id?: string | null; engine_version?: string | null; depth?: number | null; moves_iccs: string[] };
type TutorAnswer = {
  trace_id: string; context_digest: string; hint_level: number; question: string; claims: Array<{ text: string; evidence_refs: string[] }>;
  candidate_moves: string[]; evidence: TutorEvidence[]; uncertainty: string; provider: string; fallback: boolean; engine_status: string;
};
type Opening = {
  opening_id: string; name_vi: string; description: string; version: string; review_status: string;
  source_refs: Array<{ id: string; title: string; url: string; note: string }>;
  lines: Line[]; annotations: Annotation[];
  lesson: { id: string; title: string; outcomes: string[]; content_version: string; review_status: string; steps: Step[]; exercises: Exercise[] };
};
type Detail = { opening: Opening; graph: { root_position_key: string; positions: PositionNode[]; edges: Edge[] } };

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(path);
  const value = await response.json() as T & { detail?: { message?: string } };
  if (!response.ok) throw new Error(value.detail?.message ?? 'Không tải được học liệu (' + response.status + ').');
  return value;
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  const value = await response.json() as T & { detail?: { message?: string } };
  if (!response.ok) throw new Error(value.detail?.message ?? 'Không lấy được gợi ý gia sư (' + response.status + ').');
  return value;
}

export default function OpeningLab() {
  const [detail, setDetail] = useState<Detail | null>(null);
  const [error, setError] = useState('');
  const [lineId, setLineId] = useState('');
  const [ply, setPly] = useState(0);
  const [stepIndex, setStepIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [reasons, setReasons] = useState<Record<string, string>>({});
  const [submitted, setSubmitted] = useState<Record<string, boolean>>({});
  const [hintLevel, setHintLevel] = useState<Record<string, number>>({});
  const [tutorAnswers, setTutorAnswers] = useState<Record<string, TutorAnswer[]>>({});
  const [tutorErrors, setTutorErrors] = useState<Record<string, string>>({});
  const [tutorLoading, setTutorLoading] = useState<Record<string, boolean>>({});
  const [learnerId] = useState(localLearnerId);
  const [practiceGameId] = useState(newLearningId);
  const [learningRefresh, setLearningRefresh] = useState(0);
  const [rubricSelfChecks, setRubricSelfChecks] = useState<Record<string, string[]>>({});
  const [attemptReceipts, setAttemptReceipts] = useState<Record<string, AttemptReceipt | undefined>>({});
  const [attemptErrors, setAttemptErrors] = useState<Record<string, string>>({});
  const [attemptSaving, setAttemptSaving] = useState<Record<string, boolean>>({});
  const submissionIds = useRef<Record<string, string>>({});

  useEffect(() => {
    void getJson<Detail>('/v1/openings/cannon-vs-screen-horse?include_experimental=true')
      .then((result) => {
        if (!result?.opening || !result?.graph) throw new Error('Dữ liệu Opening Lab không đúng hợp đồng.');
        setDetail(result);
        setLineId(result.opening.lines[0]?.id ?? '');
      })
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : 'Không tải được Opening Lab.'));
  }, []);

  const opening = detail?.opening;
  const lesson = opening?.lesson;
  const line = opening?.lines.find((item) => item.id === lineId) ?? opening?.lines[0];
  const position = useMemo(() => {
    if (!detail) return undefined;
    const key = ply === 0 ? detail.graph.root_position_key : detail.graph.edges.find((edge) =>
      edge.move_iccs === line?.moves_iccs[ply - 1] && edge.line_ids.includes(line?.id ?? '')
    )?.to_position_key;
    return detail.graph.positions.find((item) => item.position_key === key);
  }, [detail, line?.id, line?.moves_iccs, ply]);
  const currentStep = lesson?.steps[stepIndex];
  const stepAnnotations = opening?.annotations.filter((annotation) => currentStep?.annotation_ids.includes(annotation.id)) ?? [];
  const transposition = (position?.incoming_lines.length ?? 0) > 1;

  function chooseLine(id: string) { setLineId(id); setPly(0); }
  function answer(exercise: Exercise, choice: Choice) {
    setAnswers((current) => ({ ...current, [exercise.id]: choice.id }));
    setSubmitted((current) => ({ ...current, [exercise.id]: false }));
    setAttemptReceipts((current) => ({ ...current, [exercise.id]: undefined }));
    delete submissionIds.current[exercise.id];
  }

  async function checkAnswer(exercise: Exercise) {
    const selected = exercise.choices.find((choice) => choice.id === answers[exercise.id]);
    if (!lesson || !opening || !selected || attemptSaving[exercise.id]) return;
    setSubmitted((current) => ({ ...current, [exercise.id]: true }));
    setAttemptSaving((current) => ({ ...current, [exercise.id]: true }));
    setAttemptErrors((current) => ({ ...current, [exercise.id]: '' }));
    submissionIds.current[exercise.id] ??= newLearningId();
    try {
      const receipt = await submitLearningAttempt({
        learner_id: learnerId, attempt_id: submissionIds.current[exercise.id], game_id: practiceGameId,
        lesson_id: lesson.id, exercise_id: exercise.id, exercise_version: lesson.content_version,
        selected_move: selected.move_iccs, learner_reason: reasons[exercise.id] ?? '', hint_level: hintLevel[exercise.id] ?? 0,
        rubric_self_checks: rubricSelfChecks[exercise.id] ?? [], include_experimental: opening.review_status === 'experimental',
      });
      setAttemptReceipts((current) => ({ ...current, [exercise.id]: receipt }));
      setLearningRefresh((value) => value + 1);
    } catch (reason: unknown) {
      setAttemptErrors((current) => ({ ...current, [exercise.id]: reason instanceof Error ? reason.message : 'Không lưu được lượt học.' }));
    } finally {
      setAttemptSaving((current) => ({ ...current, [exercise.id]: false }));
    }
  }
  function navigateLesson(index: number) {
    const targetStep = lesson?.steps[index];
    if (!targetStep) return;
    setStepIndex(index);
    const matchingLine = opening?.lines.find((candidate) =>
      targetStep.moves_iccs.every((move, moveIndex) => candidate.moves_iccs[moveIndex] === move)
    );
    if (matchingLine) setLineId(matchingLine.id);
    setPly(targetStep.moves_iccs.length);
  }
  async function askTutor(exercise: Exercise, selected?: Choice) {
    if (!lesson || !opening || tutorLoading[exercise.id]) return;
    const previous = hintLevel[exercise.id] ?? 0;
    const next = previous + 1;
    setTutorLoading((current) => ({ ...current, [exercise.id]: true }));
    setTutorErrors((current) => ({ ...current, [exercise.id]: '' }));
    try {
      const response = await postJson<TutorAnswer>('/v1/tutor/hint', {
        lesson_id: lesson.id,
        exercise_id: exercise.id,
        fen: exercise.fen,
        hint_level: next,
        previous_hint_level: previous,
        learner_move: selected?.move_iccs,
        learner_reason: reasons[exercise.id] ?? '',
        include_experimental: opening.review_status === 'experimental',
      });
      setTutorAnswers((current) => ({ ...current, [exercise.id]: [...(current[exercise.id] ?? []), response] }));
      setHintLevel((current) => ({ ...current, [exercise.id]: next }));
    } catch (reason: unknown) {
      setTutorErrors((current) => ({ ...current, [exercise.id]: reason instanceof Error ? reason.message : 'Gia sư tạm thời không khả dụng.' }));
    } finally {
      setTutorLoading((current) => ({ ...current, [exercise.id]: false }));
    }
  }

  if (error) return <section className="opening-lab" aria-labelledby="opening-lab-title">
    <div className="lab-heading"><div><p className="eyebrow">PHASE 3 · OPENING LAB</p><h2 id="opening-lab-title">Phòng thí nghiệm khai cuộc</h2></div></div>
    <p className="lab-error" role="status">Chưa tải được học liệu: {error}</p>
  </section>;
  if (!detail || !lesson || !line) return <section className="opening-lab" aria-labelledby="opening-lab-title"><p role="status">Đang tải học liệu khai cuộc…</p></section>;

  return <>
  <LearningDashboard learnerId={learnerId} refreshSignal={learningRefresh} onDeleted={() => { setLearningRefresh((value) => value + 1); window.location.reload(); }} />
  <section className="opening-lab" aria-labelledby="opening-lab-title">
    <div className="lab-heading">
      <div><p className="eyebrow">PHASE 3 · OPENING LAB</p><h2 id="opening-lab-title">{opening.name_vi}</h2></div>
      <span className="review-badge">{opening.review_status.toUpperCase()} · v{opening.version}</span>
    </div>
    <p className="lab-intro">{opening.description}</p>
    <div className="lab-grid">
      <div className="lab-main">
        <div className="graph-card">
          <div className="card-title"><h3>Đồ thị các biến</h3><span>{detail.graph.positions.length} vị trí · {detail.graph.edges.length} nước</span></div>
          <div className="line-tabs" role="group" aria-label="Chọn biến khai cuộc">
            {opening.lines.map((candidate, index) => <button key={candidate.id} type="button" aria-pressed={candidate.id === line.id} onClick={() => chooseLine(candidate.id)}>
              {index + 1}. {candidate.label}
            </button>)}
          </div>
          <div className="graph-position" aria-live="polite">
            <span className="eyebrow">{ply === 0 ? 'VỊ TRÍ GỐC' : 'SAU ' + ply + ' NƯỚC'}</span>
            <code>{position?.fen ?? 'Đang xác định vị trí…'}</code>
            {transposition && <p className="transposition-note">Chuyển vị: vị trí này xuất hiện trong {position?.incoming_lines.length} đường khai cuộc.</p>}
            <ol className="graph-moves">{line.moves_iccs.map((move, index) => <li key={line.id + '-' + index}>
              <button type="button" aria-current={ply === index + 1 ? 'step' : undefined} onClick={() => setPly(index + 1)}>{Math.floor(index / 2) + 1}{index % 2 ? '…' : '.'} {move}</button>
            </li>)}</ol>
          </div>
          <div className="control-row"><button className="quiet-button" type="button" onClick={() => setPly((value) => Math.max(0, value - 1))} disabled={ply === 0}>Lùi một nước</button>
            <button className="quiet-button" type="button" onClick={() => setPly((value) => Math.min(line.moves_iccs.length, value + 1))} disabled={ply >= line.moves_iccs.length}>Tiến một nước</button>
            <button className="quiet-button" type="button" onClick={() => setPly(0)}>Về đầu biến</button></div>
        </div>
        <div className="lesson-card">
          <div className="card-title"><h3>{lesson.title}</h3><span>Bài {stepIndex + 1}/{lesson.steps.length}</span></div>
          <div className="lesson-progress" aria-label={'Tiến độ bài học: bước ' + (stepIndex + 1) + ' trên ' + lesson.steps.length}><span style={{ width: (((stepIndex + 1) / lesson.steps.length) * 100) + '%' }} /></div>
          <h4>{currentStep?.title}</h4><p>{currentStep?.body}</p>
          {stepAnnotations.map((annotation) => <blockquote key={annotation.id} className="annotation-note">
            <span>{annotation.review_status.toUpperCase()} · v{annotation.version}</span>{annotation.claim}
            <small>Nguồn: {annotation.source_refs.map((sourceId) => opening.source_refs.find((source) => source.id === sourceId)?.title).filter(Boolean).join('; ')}</small>
          </blockquote>)}
          <div className="control-row"><button className="quiet-button" type="button" onClick={() => navigateLesson(Math.max(0, stepIndex - 1))} disabled={stepIndex === 0}>Bước trước</button>
            <button className="quiet-button" type="button" onClick={() => navigateLesson(Math.min(lesson.steps.length - 1, stepIndex + 1))} disabled={stepIndex >= lesson.steps.length - 1}>Bước tiếp</button></div>
        </div>
      </div>
      <aside className="lab-sidebar" aria-label="Bài tập và nguồn học liệu">
        <div className="exercise-card">
          <p className="eyebrow">LEARN · PRACTICE</p><h3>Luyện suy luận</h3>
          {lesson.exercises.map((exercise) => {
            const selected = exercise.choices.find((choice) => choice.id === answers[exercise.id]);
            const hint = hintLevel[exercise.id] ?? 0;
            const receipt = attemptReceipts[exercise.id];
            return <div className="exercise" key={exercise.id} id={`exercise-${exercise.id}`}>
              <p>{exercise.question}</p>
              {exercise.choices.map((choice) => <button className={'choice-button' + (answers[exercise.id] === choice.id ? ' choice-selected' : '')} key={choice.id} type="button" onClick={() => answer(exercise, choice)} aria-pressed={answers[exercise.id] === choice.id}>{choice.text}</button>)}
              <label className="reason-label" htmlFor={'reason-' + exercise.id}>Lý do của bạn</label>
              <textarea id={'reason-' + exercise.id} className="reason-input" rows={3} maxLength={500} value={reasons[exercise.id] ?? ''} onChange={(event) => setReasons((current) => ({ ...current, [exercise.id]: event.target.value }))} placeholder="Nêu mục tiêu hoặc điều bạn muốn kiểm tra tiếp…" />
              <fieldset className="rubric-checks"><legend>Tự đánh giá · chưa được máy chấm chất lượng</legend>{exercise.rubric.map((criterion) => <label key={criterion}>
                <input type="checkbox" checked={(rubricSelfChecks[exercise.id] ?? []).includes(criterion)} onChange={(event) => setRubricSelfChecks((current) => ({ ...current, [exercise.id]: event.target.checked ? [...(current[exercise.id] ?? []), criterion] : (current[exercise.id] ?? []).filter((item) => item !== criterion) }))} />{criterion}
              </label>)}</fieldset>
              <div className="control-row"><button className="quiet-button" type="button" onClick={() => void askTutor(exercise, selected)} disabled={hint >= 3 || tutorLoading[exercise.id] || (hint === 2 && (!selected || !(reasons[exercise.id] ?? '').trim()))}>{tutorLoading[exercise.id] ? 'Đang nghĩ…' : 'Gia sư · gợi ý ' + (hint + 1)}</button>
                <button className="quiet-button" type="button" onClick={() => void checkAnswer(exercise)} disabled={!selected || !(reasons[exercise.id] ?? '').trim() || attemptSaving[exercise.id]}>{attemptSaving[exercise.id] ? 'Đang lưu…' : attemptErrors[exercise.id] ? 'Thử lưu lại' : 'Kiểm tra câu trả lời'}</button>
                {submitted[exercise.id] && <button className="quiet-button" type="button" onClick={() => { setAnswers((current) => ({ ...current, [exercise.id]: '' })); setReasons((current) => ({ ...current, [exercise.id]: '' })); setSubmitted((current) => ({ ...current, [exercise.id]: false })); setHintLevel((current) => ({ ...current, [exercise.id]: 0 })); setTutorAnswers((current) => ({ ...current, [exercise.id]: [] })); setRubricSelfChecks((current) => ({ ...current, [exercise.id]: [] })); setAttemptReceipts((current) => ({ ...current, [exercise.id]: undefined })); setAttemptErrors((current) => ({ ...current, [exercise.id]: '' })); delete submissionIds.current[exercise.id]; }}>Thử lại</button>}</div>
              {attemptErrors[exercise.id] && <p className="lab-error" role="alert">Không lưu được tiến độ: {attemptErrors[exercise.id]}</p>}
              {receipt && <p className="attempt-receipt" role="status">Đã lưu · {receipt.outcome.points}/{receipt.outcome.points_possible} tiêu chí quan sát được · {receipt.outcome.focus_aligned ? 'lựa chọn khớp mục tiêu bài' : 'bài này cần luyện lại'} · lịch ôn {new Date(receipt.outcome.review_due_at).toLocaleDateString()}. Lý do chỉ được tính là có/không, không chấm chất lượng.</p>}
              {tutorErrors[exercise.id] && <p className="lab-error" role="alert">{tutorErrors[exercise.id]}</p>}
              {(tutorAnswers[exercise.id] ?? []).map((tutorAnswer) => <div className="answer-feedback tutor-feedback" key={tutorAnswer.trace_id} role="status">
                <strong>Gia sư · tầng {tutorAnswer.hint_level}{tutorAnswer.fallback ? ' · chế độ dự phòng' : ''}</strong>
                <p>{tutorAnswer.question}</p>
                {tutorAnswer.claims.map((claim, index) => <p key={index}>{claim.text}</p>)}
                {tutorAnswer.candidate_moves.length > 0 && <p><strong>Biến được xác minh:</strong> {tutorAnswer.candidate_moves.join(', ')}</p>}
                <p className="source-version">Bằng chứng: {tutorAnswer.evidence.map((item) => item.kind === 'engine' ? `${item.engine_id} ${item.engine_version}, depth ${item.depth}: ${item.moves_iccs.join(' ')}` : `${item.kind} · ${item.review_status ?? 'verified'}`).join(' · ')}</p>
                <p className="tutor-uncertainty">{tutorAnswer.uncertainty}</p>
              </div>)}
              {selected && submitted[exercise.id] && <div className={'answer-feedback' + (selected.correct ? ' answer-correct' : ' answer-review')} role="status">
                <strong>{selected.correct ? 'Nước minh họa hợp lệ' : 'Thử phương án khác'}</strong><p>{selected.feedback}</p>
                <p><strong>{selected.correct ? 'Bước tiếp:' : 'Phản công / kiểm tra tiếp:'}</strong> {selected.counterplay}</p>
                <p className="counterplay-line"><strong>Chuỗi nước đã kiểm tra luật:</strong> {selected.move_iccs} {selected.counterplay_moves_iccs.join(' ')}</p>
                <div className="rubric"><strong>Tự kiểm tra lý do của bạn:</strong><ul>{exercise.rubric.map((criterion) => <li key={criterion}>{criterion}</li>)}</ul></div>
              </div>}
            </div>;
          })}
        </div>
        <div className="sources-card"><h3>Nguồn và trạng thái duyệt</h3>
          <p>Nội dung hiện là thử nghiệm, chưa được biên tập viên chuyên môn duyệt.</p>
          <ul>{opening.source_refs.map((source) => <li key={source.id}><a href={source.url} target="_blank" rel="noreferrer">{source.title}</a><small>{source.note}</small></li>)}</ul>
          <p className="source-version">Bài {lesson.review_status} · phiên bản {lesson.content_version}</p>
        </div>
      </aside>
    </div>
  </section>
  </>;
}
