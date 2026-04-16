// Terroir HUB CRAFT — AI Mizuki API (工芸専門コンシェルジュ)
// 伝統的工芸品特化 / SAKEのサクラとは完全分離
const Anthropic = require('@anthropic-ai/sdk');
const { createClient } = require('@supabase/supabase-js');
const path = require('path');
const fs = require('fs');

const ALLOWED_ORIGINS = [
  'https://craft.terroirhub.com',
  'https://www.craft.terroirhub.com',
  'https://terroirhub.com',
  'http://localhost:3000',
  'http://localhost:5500',
];

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

// 伝統的工芸品ナレッジベース（静的 + DB検索）
let craftKB = null;
function loadCraftKB() {
  if (craftKB) return craftKB;
  try {
    const kbPath = path.join(__dirname, '..', 'craft', 'mizuki_kb.json');
    if (fs.existsSync(kbPath)) {
      craftKB = JSON.parse(fs.readFileSync(kbPath, 'utf-8'));
    } else {
      craftKB = [];
    }
  } catch (e) {
    craftKB = [];
  }
  return craftKB;
}

// 工芸品データベース検索
function searchCraftDB(query) {
  const kb = loadCraftKB();
  if (!kb || kb.length === 0) return [];
  const q = query.toLowerCase()
    .replace(/[　\s]+/g, ' ')
    .split(' ')
    .filter(w => w.length >= 1);

  return kb
    .map(item => {
      let score = 0;
      const searchText = [
        item.name, item.name_en, item.category_ja,
        item.prefecture_ja, item.area, item.desc,
        ...(item.techniques || []),
        ...(item.features || []),
      ].join(' ').toLowerCase();

      q.forEach(word => {
        if (searchText.includes(word)) score += word.length * 2;
      });
      return { ...item, _score: score };
    })
    .filter(i => i._score > 0)
    .sort((a, b) => b._score - a._score)
    .slice(0, 6);
}

// システムプロンプト
function buildSystemPrompt(craftContext) {
  const today = new Date().toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' });
  return `あなたは「ミズキ」、Terroir HUB CRAFTの**日本の伝統的工芸品専門AIコンシェルジュ**です。
今日の日付：${today}

## ミズキのキャラクター
- 伝統工芸への深い愛情と敬意を持つ専門家
- 職人の技術・歴史・文化的背景を丁寧に解説する
- 体験・購入・産地訪問の具体的な情報を提供する
- 正確な情報を基に、知らないことは正直に伝える
- 日本語・英語・フランス語・中国語・韓国語に対応

## 専門知識の範囲
### 経産省指定 伝統的工芸品（2026年現在 240品目以上）

**陶磁器（約30品目）**
- 九谷焼（石川）：五彩絵付け、1655年創始、加賀市・能美市・小松市
- 有田焼（佐賀）：日本初の磁器、1616年、染付・色絵、ヨーロッパ輸出「伊万里」
- 京焼・清水焼（京都）：茶の湯文化、野々村仁清、色絵・金彩
- 萩焼（山口）：「一楽二萩三唐津」、萩の七化け、朝鮮陶工
- 笠間焼（茨城）：個性が様式・関東最大、陶炎祭20万人
- 益子焼（栃木）：濱田庄司・民藝、陶器市60万人
- 美濃焼（岐阜）：国内食器シェア50%、志野・織部・瀬戸黒・黄瀬戸
- 信楽焼（滋賀）：日本六古窯・1300年・狸、自然灰釉
- 備前焼（岡山）：六古窯・釉薬不使用・緋襷・牡丹餅
- 常滑焼（愛知）：六古窯・急須日本一・朱泥・やきもの散歩道
- 砥部焼（愛媛）：白磁に呉須の手描き・厚手で丈夫
- 伊賀焼（三重）：わび・さびの茶陶、土鍋で有名
- 丹波立杭焼（兵庫）：六古窯・自然釉・窯変
- 唐津焼（佐賀）：「一楽二萩三唐津」・茶陶の名品
- 萩焼・小代焼・薩摩焼・壺屋焼（沖縄）など

**漆器（約25品目）**
- 輪島塗（石川）：地の粉・百回塗り・沈金・蒔絵・螺鈿・漆器の王様
- 会津塗（福島）：蒲生氏郷・1590年・花塗り・蒔絵・東北最大産地
- 越前漆器（福井）：業務用80%・日本最大・鯖江市河和田・1500年
- 琉球漆器（沖縄）：14世紀・王国御用品・堆錦・沈金・螺鈿
- 山中漆器（石川）：轆轤挽き・器形・蒔絵
- 木曽漆器（長野）：片道漆塗り・生活密着
- 津軽塗（青森）：変わり塗り・唐塗・研ぎ出し

**織物（約70品目）**
- 西陣織（京都）：1200年・金糸銀糸・ジャカード錦・帯地最高峰
- 博多織（福岡）：1241年・献上柄（独鈷・華皿・宝ずくし・縞）・締まり
- 結城紬（茨城）：2010年ユネスコ・真綿手紡ぎ・絣括り・地機・本結城
- 大島紬（鹿児島）：泥染め・テーチ木・縦横絣
- 京鹿の子絞り（京都）：手絞り・一粒ずつ括る
- 琉球絣（沖縄）：600種絣図案・ジャワ・インド影響・幾何学
- 塩沢紬（新潟）：上布・絣・雪さらし
- 小千谷縮（新潟）：日本最古のユネスコ登録（2009年）
- 米沢織（山形）・郡上紬・十日町絣など

**染色品（約30品目）**
- 京友禅（京都）：1688年・宮崎友禅斎・糸目糊・筆描き・手描き/型
- 加賀友禅（石川）：虫食い葉・外ぼかし・写実的草花
- 江戸小紋（東京）：極小紋様・型染め・鮫・行儀・通し
- 有松鳴海絞り（愛知）：100種絞り技法
- 長板中形（東京）：藍染め・型紙・浴衣

**金工品（約15品目）**
- 南部鉄器（岩手）：1659年・霰紋様・鉄瓶・ルーブルでも販売
- 高岡銅器（富山）：1611年・シェア90%・梵鐘・仏像・東京都庁時計
- 燕鎚起銅器（新潟）：鎚起・金属板を叩いて薄く・茶道具・鍋
- 堺打刃物（大阪）：農工具・包丁・世界の料理人が使う
- 播州刃物（兵庫）・土佐刃物（高知）など

**和紙（約10品目）**
- 越前和紙（福井）：2014年ユネスコ・1500年・紙幣・岡太神社
- 美濃和紙（岐阜）：2014年ユネスコ・1300年・薄くて丈夫・障子・あかりアート
- 石州半紙（島根）：2009年ユネスコ（先行登録）・楮100%・強靱
- 土佐和紙（高知）・因州和紙（鳥取）など

**木竹工芸品（約20品目）**
- 箱根寄木細工（神奈川）：幾何学模様の寄木・秘密箱
- 江戸指物（東京）：釘不使用・組み手・家具
- 駿河竹千筋細工（静岡）：細い竹ひごの精緻な細工
- 秋田杉桶樽（秋田）・木曽漆器の木地など

**人形・こけし（約20品目）**
- 江戸木目込人形（東京）：1740年・木目込み技法・雛人形
- 宮城伝統こけし（宮城）：5系統・轆轤・絵付け・温泉地民藝
- 京人形（京都）：御所人形・御殿飾り
- 博多人形（福岡）：素焼き・素朴な温かみ
- 今戸人形（東京）・土鈴

**仏壇・仏具（約15品目）**
- 京仏壇（京都）：金箔・蒔絵・最高峰
- 名古屋仏壇（愛知）：総ケヤキ・堅牢
- 広島仏壇（広島）・彦根仏壇（滋賀）など

### 体験・購入情報の提供方法
- 体験できる工房は要予約が多い（1,500〜5,000円が一般的）
- 購入は産地工房・百貨店・アンテナショップ・オンラインの順で案内
- 価格帯は概算で案内（日常品〜高級工芸品の幅を説明）

### 回答ルール
1. 知っている情報は自信を持って正確に答える
2. 知らない・不確かな情報は「〜と言われています」「産地にご確認ください」と明示
3. 「伝統工芸品以外」の話題（酒・食・政治等）は「私は伝統工芸専門ですので…」と丁寧に断る
4. 絵文字は適度に（1〜3個程度）
5. 回答は簡潔に200〜400字。複雑な質問は箇条書きで整理

${craftContext ? `\n=== 現在閲覧中の工芸品情報 ===\n${craftContext}\n` : ''}`;
}

module.exports = async (req, res) => {
  // CORS
  const origin = req.headers.origin || '';
  const allowedOrigin = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  res.setHeader('Access-Control-Allow-Origin', allowedOrigin);
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const { question, history = [], craftData } = req.body || {};

    // 入力バリデーション
    if (!question || typeof question !== 'string') {
      return res.status(400).json({ error: '質問を入力してください' });
    }
    const q = question.trim().slice(0, 400);
    if (q.length === 0) return res.status(400).json({ error: '質問が空です' });

    // Supabaseセッション確認（オプション）
    let userId = null;
    let userPlan = 'free';
    const authHeader = req.headers.authorization;
    if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.slice(7);
      const { data: { user } } = await supabase.auth.getUser(token);
      if (user) {
        userId = user.id;
        const { data: profile } = await supabase.from('profiles').select('plan').eq('id', userId).single();
        if (profile) userPlan = profile.plan;
      }
    }

    // レート制限（プラン別）
    const RATE_LIMITS = { free: 8, pro: 30, premium: 100 };
    const limit = RATE_LIMITS[userPlan] || 8;

    if (userId) {
      const { data: rateCheck, error: rateErr } = await supabase.rpc('check_sakura_rate_limit', {
        p_user_id: userId,
        p_limit: limit
      });
      if (!rateErr && rateCheck === false) {
        return res.status(429).json({
          error: '本日の利用上限に達しました',
          message: `${userPlan}プランの上限は1日${limit}回です。プランをアップグレードするとより多く利用できます。`,
          upgrade_url: '/craft/plans/'
        });
      }
    }

    // 工芸品DBから関連データを検索
    const searchResults = searchCraftDB(q);
    let craftContext = '';
    if (searchResults.length > 0) {
      craftContext = searchResults.map(item => {
        const lines = [];
        lines.push(`【${item.name}（${item.name_en}）】`);
        lines.push(`カテゴリ：${item.category_ja} / 産地：${item.prefecture_ja} ${item.area}`);
        if (item.founded) lines.push(`創始：${item.founded}年（${item.founded_era || ''}）`);
        if (item.desc) lines.push(`概要：${item.desc.slice(0, 200)}`);
        if (item.techniques?.length) lines.push(`技法：${item.techniques.join('・')}`);
        if (item.features?.length) lines.push(`特徴：${item.features.join(' / ')}`);
        if (item.price_range) lines.push(`価格帯：${item.price_range}`);
        if (item.workshops?.length) {
          const exp = item.workshops.filter(w => w.experience);
          if (exp.length) lines.push(`体験：${exp.map(w => `${w.name}（${w.experience_desc}）`).join('、')}`);
        }
        return lines.join('\n');
      }).join('\n\n');
    }

    // ページ固有の工芸品データ（個別ページから渡された場合）
    const pageContext = craftData ? `\n=== ページの工芸品 ===\n${JSON.stringify(craftData, null, 2)}` : '';

    // 会話履歴（最新10件）
    const safeHistory = (Array.isArray(history) ? history : [])
      .slice(-10)
      .map(m => ({
        role: m.role === 'user' ? 'user' : 'assistant',
        content: String(m.content || '').slice(0, 1000)
      }))
      .filter(m => m.content.length > 0);

    // Claude API呼び出し
    const response = await anthropic.messages.create({
      model: 'claude-opus-4-6',
      max_tokens: 800,
      system: buildSystemPrompt(craftContext + pageContext),
      messages: [
        ...safeHistory,
        { role: 'user', content: q }
      ]
    });

    const answer = response.content?.[0]?.text || 'ご質問にお答えできませんでした。';

    // ログ記録
    if (userId) {
      await supabase.from('ai_logs').insert({
        user_id: userId,
        genre: 'craft',
        question: q.slice(0, 500),
        response: answer.slice(0, 2000),
        created_at: new Date().toISOString()
      }).catch(() => {});
    }

    return res.status(200).json({
      response: answer,
      searched_crafts: searchResults.map(i => ({ id: i.id, name: i.name, prefecture: i.prefecture }))
    });

  } catch (error) {
    console.error('Mizuki API error:', error);
    if (error?.status === 429) {
      return res.status(503).json({ error: 'AIが混み合っています。しばらく後にお試しください。' });
    }
    return res.status(500).json({ error: 'サーバーエラーが発生しました。' });
  }
};
