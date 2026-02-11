# 微信公众号 HTML 优化案例

## 案例 1：干货教程类文章

### 优化前（问题）
```html
<section>
  <p>
    <span leaf="">如果你在跑 Meta 广告，一定听过这句话：</span>
    <strong><span leaf="">如果某个广告系列正在稳定出单，就别动它。</span></strong>
  </p>
  <p>
    <span leaf="">每次编辑都可能打乱算法。</span>
  </p>
  <p>
    <strong><span leaf="">❄️ "雪花球"比喻</span></strong>
  </p>
  <p>
    <span leaf="">有个投手把 Meta 算法比作雪花球：</span>
  </p>
  <p>
    <strong><span leaf="">摇晃雪花球</span></strong>
    <span leaf=""> = 你做任何操作</span>
  </p>
</section>
```

**问题分析：**
- ❌ 大量无用的 `<span leaf="">` 标签
- ❌ 没有视觉层次
- ❌ 重点内容没有突出
- ❌ 缺少间距和呼吸感
- ❌ 看起来像纯文本

### 优化后（效果）
```html
<section style="padding: 16px; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; line-height: 1.8; color: #333; font-size: 16px;">

  <!-- 开场 -->
  <p style="margin-bottom: 20px;">
    如果你在跑 Meta 广告，一定听过这句话：
  </p>
  
  <!-- 核心观点卡片 -->
  <p style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; padding: 16px 20px; border-radius: 8px; font-weight: 600; font-size: 17px; margin-bottom: 24px; text-align: center;">
    如果某个广告系列正在稳定出单，就别动它。
  </p>
  
  <p style="margin-bottom: 32px; color: #666;">
    每次编辑都可能打乱算法，让原本跑得好的广告突然崩掉。
  </p>

  <!-- 小节标题 -->
  <p style="font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 16px; padding-left: 12px; border-left: 4px solid #667eea;">
    ❄️ "雪花球"比喻
  </p>
  
  <p style="margin-bottom: 16px; color: #555;">
    有个投手把 Meta 算法比作雪花球，我觉得这个比喻挺形象的：
  </p>

  <!-- 比喻解释卡片 -->
  <div style="background: #f8f9fc; border-radius: 12px; padding: 20px; margin-bottom: 24px;">
    <p style="margin-bottom: 12px;">
      <span style="background: #667eea; color: #fff; padding: 4px 10px; border-radius: 4px; font-size: 14px; font-weight: 600;">摇晃雪花球</span>
      <span style="color: #555; margin-left: 8px;">= 你做任何操作：开广告、关广告、改设置……雪花四处飞散</span>
    </p>
    <p style="margin-bottom: 0;">
      <span style="background: #28a745; color: #fff; padding: 4px 10px; border-radius: 4px; font-size: 14px; font-weight: 600;">雪花沉淀</span>
      <span style="color: #555; margin-left: 8px;">= 不做任何操作时，算法最稳定</span>
    </p>
  </div>

</section>
```

**优化要点：**
- ✅ 清除所有无用标签
- ✅ 核心观点用渐变卡片突出
- ✅ 标题用左边框样式
- ✅ 比喻用标签+卡片组合
- ✅ 合理的间距和留白
- ✅ 统一的字体和行高

---

## 案例 2：观点类文章

### 优化前
```html
<p>我认为AI不会取代程序员，原因有三：</p>
<p>第一，AI写代码还不够可靠。</p>
<p>第二，编程不只是写代码，还有沟通和理解需求。</p>
<p>第三，AI是工具，工具需要人来使用。</p>
<p>总结：AI是助手，不是替代品。</p>
```

### 优化后
```html
<section style="padding: 16px; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif; line-height: 1.8; color: #333; font-size: 16px;">

  <p style="margin-bottom: 24px;">
    我认为 AI 不会取代程序员，原因有三：
  </p>

  <!-- 观点1 -->
  <div style="background: #fff; border: 1px solid #eee; border-radius: 12px; padding: 20px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
    <p style="font-size: 17px; font-weight: 700; color: #667eea; margin-bottom: 8px;">
      ① AI 写代码还不够可靠
    </p>
    <p style="color: #666; margin-bottom: 0; font-size: 15px;">
      经常出现逻辑错误、安全漏洞，需要人工审核
    </p>
  </div>

  <!-- 观点2 -->
  <div style="background: #fff; border: 1px solid #eee; border-radius: 12px; padding: 20px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
    <p style="font-size: 17px; font-weight: 700; color: #667eea; margin-bottom: 8px;">
      ② 编程不只是写代码
    </p>
    <p style="color: #666; margin-bottom: 0; font-size: 15px;">
      还有沟通、理解需求、架构设计、团队协作
    </p>
  </div>

  <!-- 观点3 -->
  <div style="background: #fff; border: 1px solid #eee; border-radius: 12px; padding: 20px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
    <p style="font-size: 17px; font-weight: 700; color: #667eea; margin-bottom: 8px;">
      ③ AI 是工具
    </p>
    <p style="color: #666; margin-bottom: 0; font-size: 15px;">
      工具需要人来使用，就像汽车需要司机
    </p>
  </div>

  <!-- 总结 -->
  <p style="background: #1a1a2e; color: #fff; padding: 18px 20px; border-radius: 8px; font-weight: 600; font-size: 17px; text-align: center; margin-bottom: 0;">
    🔑 AI 是助手，不是替代品
  </p>

</section>
```

---

## 案例 3：对比类内容

### 优化前
```html
<p>正确做法：</p>
<p>- 每24小时只加20%预算</p>
<p>- 让广告自己跑</p>
<p>错误做法：</p>
<p>- 每天翻倍预算</p>
<p>- 频繁修改文案</p>
```

### 优化后
```html
<section style="padding: 16px; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif; line-height: 1.8; color: #333; font-size: 16px;">

  <!-- 正确做法 -->
  <div style="background: #d4edda; border-radius: 12px; padding: 20px; margin-bottom: 16px;">
    <p style="font-size: 17px; font-weight: 700; color: #155724; margin-bottom: 14px;">
      ✅ 正确做法
    </p>
    <p style="color: #155724; margin-bottom: 8px;">• 每 24-48 小时只加 20%-50% 预算</p>
    <p style="color: #155724; margin-bottom: 0;">• 让广告自己跑，积累数据</p>
  </div>

  <!-- 错误做法 -->
  <div style="background: #f8d7da; border-radius: 12px; padding: 20px; margin-bottom: 0;">
    <p style="font-size: 17px; font-weight: 700; color: #721c24; margin-bottom: 14px;">
      ❌ 错误做法
    </p>
    <p style="color: #721c24; margin-bottom: 8px;">• 每天翻倍预算</p>
    <p style="color: #721c24; margin-bottom: 0;">• 频繁修改文案</p>
  </div>

</section>
```

---

## 常见优化清单

### 必做项
- [ ] 清除 `<span leaf="">` 等无用标签
- [ ] 添加根容器 `<section>` 并设置基础样式
- [ ] 统一字体、字号、行高
- [ ] 核心观点用卡片/背景色突出
- [ ] 标题添加左边框或底部线条
- [ ] 段落之间有合理间距（margin-bottom）
- [ ] 保留微信特殊标签（如 `<mp-style-type>`）

### 可选项
- [ ] 添加 emoji 增强可读性
- [ ] 使用渐变色提升视觉效果
- [ ] 重要数字/关键词用标签突出
- [ ] 总结部分用深色背景
- [ ] 对比内容用不同背景色区分
