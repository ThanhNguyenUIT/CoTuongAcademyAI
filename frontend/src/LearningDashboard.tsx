import { useEffect, useState } from 'react';
import { deleteLearningProgress, getLearningProgress, getNextExercise, type ExerciseRecommendation, type LearningProgress } from './learningApi';

type Props = { learnerId: string; refreshSignal: number; onDeleted: () => void };

export default function LearningDashboard({ learnerId, refreshSignal, onDeleted }: Props) {
  const [progress, setProgress] = useState<LearningProgress | null>(null);
  const [next, setNext] = useState<ExerciseRecommendation | null>(null);
  const [error, setError] = useState('');
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    let active = true;
    setError('');
    Promise.all([getLearningProgress(learnerId), getNextExercise(learnerId, true)])
      .then(([summary, recommendation]) => {
        if (active) { setProgress(summary); setNext(recommendation); }
      })
      .catch((reason: unknown) => { if (active) setError(reason instanceof Error ? reason.message : 'Không tải được tiến độ local.'); });
    return () => { active = false; };
  }, [learnerId, refreshSignal]);

  async function clearProgress() {
    if (!window.confirm('Xóa vĩnh viễn toàn bộ tiến độ local của hồ sơ này? Hành động này không thể hoàn tác.')) return;
    setDeleting(true);
    try { await deleteLearningProgress(learnerId); onDeleted(); }
    catch (reason: unknown) { setError(reason instanceof Error ? reason.message : 'Không xóa được tiến độ.'); }
    finally { setDeleting(false); }
  }

  return <section className="learning-dashboard" aria-labelledby="learning-dashboard-title">
    <div className="dashboard-head">
      <div><p className="eyebrow">PHASE 5 · TIẾN ĐỘ CÁ NHÂN</p><h2 id="learning-dashboard-title">Ôn theo điều bạn đang luyện</h2></div>
      <div className="dashboard-actions">
        <a className="quiet-button" href={`/v1/learning/export/${encodeURIComponent(learnerId)}`} download="xiangqi-learning-progress.json">Xuất dữ liệu</a>
        <button className="quiet-button" type="button" onClick={() => void clearProgress()} disabled={deleting}>{deleting ? 'Đang xóa…' : 'Xóa tiến độ'}</button>
      </div>
    </div>
    {error && <p className="lab-error" role="alert">{error}</p>}
    <p className="dashboard-summary">{progress ? `${progress.total_attempts} lượt trả lời · ${progress.due_reviews} bài đến lịch ôn. Chỉ số phản ánh lựa chọn khớp mục tiêu bài và việc đã nhập lý do; văn bản lý do không được chấm tự động.` : 'Đang tải tiến độ…'}</p>
    {progress?.skills.length ? <div className="skill-grid">{progress.skills.map((skill) => <div className="skill-tile" key={skill.skill_id}>
      <strong>{skill.name}</strong><span>{skill.focus_aligned}/{skill.sample_size} lượt khớp mục tiêu · mẫu n={skill.sample_size}</span>
      <span>Lỗi lặp gần nhất: {skill.repeated_errors} · {skill.next_review_at ? `ôn ${new Date(skill.next_review_at).toLocaleDateString()}` : 'chưa có lịch ôn'}</span>
    </div>)}</div> : !error && <p className="privacy-note">Chưa có mẫu tiến độ. Hãy hoàn thành một bài và ghi lại lựa chọn cùng lời giải thích.</p>}
    {next && <div className="next-exercise"><div><strong>Bài nên làm tiếp: {next.exercise_id}</strong><p>{next.reason}</p><p>Kỹ năng: {next.skill_ids.join(', ')}</p></div>
      <button className="quiet-button" type="button" onClick={() => document.getElementById(`exercise-${next.exercise_id}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' })}>Mở bài gợi ý</button>
    </div>}
    <p className="privacy-note">Hồ sơ cục bộ ẩn danh trong trình duyệt này. Dữ liệu được lưu tại máy chạy backend; không có tài khoản hoặc đồng bộ đám mây. Có thể xuất hoặc xóa tại đây.</p>
  </section>;
}
