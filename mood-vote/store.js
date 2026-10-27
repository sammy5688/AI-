/* 資料存取：沒有 Firebase 設定時用「試看模式」（存在這台電腦的瀏覽器），
   有設定時用 Firestore。學員頁與展示頁共用。

   Firestore 資料結構（不含任何個資）：
     moodRooms/{場次}                 { round: 第幾輪, at }
     moodRooms/{場次}/votes/{裝置碼}  { mood: 選項序號, round, at }
   每支手機只有一筆，改選就覆蓋；按「重新開始」只把 round 加一，舊票自然不算。 */
(function () {
  var SDK = "https://www.gstatic.com/firebasejs/10.12.2/";
  var cfg = window.MOOD_CONFIG || {};
  var optionCount = (cfg.options || []).length;

  function safeGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function safeSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  function deviceId() {
    var id = safeGet("moodvote:device");
    if (!id) {
      id = Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
      safeSet("moodvote:device", id);
    }
    return id;
  }

  function tally(votes, round) {
    var counts = [];
    for (var i = 0; i < optionCount; i++) counts.push(0);
    votes.forEach(function (v) {
      if (v.round === round && v.mood >= 0 && v.mood < optionCount) counts[v.mood]++;
    });
    return counts;
  }

  /* ---------- 試看模式 ---------- */
  function demoStore(room) {
    var key = "moodvote:demo:" + room;
    var listeners = [];
    function read() {
      try { return JSON.parse(safeGet(key)) || { round: 1, votes: {} }; }
      catch (e) { return { round: 1, votes: {} }; }
    }
    function write(d) { safeSet(key, JSON.stringify(d)); emit(); }
    function emit() { listeners.forEach(function (fn) { fn(read()); }); }
    window.addEventListener("storage", function (e) { if (e.key === key) emit(); });
    function listen(fn) { listeners.push(fn); fn(read()); }

    return {
      mode: "demo",
      watchRound: function (cb) { listen(function (d) { cb(d.round); }); },
      watchCounts: function (cb) {
        listen(function (d) {
          var list = Object.keys(d.votes).map(function (k) { return d.votes[k]; });
          cb(tally(list, d.round), d.round);
        });
      },
      vote: function (id, mood, round) {
        var d = read(); d.votes[id] = { mood: mood, round: round }; write(d);
        return Promise.resolve();
      },
      nextRound: function (round) {
        var d = read(); d.round = round + 1; write(d); return Promise.resolve();
      },
      simulate: function (n) {
        var d = read();
        for (var i = 0; i < n; i++) {
          var r = Math.random(), m = r < .35 ? 0 : r < .65 ? 1 : r < .8 ? 2 : 3;
          d.votes["sim" + Math.random().toString(36).slice(2)] = { mood: Math.min(m, optionCount - 1), round: d.round };
        }
        write(d);
      }
    };
  }

  /* ---------- 正式模式（Firestore） ---------- */
  function liveStore(room) {
    return Promise.all([
      import(SDK + "firebase-app.js"),
      import(SDK + "firebase-firestore.js")
    ]).then(function (mods) {
      var app = mods[0].initializeApp(cfg.firebase);
      var fs = mods[1];
      var db = fs.getFirestore(app);
      var roomRef = fs.doc(db, "moodRooms", room);
      var votesRef = fs.collection(db, "moodRooms", room, "votes");

      function watchRound(cb) {
        fs.onSnapshot(roomRef, function (snap) {
          var r = snap.exists() ? snap.data().round : 1;
          cb(typeof r === "number" ? r : 1);
        });
      }

      return {
        mode: "live",
        watchRound: watchRound,
        watchCounts: function (cb) {
          var stop = null;
          watchRound(function (round) {
            if (stop) stop();
            var q = fs.query(votesRef, fs.where("round", "==", round));
            stop = fs.onSnapshot(q, function (qs) {
              var list = [];
              qs.forEach(function (d) { list.push(d.data()); });
              cb(tally(list, round), round);
            });
          });
        },
        vote: function (id, mood, round) {
          return fs.setDoc(fs.doc(votesRef, id), { mood: mood, round: round, at: fs.serverTimestamp() });
        },
        nextRound: function (round) {
          return fs.setDoc(roomRef, { round: round + 1, at: fs.serverTimestamp() });
        }
      };
    });
  }

  window.MoodStore = {
    deviceId: deviceId,
    room: function () {
      var r = new URLSearchParams(location.search).get("r") || "main";
      return r.replace(/[^\w-]/g, "").slice(0, 30) || "main";
    },
    connect: function (room) {
      var f = cfg.firebase || {};
      if (!f.apiKey || !f.projectId) return Promise.resolve(demoStore(room));
      return liveStore(room);
    }
  };
})();
