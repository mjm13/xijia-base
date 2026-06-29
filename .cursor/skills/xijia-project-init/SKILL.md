---
name: xijia-project-init
description: 瀵硅瘽椹卞姩鍒濆鍖栨柊椤圭洰缁撴瀯涓庢枃妗ｉ鏋躲€傜敤浜庡叏鏂版垨绌轰粨搴撳喎鍚姩锛屼笉瑕嗙洊宸插垵濮嬪寲浠撳簱锛涙妧鏈爤蹇呴』鍏堢‘璁わ紝鍐嶈嚜鍔ㄥ畨瑁呭搴旈珮璇勫垎鎶€鑳姐€?---

# Xijia Project Init

## 鐩爣锛堝垵濮嬪寲杈圭晫锛?
鍦?*绌轰粨搴?*閲岄€氳繃瀵硅瘽涓€娆℃€у畬鎴愬彲杩愯鐨勭爺鍙戦鏋舵枃妗ｅ垵濮嬪寲锛屽苟鍦ㄧ敤鎴风‘璁ゆ妧鏈爤鍚庤嚜鍔ㄥ畨瑁呭搴旀妧鑳姐€?
鏈妧鑳藉彧璐熻矗锛堝繀椤伙級锛?
- 鍒濆鍖栭」鐩粨鏋勪笌鏂囨。楠ㄦ灦锛堝惈 `AGENTS.md`锛?- 璁胯皥骞剁‘璁ゆ妧鏈爤
- 鎶€鏈爤纭鍚庤嚜鍔ㄥ畨瑁呴珮璇勫垎鎶€鑳?- 杈撳嚭鍙拷婧垵濮嬪寲鎶ュ憡锛堟竻鍗?+ 鏉ユ簮 + 瀹夎缁撴灉锛?
鏈妧鑳戒笉璐熻矗锛堢姝級锛?
- 瀹炵幇涓氬姟浠ｇ爜
- 鎺ㄨ繘鍏蜂綋闇€姹傜殑 explore/propose/apply锛堣繖鐢?`xijia-ops-pipeline` 璐熻矗锛?- 鍦ㄥ凡鏈夐」鐩笂瑕嗙洊鏂囨。鎴栭噸鍐欏凡瀛樺湪鏂囦欢
- 鍦ㄧ敤鎴锋湭纭鎶€鏈爤鍓嶅畨瑁呬换浣曟妧鑳?
## 瑙﹀彂鏃舵満

- 鐢ㄦ埛璇粹€滃垵濮嬪寲椤圭洰鈥濃€滀粠闆舵惌楠ㄦ灦鈥濃€滅敓鎴愬垵濮嬫枃妗ｂ€?- 鐢ㄦ埛浣跨敤 `/xijia:init`

## 寮哄埗瑙勫垯锛圚ard Gates锛?
1. 鍏堝仛浠撳簱淇濇姢妫€鏌ワ紙Guard锛夛細
   - 鑻ュ瓨鍦?`docs/` 鎴?`AGENTS.md`锛岄粯璁ゅ仠姝㈠苟鎻愮ず鈥滆 init 闈㈠悜绌轰粨搴撯€?   - 浠呭綋鐢ㄦ埛鏄庣‘鍏佽鈥滆ˉ榻愮己澶变笖涓嶈鐩栤€濇椂锛屾墠杩涘叆琛ラ綈妯″紡
2. 鍒濆鍖栧墠蹇呴』瀹屾垚璁胯皥骞跺杩扮‘璁わ紙Manifest Confirm锛?3. 鎶€鏈爤蹇呴』鐢辩敤鎴风‘璁わ紝妯″瀷涓嶅彲鎿呰嚜鎸囧畾
4. 璇勫垎涓庡畨瑁呭繀椤婚€忔槑锛氳褰曞€欓€夈€佽瘎鍒嗐€佸叆閫夌悊鐢?5. 鎶€鑳藉畨瑁呴伒寰€滄瘡涓妧鏈爤鍙栬瘎鍒嗘渶楂樼殑 2-3 涓妧鑳解€?6. 瀹夎鍚庡繀椤绘牎楠?`SKILL.md` frontmatter锛歚name` 涓庣洰褰曞悓鍚?7. 鑻?`skills` CLI 瀹夎鍒?`.agents/skills/`锛屽繀椤绘惉杩愬埌 `.cursor/skills/`
8. 产出初始化锁文件（`skills-lock.json`）时要在报告中说明用途
9. **init 栈相关 skill 总量 ≤10**；找不到/安装失败则跳过，禁止整库或无关 skill 顶替；0 个成功仍可 done（须列 Skills Skipped）
## 鎵ц姝ラ锛圫OP锛?
### 1) 浠撳簱淇濇姢妫€鏌ワ紙Guard锛?
- 妫€鏌ユ槸鍚﹀凡瀛樺湪 `docs/`銆乣AGENTS.md`
- 鑻ュ瓨鍦紝榛樿涓骞舵彁绀烘敼鐢?`/xijia:start`
- 浠呭綋鐢ㄦ埛鏄庣‘瑕佹眰鈥滆ˉ榻愭ā寮忥紙浠呮柊澧炰笉瑕嗙洊锛夆€濇椂缁х画

### 2) 璁胯皥锛堝彧闂繀瑕侀」锛?
鑷冲皯鏀堕泦浠ヤ笅瀛楁锛?
- 椤圭洰鍚嶇О
- 椤圭洰涓€鍙ヨ瘽鐩爣
- 鏄惁闇€瑕佸墠绔紙鏄?鍚︼級
- 鏄惁闇€瑕佹暟鎹簱锛堟槸/鍚︼級
- 棣栨壒妯″潡锛?-2 涓級
- 鎶€鏈爤鍊欓€夛紙鍚庣銆佸墠绔€佹暟鎹簱銆侀儴缃诧級

骞惰ˉ鍏呬袱涓喅绛栭」锛?
- 鍒濆鍖栨ā寮忥細`绌轰粨搴撳垵濮嬪寲` / `琛ラ綈妯″紡锛堜粎鏂板锛塦
- 鎶€鑳藉畨瑁呯瓥鐣ワ細`鑷姩瀹夎` / `浠呯敓鎴愭帹鑽愭竻鍗昤

### 3) 缁撴瀯棰勮骞剁‘璁わ紙Manifest Confirm锛?
鍏堝睍绀哄皢鍒涘缓鐨勬竻鍗曪紝鍐嶈姹傜‘璁ゃ€傞粯璁ゆ竻鍗曪細

- `AGENTS.md`
- `docs/constitution.md`
- `docs/README.md`
- `docs/decisions/0001-project-bootstrap.md`
- `docs/domain/README.md`
- `docs/requirements/requirements-template.md`
- `docs/requirements/technical-requirement-template.md`
- `docs/requirements/backlog.md`
- `docs/openspec/config.yaml`

鎸夐渶鍒涘缓锛堜笉鍦?init 棰勭敓鎴愶級锛?
- `docs/architecture.md`锛氶渶姹傛敹灏鹃樁娈甸渶瑕佹矇娣€鏋舵瀯鍐崇瓥鏃跺垱寤?鏇存柊
- `docs/capability-map.md`锛氶渶姹傛敹灏鹃樁娈靛懡涓兘鍔涜拷婧Е鍙戞潯浠舵椂鍒涘缓/鏇存柊
- `docs/domain/{context-map,domain-model,ubiquitous-language}.md`锛氶涓笟鍔?change 鏀跺熬鏃跺垱寤?鏇存柊锛沬nit 闃舵 `docs/domain/` 鍙惈 `README.md`
- 涓嶅垱寤?`docs/domain/developing/`锛氿煍?棰嗗煙鑽夌缃簬瀵瑰簲 change 鏂囦欢澶?`docs/openspec/changes/<name>/domain/`

### 4) 娓叉煋妯℃澘骞跺啓鍏ワ紙Scaffold锛?
- 浣跨敤 `templates/` 鍐呮ā鏉跨敓鎴愭枃浠?- 鍗犱綅绗︽渶灏忛泦锛?  - `{{project_name}}`
  - `{{project_goal}}`
  - `{{primary_modules}}`
  - `{{chosen_stack_summary}}`
  - `{{author}}`
  - `{{date}}`
- 闈炵┖浠撳簱琛ラ綈妯″紡涓嬶細鍙垱寤虹己澶辨枃浠讹紝涓嶈鐩栧凡瀛樺湪鏂囦欢

### 5) 技术栈确认后安装技能（Skills Bootstrap）

流程：

1. 列出候选技能来源（`skills.sh`/GitHub）
2. 对每个候选计算评分（0–100）
3. 每个技术栈选择 Top 2–3（去重）
4. **全局硬上限：init 阶段最多安装 10 个 skill**（含从 `.agents/skills/` 搬运到 `.cursor/skills/` 的项；不含项目模板自带的 xijia 工作流 skill）
5. 安装到 `.cursor/skills/`（必要时从 `.agents/skills/` 搬运后立即删除 `.agents/` 中未选中项）
6. 校验 `SKILL.md` + frontmatter 一致性
7. 生成安装报告（候选、评分、入选、成功/跳过/失败原因）

**找不到就不装（Hard Gate）**

- 单个 skill 按名/路径安装失败、repo 不存在、或无可信候选：**跳过**，写入 Init Report 的 `Skills Skipped`
- **禁止**：整库安装、随机换其它 skill、用 unrelated repo 兜底、静默多装
- 某技术栈 0 个 skill 安装成功 **允许** init 继续完成（文档骨架仍须交付）；不得因此 alone 置 `blocked`

默认映射（可覆盖，仍受 ≤10 上限约束）：

- FastAPI: `fastapi-best-practices`, `fastapi-reference`
- Vue: `vue-best-practices`
- UI/UX: `ui-ux-pro-max`
- Django: `django-patterns`, `django-view-generator`

说明：基线引擎保持技术栈无关；具体测试命令、工程目录与实现细节由已安装的技术栈技能承载。
### 6) 浜や粯鎶ュ憡锛圛nit Report锛?
鑷冲皯鍖呭惈锛?
- 鍒濆鍖栨ā寮忎笌 Guard 缁撹
- 鍒涘缓鏂囦欢娓呭崟锛堟柊澧?璺宠繃锛?- 鎶€鏈爤纭鎽樿
- 鎶€鑳借瘎鍒嗕笌鍏ラ€夋槑缁?- 鎶€鑳藉畨瑁呯粨鏋滐紙鎴愬姛/澶辫触/閲嶈瘯鍛戒护锛?- 涓嬩竴姝ワ細`/xijia:start <棣栦釜闇€姹?`

### 7) 鑷锛圫elf-Check锛岃繘鍏?done 鍓嶅己鍒舵墽琛岋級

鑷娓呭崟锛?
1. `requiredFiles`锛氭渶灏忎氦浠橀泦鍏抽敭鏂囦欢閫愰」瀛樺湪鎬ф鏌?   - `docs/constitution.md` 蹇呴』瀛樺湪锛堥」鐩‖绾︽潫鍏ュ彛锛?   - 鎸夐渶鍒涘缓鏂囦欢涓嶈鍏?init 闃舵蹇呴€夐」锛歚docs/architecture.md`銆乣docs/capability-map.md`銆乣docs/domain/{context-map,domain-model,ubiquitous-language,data-dictionary}.md`
2. `frontmatterValidity`锛歚.cursor/skills/**/SKILL.md` 鐨?`name` 涓庣洰褰曞悓鍚?3. `entrypointAvailability`锛歚/xijia:start`銆乣/xijia:status`銆乣/xijia:stop` 鍏ュ彛鏂囦欢瀛樺湪涓斿熀纭€瀛楁瀹屾暣
4. `driftScan`锛氭寜瑙勫垯婕傜Щ榛戝悕鍗曟壂鎻忥紙瑙?`06-rule-drift-guard.mdc`锛?
杈撳嚭瑕佹眰锛?
- 閫愰」缁欏嚭 `pass/fail` 涓庢槑缁?- 浠讳竴澶辫触鍗?`blocked`锛屼笉寰楄繘鍏?`done`
- 蹇呴』闄勪慨澶嶅缓璁笌閲嶈瘯璺緞

## 杈撳嚭鏍煎紡锛堝浐瀹氾級

```markdown
## Xijia Init Status

- Stage: <guard|interview|manifest-confirm|scaffold|skills-bootstrap|done>
- Mode: <empty-repo|supplement-only>
- Created: <created files>
- Skipped: <existing files kept untouched>
- Stack Confirmed: <summary>
- Skills Selected: <name + score + source>
- Skills Installed: <success list>
- Skills Skipped: <name + reason; not found / install failed / cap reached>
- Next: </xijia:start ...>
- Blockers: <none or list>
```

## 澶辫触澶勭悊

- 闈炵┖浠撳簱锛氫腑姝㈠苟鎻愮ず鈥滀娇鐢?`/xijia:start` 鎴栬繘鍏ヨˉ榻愭ā寮忥紙浠呮柊澧炰笉瑕嗙洊锛夆€?- 鎶€鑳藉畨瑁呭け璐ワ細璁板綍澶辫触椤逛笌閲嶈瘯鍛戒护锛屼笉涓柇鏂囨。鍒濆鍖栫粨鏋滃洖鎶?- `self-check` 澶辫触锛氱姸鎬佺疆涓?`blocked`锛岃緭鍑哄け璐ラ」涓庝慨澶嶅缓璁紝绂佹瀹ｅ憡鍒濆鍖栧畬鎴?

## Install Enforcement (Hard Gate)

- Default install strategy is `auto install`.
- Use `recommendation-only` only when the user explicitly selects it.
- **数量上限**：init 阶段安装到 `.cursor/skills/` 的栈相关 skill **≤10**；超过即 `blocked`，须卸载多余项后重跑 self-check。
- **禁止整库 / 乱装**：不得执行 `npx skills add <owner>/<repo> -y` 等无 skill 过滤的 bulk 命令；不得用未入选、未评分、与技术栈无关的 skill 顶替。
- **找不到就不装**：按 **单个 skill 名/路径** 安装；失败或未找到 → `Skills Skipped` + 原因，写入 backlog（可选），**继续 init**；禁止整库 fallback、禁止“相似 skill”自动替换。
- **`skills-lock.json`**：若生成，条目数须 **≤10** 且与 Init Report 一致；>10 视为误装，`blocked`。
- In `auto install` mode:
  - **全部跳过 / 0 个成功**：允许 `done`（文档骨架与 self-check 通过即可）；Init Report 须列明 skipped 项
  - report install evidence (`commands + key outputs + skip/fail reasons`) in Init Status
