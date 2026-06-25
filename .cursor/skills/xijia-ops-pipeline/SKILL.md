---
name: xijia-ops-pipeline
description: 缁熶竴缂栨帓闇€姹傚垎绾с€丱penSpec 宸ヤ綔娴併€丼uperpowers 瀹炵幇鏂规硶鍜屽綊妗ｅ洖鐏屻€傜敤浜庣敤鎴峰笇鏈涗竴閿帹杩涚鍒扮鐮斿彂銆佸噺灏戞紡姝ラ銆佸己鍒堕棴鐜椂銆?---

# Xijia Ops Pipeline

## 鐩爣

鎻愪緵涓€涓粺涓€鍏ュ彛锛屽皢鏈」鐩殑瑙勫垯銆佸懡浠や笌鎶€鑳戒覆鎴愬彲鎵ц闂幆锛?
- 闇€姹傚垎绾э紙green/yellow/red锛?- change 绫诲瀷鍒ゅ畾锛坆usiness/technical/hybrid锛?- OpenSpec 浜х墿涓庡疄鐜?- Superpowers 鐨?TDD/璋冭瘯/楠岃瘉/璇勫
- 褰掓。涓庣煡璇嗗洖鐏岋紙change 鑽夌 -> docs/domain锛?
## 浣曟椂浣跨敤

褰撶敤鎴疯〃杈句互涓嬫剰鍥炬椂浣跨敤锛?
- 鈥滃畬鏁存帹杩涜繖涓渶姹傗€?- 鈥滄寜椤圭洰鏍囧噯浠庨渶姹傚仛鍒板綊妗ｂ€?- 鈥滀笉瑕佹紡姝ラ锛屽府鎴戣窇瀹屾暣娴佺▼鈥?- 鈥渪ijia 娴佺▼鏉ヤ竴閬嶁€?
## 杈撳叆

- 闇€姹傛弿杩帮紙蹇呭～锛?- 鍙€?change 鍚嶇О锛坘ebab-case锛?- 鍙€夊鏉傚害鍋忓ソ锛堥粯璁よ嚜鍔ㄥ垎绾э級

## 鍥哄畾绾︽潫

1. 涓ユ牸閬靛畧 `.cursor/rules/00-workflow.mdc`
2. 鍏堝垎绾у啀閫夋祦绋嬶紙green/yellow/red锛?3. 鍏堝垽 change type 鍐?propose锛坆usiness/technical/hybrid锛?4. 鏈綊妗ｉ鍩熻崏绋垮彧鍐?`docs/openspec/changes/<name>/domain/`
5. 浠呭湪褰掓。鍚庨€氳繃 `sync-knowledge` 鎻愬崌鍒?`docs/domain/*`

## 缂栨帓鎬昏

### A. 鍏ュ彛鍒嗙骇锛堝繀椤伙級

鍏堟寜澶嶆潅搴﹀垎妗ｏ細

- **green**锛氶厤缃?鏂囨/鏍峰紡/绠€鍗曠嫭绔嬫敼鍔? 
  -> 璋冪敤 `writing-plans`锛岃鍒掑彲钀?`docs/plans/`锛岄€氬父涓嶈繘 OpenSpec
- **yellow**锛氬崟涓婁笅鏂囧父瑙勫姛鑳? 
  -> `writing-plans` + 鍙€?`brainstorming`锛屽繀瑕佹椂鍐嶅崌 red
- **red**锛氭牳蹇冧笟鍔°€佸鏉傝鍒欍€佽法涓婁笅鏂? 
  -> 杩涘叆瀹屾暣 OpenSpec + Superpowers 娴佺▼锛圔 娈碉級
- **馃И spike锛堟帰閽堬紝姝ｄ氦浜庡鏉傚害锛?*锛氶摼璺弗閲嶄笉娓?鍙鎬ф湭鐭ユ椂鍏堟帰璺? 
  -> 璧?green 鐨勮交閲忚妭濂忥紝鍙戠幇钀?`docs/plans/<spike-name>.md`锛泂pike 浠ｇ爜涓嶅緱褰撴垚鏋滀氦浠橈紝浜у嚭鍠傛寮?change 閲嶅仛

濡傛灉鎷夸笉鍑嗭細鍏堜綆妗ｏ紝澶嶆潅搴︿笂鍗囧啀鍗囩骇銆?
**杩唬鍒囩墖锛堥粯璁ゅЭ鎬侊級**锛氶渶姹傛棤娉曚竴娆℃弿杩板畬鏃讹紝涓€涓?change = 涓€鏉＄鍒扮钖勫垏鐗囷紙闈炴暣妯″潡锛夛紝鍛藉悕鍒囩墖鍖栵紱proposal 蹇呭惈 `In Scope / Out of Scope / Open Questions & Deferred` 涓夋锛屾兂涓嶆竻鐨勯摼璺樉寮?park銆?
### A.1 Green/Yellow 鏀跺熬娓呭崟锛堝繀椤伙級

褰撻渶姹備笉杩涘叆 OpenSpec锛堭煙?馃煛锛夋椂锛屾敹灏惧繀椤婚€愰」鍕鹃€夛細

1. 楠岃瘉璇佹嵁宸茶緭鍑猴紙娴嬭瘯/鏋勫缓/妫€鏌ュ懡浠ょ粨鏋滐級
2. 宸叉墽琛屻€屾矇娣€涓夐棶銆嶅苟鍐欏叆鍘诲悜锛?   - 涓氬姟瑙勫垯/涓嶅彉閲?-> `docs/domain/*`
   - 鍐崇瓥鍘熷洜 -> `docs/decisions/*`锛圓DR锛?   - 瀛楁涓氬姟璇箟 -> `docs/domain/data-dictionary.md`
3. 鍛戒腑瑙﹀彂鏉′欢鏃舵洿鏂?`docs/capability-map.md`
4. 鍐欏叆浜哄伐楠屾敹璇存槑锛堥渶姹傛枃妗ｆ垨 `docs/plans/*`锛?5. 涓诲姩鎻愮ず鐢ㄦ埛鎵ц commit锛涙湭 commit 涓嶅緱寮€濮嬩笅涓€闇€姹?
### B. Red 妗ｅ畬鏁撮摼璺?
1. **鎺㈢储**
   - 璋冪敤 `openspec-explore`
   - 鑻ヤ负 business/hybrid锛氳皟鐢?`ddd-modeling`锛屽啓 `docs/openspec/changes/<name>/domain/`

2. **鎻愭**
   - 璋冪敤 `openspec-propose`锛堟垨 `/opsx:propose`锛?   - 寮哄埗鍐欏叆 change type锛歚business|technical|hybrid`

3. **涓€鑷存€у垎鏋愶紙瀹炵幇鍓嶉椄闂級**
   - 璋冪敤 `openspec-analyze`锛堟垨 `/opsx:analyze`锛?   - 鑻?`Verdict: blocked`锛屽厛淇?`proposal/design/tasks/spec` 鍐嶈繘鍏ュ疄鐜?
4. **瀹炵幇**
   - 蹇呴』璋冪敤 `openspec-superpowers-apply`
   - 瀹炵幇鏈熷己鍒舵妧鑳介摼锛?     - `test-driven-development`
     - `systematic-debugging`锛堝け璐ユ椂锛?     - `verification-before-completion`
     - `requesting-code-review`

5. **瑙勬牸鍚屾**
   - 璋冪敤 `openspec-sync-specs`锛堟垨 `/opsx:sync`锛?
6. **褰掓。**
   - 璋冪敤 `openspec-archive-change`锛堟垨 `/opsx:archive`锛?
7. **鐭ヨ瘑鍥炵亴**
   - 璋冪敤 `sync-knowledge`
   - 灏嗗凡钀藉湴鍐呭浠?change 鑽夌 `docs/openspec/changes/<name>/domain/*` 鎻愬崌鍒?`docs/domain/*`

### C. 鏀惧純璺緞

褰撶敤鎴峰喅瀹氫腑姝細

- 璋冪敤 `abandon-change`
- 涓㈠純 change 鑽夌锛堥殢 change 涓€骞舵斁寮冿紝`docs/domain` 涓嶅彈褰卞搷锛?- 涓嶆墽琛?sync

## Approval Gates锛堝懡涓嵆鏆傚仠锛?
鍑虹幇浠ヤ笅浠讳竴椤瑰繀椤昏姹傜敤鎴风‘璁わ細

- 鐮村潖鎬ф暟鎹簱鍙樻洿
- 鏂板鍏抽敭澶栭儴渚濊禆
- 鍒犻櫎/涓嬬嚎宸蹭笂绾胯兘鍔?- 鏉冮檺銆佸瘑閽ャ€佸畨鍏ㄧ瓥鐣ュ彉鏇?- 璺ㄩ檺鐣屼笂涓嬫枃澶ц皟鏁?
## 姣忛樁娈佃緭鍑烘ā鏉?
```markdown
## Xijia Pipeline Status

- Tier: <green|yellow|red>
- Change Type: <business|technical|hybrid>
- Stage: <explore|propose|analyze|apply|verify|sync|archive|sync-knowledge|abandon>
- Done: <what completed>
- Next: <next command/skill>
- Blockers: <none or list>
```

## 瀹屾垚鍒ゅ畾锛堥棴鐜畾涔夛級

浠呭綋婊¤冻浠ヤ笅**鍏ㄩ儴**鏉′欢鎵嶅彲瀹ｅ憡**褰撳墠闇€姹?*瀹屾垚锛屽苟杩涘叆涓嬩竴闇€姹傦細

1. 浠诲姟瀹炵幇涓庨獙璇侀€氳繃锛堟湁鍛戒护璇佹嵁锛?2. 鏈垏鐗?In Scope 鐨?AC 鍧囨湁閫氳繃娴嬭瘯锛坄Deferred` AC 闄ゅ锛?3. specs 宸插悓姝ワ紙鎴栨槑纭‘璁よ烦杩囧苟璇存槑鍘熷洜锛?4. change 宸插綊妗?5. `sync-knowledge` 宸叉墽琛岋紙馃敶锛夛紱馃煝/馃煛 绛変环鏂囨。宸叉洿鏂?6. `docs/domain` 涓?change 鑽夌鐘舵€佷竴鑷达紝鏃犳偓鎸傛潯鐩?7. **宸插啓鍏ャ€屼汉宸ラ獙鏀惰鏄庛€?*锛氳拷鍔犲埌闇€姹傛枃浠?`# 楠屾敹璁板綍` 娈碉紙馃煝/馃煛 鍙湁璁″垝鏂囨。鏃惰拷鍔犲埌 `docs/plans/`锛夛紝骞跺湪鎽樿澶嶈堪
8. **commit 鏀跺熬鐘舵€佸凡鏄庣‘**锛氳嫢鐢ㄦ埛宸茶姹傛彁浜わ紝鍒?commit 蹇呴』鎴愬姛锛涜嫢鐢ㄦ埛灏氭湭瑕佹眰鎻愪氦锛屽繀椤绘槑纭爣娉ㄢ€滃緟鐢ㄦ埛瑙﹀彂 commit鈥濓紝涓斾笉寰楀紑濮嬩笅涓€闇€姹?
> 馃煝/馃煛 涓嶈蛋 OpenSpec锛屼絾绗?7鈥? 鏉″悓鏍峰繀椤绘弧瓒炽€?
**杩涘叆涓嬩竴闇€姹傚墠**锛氳繍琛?`git status`锛屼笉寰楀瓨鍦ㄤ笂涓€闇€姹傜殑鏈彁浜ゆ敼鍔紱鑻ユ湁锛屽厛瀹屾垚 commit 鍐嶇户缁€?
## 寤鸿璋冪敤鏂瑰紡

- 鏄惧紡璋冪敤锛歚浣跨敤 xijia-ops-pipeline 鎺ㄨ繘杩欎釜闇€姹俙
- 瀵?red 妗ｏ細浼樺厛浠庘€滃垎绾?+ 鍒ゅ瀷 + explore鈥濆紑濮嬶紝涓嶇洿鎺ュ啓浠ｇ爜


## 自治护栏（预算与恢复）

- 命中长链自治任务时，启用 51-autonomy-guards.mdc：预算阈值 + stop-and-report。
- 恢复点以 	asks.md 勾选与 openspec status 为准。

