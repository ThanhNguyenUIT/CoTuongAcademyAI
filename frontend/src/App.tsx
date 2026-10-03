import Board from './Board';
import OpeningLab from './OpeningLab';

export default function App() {
  return (
    <main className="academy-app">
      <header className="academy-header">
        <a href="#home" aria-label="Học viện Cờ Tướng AI, trang chủ"><span aria-hidden="true">象</span> HỌC VIỆN CỜ TƯỚNG</a>
        <span className="prototype-badge">BẢN THỬ NGHIỆM</span>
      </header>
      <section id="home" className="board-intro">
        <p className="eyebrow">LOCAL ENGINE + AI TUTOR + LEARNING · PHASE 5</p>
        <h1>Chơi một nước.<br /><em>Hiểu cả thế cờ.</em></h1>
        <p>Di chuyển từng quân, thử phản ứng của engine local, rồi dùng các gợi ý gia sư có nguồn và được giới hạn theo bằng chứng.</p>
      </section>
      <Board />
      <OpeningLab />
      <footer className="academy-footer">Luật nước đi được xác nhận ở backend · Engine chạy local · Quy ước tọa độ: ICCS, Đỏ ở dưới.</footer>
    </main>
  );
}
