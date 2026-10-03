---
name: draw
description: OpenAI gpt-image-2 生圖技能。當使用者要求「畫一張」、「生一張圖」、「做一張圖」、「產生圖片」、「畫個封面」、「畫插圖」、「畫示意圖」、「畫分鏡」，或「改這張圖」「把背景換成 XX」等任何需要 AI 生成或修改圖像的情境時，請一定要使用此技能。此技能會呼叫本 repo 的 .claude/skills/draw/draw.py，以 gpt-image-2 生圖，預設 low 品質，存檔至當前專案的 slides/generated/（若無 slides/ 則存到 ./generated/）。
---

# 小克生圖技能（gpt-image-2）

## 觸發情境
- 「畫一張 XX」「生一張圖」「做一張圖」「幫我生圖」「產生圖片」
- 「畫個封面／插圖／示意圖／分鏡」
- 「改這張圖」「修改圖片」「把背景換成 XX」（→ 改圖模式，需提供圖片路徑）

## 使用前檢查（雲端環境每次開新 session 都要）
1. 套件：`python3 -c "import openai"` 失敗就執行 `pip install -q openai --break-system-packages`
2. 金鑰：需要環境變數 `OPENAI_API_KEY`。若沒有，**不要請使用者把金鑰貼到對話裡**，請他到雲端環境設定（標題列的環境選單 → Edit）新增環境變數 `OPENAI_API_KEY`，再開新 session。

## 使用方式
```bash
python3 .claude/skills/draw/draw.py "要畫的內容" --name 檔名前綴
```
（從 repo 根目錄執行；在其他位置請改用絕對路徑）

### 參數
- `prompt`（必填）：要畫什麼
- `--size`：`1024x1024`（方，預設）/ `1536x1024`（橫）/ `1024x1536`（直）
- `--quality`：`low`（預設）/ `medium` / `high`
- `--n`：生成張數 1–8
- `--name`：檔名前綴
- `--outdir`：輸出目錄
- `--edit IMAGE_PATH`：改圖模式（指定來源圖）
- `--mask MASK_PATH`：遮罩圖片（搭配 --edit 使用）

## 判斷 quality 等級的原則
**預設永遠用 `low`**（省錢 + 速度優先）

- **low**：99% 情境。簡報、教學插圖、封面、demo 都夠。
- **medium**：通常不用。
- **high**：實體印刷、圖中文字需零錯才用。

不確定就 **low**，不要自作主張升級。實際費用以 OpenAI 官方 pricing 為準。

## 錯誤處理
- `403 Organization must be verified` → 到 platform.openai.com/settings/organization/general 做 Individual 驗證
- `401 Invalid API key` → 檢查環境變數 `OPENAI_API_KEY`
- `429` / insufficient quota → 額度用完，到 Billing 儲值

## 輸出
PNG 檔，格式：`<name>_<YYYYMMDD_HHMMSS>.png`。生成後用 SendUserFile 把圖片傳給使用者看。
