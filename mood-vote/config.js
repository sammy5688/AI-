/* 心情投票的設定檔：要改題目、選項、或接上 Firebase，只要改這個檔案。 */
window.MOOD_CONFIG = {

  /* ① Firebase 設定
     還沒填（apiKey 是空的）→ 自動進入「試看模式」，只有同一台電腦的分頁會同步。
     填好之後 → 正式模式，全場手機即時同步。
     取得方式：Firebase 主控台 → 專案設定 → 一般 → 你的應用程式 → 網頁應用程式 → SDK 設定（Config） */
  firebase: {
    apiKey: "AIzaSyAyWpIYaDJW5CGlom5iSEXYA-rHFM5yqNk",
    authDomain: "tendshine-18fa2.firebaseapp.com",
    projectId: "tendshine-18fa2",
    storageBucket: "tendshine-18fa2.firebasestorage.app",
    messagingSenderId: "1015485869736",
    appId: "1:1015485869736:web:210beec98454a691a95c9d"
  },

  /* ② 題目 */
  question: "此刻，你的心情比較像哪一種天氣？",

  /* ③ 選項（最多 6 個；順序就是畫面上的順序） */
  options: [
    { emoji: "☀️", label: "晴天",     note: "心情不錯",   color: "#E9A23B" },
    { emoji: "⛅", label: "多雲",     note: "還可以",     color: "#8FA7C9" },
    { emoji: "🌧️", label: "下雨",     note: "有點沉重",   color: "#7C68AE" },
    { emoji: "🌈", label: "雨過天晴", note: "正在好轉",   color: "#5E9C7A" }
  ],

  /* ④ 學員送出後看到的話 */
  thanks: "謝謝你的分享。每一種心情都值得被看見。"
};
