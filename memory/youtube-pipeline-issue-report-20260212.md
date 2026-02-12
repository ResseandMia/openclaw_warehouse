# YouTube Pipeline 执行问题报告

**执行时间**: 2026-02-12 15:55 - 16:10 (UTC+8)  
**视频**: How Organic Dropshipping Actually Works Now - Mark Builds Brands  
**执行模式**: 单 Agent 全流程 (Kimi K2.5)  
**技能版本**: Claude 优化版 (2026-02-12)

---

## 问题汇总

| 序号 | 问题 | 严重程度 | 影响步骤 | 状态 |
|------|------|----------|----------|------|
| 1 | Nano Banana API 图片生成失败 | 高 | Step 4 | 未解决 |
| 2 | Prompt 过长可能导致失败 | 中 | Step 4 | 待验证 |
| 3 | 卡片图包含中文文本 | 低 | Step 4 | 待验证 |
| 4 | Notion 分段写入需要优化 | 低 | Step 5 | 已解决 |

---

## 问题详情

### 问题 1: Nano Banana API 图片生成失败 ⚠️ 严重

**现象**:
- 3张图片全部生成失败
- 状态: `status=3` (失败)
- 错误信息: `"系统错误 请重试"`

**时间线**:
```
15:55:21 - 提交3张图片任务
15:55:26 - 第1次轮询: status=0 (进行中)
15:55:31 - 第2次轮询: status=0 (进行中)
15:55:36 - 第3次轮询: status=0 (进行中)
15:55:41 - 第4次轮询: status=0 (进行中)
15:55:46 - 第5次轮询: status=0 (进行中)
15:55:51 - 第6次轮询: status=0 (进行中)
16:01:xx - 最终查询: status=3 (全部失败)
```

**分析**:
1. 任务提交成功，获取了 task ID
2. 轮询过程中状态一直为0（进行中）
3. 最终状态变为3（失败）
4. 3张图都是同样的错误

**可能原因**:
1. **Prompt 过长**: 每张图85-92个词，加上 base style 前缀约25词，总计110-117词
2. **包含中文**: 卡片图的 prompt 包含"内容与文案的残酷真相"
3. **场景描述复杂**: 包含多个对象和细节（fidget spinners, mini cameras, crossroad sign等）
4. **API 服务不稳定**: 可能是服务商临时问题

**降级方案执行**:
- ✅ 使用视频原始缩略图替代
- ✅ 版本B文章中替换占位符
- ✅ 如实报告失败状态

**建议**:
1. 缩短 Prompt 到 50-60 词
2. 去掉中文，使用英文描述
3. 简化场景，减少对象数量
4. 考虑添加备用图片服务（DALL-E）

---

### 问题 2: Prompt 过长

**现象**:
- PROMPT_COVER: 约 110 词
- PROMPT_INLINE: 约 113 词
- PROMPT_CARD: 约 117 词

**当前 Prompt 结构**:
```
BASE_STYLE (25词) + VISUAL_DESCRIPTION (35-45词) + COMPOSITION (15-20词) + ASPECT_RATIO (3词)
```

**优化建议**:
```
BASE_STYLE (25词) + SIMPLIFIED_VISUAL (20-25词) + ASPECT_RATIO (3词)
目标: 50-60 词总计
```

**简化示例**:
```
# 原封面图 Prompt (110词)
cute kawaii-style digital illustration, warm beige/cream background, soft pastel colors, 
rounded cartoon elements, cheerful decorative details like confetti and banners, clean layout, 
friendly and professional, flat design with subtle shadows, a cute cat with shocked expression 
looking at a laptop screen showing dollar signs and shopping bags, surrounded by nostalgic 
2018-style fidget spinners and mini cameras, wide banner composition with space for title 
text on the right side, 16:9 aspect ratio

# 简化后 (55词)
cute kawaii-style digital illustration, warm beige background, soft pastel colors, 
rounded cartoon elements, cheerful details, a cute cat with laptop and shopping bags, 
16:9 aspect ratio
```

---

### 问题 3: 卡片图包含中文

**现象**:
- 卡片图 prompt 包含: `"内容与文案的残酷真相"`
- Nano Banana API 可能对中文支持不佳

**当前卡片图 Prompt**:
```
...with prominent Chinese text reading '内容与文案的残酷真相'...
```

**建议**:
1. 去掉中文文本
2. 改用英文描述文字内容
3. 或不在图片中包含文字，后期用工具添加

---

### 问题 4: Notion 分段写入优化

**现象**:
- 初次尝试写入完整文章失败
- 需要分批追加内容

**解决方案**:
采用三段式写入:
1. 第一段: 页面创建 + 属性 + 存档版开头
2. 第二段: 存档版完整内容
3. 第三段: 二创文章（分3次追加）
4. 第四段: 素材区域和状态汇总

**执行结果**:
- ✅ 成功分段写入
- ✅ 内容完整保留
- ✅ 无截断或丢失

---

## 成功经验

### ✅ 正确执行的项目

1. **字幕提取**: TranscriptAPI 调用成功，1764字符
2. **内容消化**: Kimi K2.5 生成，符合质量门禁
3. **API 接口**: 使用正确的 `/api/async/detail` 接口
4. **轮询逻辑**: 5秒间隔，3图并行轮询
5. **降级策略**: 图片失败时使用视频缩略图
6. **状态报告**: 如实报告每张图的实际状态
7. **Notion 写入**: 分段写入成功，内容完整

### ✅ 优化后的改进

1. **强制使用 Kimi K2.5** - 未降级到 MiniMax
2. **必须调用 TranscriptAPI** - 未使用摘要替代
3. **图片 Prompt 包含 base style** - 硬编码前缀
4. **状态报告准确** - 明确说明失败情况
5. **Notion 分段写入** - 完整保留内容

---

## 成本统计

| 项目 | 计划成本 | 实际成本 | 差异 |
|------|----------|----------|------|
| Transcript API | 1 credit | 1 credit | ✅ |
| 图片生成 (3张) | ¥0.09 | ¥0.00 | 失败未扣费 |
| **总计** | **1 credit + ¥0.09** | **1 credit** | 节省 ¥0.09 |

---

## 后续行动建议

### 短期 (立即)
1. 缩短图片 Prompt 到 50-60 词
2. 去掉中文文本
3. 重新测试图片生成

### 中期 (本周)
1. 添加备用图片服务（DALL-E）
2. 优化 Prompt 模板
3. 添加图片生成重试机制

### 长期 (本月)
1. 监控 Nano Banana API 稳定性
2. 考虑多服务商并行策略
3. 建立图片生成成功率统计

---

## 附件

### 失败的 Task IDs
- 封面图: `image_a95ffaf1-80bd-4f24-97c2-7b3395dac548`
- 配图: `image_1e9fcc4f-24b8-4423-98d6-97499855cf93`
- 卡片图: `image_27072063-de21-4e68-b5c2-89e4e1b74886`

### Notion 页面
- 链接: https://www.notion.so/How-Organic-Dropshipping-Actually-Works-Now-Mark-Builds-Brands-30583d24986d8118acd1effefac8d685
- ID: `30583d24-986d-8118-acd1-effefac8d685`

---

**报告生成时间**: 2026-02-12 16:25 UTC+8  
**报告人**: 咪咪大人 🐱
