// Terroir HUB — 共通features.js（お気に入り・教科書ゲート・サクラ制限・クエスト等）
// ジャンル共通: window.THUB_CONFIG で色・パス・ジャンルを切替

(function(){
  'use strict';

  // ══════════════════════════════════════
  // Config parameterization
  // ══════════════════════════════════════
  var CFG = window.THUB_CONFIG || {};
  var GENRE = CFG.genre || 'sake';
  var BRAND_COLOR = CFG.brandColor || '#B8452A';
  var BASE_PATH = CFG.basePath || '/sake';
  var API_BASE = CFG.apiBase || '';

  function escHtml(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');}

  // ══════════════════════════════════════
  // 1. お気に入り保存
  // ══════════════════════════════════════
  var FAV_KEY = 'thub_favorites';

  function getFavs(){
    return JSON.parse(localStorage.getItem(FAV_KEY) || '[]');
  }
  function saveFavs(favs){
    localStorage.setItem(FAV_KEY, JSON.stringify(favs));
  }

  window.thubToggleFav = async function(breweryId, breweryName){
    // ログインチェック
    if(!window.thubAuth || !window.thubAuth.isLoggedIn){
      if(typeof showAuth === 'function') showAuth('login');
      return;
    }

    var favs = getFavs();
    var idx = favs.findIndex(function(f){ return f.brewery_id === breweryId; });

    if(idx >= 0){
      // 削除
      favs.splice(idx, 1);
      saveFavs(favs);
      updateFavButton(breweryId, false);
      showFavToast('お気に入りから削除しました');

      // Supabase削除
      if(window.thubAuth.supabase){
        window.thubAuth.supabase.from('favorites')
          .delete()
          .eq('user_id', window.thubAuth.user.id)
          .eq('brewery_id', breweryId);
      }
    } else {
      // 追加
      favs.push({ brewery_id: breweryId, brewery_name: breweryName, timestamp: new Date().toISOString() });
      saveFavs(favs);
      updateFavButton(breweryId, true);
      showFavToast('お気に入りに追加しました ❤');

      // Supabase保存 (genre-aware)
      if(window.thubAuth.supabase){
        window.thubAuth.supabase.from('favorites').insert({
          user_id: window.thubAuth.user.id,
          brewery_id: breweryId,
          brewery_name: breweryName,
          genre: GENRE
        });
      }

      // Track
      if(window.thub) window.thub.favorite(breweryId, breweryName);
    }
  };

  function updateFavButton(breweryId, isFav){
    var btn = document.getElementById('fav-btn-' + breweryId);
    if(btn){
      btn.textContent = isFav ? '❤ お気に入り済み' : '🤍 お気に入り';
      btn.style.color = isFav ? '#e05c5c' : '#999';
      btn.style.borderColor = isFav ? '#e05c5c' : '#ddd';
    }
    // Generic button (on brewery pages)
    var genBtn = document.getElementById('fav-btn');
    if(genBtn){
      genBtn.textContent = isFav ? '❤ お気に入り済み' : '🤍 お気に入りに追加';
      genBtn.style.color = isFav ? '#e05c5c' : '#999';
      genBtn.style.borderColor = isFav ? '#e05c5c' : '#ddd';
    }
  }

  window.thubIsFav = function(breweryId){
    return getFavs().some(function(f){ return f.brewery_id === breweryId; });
  };

  // お気に入り一覧表示
  window.thubShowFavs = function(){
    var favs = getFavs();
    var content = '';
    if(favs.length === 0){
      content = '<div style="text-align:center;padding:32px;color:#aaa;font-size:13px;">まだお気に入りがありません</div>';
    } else {
      content = favs.map(function(f){
        return '<div style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid #f0f0f0;">' +
          '<div style="flex:1;font-size:13px;font-weight:500;color:#333;">' + escHtml(f.brewery_name) + '</div>' +
          '<button data-fav-id="' + escHtml(f.brewery_id) + '" data-fav-name="' + escHtml(f.brewery_name) + '" style="background:none;border:none;color:#e05c5c;font-size:12px;cursor:pointer;">削除</button>' +
        '</div>';
      }).join('');
    }

    var modal = document.createElement('div');
    modal.id = 'fav-modal';
    modal.style.cssText = 'position:fixed;inset:0;z-index:700;background:rgba(0,0,0,0.4);backdrop-filter:blur(8px);display:flex;align-items:center;justify-content:center;';
    modal.onclick = function(e){ if(e.target === modal) modal.remove(); };
    modal.innerHTML = '<div style="background:#fff;border-radius:14px;max-width:440px;width:calc(100% - 32px);padding:28px;box-shadow:0 16px 48px rgba(0,0,0,0.12);max-height:85vh;overflow-y:auto;">' +
      '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">' +
        '<div style="font-family:\'Shippori Mincho\',serif;font-size:18px;font-weight:600;">❤ お気に入り</div>' +
        '<button onclick="this.closest(\'#fav-modal\').remove()" style="background:#fafaf8;border:none;width:26px;height:26px;border-radius:6px;cursor:pointer;color:#999;font-size:13px;">✕</button>' +
      '</div>' +
      '<div>' + content + '</div>' +
    '</div>';
    document.body.appendChild(modal);
    modal.addEventListener('click', function(e){
      var btn = e.target.closest('[data-fav-id]');
      if(btn){ thubToggleFav(btn.dataset.favId, btn.dataset.favName); modal.remove(); }
    });
  };

  function showFavToast(msg){
    var toast = document.createElement('div');
    toast.style.cssText = 'position:fixed;bottom:80px;left:50%;transform:translateX(-50%);background:#333;color:#fff;padding:10px 20px;border-radius:8px;font-size:13px;z-index:800;animation:fadeInUp 0.3s ease;';
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(function(){ toast.style.opacity = '0'; toast.style.transition = 'opacity 0.3s'; setTimeout(function(){ toast.remove(); }, 300); }, 2000);
  }

  // ══════════════════════════════════════
  // 2. サクラ利用回数制限 (Credit System)
  // ══════════════════════════════════════
  function getPlan(){
    if(window.thubAuth && window.thubAuth.plan) return window.thubAuth.plan;
    return 'free';
  }

  // ── DB-backed credit system ──
  // Credits are now managed in Supabase via consume_credit/get_credits RPCs
  // We keep a sessionStorage cache for display purposes only
  function getCachedCredits() {
    try {
      var c = JSON.parse(sessionStorage.getItem('thub_credits_cache') || '{}');
      if (c.ok) return { remaining: c.remaining || 0, bonus: c.bonus || 0, plan: c.plan || 'free' };
    } catch(e) {}
    return { remaining: 0, bonus: 0, plan: 'free' };
  }

  function estimateSakuraUnits(text){
    var length = (text || '').trim().length;
    if(!length) return 0;
    return Math.max(1, Math.min(3, Math.ceil(length / 120)));
  }

  // ── Anonymous credits (localStorage-based, unchanged) ──
  var ANON_CREDIT_KEY = 'thub_anon_credits';

  function getAnonCredits(){
    var data = JSON.parse(localStorage.getItem(ANON_CREDIT_KEY) || '{}');
    var month = new Date().toISOString().slice(0,7);
    if(data.month !== month){
      var limit = window.innerWidth > 700 ? 8 : 3; // PC=8回, スマホ=3回
      return { month: month, remaining: limit, used: 0 };
    }
    return data;
  }
  function saveAnonCredits(c){
    localStorage.setItem(ANON_CREDIT_KEY, JSON.stringify(c));
  }

  // ── Legacy localStorage credits (kept as fallback / offline) ──
  var CREDIT_KEY = 'thub_credits';
  var BONUS_KEY = 'thub_bonus_credits';

  function getCredits(){
    var data = JSON.parse(localStorage.getItem(CREDIT_KEY) || '{}');
    var month = new Date().toISOString().slice(0,7);
    if(data.month !== month){
      var plan = getPlan();
      var base = plan === 'premium' ? 300 : plan === 'pro' ? 100 : 5;
      return { month: month, remaining: base, used: 0 };
    }
    return data;
  }
  function saveCredits(credits){
    localStorage.setItem(CREDIT_KEY, JSON.stringify(credits));
  }
  function getBonusCredits(){
    return parseInt(localStorage.getItem(BONUS_KEY) || '0', 10);
  }
  function saveBonusCredits(n){
    localStorage.setItem(BONUS_KEY, String(Math.max(0, n)));
  }

  // 購入完了時のクレジット加算（URLパラメータから）
  function checkCreditPurchase(){
    var params = new URLSearchParams(window.location.search);
    var purchased = parseInt(params.get('credit_purchased') || '0', 10);
    if(purchased > 0){
      if(window.thub && typeof window.thub.track === 'function'){
        window.thub.track('sakura_purchase_complete', {
          purchase_type: 'extra_credits',
          credits: purchased
        });
      }
      if(window.thub && typeof window.thub.purchase === 'function'){
        window.thub.purchase('extra_credits', purchased);
      }
      var current = getBonusCredits();
      saveBonusCredits(current + purchased);
      // Supabaseからも同期（Webhookで加算済み）
      syncBonusFromSupabase();
      showFavToast(purchased + ' クレジットを追加しました');
      // URLからパラメータ除去
      var url = new URL(window.location);
      url.searchParams.delete('credit_purchased');
      window.history.replaceState({}, '', url);
    }
  }

  function syncBonusFromSupabase(){
    if(!window.thubAuth || !window.thubAuth.supabase || !window.thubAuth.user) return;
    window.thubAuth.supabase.from('profiles')
      .select('bonus_credits')
      .eq('id', window.thubAuth.user.id)
      .single()
      .then(function(res){
        if(res.data && typeof res.data.bonus_credits === 'number'){
          saveBonusCredits(res.data.bonus_credits);
        }
      });
  }

  // ── Low credit warning / upsell helpers ──
  function showLowCreditWarning(total, plan) {
    if(window.thub && typeof window.thub.track === 'function'){
      window.thub.track('sakura_credit_warning', {
        remaining: total,
        plan: plan || 'free'
      });
    }
    var msg = '🌸 残り' + total + 'クレジットです。';
    if (plan === 'free') {
      msg += 'ここから比較や好みの深掘りまで進めるなら、Proの月100クレジットが向いています。';
    } else if (plan === 'pro') {
      msg += '続けて使うなら追加クレジット購入もできます。';
    }
    setTimeout(function(){
      if(typeof addAtlasMsg === 'function') addAtlasMsg('bot', msg);
      else if(typeof addMsg === 'function') addMsg('butler', msg);
      else if(typeof addM === 'function') addM('bot', msg);
    }, 600);
  }

  function showCreditUpsell(plan) {
    if(window.thub && typeof window.thub.track === 'function'){
      window.thub.track('sakura_trial_paywall', {
        plan: plan || 'free'
      });
    }
    var msg = '🌸 今月のクレジットを使い切りました。\n\n';
    if (plan === 'free') {
      msg += '無料5クレジットの次は、ProかPremiumを選べます。Proは月100クレジット、Premiumは月300クレジットです。';
    } else {
      msg += '続ける場合は、追加クレジット購入へ進んでください。追加分は使い切るまで有効です。';
    }
    if(typeof addAtlasMsg === 'function') addAtlasMsg('bot', msg);
    else if(typeof addMsg === 'function') addMsg('butler', msg);
    else if(typeof addM === 'function') addM('bot', msg);
    if (plan === 'free') showSakuraPlanButtons();
    else showSakuraCreditShopButton();
  }

  // PWAインストール誘導モーダル
  function showPwaPrompt(){
    var modal = document.createElement('div');
    modal.id = 'pwa-prompt';
    modal.style.cssText = 'position:fixed;inset:0;z-index:700;background:rgba(0,0,0,0.5);backdrop-filter:blur(8px);display:flex;align-items:center;justify-content:center;padding:16px;';
    modal.onclick = function(e){ if(e.target === modal) modal.remove(); };
    modal.innerHTML = '<div style="background:#fff;border-radius:16px;max-width:400px;width:100%;padding:32px;text-align:center;box-shadow:0 16px 48px rgba(0,0,0,0.15);">' +
      '<div style="font-size:48px;margin-bottom:12px;">🌸</div>' +
      '<div style="font-family:Shippori Mincho,serif;font-size:20px;font-weight:700;color:#333;margin-bottom:8px;">アプリで使おう</div>' +
      '<div style="font-size:13px;color:#888;line-height:1.8;margin-bottom:20px;">AIサクラはアプリ版でご利用いただけます。<br>ホーム画面に追加してください。</div>' +
      '<div style="background:#fafaf8;border-radius:10px;padding:14px;margin-bottom:16px;text-align:left;font-size:12px;color:#555;line-height:2;">' +
        '<strong>追加方法：</strong><br>' +
        '① 下部の共有ボタン <span style="font-size:16px;">&#x2191;</span> をタップ<br>' +
        '② 「ホーム画面に追加」を選択' +
      '</div>' +
      '<button onclick="this.closest(\'#pwa-prompt\').remove()" style="background:' + BRAND_COLOR + ';color:#fff;border:none;padding:10px 24px;border-radius:8px;font-size:14px;cursor:pointer;font-weight:500;">閉じる</button>' +
    '</div>';
    document.body.appendChild(modal);
  }

  // チャット内にPWAインストールTIPを表示
  function showPwaTip(i18n){
    if(!i18n) return;
    var chat = document.getElementById('atlas-chat') || document.getElementById('chat') || document.getElementById('pc');
    if(!chat) return;
    if(isPWA()) return; // 既にPWAなら不要
    var div = document.createElement('div');
    div.style.cssText = 'background:#f0f9ff;border:1px solid #bae6fd;border-radius:12px;padding:14px 16px;margin:8px 0;';
    div.innerHTML = '<div style="font-size:13px;font-weight:600;color:#0369a1;margin-bottom:6px;">' + escHtml(i18n.pwaTitle) + '</div>' +
      '<div style="font-size:12px;color:#555;margin-bottom:8px;">' + escHtml(i18n.pwaDesc) + '</div>' +
      '<div style="font-size:11px;color:#888;white-space:pre-line;line-height:1.8;">' + escHtml(i18n.pwaHow) + '</div>';
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
  }

  function showSakuraLineButton(){
    var chat = document.getElementById('atlas-chat') || document.getElementById('chat') || document.getElementById('pc');
    if(!chat) return;
    var div = document.createElement('div');
    div.style.cssText = 'display:flex;flex-direction:column;gap:10px;align-items:center;padding:16px;';
    div.innerHTML = '<a href="/api/line-login" style="display:flex;align-items:center;justify-content:center;gap:10px;background:#06C755;color:#fff;border:none;padding:14px 24px;border-radius:12px;font-size:15px;font-weight:700;cursor:pointer;text-decoration:none;width:100%;max-width:300px;box-shadow:0 4px 12px rgba(6,199,85,0.3);"><svg width="22" height="22" viewBox="0 0 24 24" fill="white"><path d="M12 2C6.48 2 2 5.82 2 10.5c0 4.01 3.56 7.37 8.36 8.17.33.07.78.22.89.5.1.26.07.66.03.92l-.14.87c-.04.26-.2 1.02.89.56s5.93-3.5 8.09-5.98C21.72 13.76 22 12.17 22 10.5 22 5.82 17.52 2 12 2z"/></svg>LINEでサクラを使う</a>' +
      '<div style="font-size:11px;color:#aaa;">友だち追加するだけで使えます</div>' +
      '<div style="display:flex;gap:8px;margin-top:4px;">' +
        '<button onclick="showAuth(\'login\')" style="background:none;border:1px solid #ddd;color:#888;padding:8px 16px;border-radius:8px;font-size:12px;cursor:pointer;">メールでログイン</button>' +
      '</div>';
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
  }

  function showSakuraAuthButtons(){
    var chat = document.getElementById('atlas-chat') || document.getElementById('chat') || document.getElementById('pc');
    if(!chat) return;
    var div = document.createElement('div');
    div.style.cssText = 'display:flex;flex-direction:column;gap:8px;align-items:center;padding:12px;';
    div.innerHTML = '<a href="/api/line-login" style="display:flex;align-items:center;justify-content:center;gap:8px;background:#06C755;color:#fff;border:none;padding:12px 24px;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;text-decoration:none;width:100%;max-width:280px;"><svg width="20" height="20" viewBox="0 0 24 24" fill="white"><path d="M12 2C6.48 2 2 5.82 2 10.5c0 4.01 3.56 7.37 8.36 8.17.33.07.78.22.89.5.1.26.07.66.03.92l-.14.87c-.04.26-.2 1.02.89.56s5.93-3.5 8.09-5.98C21.72 13.76 22 12.17 22 10.5 22 5.82 17.52 2 12 2z"/></svg>LINEでログイン</a>' +
      '<div style="display:flex;gap:8px;width:100%;max-width:280px;">' +
        '<button onclick="showAuth(\'signup\')" style="flex:1;background:' + BRAND_COLOR + ';color:#fff;border:none;padding:10px 16px;border-radius:8px;font-size:13px;font-weight:500;cursor:pointer;">メールで登録</button>' +
        '<button onclick="showAuth(\'login\')" style="flex:1;background:none;border:1px solid ' + BRAND_COLOR + ';color:' + BRAND_COLOR + ';padding:10px 16px;border-radius:8px;font-size:13px;cursor:pointer;">ログイン</button>' +
      '</div>';
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
  }

  // チャット内にプラン選択ボタンを表示
  function showSakuraPlanButtons(){
    var chat = document.getElementById('atlas-chat') || document.getElementById('chat') || document.getElementById('pc');
    if(!chat) return;
    var div = document.createElement('div');
    div.style.cssText = 'display:flex;flex-direction:column;gap:8px;align-items:center;padding:12px;';
    div.innerHTML = '<button onclick="if(window.thub&&window.thub.track){window.thub.track(\'sakura_upgrade_cta_click\',{placement:\'chat\',target_plan:\'pro\'})}if(window.thubAuth&&window.thubAuth.isLoggedIn){if(window.thubSubscribe)thubSubscribe(\'pro\')}else{sessionStorage.setItem(\'thub_pending_plan\',\'pro\');showAuth(\'signup\')}" style="background:' + BRAND_COLOR + ';color:#fff;border:none;padding:12px 28px;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;">Proを始める（月100クレジット / ¥500）</button>' +
      '<button onclick="if(window.thub&&window.thub.track){window.thub.track(\'sakura_upgrade_cta_click\',{placement:\'chat\',target_plan:\'premium\'})}if(window.thubAuth&&window.thubAuth.isLoggedIn){if(window.thubSubscribe)thubSubscribe(\'premium\')}else{sessionStorage.setItem(\'thub_pending_plan\',\'premium\');showAuth(\'signup\')}" style="background:#fff;color:' + BRAND_COLOR + ';border:1px solid ' + BRAND_COLOR + ';padding:12px 28px;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;">Premiumを始める（月300クレジット / ¥1,500）</button>' +
      '<a href="' + BASE_PATH + '/plans/" style="font-size:11px;color:#888;text-decoration:none;">プランの詳細を見る →</a>';
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
  }

  function showSakuraCreditShopButton(){
    var chat = document.getElementById('atlas-chat') || document.getElementById('chat') || document.getElementById('pc');
    if(!chat) return;
    var div = document.createElement('div');
    div.style.cssText = 'display:flex;flex-direction:column;gap:8px;align-items:center;padding:12px;';
    div.innerHTML = '<button onclick="if(window.thub&&window.thub.track){window.thub.track(\'sakura_upgrade_cta_click\',{placement:\'chat\',target_plan:\'extra_credits\'})}thubShowCreditShop()" style="background:' + BRAND_COLOR + ';color:#fff;border:none;padding:12px 28px;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;">追加クレジットを購入する</button>' +
      '<div style="font-size:11px;color:#888;">10クレジット ¥300から、使い切るまで有効</div>';
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
  }

  function isMobile(){ return window.innerWidth <= 700; }
  function isPWA(){ return window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true; }

  // ── thubCheckSakuraLimit: async + DB-backed for logged-in users ──
  window.thubCheckSakuraLimit = async function(question){
    if(!window.thubAuth || !window.thubAuth.isLoggedIn){
      var loginMsg = '🌸 AIサクラはログイン後にご利用いただけます。\n\n無料会員は月5クレジット、Proは月100クレジットです。';
      if(typeof addAtlasMsg === 'function') addAtlasMsg('bot', loginMsg);
      else if(typeof addMsg === 'function') addMsg('butler', loginMsg);
      else if(typeof addM === 'function') addM('bot', loginMsg);
      showSakuraAuthButtons();
      return false;
    }

    var requiredUnits = estimateSakuraUnits(question);

    // ── Logged-in: check DB balance ──
    var sb = window.thubAuth.supabase;
    if(sb){
      try {
        var res = await sb.rpc('get_credits', { p_user_id: window.thubAuth.user.id });
        if(res.data && res.data.ok){
          sessionStorage.setItem('thub_credits_cache', JSON.stringify(res.data));
          var total = (res.data.remaining || 0) + (res.data.bonus || 0);
          if(total >= requiredUnits){
            if(total > 0 && total <= 3){
              showLowCreditWarning(total, res.data.plan);
            }
            return true;
          }
          showCreditUpsell(res.data.plan || 'free');
          return false;
        }
        showCreditUpsell(res.data ? res.data.plan : 'free');
        return false;
      } catch(e){
        console.warn('[CREDITS] DB check failed:', e);
        showFavToast('クレジット残高を確認できませんでした');
        return false;
      }
    }
    return false;
  };

  window.thubGetSakuraRemaining = function(){
    // Try DB cache first
    var cached = getCachedCredits();
    if(cached.remaining > 0 || cached.bonus > 0){
      return cached.remaining + cached.bonus;
    }
    // Fallback to localStorage
    return getCachedCredits().remaining + getCachedCredits().bonus;
  };

  // クレジット購入モーダル
  window.thubShowCreditShop = function(){
    showCreditShopModal();
  };

  function showCreditShopModal(){
    var plan = getPlan();
    if(plan === 'free'){
      showFreeMessage();
      return;
    }
    if(!window.thubAuth || !window.thubAuth.isLoggedIn){
      if(typeof showAuth === 'function') showAuth('login');
      return;
    }

    var modal = document.createElement('div');
    modal.id = 'credit-shop-modal';
    modal.style.cssText = 'position:fixed;inset:0;z-index:700;background:rgba(0,0,0,0.4);backdrop-filter:blur(8px);display:flex;align-items:center;justify-content:center;';
    modal.onclick = function(e){ if(e.target === modal) modal.remove(); };

    var cached = getCachedCredits();
    var credits = { remaining: cached.remaining || 0 };
    var bonusVal = cached.bonus || 0;
    var total = credits.remaining + bonusVal;

    modal.innerHTML = '<div style="background:#fff;border-radius:14px;max-width:440px;width:calc(100% - 32px);padding:28px;text-align:center;box-shadow:0 16px 48px rgba(0,0,0,0.12);">' +
      '<div style="font-family:Shippori Mincho,serif;font-size:18px;font-weight:600;color:#333;margin-bottom:4px;">クレジット追加</div>' +
      '<div style="font-size:12px;color:#aaa;margin-bottom:20px;">現在の残り: ' + total + ' クレジット' + (bonusVal > 0 ? '（うち追加分 ' + bonusVal + '）' : '') + '</div>' +
      '<div style="display:flex;flex-direction:column;gap:10px;margin-bottom:20px;">' +
        buildPackButton(10, 300) +
        buildPackButton(30, 600) +
        buildPackButton(50, 800) +
      '</div>' +
      '<div style="font-size:11px;color:#bbb;margin-bottom:16px;">追加クレジットは使い切るまで有効です（月リセットなし）</div>' +
      '<button onclick="this.closest(\'#credit-shop-modal\').remove()" style="background:none;border:none;color:#aaa;font-size:12px;cursor:pointer;">閉じる</button>' +
      '</div>';
    document.body.appendChild(modal);
  }

  function buildPackButton(credits, price){
    var perCredit = Math.round(price / credits);
    return '<button onclick="thubBuyCredits(' + credits + ')" style="display:flex;align-items:center;justify-content:space-between;width:100%;padding:14px 16px;border:1px solid #e8e4df;border-radius:10px;background:#fafaf8;cursor:pointer;transition:border-color 0.2s;" onmouseover="this.style.borderColor=\'' + BRAND_COLOR + '\'" onmouseout="this.style.borderColor=\'#e8e4df\'">' +
      '<div style="text-align:left;">' +
        '<div style="font-size:15px;font-weight:600;color:#333;">' + credits + ' クレジット</div>' +
        '<div style="font-size:11px;color:#aaa;">1クレジットあたり約' + perCredit + '円</div>' +
      '</div>' +
      '<div style="font-size:16px;font-weight:700;color:' + BRAND_COLOR + ';">&yen;' + price.toLocaleString() + '</div>' +
      '</button>';
  }

  window.thubBuyCredits = async function(pack){
    var btn = event && event.target ? event.target.closest('button') : null;
    if(btn){ btn.disabled = true; btn.style.opacity = '0.5'; }

    try {
      var userId = window.thubAuth && window.thubAuth.user ? window.thubAuth.user.id : null;
      if(!userId){ showFavToast('ログインが必要です'); return; }
      var sessionRes = await window.thubAuth.supabase.auth.getSession();
      var accessToken = sessionRes && sessionRes.data && sessionRes.data.session ? sessionRes.data.session.access_token : '';
      if(!accessToken){ showFavToast('再ログインしてください'); return; }
      if(window.thub && typeof window.thub.track === 'function'){
        window.thub.track('sakura_purchase_start', {
          purchase_type: 'extra_credits',
          pack: Number(pack)
        });
      }

      var res = await fetch(API_BASE + '/api/create-checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + accessToken
        },
        body: JSON.stringify({ pack: String(pack) }),
      });
      var data = await res.json();
      if(data.url){
        window.location.href = data.url;
      } else {
        showFavToast('エラーが発生しました');
      }
    } catch(e){
      showFavToast('通信エラー');
    } finally {
      if(btn){ btn.disabled = false; btn.style.opacity = '1'; }
    }
  };

  // ページ読み込み時に購入完了チェック
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', checkCreditPurchase);
  } else {
    checkCreditPurchase();
  }

  function showLoginMessage(){
    var modal = document.createElement('div');
    modal.id = 'login-modal';
    modal.style.cssText = 'position:fixed;inset:0;z-index:700;background:rgba(0,0,0,0.4);backdrop-filter:blur(8px);display:flex;align-items:center;justify-content:center;';
    modal.onclick = function(e){ if(e.target === modal) modal.remove(); };
    modal.innerHTML = '<div style="background:#fff;border-radius:14px;max-width:440px;width:calc(100% - 32px);padding:28px;text-align:center;box-shadow:0 16px 48px rgba(0,0,0,0.12);">' +
      '<div style="font-size:40px;margin-bottom:12px;">🍶</div>' +
      '<div style="font-family:Shippori Mincho,serif;font-size:18px;font-weight:600;color:#333;margin-bottom:8px;">ログインでサクラが使えます</div>' +
      '<div style="font-size:13px;color:#888;margin-bottom:16px;line-height:1.7;">無料会員登録だけで、AIサクラを月5クレジットまで試せます。<br>おすすめ提案、料理ペアリング、蔵比較まで体験できます。</div>' +
      '<button onclick="if(window.thub&&window.thub.track){window.thub.track(\'sakura_upgrade_cta_click\',{placement:\'login_modal\',target_plan:\'free_signup\'})}this.closest(\'#login-modal\').remove();showAuth(\'signup\');" style="background:' + BRAND_COLOR + ';color:#fff;border:none;padding:10px 24px;border-radius:8px;font-size:13px;cursor:pointer;font-weight:500;">無料会員登録（30秒）</button>' +
      '<div style="margin-top:10px;"><button onclick="this.closest(\'#login-modal\').remove();showAuth(\'login\');" style="background:none;border:none;color:' + BRAND_COLOR + ';font-size:12px;cursor:pointer;">ログインはこちら</button></div>' +
      '<div style="margin-top:12px;"><button onclick="this.closest(\'#login-modal\').remove()" style="background:none;border:none;color:#aaa;font-size:12px;cursor:pointer;">閉じる</button></div>' +
      '</div>';
    document.body.appendChild(modal);
  }

  function showFreeMessage(){
    var modal = document.createElement('div');
    modal.id = 'free-msg-modal';
    modal.style.cssText = 'position:fixed;inset:0;z-index:700;background:rgba(0,0,0,0.4);backdrop-filter:blur(8px);display:flex;align-items:center;justify-content:center;';
    modal.onclick = function(e){ if(e.target === modal) modal.remove(); };
    modal.innerHTML = '<div style="background:#fff;border-radius:14px;max-width:440px;width:calc(100% - 32px);padding:28px;text-align:center;box-shadow:0 16px 48px rgba(0,0,0,0.12);">' +
      '<div style="font-size:40px;margin-bottom:12px;">🌸</div>' +
      '<div style="font-family:Shippori Mincho,serif;font-size:18px;font-weight:600;color:#333;margin-bottom:8px;">次のプランを選べます</div>' +
      '<div style="font-size:13px;color:#888;margin-bottom:16px;line-height:1.7;">無料5クレジットの次は、使い方に合わせてProかPremiumを選べます。<br>比較を続けるならPro、しっかり使うならPremiumです。</div>' +
      '<div style="display:flex;flex-direction:column;gap:10px;">' +
      '<button onclick="if(window.thub&&window.thub.track){window.thub.track(\'sakura_upgrade_cta_click\',{placement:\'free_modal\',target_plan:\'pro\'})}this.closest(\'#free-msg-modal\').remove();if(window.thubSubscribe)thubSubscribe(\'pro\')" style="background:' + BRAND_COLOR + ';color:#fff;border:none;padding:12px 20px;border-radius:8px;font-size:13px;cursor:pointer;font-weight:600;">Proを始める（月100クレジット / ¥500）</button>' +
      '<button onclick="if(window.thub&&window.thub.track){window.thub.track(\'sakura_upgrade_cta_click\',{placement:\'free_modal\',target_plan:\'premium\'})}this.closest(\'#free-msg-modal\').remove();if(window.thubSubscribe)thubSubscribe(\'premium\')" style="background:#fff;color:' + BRAND_COLOR + ';border:1px solid ' + BRAND_COLOR + ';padding:12px 20px;border-radius:8px;font-size:13px;cursor:pointer;font-weight:600;">Premiumを始める（月300クレジット / ¥1,500）</button>' +
      '<a href="#plans" style="font-size:12px;color:#888;text-decoration:none;">プランの詳細を見る →</a>' +
      '</div>' +
      '<div style="margin-top:12px;"><button onclick="this.closest(\'#free-msg-modal\').remove()" style="background:none;border:none;color:#aaa;font-size:12px;cursor:pointer;">閉じる</button></div>' +
      '</div>';
    document.body.appendChild(modal);
  }

  // Freeユーザー向けPro誘導バナーをチャットパネルに自動注入
  function injectProNudge(){
    var plan = getPlan();
    // index.htmlのpro-nudgeは既存なので蔵ページ用のみ注入
    var panel = document.querySelector('.overlay .panel, .overlay .chat-panel');
    if(!panel) return;
    if(document.getElementById('sakura-pro-nudge')) return;
    var sugs = panel.querySelector('#sugs, .sugs');
    var inp = panel.querySelector('.inp-row, .inp');
    var target = inp || sugs;
    if(!target) return;
    var nudge = document.createElement('div');
    nudge.id = 'sakura-pro-nudge';
    nudge.style.cssText = 'display:none;padding:6px 14px;background:linear-gradient(90deg,rgba(184,69,42,0.06),rgba(212,114,138,0.06));border-top:1px solid rgba(184,69,42,0.1);';
    nudge.innerHTML = '<div style="display:flex;align-items:center;justify-content:space-between;gap:8px;">' +
      '<div style="font-size:11px;color:#888;line-height:1.5;">' +
      '<span style="color:' + BRAND_COLOR + ';font-weight:600;">Pro</span>にすると、AIサクラがあなた専用のソムリエに' +
      '</div>' +
      '<button onclick="var m=this.closest(\'.overlay\');if(m)m.classList.remove(\'open\');if(window.thubAuth&&window.thubAuth.isLoggedIn){if(typeof thubSubscribe===\'function\')thubSubscribe(\'pro\')}else{if(typeof showAuth===\'function\')showAuth(\'signup\')}" style="flex-shrink:0;background:' + BRAND_COLOR + ';color:#fff;border:none;padding:5px 12px;border-radius:6px;font-size:10px;font-weight:600;cursor:pointer;white-space:nowrap;">月100クレジット</button>' +
      '</div>';
    target.parentNode.insertBefore(nudge, target);
  }
  // チャットパネルオープン時にnudge表示を更新（蔵ページのインラインopenPanelをラップ）
  function wrapOpenPanelForNudge(){
    if(typeof window.openPanel === 'function' && !window._openPanelWrapped){
      var orig = window.openPanel;
      window.openPanel = function(){
        orig.apply(this, arguments);
        var plan = getPlan();
        var nudge = document.getElementById('sakura-pro-nudge') || document.getElementById('pro-nudge');
        if(nudge){ nudge.style.display = plan === 'free' ? 'block' : 'none'; }
      };
      window._openPanelWrapped = true;
    }
  }

  // DOMReady時にnudgeを注入
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', function(){ injectProNudge(); wrapOpenPanelForNudge(); });
  } else {
    injectProNudge();
    wrapOpenPanelForNudge();
  }

  function showCreditModal(plan, credits){
    var modal = document.createElement('div');
    modal.id = 'credit-modal';
    modal.style.cssText = 'position:fixed;inset:0;z-index:700;background:rgba(0,0,0,0.4);backdrop-filter:blur(8px);display:flex;align-items:center;justify-content:center;';
    modal.onclick = function(e){ if(e.target === modal) modal.remove(); };

    var choicesHtml = '';
    if (plan === 'pro') {
      // Pro会員 → 2つの選択肢を明確に
      choicesHtml = '<div style="display:flex;flex-direction:column;gap:12px;margin-top:20px;">' +
        '<button onclick="this.closest(\'#credit-modal\').remove();if(typeof thubSubscribe===\'function\')thubSubscribe(\'premium\')" style="width:100%;padding:16px;background:linear-gradient(135deg,' + BRAND_COLOR + ',#8B3520);color:#fff;border:none;border-radius:12px;cursor:pointer;text-align:left;">' +
          '<div style="font-size:15px;font-weight:700;">Premiumにアップグレード</div>' +
          '<div style="font-size:12px;opacity:0.85;margin-top:4px;">月300クレジット — ¥1,500/月</div>' +
        '</button>' +
        '<button onclick="this.closest(\'#credit-modal\').remove();thubShowCreditShop();" style="width:100%;padding:16px;background:#fff;border:1.5px solid ' + BRAND_COLOR + ';border-radius:12px;cursor:pointer;text-align:left;">' +
          '<div style="font-size:15px;font-weight:700;color:' + BRAND_COLOR + ';">クレジットを追加購入</div>' +
          '<div style="font-size:12px;color:#888;margin-top:4px;">10回¥300〜 使い切るまで有効</div>' +
        '</button>' +
      '</div>';
    } else if (plan === 'premium') {
      choicesHtml = '<div style="margin-top:20px;">' +
        '<button onclick="this.closest(\'#credit-modal\').remove();thubShowCreditShop();" style="width:100%;padding:16px;background:' + BRAND_COLOR + ';color:#fff;border:none;border-radius:12px;cursor:pointer;">' +
          '<div style="font-size:15px;font-weight:700;">クレジットを追加購入</div>' +
          '<div style="font-size:12px;opacity:0.85;margin-top:4px;">10回¥300〜 使い切るまで有効</div>' +
        '</button>' +
        '<div style="font-size:11px;color:#aaa;margin-top:8px;">月額クレジットは来月リセットされます</div>' +
      '</div>';
    }

    modal.innerHTML = '<div style="background:#fff;border-radius:14px;max-width:440px;width:calc(100% - 32px);padding:28px;text-align:center;box-shadow:0 16px 48px rgba(0,0,0,0.12);">' +
      '<div style="font-size:40px;margin-bottom:12px;">🌸</div>' +
      '<div style="font-family:Shippori Mincho,serif;font-size:18px;font-weight:600;color:#333;margin-bottom:8px;">今月のクレジットを使い切りました</div>' +
      '<div style="font-size:13px;color:#888;margin-bottom:4px;line-height:1.7;">今月 ' + credits.used + 'クレジット分、サクラを利用しました。</div>' +
      choicesHtml +
      '<div style="margin-top:16px;"><button onclick="this.closest(\'#credit-modal\').remove()" style="background:none;border:none;color:#aaa;font-size:12px;cursor:pointer;">来月まで待つ</button></div>' +
      '</div>';
    document.body.appendChild(modal);
  }

  // ══════════════════════════════════════
  // 3. 教科書ゲート
  // ══════════════════════════════════════
  window.thubCheckTextbookAccess = function(chapter){
    // 第1-5章: 無料
    if(chapter <= 5) return true;

    // 第6章以降: ログイン + Pro以上
    if(!window.thubAuth || !window.thubAuth.isLoggedIn){
      showTextbookGate('login', chapter);
      return false;
    }

    var plan = getPlan();
    if(plan === 'free'){
      showTextbookGate('upgrade', chapter);
      return false;
    }

    return true; // pro or premium
  };

  function showTextbookGate(type, chapter){
    var modal = document.createElement('div');
    modal.id = 'textbook-gate';
    modal.style.cssText = 'position:fixed;inset:0;z-index:700;background:rgba(0,0,0,0.4);backdrop-filter:blur(8px);display:flex;align-items:center;justify-content:center;';
    modal.onclick = function(e){ if(e.target === modal) modal.remove(); };

    var content = type === 'login'
      ? '<div style="font-family:\'Shippori Mincho\',serif;font-size:18px;font-weight:600;color:#333;margin-bottom:8px;">ログインが必要です</div>' +
         '<div style="font-size:13px;color:#888;margin-bottom:16px;">第' + chapter + '章以降はログインしてお読みいただけます。</div>' +
         '<button onclick="this.closest(\'#textbook-gate\').remove();showAuth(\'login\');" style="background:' + BRAND_COLOR + ';color:#fff;border:none;padding:10px 24px;border-radius:8px;font-size:13px;cursor:pointer;font-weight:500;">ログイン / 無料登録</button>'
      : '<div style="font-family:\'Shippori Mincho\',serif;font-size:18px;font-weight:600;color:#333;margin-bottom:8px;">Pro プランで読めます</div>' +
         '<div style="font-size:13px;color:#888;margin-bottom:6px;">第' + chapter + '章はPro / Premiumプランの方がお読みいただけます。</div>' +
         '<div style="font-size:12px;color:#aaa;margin-bottom:16px;">教科書全12章 + AI比較 + 履歴保存</div>' +
         '<a href="#plans" onclick="this.closest(\'#textbook-gate\').remove()" style="display:inline-block;background:' + BRAND_COLOR + ';color:#fff;padding:10px 24px;border-radius:8px;text-decoration:none;font-size:13px;font-weight:500;">Proプラン（月100クレジット / ¥500）を見る</a>';

    modal.innerHTML = '<div style="background:#fff;border-radius:14px;max-width:440px;width:calc(100% - 32px);padding:28px;text-align:center;box-shadow:0 16px 48px rgba(0,0,0,0.12);">' +
      '<div style="font-size:40px;margin-bottom:12px;">📖</div>' +
      content +
      '<div style="margin-top:12px;"><button onclick="this.closest(\'#textbook-gate\').remove()" style="background:none;border:none;color:#aaa;font-size:12px;cursor:pointer;">閉じる</button></div>' +
    '</div>';
    document.body.appendChild(modal);
  }

  // ══════════════════════════════════════
  // 5. 飲酒ログ（Sake Diary）
  // ══════════════════════════════════════
  var LOG_KEY = 'thub_sake_log';

  function getLogs(){ return JSON.parse(localStorage.getItem(LOG_KEY) || '[]'); }
  function saveLogs(logs){ localStorage.setItem(LOG_KEY, JSON.stringify(logs)); }

  window.thubLogSake = function(breweryId, breweryName, brandName){
    if(!window.thubAuth || !window.thubAuth.isLoggedIn){
      if(typeof showAuth === 'function') showAuth('login');
      return;
    }
    // Show log modal
    var modal = document.createElement('div');
    modal.id = 'sake-log-modal';
    modal.style.cssText = 'position:fixed;inset:0;z-index:700;background:rgba(0,0,0,0.4);backdrop-filter:blur(8px);display:flex;align-items:center;justify-content:center;';
    modal.onclick = function(e){ if(e.target === modal) modal.remove(); };
    modal.innerHTML = '<div style="background:#fff;border-radius:14px;max-width:440px;width:calc(100% - 32px);padding:28px;box-shadow:0 16px 48px rgba(0,0,0,0.12);">' +
      '<div style="font-family:\'Shippori Mincho\',serif;font-size:18px;font-weight:600;margin-bottom:20px;">🍶 飲酒記録</div>' +
      '<div style="font-size:14px;color:#333;margin-bottom:6px;font-weight:500;">' + escHtml(breweryName) + '</div>' +
      '<input id="log-brand" type="text" value="' + escHtml(brandName || '') + '" placeholder="銘柄名" style="width:100%;padding:10px 12px;border:1px solid #ddd;border-radius:8px;font-size:14px;margin-bottom:12px;font-family:\'Noto Sans JP\',sans-serif;">' +
      '<div style="margin-bottom:12px;">' +
        '<div style="font-size:12px;color:#888;margin-bottom:6px;">評価</div>' +
        '<div id="log-stars" style="display:flex;gap:4px;font-size:28px;cursor:pointer;">' +
          '<span onclick="setLogStar(1)" data-star="1">☆</span>' +
          '<span onclick="setLogStar(2)" data-star="2">☆</span>' +
          '<span onclick="setLogStar(3)" data-star="3">☆</span>' +
          '<span onclick="setLogStar(4)" data-star="4">☆</span>' +
          '<span onclick="setLogStar(5)" data-star="5">☆</span>' +
        '</div>' +
      '</div>' +
      '<textarea id="log-memo" placeholder="メモ（味わい・感想など）" rows="3" style="width:100%;padding:10px 12px;border:1px solid #ddd;border-radius:8px;font-size:13px;resize:vertical;font-family:\'Noto Sans JP\',sans-serif;margin-bottom:16px;"></textarea>' +
      '<div style="display:flex;gap:8px;">' +
        '<button id="log-submit-btn" data-brewery-id="' + escHtml(breweryId) + '" data-brewery-name="' + escHtml(breweryName) + '" style="flex:1;background:' + BRAND_COLOR + ';color:#fff;border:none;padding:12px;border-radius:8px;font-size:14px;cursor:pointer;font-weight:500;">記録する</button>' +
        '<button onclick="this.closest(\'#sake-log-modal\').remove()" style="background:#fafaf8;border:1px solid #ddd;padding:12px 16px;border-radius:8px;font-size:13px;cursor:pointer;color:#666;">閉じる</button>' +
      '</div>' +
    '</div>';
    document.body.appendChild(modal);
    document.getElementById('log-submit-btn').addEventListener('click', function(){
      submitSakeLog(this.dataset.breweryId, this.dataset.breweryName);
    });
  };

  var logStarValue = 0;
  window.setLogStar = function(n){
    logStarValue = n;
    document.querySelectorAll('#log-stars span').forEach(function(s){
      s.textContent = parseInt(s.dataset.star) <= n ? '★' : '☆';
      s.style.color = parseInt(s.dataset.star) <= n ? BRAND_COLOR : '#ddd';
    });
  };

  window.submitSakeLog = function(breweryId, breweryName){
    var brand = document.getElementById('log-brand').value.trim();
    var memo = document.getElementById('log-memo').value.trim();
    var log = {
      brewery_id: breweryId,
      brewery_name: breweryName,
      brand: brand,
      rating: logStarValue,
      memo: memo,
      timestamp: new Date().toISOString()
    };
    var logs = getLogs();
    logs.unshift(log);
    saveLogs(logs);
    logStarValue = 0;

    // Supabase保存 (genre-aware)
    if(window.thubAuth && window.thubAuth.supabase){
      window.thubAuth.supabase.from('sake_logs').insert({
        user_id: window.thubAuth.user.id,
        brewery_id: breweryId,
        brewery_name: breweryName,
        brand_name: brand,
        rating: log.rating,
        memo: memo,
        genre: GENRE
      });
    }

    // Track
    if(window.thub) window.thub.track('sake_log', { brewery_id: breweryId, brand: brand, rating: log.rating });

    document.getElementById('sake-log-modal').remove();
    showFavToast('🍶 飲酒記録を保存しました！');
    checkBadges();
  };

  // 飲酒ログ一覧
  window.thubShowLogs = function(){
    var logs = getLogs();
    var content = '';
    if(logs.length === 0){
      content = '<div style="text-align:center;padding:32px;color:#aaa;font-size:13px;">まだ記録がありません。<br>蔵ページの「飲んだ！」ボタンから記録できます。</div>';
    } else {
      content = '<div style="font-size:12px;color:#888;margin-bottom:12px;">合計 ' + logs.length + ' 杯</div>';
      content += logs.slice(0, 30).map(function(l){
        var stars = '';
        for(var i=1;i<=5;i++) stars += i <= l.rating ? '★' : '☆';
        var date = l.timestamp ? l.timestamp.slice(0,10) : '';
        return '<div style="padding:12px 0;border-bottom:1px solid #f0f0f0;">' +
          '<div style="display:flex;justify-content:space-between;align-items:center;">' +
            '<div style="font-size:14px;font-weight:500;color:#333;">' + escHtml(l.brewery_name) + '</div>' +
            '<div style="font-size:11px;color:#aaa;">' + date + '</div>' +
          '</div>' +
          (l.brand ? '<div style="font-size:13px;color:' + BRAND_COLOR + ';margin-top:2px;">' + escHtml(l.brand) + '</div>' : '') +
          '<div style="color:' + BRAND_COLOR + ';font-size:14px;margin-top:2px;">' + stars + '</div>' +
          (l.memo ? '<div style="font-size:12px;color:#666;margin-top:4px;line-height:1.6;">' + escHtml(l.memo) + '</div>' : '') +
        '</div>';
      }).join('');
    }
    showFeatureModal('🍶 Sake Diary', content);
  };

  // ══════════════════════════════════════
  // 6. 飲みたいリスト（Wishlist）
  // ══════════════════════════════════════
  var WISH_KEY = 'thub_wishlist';

  function getWishlist(){ return JSON.parse(localStorage.getItem(WISH_KEY) || '[]'); }
  function saveWishlist(list){ localStorage.setItem(WISH_KEY, JSON.stringify(list)); }

  window.thubToggleWish = function(breweryId, breweryName, brandName){
    if(!window.thubAuth || !window.thubAuth.isLoggedIn){
      if(typeof showAuth === 'function') showAuth('login');
      return;
    }
    var list = getWishlist();
    var key = breweryId + '_' + (brandName || '');
    var idx = list.findIndex(function(w){ return (w.brewery_id + '_' + (w.brand||'')) === key; });

    if(idx >= 0){
      list.splice(idx, 1);
      saveWishlist(list);
      showFavToast('飲みたいリストから削除しました');
    } else {
      list.unshift({ brewery_id: breweryId, brewery_name: breweryName, brand: brandName || '', timestamp: new Date().toISOString() });
      saveWishlist(list);
      showFavToast('🍶 飲みたいリストに追加しました！');

      if(window.thubAuth && window.thubAuth.supabase){
        window.thubAuth.supabase.from('wishlist').insert({
          user_id: window.thubAuth.user.id,
          brewery_id: breweryId,
          brewery_name: breweryName,
          brand_name: brandName || '',
          genre: GENRE
        });
      }
    }
  };

  window.thubIsWished = function(breweryId, brandName){
    var key = breweryId + '_' + (brandName || '');
    return getWishlist().some(function(w){ return (w.brewery_id + '_' + (w.brand||'')) === key; });
  };

  window.thubShowWishlist = function(){
    var list = getWishlist();
    var content = '';
    if(list.length === 0){
      content = '<div style="text-align:center;padding:32px;color:#aaa;font-size:13px;">まだリストが空です。<br>気になる銘柄を「飲みたい」ボタンで追加しましょう。</div>';
    } else {
      content = list.map(function(w){
        return '<div style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid #f0f0f0;">' +
          '<div style="flex:1;">' +
            '<div style="font-size:13px;font-weight:500;color:#333;">' + escHtml(w.brewery_name) + '</div>' +
            (w.brand ? '<div style="font-size:12px;color:' + BRAND_COLOR + ';">' + escHtml(w.brand) + '</div>' : '') +
          '</div>' +
          '<button data-wish-id="' + escHtml(w.brewery_id) + '" data-wish-name="' + escHtml(w.brewery_name) + '" data-wish-brand="' + escHtml(w.brand||'') + '" style="background:none;border:none;color:#e05c5c;font-size:12px;cursor:pointer;">削除</button>' +
        '</div>';
      }).join('');
    }
    showFeatureModal('📋 飲みたいリスト', content);
    var fmModal = document.getElementById('feature-modal');
    if(fmModal){
      fmModal.addEventListener('click', function(e){
        var btn = e.target.closest('[data-wish-id]');
        if(btn){ thubToggleWish(btn.dataset.wishId, btn.dataset.wishName, btn.dataset.wishBrand); fmModal.remove(); }
      });
    }
  };

  // ══════════════════════════════════════
  // 7. バッジ/称号（ゲーミフィケーション）
  // ══════════════════════════════════════
  var BADGE_KEY = 'thub_badges';
  var BADGE_SHOWN_KEY = 'thub_badges_shown';

  var BADGE_DEFS = [
    { id: 'first_log', name: '初めての一杯', desc: '飲酒記録を初めて付けた', icon: '🍶', condition: function(){ return getLogs().length >= 1; }},
    { id: 'log_5', name: '日本酒ファン', desc: '5杯の飲酒記録', icon: '🌸', condition: function(){ return getLogs().length >= 5; }},
    { id: 'log_10', name: '日本酒通', desc: '10杯の飲酒記録', icon: '🏅', condition: function(){ return getLogs().length >= 10; }},
    { id: 'log_30', name: '酒豪', desc: '30杯の飲酒記録', icon: '🏆', condition: function(){ return getLogs().length >= 30; }},
    { id: 'log_100', name: '日本酒マイスター', desc: '100杯の飲酒記録', icon: '👑', condition: function(){ return getLogs().length >= 100; }},
    { id: 'stamp_1', name: '蔵巡りデビュー', desc: '初めてのチェックイン', icon: '📍', condition: function(){ return getStamps().length >= 1; }},
    { id: 'stamp_5', name: '蔵巡り愛好家', desc: '5蔵でチェックイン', icon: '🗺️', condition: function(){ return getStamps().length >= 5; }},
    { id: 'stamp_10', name: '蔵巡りマスター', desc: '10蔵でチェックイン', icon: '⭐', condition: function(){ return getStamps().length >= 10; }},
    { id: 'stamp_47', name: '全国制覇', desc: '47都道府県の蔵でチェックイン', icon: '🇯🇵', condition: function(){
      var prefs = new Set();
      getStamps().forEach(function(s){ if(s.region) prefs.add(s.region); });
      return prefs.size >= 47;
    }},
    { id: 'fav_5', name: 'お気に入りコレクター', desc: '5蔵をお気に入り', icon: '❤️', condition: function(){ return getFavs().length >= 5; }},
    { id: 'wish_5', name: '探求者', desc: '5銘柄を飲みたいリストに', icon: '📋', condition: function(){ return getWishlist().length >= 5; }},
    { id: 'taste_set', name: '自分を知る', desc: '味覚診断を完了', icon: '🎯', condition: function(){ try{ return !!JSON.parse(localStorage.getItem('sakura_taste_profile')); }catch(e){return false;} }},
    { id: 'region_niigata', name: '新潟マスター', desc: '新潟県の蔵を3蔵以上記録', icon: '🌾', condition: function(){
      return getLogs().filter(function(l){ return isRegion(l.brewery_id, '新潟県'); }).length >= 3;
    }},
    { id: 'region_kyoto', name: '京都マスター', desc: '京都府の蔵を3蔵以上記録', icon: '⛩️', condition: function(){
      return getLogs().filter(function(l){ return isRegion(l.brewery_id, '京都府'); }).length >= 3;
    }},
    { id: 'region_hyogo', name: '灘マスター', desc: '兵庫県の蔵を3蔵以上記録', icon: '🏔️', condition: function(){
      return getLogs().filter(function(l){ return isRegion(l.brewery_id, '兵庫県'); }).length >= 3;
    }},
  ];

  function isRegion(breweryId, region){
    if(!window.SAKURA_KB) return false;
    var b = window.SAKURA_KB.find(function(kb){ return kb.id === breweryId; });
    return b && b.region === region;
  }

  function getStamps(){
    return JSON.parse(localStorage.getItem('thub_stamps') || '[]');
  }

  function getBadges(){ return JSON.parse(localStorage.getItem(BADGE_KEY) || '[]'); }
  function saveBadges(badges){ localStorage.setItem(BADGE_KEY, JSON.stringify(badges)); }
  function getBadgesShown(){ return JSON.parse(localStorage.getItem(BADGE_SHOWN_KEY) || '[]'); }
  function saveBadgesShown(shown){ localStorage.setItem(BADGE_SHOWN_KEY, JSON.stringify(shown)); }

  function checkBadges(){
    var earned = getBadges();
    var shown = getBadgesShown();
    var newBadges = [];

    BADGE_DEFS.forEach(function(def){
      if(earned.includes(def.id)) return;
      if(def.condition()){
        earned.push(def.id);
        if(!shown.includes(def.id)){
          newBadges.push(def);
          shown.push(def.id);
        }
      }
    });

    saveBadges(earned);
    saveBadgesShown(shown);

    // Show new badge notification
    newBadges.forEach(function(badge, i){
      setTimeout(function(){
        showBadgeNotification(badge);
      }, i * 2000);
    });
  }

  function showBadgeNotification(badge){
    var notif = document.createElement('div');
    notif.style.cssText = 'position:fixed;top:70px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,' + BRAND_COLOR + ',#D4728A);color:#fff;padding:16px 24px;border-radius:12px;z-index:900;box-shadow:0 8px 32px rgba(184,69,42,0.3);display:flex;align-items:center;gap:12px;animation:fadeInUp 0.5s ease;';
    notif.innerHTML = '<div style="font-size:32px;">' + escHtml(badge.icon) + '</div><div><div style="font-size:10px;letter-spacing:0.12em;opacity:0.8;">NEW BADGE</div><div style="font-size:16px;font-weight:600;">' + escHtml(badge.name) + '</div><div style="font-size:11px;opacity:0.8;">' + escHtml(badge.desc) + '</div></div>';
    document.body.appendChild(notif);
    setTimeout(function(){ notif.style.opacity = '0'; notif.style.transition = 'opacity 0.5s'; setTimeout(function(){ notif.remove(); }, 500); }, 3500);
  }

  window.thubShowBadges = function(){
    var earned = getBadges();
    var content = BADGE_DEFS.map(function(def){
      var isEarned = earned.includes(def.id);
      return '<div style="display:flex;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid #f0f0f0;' + (isEarned ? '' : 'opacity:0.35;') + '">' +
        '<div style="font-size:28px;width:40px;text-align:center;">' + (isEarned ? def.icon : '🔒') + '</div>' +
        '<div>' +
          '<div style="font-size:14px;font-weight:500;color:#333;">' + def.name + '</div>' +
          '<div style="font-size:12px;color:#888;">' + def.desc + '</div>' +
        '</div>' +
      '</div>';
    }).join('');
    content = '<div style="font-size:12px;color:#888;margin-bottom:12px;">' + earned.length + ' / ' + BADGE_DEFS.length + ' 獲得</div>' + content;
    showFeatureModal('🏆 バッジコレクション', content);
  };

  // ページ読み込み時にバッジチェック
  setTimeout(checkBadges, 2000);

  // ══════════════════════════════════════
  // 8. レベル & XPシステム
  // ══════════════════════════════════════
  var XP_KEY = 'thub_xp';
  var STREAK_KEY = 'thub_streak';

  var LEVELS = [
    { lv: 1, name: '初心者', xp: 0, icon: '🌱' },
    { lv: 2, name: '日本酒入門', xp: 50, icon: '🍶' },
    { lv: 3, name: '日本酒好き', xp: 150, icon: '🌸' },
    { lv: 4, name: '利き酒見習い', xp: 300, icon: '🎋' },
    { lv: 5, name: '利き酒師', xp: 500, icon: '🏅' },
    { lv: 6, name: '日本酒通', xp: 800, icon: '⭐' },
    { lv: 7, name: '酒豪', xp: 1200, icon: '🔥' },
    { lv: 8, name: '蔵元の友', xp: 1800, icon: '🏆' },
    { lv: 9, name: '日本酒マイスター', xp: 2500, icon: '💎' },
    { lv: 10, name: '酒仙', xp: 3500, icon: '👑' },
  ];

  // XP actions
  var XP_ACTIONS = {
    log: 15,        // 飲酒記録
    checkin: 30,    // チェックイン
    fav: 5,         // お気に入り
    wish: 5,        // 飲みたい追加
    taste: 20,      // 味覚診断完了
    badge: 25,      // バッジ獲得
    streak: 10,     // 連続ログイン1日ごと
    challenge: 50,  // チャレンジ達成
  };

  function getXP(){ return parseInt(localStorage.getItem(XP_KEY) || '0', 10); }
  function addXP(amount, reason){
    var xp = getXP() + amount;
    localStorage.setItem(XP_KEY, String(xp));
    var oldLv = getLevel(xp - amount);
    var newLv = getLevel(xp);
    if(newLv.lv > oldLv.lv){
      showLevelUp(newLv);
    } else {
      showXPToast('+' + amount + ' XP ' + (reason || ''));
    }
    return xp;
  }

  function getLevel(xp){
    if(typeof xp === 'undefined') xp = getXP();
    var level = LEVELS[0];
    for(var i = LEVELS.length - 1; i >= 0; i--){
      if(xp >= LEVELS[i].xp){ level = LEVELS[i]; break; }
    }
    return level;
  }

  function getNextLevel(xp){
    if(typeof xp === 'undefined') xp = getXP();
    for(var i = 0; i < LEVELS.length; i++){
      if(LEVELS[i].xp > xp) return LEVELS[i];
    }
    return null;
  }

  function showXPToast(msg){
    var toast = document.createElement('div');
    toast.style.cssText = 'position:fixed;bottom:120px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,' + BRAND_COLOR + ',#D4728A);color:#fff;padding:8px 18px;border-radius:20px;font-size:13px;font-weight:600;z-index:850;animation:fadeInUp 0.3s ease;box-shadow:0 4px 16px rgba(184,69,42,0.3);';
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(function(){ toast.style.opacity='0'; toast.style.transition='opacity 0.3s'; setTimeout(function(){toast.remove();},300); }, 1800);
  }

  function showLevelUp(level){
    var overlay = document.createElement('div');
    overlay.style.cssText = 'position:fixed;inset:0;z-index:900;background:rgba(0,0,0,0.6);backdrop-filter:blur(12px);display:flex;align-items:center;justify-content:center;animation:fadeInUp 0.4s ease;';
    overlay.onclick = function(){ overlay.remove(); };
    overlay.innerHTML = '<div style="background:#fff;border-radius:20px;padding:40px 32px;text-align:center;max-width:440px;box-shadow:0 24px 64px rgba(0,0,0,0.2);" onclick="event.stopPropagation()">' +
      '<div style="font-size:56px;margin-bottom:12px;animation:pulse 1s infinite;">' + level.icon + '</div>' +
      '<div style="font-size:11px;letter-spacing:0.2em;color:' + BRAND_COLOR + ';font-weight:600;margin-bottom:8px;">LEVEL UP!</div>' +
      '<div style="font-family:\'Shippori Mincho\',serif;font-size:28px;font-weight:700;color:#333;margin-bottom:4px;">Lv.' + level.lv + '</div>' +
      '<div style="font-size:18px;color:' + BRAND_COLOR + ';font-weight:600;margin-bottom:16px;">' + level.name + '</div>' +
      '<div style="font-size:13px;color:#888;">おめでとうございます！</div>' +
      '<button onclick="this.closest(\'div\').parentElement.remove()" style="margin-top:20px;background:' + BRAND_COLOR + ';color:#fff;border:none;padding:10px 32px;border-radius:10px;font-size:14px;cursor:pointer;">続ける</button>' +
    '</div>';
    document.body.appendChild(overlay);
  }

  // XPをアクション時に付与（既存関数をラップ）
  var origSubmitLog = window.submitSakeLog;
  window.submitSakeLog = function(breweryId, breweryName){
    origSubmitLog(breweryId, breweryName);
    addXP(XP_ACTIONS.log, '飲酒記録');
    checkStreak();
  };

  // ══════════════════════════════════════
  // 9. 連続記録ストリーク
  // ══════════════════════════════════════
  function getStreak(){
    return JSON.parse(localStorage.getItem(STREAK_KEY) || '{"count":0,"lastDate":""}');
  }

  function checkStreak(){
    var streak = getStreak();
    var today = new Date().toISOString().slice(0,10);
    var yesterday = new Date(Date.now() - 86400000).toISOString().slice(0,10);

    if(streak.lastDate === today) return; // 今日はもう記録済み
    if(streak.lastDate === yesterday){
      streak.count++;
      streak.lastDate = today;
    } else {
      streak.count = 1;
      streak.lastDate = today;
    }
    localStorage.setItem(STREAK_KEY, JSON.stringify(streak));

    if(streak.count >= 2){
      addXP(XP_ACTIONS.streak, '連続' + streak.count + '日');
    }
    if(streak.count === 3 || streak.count === 7 || streak.count === 14 || streak.count === 30){
      showFavToast('🔥 ' + streak.count + '日連続記録中！すごい！');
    }
  }

  // ══════════════════════════════════════
  // 10. ウィークリーチャレンジ
  // ══════════════════════════════════════
  var CHALLENGE_KEY = 'thub_challenges';

  var CHALLENGE_TEMPLATES = [
    { id: 'log_3', title: '今週3杯飲もう', desc: '飲酒記録を3回つけよう', target: 3, type: 'log', icon: '🍶' },
    { id: 'try_junmai', title: '純米酒を試そう', desc: '純米酒を1種類記録しよう', target: 1, type: 'log_type', match: '純米', icon: '🌾' },
    { id: 'try_ginjo', title: '吟醸酒を試そう', desc: '吟醸酒を1種類記録しよう', target: 1, type: 'log_type', match: '吟醸', icon: '✨' },
    { id: 'fav_3', title: '3蔵をお気に入り', desc: 'お気に入りを3蔵追加しよう', target: 3, type: 'fav', icon: '❤️' },
    { id: 'wish_3', title: '飲みたい3銘柄', desc: '飲みたいリストに3つ追加', target: 3, type: 'wish', icon: '📋' },
    { id: 'new_pref', title: '新しい県を開拓', desc: '未記録の県の蔵を記録しよう', target: 1, type: 'new_pref', icon: '🗺️' },
    { id: 'high_rate', title: '★5の酒を見つけよう', desc: '★5つの記録をつけよう', target: 1, type: 'rating5', icon: '⭐' },
    { id: 'log_5', title: '5杯チャレンジ', desc: '今週5杯記録しよう', target: 5, type: 'log', icon: '🔥' },
  ];

  function getCurrentChallenge(){
    var data = JSON.parse(localStorage.getItem(CHALLENGE_KEY) || '{}');
    var weekNum = getWeekNumber();
    if(data.week !== weekNum){
      // New week, new challenge
      var idx = weekNum % CHALLENGE_TEMPLATES.length;
      data = { week: weekNum, challenge: CHALLENGE_TEMPLATES[idx], completed: false, progress: 0 };
      localStorage.setItem(CHALLENGE_KEY, JSON.stringify(data));
    }
    // Update progress
    data.progress = calcChallengeProgress(data.challenge);
    if(data.progress >= data.challenge.target && !data.completed){
      data.completed = true;
      localStorage.setItem(CHALLENGE_KEY, JSON.stringify(data));
      addXP(XP_ACTIONS.challenge, 'チャレンジ達成！');
      showFavToast('🎉 ウィークリーチャレンジ達成！+50XP');
    }
    return data;
  }

  function calcChallengeProgress(ch){
    var logs = getLogs();
    var weekStart = getWeekStart();
    var thisWeekLogs = logs.filter(function(l){ return l.timestamp >= weekStart; });

    if(ch.type === 'log') return thisWeekLogs.length;
    if(ch.type === 'log_type') return thisWeekLogs.filter(function(l){ return (l.brand||'').includes(ch.match) || getBrandType(l).includes(ch.match); }).length;
    if(ch.type === 'fav') return JSON.parse(localStorage.getItem('thub_favorites')||'[]').length;
    if(ch.type === 'wish') return JSON.parse(localStorage.getItem('thub_wishlist')||'[]').length;
    if(ch.type === 'rating5') return thisWeekLogs.filter(function(l){ return l.rating === 5; }).length;
    if(ch.type === 'new_pref'){
      var oldPrefs = new Set(logs.filter(function(l){return l.timestamp < weekStart;}).map(function(l){return getBreweryPref(l.brewery_id);}));
      var newPrefs = thisWeekLogs.filter(function(l){ return !oldPrefs.has(getBreweryPref(l.brewery_id)); });
      return newPrefs.length;
    }
    return 0;
  }

  function getBrandType(log){
    if(!window.SAKURA_KB) return '';
    var b = window.SAKURA_KB.find(function(kb){return kb.id===log.brewery_id;});
    if(!b || !b.brands) return '';
    var brand = b.brands.find(function(br){return typeof br==='object' && br.name===log.brand;});
    return brand ? (brand.type||'') : '';
  }

  function getBreweryPref(id){
    if(!window.SAKURA_KB) return '';
    var b = window.SAKURA_KB.find(function(kb){return kb.id===id;});
    return b ? (b.region||'') : '';
  }

  function getWeekNumber(){
    var now = new Date();
    var start = new Date(now.getFullYear(), 0, 1);
    return Math.ceil(((now - start) / 86400000 + start.getDay() + 1) / 7);
  }

  function getWeekStart(){
    var now = new Date();
    var day = now.getDay();
    var diff = now.getDate() - day + (day === 0 ? -6 : 1);
    return new Date(now.getFullYear(), now.getMonth(), diff).toISOString().slice(0,10);
  }

  // Expose for mypage
  window.thubGetXP = getXP;
  window.thubGetLevel = getLevel;
  window.thubGetNextLevel = getNextLevel;
  window.thubGetStreak = getStreak;
  window.thubGetCurrentChallenge = getCurrentChallenge;
  window.thubLEVELS = LEVELS;

  // Check challenge on load
  setTimeout(function(){ getCurrentChallenge(); }, 3000);

  // ══════════════════════════════════════
  // 共通モーダル
  // ══════════════════════════════════════
  function showFeatureModal(title, content){
    var modal = document.createElement('div');
    modal.id = 'feature-modal';
    modal.style.cssText = 'position:fixed;inset:0;z-index:700;background:rgba(0,0,0,0.4);backdrop-filter:blur(8px);display:flex;align-items:center;justify-content:center;';
    modal.onclick = function(e){ if(e.target === modal) modal.remove(); };
    modal.innerHTML = '<div style="background:#fff;border-radius:14px;max-width:440px;width:calc(100% - 32px);padding:28px;box-shadow:0 16px 48px rgba(0,0,0,0.12);max-height:85vh;overflow-y:auto;">' +
      '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">' +
        '<div style="font-family:\'Shippori Mincho\',serif;font-size:18px;font-weight:600;">' + title + '</div>' +
        '<button onclick="this.closest(\'#feature-modal\').remove()" style="background:#fafaf8;border:none;width:26px;height:26px;border-radius:6px;cursor:pointer;color:#999;font-size:13px;">✕</button>' +
      '</div>' +
      '<div>' + content + '</div>' +
    '</div>';
    document.body.appendChild(modal);
  }

  // ══════════════════════════════════════
  // CSS
  // ══════════════════════════════════════
  var style = document.createElement('style');
  style.textContent = '@keyframes fadeInUp{from{opacity:0;transform:translateX(-50%) translateY(10px)}to{opacity:1;transform:translateX(-50%) translateY(0)}}';
  document.head.appendChild(style);

})();

// みんなの記録セクション自動挿入（蔵ページ）
(function(){
  var CFG = window.THUB_CONFIG || {};
  var BRAND_COLOR = CFG.brandColor || '#B8452A';
  var BASE_PATH = CFG.basePath || '/sake';

  var visitSection = document.getElementById('visit');
  if(!visitSection) return;

  // URLから brewery_id を取得
  var pathParts = window.location.pathname.split('/');
  var breweryId = pathParts[pathParts.length - 1].replace('.html','');
  if(!breweryId) return;

  // 蔵名を取得
  var breweryName = '';
  var titleEl = document.querySelector('.hero-title');
  if(titleEl) breweryName = titleEl.textContent.trim();

  var SUPABASE_URL = 'https://hhwavxavuqqfiehrogwv.supabase.co';
  var SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imhod2F2eGF2dXFxZmllaHJvZ3d2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM5Njk3MzAsImV4cCI6MjA4OTU0NTczMH0.tHMQ_u51jp69AMUKKtTvxL09Sr11JFPKGRhKMmUzEjg';

  // sake_logs と quest_photos を同時取得
  Promise.all([
    fetch(SUPABASE_URL + '/rest/v1/sake_logs?brewery_id=eq.' + breweryId + '&select=brand_name,rating,comment,created_at&order=created_at.desc&limit=5', {
      headers: {'apikey': SUPABASE_KEY, 'Authorization': 'Bearer ' + SUPABASE_KEY}
    }).then(function(r){ return r.json(); }).catch(function(){ return []; }),
    fetch(SUPABASE_URL + '/rest/v1/quest_photos?brewery_id=eq.' + breweryId + '&status=eq.approved&select=image_url,brand_name,created_at&order=created_at.desc&limit=4', {
      headers: {'apikey': SUPABASE_KEY, 'Authorization': 'Bearer ' + SUPABASE_KEY}
    }).then(function(r){ return r.json(); }).catch(function(){ return []; })
  ]).then(function(results){
    var logs = results[0] || [];
    var photos = results[1] || [];

    if(logs.length === 0 && photos.length === 0) return;

    function escH(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}

    var html = '<section style="padding:48px 24px;max-width:960px;margin:0 auto;">';
    html += '<div style="font-size:9px;letter-spacing:0.35em;color:' + BRAND_COLOR + ';text-transform:uppercase;margin-bottom:8px;">Community</div>';
    html += '<div style="font-family:Shippori Mincho,serif;font-size:clamp(22px,4vw,34px);margin-bottom:20px;">みんなの記録</div>';

    // 写真
    if(photos.length > 0){
      html += '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px;margin-bottom:20px;">';
      photos.forEach(function(p){
        html += '<img src="' + escH(p.image_url) + '" alt="' + escH(p.brand_name || '') + '" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:8px;" loading="lazy">';
      });
      html += '</div>';
    }

    // 飲酒記録
    if(logs.length > 0){
      // 平均評価
      var rated = logs.filter(function(l){return l.rating > 0;});
      if(rated.length > 0){
        var avg = (rated.reduce(function(s,l){return s+l.rating;},0) / rated.length).toFixed(1);
        html += '<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">';
        html += '<div style="font-size:32px;font-weight:700;color:' + BRAND_COLOR + ';font-family:Inter,sans-serif;">' + avg + '</div>';
        html += '<div><div style="color:#D4728A;font-size:16px;">';
        for(var i=1;i<=5;i++) html += i<=Math.round(parseFloat(avg))?'★':'☆';
        html += '</div><div style="font-size:11px;color:#aaa;">' + rated.length + '件の評価</div></div></div>';
      }

      html += '<div>';
      logs.forEach(function(l){
        var stars = '';
        if(l.rating > 0) for(var i=1;i<=5;i++) stars += '<span style="color:'+(i<=l.rating?'#D4728A':'#e5e5e5')+';">★</span>';
        var date = l.created_at ? new Date(l.created_at).toLocaleDateString('ja-JP') : '';
        html += '<div style="padding:10px 0;border-bottom:1px solid #f0f0f0;">';
        if(l.brand_name) html += '<div style="font-size:13px;font-weight:500;color:#333;">' + escH(l.brand_name) + '</div>';
        if(stars) html += '<div style="font-size:13px;">' + stars + '</div>';
        if(l.comment) html += '<div style="font-size:12px;color:#888;margin-top:2px;">' + escH(l.comment) + '</div>';
        html += '<div style="font-size:10px;color:#ccc;margin-top:2px;">' + date + '</div></div>';
      });
      html += '</div>';
    }

    // CTA
    html += '<div style="text-align:center;margin-top:20px;">';
    html += '<a href="https://terroirhub.com/quest/" style="display:inline-flex;align-items:center;gap:6px;font-size:13px;color:' + BRAND_COLOR + ';font-weight:500;text-decoration:none;border:1px solid rgba(184,69,42,0.25);padding:8px 20px;border-radius:8px;">テロワールクエストで記録する →</a>';
    html += '</div></section>';

    visitSection.insertAdjacentHTML('beforebegin', html);
  });
})();

// SNSシェアボタン自動挿入
(function(){
  if(!document.querySelector('.site-footer')) return;
  var title = document.title || '';
  var url = encodeURIComponent(window.location.href);
  var text = encodeURIComponent(title);
  var shareHtml = '<div style="text-align:center;padding:20px 24px;background:#f5f2ec;border-top:1px solid #eee;">' +
    '<div style="font-size:12px;color:#999;margin-bottom:10px;">この蔵をシェア</div>' +
    '<div style="display:flex;gap:12px;justify-content:center;">' +
      '<a href="https://twitter.com/intent/tweet?text='+text+'&url='+url+'" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;background:#333;color:#fff;border-radius:50%;text-decoration:none;font-size:16px;font-weight:700;">𝕏</a>' +
      '<a href="https://www.facebook.com/sharer/sharer.php?u='+url+'" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;background:#1877F2;color:#fff;border-radius:50%;text-decoration:none;font-size:16px;">f</a>' +
      '<a href="https://line.me/R/msg/text/?'+text+'%20'+url+'" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;background:#06C755;color:#fff;border-radius:50%;text-decoration:none;font-size:13px;font-weight:700;">LINE</a>' +
    '</div></div>';
  var footer = document.querySelector('.site-footer');
  if(footer) footer.insertAdjacentHTML('beforebegin', shareHtml);
})();

// テロワールクエスト自動読み込み
(function(){
  var CFG = window.THUB_CONFIG || {};
  var BASE_PATH = CFG.basePath || '/sake';
  var s = document.createElement('script');
  s.src = BASE_PATH + '/quest.js';
  s.defer = true;
  document.head.appendChild(s);
})();

// タブバーはPWAのみ表示
(function(){
  var isPWA = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
  if(isPWA){
    var tabBar = document.getElementById('tab-bar');
    if(tabBar) tabBar.style.display = 'flex';
  }
})();

// ═══ PC版 Atlas風 サクラ右パネル ═══
(function(){
  if(window.innerWidth <= 700) return; // スマホはスキップ

  // 既にパネルがある場合はスキップ（検索ページなど）
  if(document.querySelector('.page-sakura') || document.querySelector('.sk-chat')) return;

  var CFG = window.THUB_CONFIG || {};
  var BRAND_COLOR = CFG.brandColor || '#B8452A';
  var BASE_PATH = CFG.basePath || '/sake';
  var AI_NAME = CFG.aiName || 'サクラ';
  var AI_EMOJI = CFG.aiEmoji || '🌸';
  var AI_PLACEHOLDER = CFG.aiPlaceholder || (AI_NAME + 'に聞いてみる…');
  var AI_GREETING = CFG.aiGreeting || ('こんにちは、' + AI_NAME + 'です。' + AI_EMOJI + '\n\n最初の5クレジットで、好みに合う提案、産地の比較まで案内できます。まずは下の質問例から試してください。');
  var AI_SUGGESTIONS = CFG.aiSuggestions || ['初心者向けで外さない日本酒を3つ教えて','刺身に合う辛口を理由つきで教えて','新潟で見学しやすい蔵を比べて','獺祭が好きなら次に何を飲むべき？'];
  var AI_AVATAR = CFG.aiAvatar || (AI_AVATAR);

  var HISTORY_KEY = 'thub_sakura_pc_history';
  var STATE_KEY = 'thub_sakura_pc_open';
  // デフォルトはopen（ユーザーが明示的に閉じた場合のみclosed）
  var isOpen = localStorage.getItem(STATE_KEY) !== 'closed';

  // CSS注入
  var style = document.createElement('style');
  style.textContent = '\
    .atlas-panel{position:fixed;top:0;right:0;bottom:0;width:380px;min-width:280px;max-width:600px;background:#fff;box-shadow:-2px 0 12px rgba(0,0,0,0.04);display:flex;flex-direction:column;z-index:90;transition:transform 0.3s cubic-bezier(0.16,1,0.3,1);}\
    .atlas-panel.closed{transform:translateX(100%);}\
    .atlas-resize{position:absolute;left:0;top:0;bottom:0;width:5px;cursor:col-resize;z-index:10;}\
    .atlas-resize:hover,.atlas-resize.active{background:' + BRAND_COLOR + '33;}\
    body.atlas-open{margin-right:380px;transition:margin-right 0.3s;}\
    body.atlas-closed{margin-right:0;}\
    .atlas-toggle{position:fixed;right:16px;top:62px;z-index:1001;width:36px;height:36px;background:linear-gradient(135deg,' + BRAND_COLOR + ',' + BRAND_COLOR + 'cc);border:none;border-radius:50%;color:#fff;font-size:17px;cursor:pointer;box-shadow:0 2px 8px ' + BRAND_COLOR + '66;display:flex;align-items:center;justify-content:center;transition:all 0.2s;}\
    .atlas-toggle:hover{transform:scale(1.1);}\
    .atlas-hdr{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid #eee;flex-shrink:0;}\
    .atlas-hdr-l{display:flex;align-items:center;gap:10px;}\
    .atlas-av{width:32px;height:32px;border-radius:50%;object-fit:cover;}\
    .atlas-name{font-size:14px;font-weight:600;color:#333;}\
    .atlas-status{font-size:10px;color:#4caf7d;}\
    .atlas-close{background:#f5f2ec;border:none;width:32px;height:32px;border-radius:50%;cursor:pointer;font-size:16px;color:' + BRAND_COLOR + ';display:flex;align-items:center;justify-content:center;transition:background 0.15s;}\
    .atlas-close:hover{background:#eee;}\
    .atlas-chat{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:10px;background:#fafaf8;}\
    .atlas-msg{display:flex;gap:8px;animation:atlasFade 0.3s ease;}\
    @keyframes atlasFade{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}\
    .atlas-msg.user{flex-direction:row-reverse;}\
    .atlas-msg .atlas-mav{width:28px;height:28px;border-radius:50%;flex-shrink:0;overflow:hidden;}\
    .atlas-msg .atlas-mav img{width:100%;height:100%;object-fit:cover;}\
    .atlas-bubble{max-width:85%;padding:10px 14px;border-radius:12px;font-size:13px;line-height:1.8;color:#333;}\
    .atlas-msg.bot .atlas-bubble{background:#fff;border:1px solid ' + BRAND_COLOR + '1a;}\
    .atlas-msg.user .atlas-bubble{background:' + BRAND_COLOR + '0d;}\
    .atlas-inp{padding:10px 14px;border-top:1px solid #eee;display:flex;gap:8px;flex-shrink:0;background:#fff;}\
    .atlas-inp textarea{flex:1;background:#f5f5f3;border:1px solid #eee;border-radius:8px;color:#333;font-family:\'Noto Sans JP\',sans-serif;font-size:13px;padding:8px 10px;outline:none;resize:none;line-height:1.5;}\
    .atlas-inp textarea:focus{border-color:' + BRAND_COLOR + ';}\
    .atlas-inp button{background:' + BRAND_COLOR + ';border:none;color:#fff;width:36px;height:36px;border-radius:8px;cursor:pointer;font-size:15px;font-weight:700;flex-shrink:0;}\
  ';
  document.head.appendChild(style);

  // HTML生成
  var panel = document.createElement('div');
  panel.className = 'atlas-panel' + (isOpen ? '' : ' closed');
  panel.innerHTML = '\
    <div class="atlas-resize" id="atlas-resize"></div>\
    <div class="atlas-hdr">\
      <div class="atlas-hdr-l">\
        <span style="font-size:20px;line-height:1;">' + AI_EMOJI + '</span>\
        <div>\
          <div class="atlas-name">' + AI_NAME + '</div>\
          <div class="atlas-status">オンライン</div>\
        </div>\
      </div>\
      <div style="display:flex;gap:6px;"><button class="atlas-close" onclick="clearAtlasHistory()" title="履歴クリア" style="font-size:13px;">🗑</button><button class="atlas-close" onclick="toggleAtlasPanel()" title="閉じる">✕</button></div>\
    </div>\
    <div class="atlas-chat" id="atlas-chat"></div>\
    <div class="atlas-inp">\
      <textarea id="atlas-input" rows="1" placeholder="' + AI_PLACEHOLDER + '" onkeydown="if(event.key===\'Enter\'&&!event.shiftKey){event.preventDefault();atlasSend();}"></textarea>\
      <button onclick="atlasSend()">↑</button>\
    </div>\
  ';
  document.body.appendChild(panel);

  // トグルボタン
  var toggleBtn = document.createElement('button');
  toggleBtn.className = 'atlas-toggle';
  toggleBtn.innerHTML = AI_EMOJI;
  toggleBtn.onclick = function(){ toggleAtlasPanel(); };
  document.body.appendChild(toggleBtn);

  // body class
  document.body.classList.add(isOpen ? 'atlas-open' : 'atlas-closed');

  // トグル
  window.toggleAtlasPanel = function(){
    var p = document.querySelector('.atlas-panel');
    var btn = document.querySelector('.atlas-toggle');
    if(p.classList.contains('closed')){
      p.classList.remove('closed');
      document.body.classList.remove('atlas-closed');
      document.body.classList.add('atlas-open');
      localStorage.setItem(STATE_KEY, 'open');
      var w = parseInt(p.style.width) || 380;
      document.body.style.marginRight = w + 'px';
      if(btn) btn.style.right = (w + 16) + 'px';
    } else {
      p.classList.add('closed');
      document.body.classList.remove('atlas-open');
      document.body.classList.add('atlas-closed');
      localStorage.setItem(STATE_KEY, 'closed');
      document.body.style.marginRight = '0';
      if(btn) btn.style.right = '16px';
    }
  };

  // bodyのmarginとボタン位置を設定
  if(isOpen){
    document.body.style.marginRight = '380px';
    toggleBtn.style.right = (380 + 16) + 'px';
  }

  // リサイズ
  var handle = document.getElementById('atlas-resize');
  var dragging = false;
  handle.addEventListener('mousedown', function(e){
    e.preventDefault(); dragging = true;
    handle.classList.add('active');
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  });
  document.addEventListener('mousemove', function(e){
    if(!dragging) return;
    var w = window.innerWidth - e.clientX;
    if(w < 280) w = 280;
    if(w > 600) w = 600;
    panel.style.width = w + 'px';
    document.body.style.marginRight = w + 'px';
  });
  document.addEventListener('mouseup', function(){
    if(!dragging) return;
    dragging = false;
    handle.classList.remove('active');
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  });

  // 会話履歴の読み込み
  function loadHistory(){
    try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'); } catch(e){ return []; }
  }
  function saveHistory(msgs){
    try { localStorage.setItem(HISTORY_KEY, JSON.stringify(msgs.slice(-30))); } catch(e){}
  }

  function escHtmlAtlas(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}

  function addAtlasMsg(role, text){
    var chat = document.getElementById('atlas-chat');
    var d = document.createElement('div');
    d.className = 'atlas-msg ' + role;
    var av = role === 'bot' ? '<div class="atlas-mav" style="width:28px;height:28px;border-radius:50%;background:rgba(0,0,0,0.06);display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;">' + AI_EMOJI + '</div>' : '';
    d.innerHTML = av + '<div class="atlas-bubble">' + escHtmlAtlas(text).replace(/\n/g,'<br>') + '</div>';
    chat.appendChild(d);
    chat.scrollTop = chat.scrollHeight;
    // 履歴に保存
    var history = loadHistory();
    history.push({role: role, text: text});
    saveHistory(history);
  }

  function renderAtlasSugs(){
    var el = document.getElementById('atlas-sugs');
    if(!el) return;
    var items = AI_SUGGESTIONS;
    el.innerHTML = items.map(function(text){
      return '<button type="button" onclick="if(window.thub&&window.thub.track){window.thub.track(\'sakura_trial_suggestion_click\',{suggestion:' + JSON.stringify(text) + '})}var i=document.getElementById(\'atlas-input\'); if(i){i.value=' + JSON.stringify(text) + '; i.focus();}" style="border:1px solid rgba(184,69,42,0.16);background:#fff;color:#6b4a41;border-radius:999px;padding:8px 12px;font-size:12px;cursor:pointer;line-height:1.4;">' + escHtmlAtlas(text) + '</button>';
    }).join('');
  }

  // 初期化: 履歴を復元
  var history = loadHistory();
  var chat = document.getElementById('atlas-chat');
  if(history.length > 0){
    history.forEach(function(m){
      var d = document.createElement('div');
      d.className = 'atlas-msg ' + m.role;
      var av = m.role === 'bot' ? '<div class="atlas-mav"><img src="' + BASE_PATH + '/sakura.jpg" alt=""></div>' : '';
      d.innerHTML = av + '<div class="atlas-bubble">' + escHtmlAtlas(m.text).replace(/\n/g,'<br>') + '</div>';
      chat.appendChild(d);
    });
    chat.scrollTop = chat.scrollHeight;
  } else {
    addAtlasMsg('bot', AI_GREETING);
    if(window.thub && typeof window.thub.track === 'function'){
      window.thub.track('sakura_trial_intro_impression', { placement: 'atlas' });
    }
  }
  renderAtlasSugs();

  // 履歴クリア
  window.clearAtlasHistory = function(){
    if(!confirm('チャット履歴をクリアしますか？')) return;
    localStorage.removeItem(HISTORY_KEY);
    document.getElementById('atlas-chat').innerHTML = '';
    addAtlasMsg('bot', AI_GREETING);
  };

  // 送信
  window.atlasSend = async function(){
    var inp = document.getElementById('atlas-input');
    var q = inp.value.trim();
    if(!q) return;
    if(q.length > 300){
      addAtlasMsg('bot', '🌸 1回の質問は300文字以内でお願いします。短く分けてもらえると、より正確に案内できます。');
      return;
    }
    inp.value = '';
    var sugsEl = document.getElementById('atlas-sugs');
    if(sugsEl) sugsEl.innerHTML = '';
    addAtlasMsg('user', q);

    if(window.thubCheckSakuraLimit){
      var allowed = await Promise.resolve(window.thubCheckSakuraLimit(q));
      if(!allowed) return;
    }
    var priorUserMessages = loadHistory().filter(function(m){ return m.role === 'user'; }).length;
    if(priorUserMessages === 1 && window.thub && typeof window.thub.track === 'function' && window.thubAuth && window.thubAuth.plan === 'free'){
      window.thub.track('sakura_trial_first_query', {
        question_length: q.length,
        estimated_units: estimateSakuraUnits(q)
      });
    }
    doAtlasSend(q);
  };

  async function doAtlasSend(q){
    // タイピング表示
    var chat = document.getElementById('atlas-chat');
    var tp = document.createElement('div');
    tp.className = 'atlas-msg bot'; tp.id = 'atlas-typing';
    tp.innerHTML = '<div class="atlas-mav"><img src="' + BASE_PATH + '/sakura.jpg" alt=""></div><div class="atlas-bubble"><span style="color:#ccc;">考え中...</span></div>';
    chat.appendChild(tp); chat.scrollTop = chat.scrollHeight;

    // Claude API呼び出し
    try {
      var sessionRes = await window.thubAuth.supabase.auth.getSession();
      var accessToken = sessionRes && sessionRes.data && sessionRes.data.session ? sessionRes.data.session.access_token : '';
      if(!accessToken){
        var missingTokenEl = document.getElementById('atlas-typing');
        if(missingTokenEl) missingTokenEl.remove();
        addAtlasMsg('bot', '🌸 セッションを確認できませんでした。もう一度ログインしてください。');
        showSakuraAuthButtons();
        renderAtlasSugs();
        return;
      }

      var response = await fetch('/api/sakura', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + accessToken
        },
        body: JSON.stringify({
          question: q,
          context: '',
          history: loadHistory().filter(function(m){return m.role==='user'||m.role==='bot';}).map(function(m){return{role:m.role==='bot'?'assistant':'user',content:m.text};}).slice(-10)
        })
      });
      var data = await response.json();
      var el = document.getElementById('atlas-typing');
      if(el) el.remove();
      if(data.answer){
        if(data.usage){
          sessionStorage.setItem('thub_credits_cache', JSON.stringify({
            ok: true,
            remaining: data.usage.remaining || 0,
            bonus: data.usage.bonus || 0,
            plan: data.usage.plan || (window.thubAuth ? window.thubAuth.plan : 'free')
          }));
        }
        addAtlasMsg('bot', data.answer);
        if(data.usage && (data.usage.remaining + data.usage.bonus) <= 3 && (data.usage.remaining + data.usage.bonus) > 0){
          showLowCreditWarning(data.usage.remaining + data.usage.bonus, data.usage.plan);
        }
      } else if(response.status === 401 || data.error === 'Login required'){
        addAtlasMsg('bot', '🌸 AIサクラはログイン後にご利用いただけます。');
        showSakuraAuthButtons();
      } else if(response.status === 402 || data.error === 'Not enough credits'){
        showCreditUpsell(window.thubAuth && window.thubAuth.plan ? window.thubAuth.plan : 'free');
      } else if(response.status === 429){
        addAtlasMsg('bot', '🌸 ただいま質問が集中しています。少し時間を空けてからお試しください。');
      } else if(data.error){
        addAtlasMsg('bot', 'すみません、' + data.error + '。');
      } else {
        addAtlasMsg('bot', 'すみません、うまく回答できませんでした。もう一度お試しください。');
      }
      renderAtlasSugs();
    } catch(e){
      var el = document.getElementById('atlas-typing');
      if(el) el.remove();
      addAtlasMsg('bot', '通信エラーが発生しました。もう一度お試しください。');
      renderAtlasSugs();
    }
  }

  // loadHistory を atlasSend 内の doAtlasSend からアクセスできるようにスコープ外公開はしないが、
  // doAtlasSend は同じ IIFE 内なのでアクセス可能

  // 既存のFAB/overlay チャットを非表示（Atlas パネルが代替）
  var fab = document.querySelector('.fab');
  var fabLabel = document.querySelector('.fab-label');
  if(fab) fab.style.display = 'none';
  if(fabLabel) fabLabel.style.display = 'none';

  // 既存のopenPanelをAtlasパネルのフォーカスに変更（DOMContentLoaded後に実行）
  function hookOpenPanel(){
    window.openPanel = function(){
      var p = document.querySelector('.atlas-panel');
      if(p && p.classList.contains('closed')){
        toggleAtlasPanel();
      }
      var inp = document.getElementById('atlas-input');
      if(inp) inp.focus();
    };
  }
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', hookOpenPanel);
  } else {
    hookOpenPanel();
  }
})();

// PWA Service Worker登録
if('serviceWorker' in navigator){
  navigator.serviceWorker.register('/sw.js').catch(function(){});
}
