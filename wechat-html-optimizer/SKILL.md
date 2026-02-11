---
name: wechat-html-optimizer
description: 优化微信公众号文章的HTML代码，使其更专业、美观、易读。当用户提供微信公众号的HTML内容并要求优化、美化、排版时触发此skill。触发词包括：微信公众号、公众号排版、微信文章优化、HTML美化、公众号HTML、微信排版、wechat article、mp weixin等。
---

# 微信公众号 HTML 优化器

将杂乱的微信公众号 HTML 代码转换为专业、美观、移动端友好的排版。

## 触发条件

- 用户提供微信公众号的 HTML 代码
- 用户要求优化/美化/排版公众号文章
- 用户提到"微信"、"公众号"、"mp"等关键词配合 HTML 内容

## 设计原则

### 1. 移动优先
- 微信公众号 90%+ 流量来自手机
- 所有尺寸使用 `px` 而非 `rem`（微信不支持 rem）
- 字号最小 14px，正文建议 16px
- 行高建议 1.75-1.8
- 内边距 16-20px

### 2. 视觉层次
- **一级标题**：20-22px，粗体，配合左边框或底色
- **二级标题**：17-18px，粗体
- **正文**：16px，行高 1.8
- **辅助文字**：14-15px，灰色 #666 或 #888

### 3. 色彩系统

#### 推荐主色方案
| 风格 | 主色 | 渐变 |
|------|------|------|
| 商务蓝 | `#2B5CE6` | `linear-gradient(135deg, #667eea 0%, #764ba2 100%)` |
| 活力橙 | `#FF6B35` | `linear-gradient(135deg, #f093fb 0%, #f5576c 100%)` |
| 清新绿 | `#11998e` | `linear-gradient(135deg, #11998e 0%, #38ef7d 100%)` |
| 科技紫 | `#667eea` | `linear-gradient(135deg, #667eea 0%, #764ba2 100%)` |
| 沉稳黑 | `#1a1a2e` | `linear-gradient(135deg, #434343 0%, #000000 100%)` |

#### 功能色
| 用途 | 颜色 | 背景色 |
|------|------|--------|
| 提示/信息 | `#1a5276` | `#e8f4fd` |
| 警告/注意 | `#856404` | `#fff3cd` |
| 成功/正确 | `#28a745` | `#d4edda` |
| 错误/危险 | `#e74c3c` | `#f8d7da` |
| 中性/引用 | `#555` | `#f8f9fc` |

### 4. 组件库

详见 `references/components.md`

## 优化流程

### Step 1: 分析原始内容
- 识别内容结构（标题、段落、列表、引用等）
- 提取核心观点和关键信息
- 判断文章风格（干货、故事、教程、观点等）

### Step 2: 规划视觉层次
- 确定主色调（根据内容调性）
- 规划重点突出元素（核心观点、金句、结论）
- 设计信息卡片和分隔方式

### Step 3: 应用组件
- 用卡片组件包装重要内容
- 用标签/徽章突出关键词
- 用图标增强可读性
- 用分隔线划分内容区块

### Step 4: 代码清理
- 移除多余的 `<span leaf="">` 等无用标签
- 合并重复的样式
- 确保所有样式都是内联的（微信要求）
- 保留必要的微信特殊标签（如 `<mp-style-type>`）

## 微信 HTML 限制

### 必须遵守
- ✅ 所有样式必须内联（`style="..."`）
- ✅ 使用 `px` 单位，不用 `rem`/`em`
- ✅ 图片使用 `data-src` 属性
- ✅ 保留 `<section>` 作为根容器
- ✅ 保留 `<mp-style-type>` 等微信特殊标签

### 不支持的特性
- ❌ 外部 CSS 文件
- ❌ `<style>` 标签
- ❌ CSS 类名（`.class`）
- ❌ JavaScript
- ❌ `position: fixed`
- ❌ `@media` 媒体查询
- ❌ CSS 变量 `var(--xxx)`
- ❌ `rem`/`em`/`vh`/`vw` 单位

## 输出格式

```html
<section style="padding: 16px; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; line-height: 1.8; color: #333; font-size: 16px;">

  <!-- 文章内容 -->

</section>
<p style="display: none;">
  <mp-style-type data-value="10000"></mp-style-type>
</p>
```

## 常用图标参考

微信支持的 Unicode 表情/符号：
- 💡 提示/想法
- 📌 重点/固定
- ✅ 正确/完成
- ❌ 错误/禁止
- ⚠️ 警告
- 🔑 关键点
- 🎯 目标/答案
- 📊 数据/图表
- 💰 金钱/价格
- 🔥 热门/火爆
- ❄️ 冷门/冷却
- ⭐ 星级/推荐
- 👆 向上指/上文
- 👇 向下指/下文
- ① ② ③ ④ ⑤ 序号

## 参考文件

- `references/components.md` - 完整组件代码库
- `references/color-schemes.md` - 更多配色方案
- `references/examples.md` - 优化案例对比
